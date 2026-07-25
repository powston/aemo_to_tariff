import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from aemo_to_tariff.ausgrid import convert_feed_in_tariff, time_zone, convert, calculate_demand_fee

class TestAusgrid(unittest.TestCase):
    def test_ea_025_peak(self):
        # April is a shoulder month for EA025 (peak_months = Nov-Mar + Jun-Aug),
        # so Peak is skipped and off-peak applies at 5.1535 c/kWh in 2025–26.
        # Previously this test asserted the buggy slope/intercept fallback of
        # ~22.13 because the off-peak window didn't cover 17:45.
        interval_time = datetime(2025, 4, 22, 17, 45, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'EA025'
        rrp = 136.7
        expected_price = (rrp / 10 + 5.1535) * 1.12
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price * 1.0902, expected_price, places=2)
        feed_in = convert_feed_in_tariff(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(feed_in, 13.66, places=1)
    
    def test_ea_029_peak_summer(self):
        interval_time = datetime(2025, 1, 22, 17, 45, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'EA029'
        rrp = 299.99
        expected_price = 35.25773521
        price = convert_feed_in_tariff(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.042, expected_price, places=1)
    
    
    def test_ea_025_peak_summer(self):
        interval_time = datetime(2025, 1, 22, 17, 45, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'EA025'
        rrp = 136.7
        expected_price = 48.0648
        price = convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.0485, expected_price, places=1)
    
    def test_feed_ausgrid_functionality(self):
        interval_time = datetime(2023, 1, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 100.0)
        self.assertAlmostEqual(feed_in_price, 10.00, places=1)

    def test_ea_305_demand(self):
        tariff_code = 'EA305'
        expected_price = 1611.0919
        price = calculate_demand_fee(tariff_code, 179.05, 30)
        self.assertAlmostEqual(price, expected_price, places=1)

    def test_ea_305_peak(self):
        # EA305 LV business is non-seasonal (no peak_months) — Peak applies
        # year-round, 15:00–22:59 at 7.3723 c/kWh in 2025–26.
        # Previously this assertion targeted the buggy slope/intercept default
        # of ~22.1471 because Peak was being skipped on every tariff without
        # peak_months. Now it asserts the real Peak rate.
        interval_time = datetime(2025, 4, 22, 17, 45, tzinfo=ZoneInfo(time_zone()))
        rrp = 136.7
        expected_price = (rrp / 10 + 7.3723) * 1.12
        price = convert(interval_time, 'EA305', rrp)
        self.assertAlmostEqual(price * 1.0821, expected_price, places=2)
    
    def test_ea_305_off_peak(self):
        interval_time = datetime(2025, 4, 22, 12, 45, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'EA305'
        rrp = 136.7
        expected_price = 17.192
        price = convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.1079, expected_price, places=1)

    def test_ea_025_peak_2026_27(self):
        # Post-1-Jul-2026: peak rate 29.245 → 32.5164
        interval_time = datetime(2026, 7, 22, 17, 45, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'EA025', 136.7)
        self.assertAlmostEqual(price, 13.67 + 32.5164 * 1.1, places=2)

    def test_ea_305_sunday_evening(self):
        # Regression: EA305 has no 'peak_months' field. Previously this caused
        # is_peak_month to be False year-round → Peak skipped → fall-through to
        # the slope/intercept default (~5.59 c/kWh + RRP). Should return Peak
        # rate at Sun 18:00.
        interval_time = datetime(2026, 1, 18, 18, 0, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'EA305', 0.0)
        self.assertAlmostEqual(price, 7.3723 * 1.1, places=4)

    def test_ea_025_shoulder_month_offpeak(self):
        # Regression: EA025 in a shoulder month (Apr/May/Sep/Oct) at peak time.
        # Peak is skipped (not in peak_months), and the off-peak window now
        # covers all 24h, so off-peak rate should apply.
        interval_time = datetime(2025, 4, 22, 17, 45, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'EA025', 0.0)
        self.assertAlmostEqual(price, 5.1535 * 1.1, places=4)