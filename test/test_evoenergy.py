import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
import aemo_to_tariff.evoenergy as evoenergy

class TestEvoenergy(unittest.TestCase):
    def test_some_evoenergy_functionality(self):
        interval_time = datetime(2025, 2, 20, 13, 45, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = '017'
        rrp = -27.14
        expected_price = 0.916755
        price = evoenergy.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.05, expected_price, places=2)

    def test_peak_evoenergy_functionality(self):
        interval_time = datetime(2025, 3, 28, 15, 55, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = '017'
        rrp = 119.63
        expected_price = 17.46672
        price = evoenergy.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 0.96, expected_price, places=1)

    def test_noon_evoenergy_april(self):
        interval_time = datetime(2025, 4, 30, 12, 00, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = '017'
        rrp = -23.5
        expected_price = 1.026793
        price = evoenergy.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        print(f"Loss factor: {loss_factor}")
        self.assertAlmostEqual(price * 0.83, expected_price, places=1)

    def test_peak_evoenergy_late_april(self):
        interval_time = datetime(2026, 4, 30, 7, 40, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = '017'
        rrp = -1.8
        expected_price = 18.82
        price = evoenergy.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        print(f"Loss factor: {loss_factor}")
        self.assertAlmostEqual(price * 1.06796, expected_price, places=1)

    def test_evoenergy_017_2026_27_peak(self):
        # Post-1-Jul-2026 New Residential TOU peak: 16.184 → 16.049 (incl 10% GST)
        interval_time = datetime(2026, 7, 20, 18, 0, tzinfo=ZoneInfo('Australia/Sydney'))
        price = evoenergy.convert(interval_time, '017', 100.0)
        self.assertAlmostEqual(price, 10.0 + 16.049 * 1.1, places=2)

    def test_evoenergy_090_midday(self):
        # Regression: tariff 090 has no peak_months. Previously is_peak_month
        # defaulted to False, so the 'Peak' period (7am–5pm) was always
        # skipped and any midday lookup fell through to the slope/intercept
        # default. Verify Peak now applies.
        interval_time = datetime(2025, 9, 16, 11, 0, tzinfo=ZoneInfo('Australia/Sydney'))
        price = evoenergy.convert(interval_time, '090', 0.0)
        # 2025–26 schedule peak rate 17.518 c/kWh × 1.1 GST = 19.27 c/kWh
        self.assertAlmostEqual(price, 17.518 * 1.1, places=2)

    def test_evoenergy_015_shoulder_month_morning(self):
        # Regression: 015 has peak_months [11,12,1,2,3,6,7,8]. In shoulder
        # months (Apr/May/Sep/Oct) at 8am Peak is skipped and previously no
        # other period covered 7-9, so the lookup fell through to the
        # slope/intercept default. Should now return Shoulder rate.
        interval_time = datetime(2025, 4, 15, 8, 0, tzinfo=ZoneInfo('Australia/Sydney'))
        price = evoenergy.convert(interval_time, '015', 0.0)
        self.assertAlmostEqual(price, 8.199 * 1.1, places=2)

    def test_evoenergy_018_shoulder_month_evening(self):
        # Same fix on 018: in shoulder months 17–21 should return Off-peak.
        interval_time = datetime(2025, 10, 15, 18, 0, tzinfo=ZoneInfo('Australia/Sydney'))
        price = evoenergy.convert(interval_time, '018', 0.0)
        self.assertAlmostEqual(price, 5.665 * 1.1, places=2)
