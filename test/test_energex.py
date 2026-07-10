import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
import aemo_to_tariff.energex as energex

BRISBANE = ZoneInfo('Australia/Brisbane')


class TestEnergex(unittest.TestCase):
    def test_feed_in_convert(self):
        interval_time = datetime(2023, 1, 15, 17, 0, tzinfo=BRISBANE)
        tariff_code = '6900'
        feed_in_price = energex.convert_feed_in_tariff(interval_time, tariff_code, 100.0)
        self.assertAlmostEqual(feed_in_price, 10.00, places=1)

    def test_convert_2025_26(self):
        # Before 1 July 2026 transition: uses 2025–26 prices (Overnight 4.868 c/kWh)
        interval_time = datetime(2023, 7, 15, 10, 0, tzinfo=BRISBANE)
        price = energex.convert(interval_time, '6900', 100.0)
        self.assertAlmostEqual(price, 14.868, places=2)

    def test_convert_2026_27(self):
        # On/after 1 July 2026: uses 2026–27 prices (Overnight 6.069 c/kWh)
        interval_time = datetime(2026, 7, 15, 10, 0, tzinfo=BRISBANE)
        price = energex.convert(interval_time, '6900', 100.0)
        self.assertAlmostEqual(price, 16.069, places=2)

    def test_get_daily_fee_2025_26(self):
        interval_time = datetime(2025, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('6900', 20000, interval_time=interval_time), 55.6, 3)

    def test_get_daily_fee_2026_27(self):
        interval_time = datetime(2026, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('6900', 20000, interval_time=interval_time), 65.1, 3)


class TestTwoWayTariff(unittest.TestCase):

    def test_import_peak_summer(self):
        # Summer peak: Jan 15, 18:00 → Peak rate 19.533
        dt = datetime(2027, 1, 15, 18, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 19.533, places=2)

    def test_import_offpeak_summer(self):
        # Summer off-peak: Jan 15, 12:00 → Off-Peak 0.434
        dt = datetime(2027, 1, 15, 12, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 0.434, places=2)

    def test_import_shoulder_summer(self):
        # Summer shoulder: Jan 15, 21:00 → Shoulder 6.069
        dt = datetime(2027, 1, 15, 21, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 6.069, places=2)

    def test_import_offpeak_nonsummer(self):
        # Non-summer off-peak: Jul 15, 12:00 → Off-Peak 0.434
        dt = datetime(2026, 7, 15, 12, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 0.434, places=2)

    def test_import_shoulder_nonsummer(self):
        # Non-summer shoulder (no peak period): Jul 15, 18:00 → Shoulder 6.069
        dt = datetime(2026, 7, 15, 18, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 6.069, places=2)

    def test_export_reward_summer(self):
        # Summer export reward: Jan 15, 18:00 → -12.195
        dt = datetime(2027, 1, 15, 18, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0 - 12.195, places=2)

    def test_export_charge_nonsummer(self):
        # Non-summer export charge 11:00-13:00: Jul 15, 12:00 → +2.210
        dt = datetime(2026, 7, 15, 12, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0 + 2.210, places=2)

    def test_export_bel_exempt(self):
        # BEL exempt window 10:00-11:00: Jul 15, 10:30 → 0 network
        dt = datetime(2026, 7, 15, 10, 30, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0 + 0.0, places=2)

    def test_export_no_charge_nonsummer_evening(self):
        # Non-summer evening export: no charge
        dt = datetime(2026, 7, 15, 20, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0, places=2)

    def test_pre_july_2026_returns_spot_only(self):
        # Before 1 July 2026 — tariff doesn't exist, should return spot only
        dt = datetime(2025, 12, 15, 18, 0, tzinfo=BRISBANE)  # summer but pre-2026-27
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0, places=2)  # spot only, no network

    def test_pre_july_2026_export_returns_spot_only(self):
        # Before 1 July 2026 — export, should return spot only
        dt = datetime(2025, 12, 15, 18, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0, places=2)  # spot only, no network

    def test_daily_fee_96200(self):
        # Fee table is $/day; get_daily_fee returns cents/day.
        interval_time = datetime(2026, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('96200', interval_time=interval_time), 65.1, 3)

    def test_translate_tariff_96200(self):
        # 96200 must not be truncated
        self.assertEqual(energex.translate_tariff('96200'), '96200')

    def test_convert_96200_dispatches(self):
        # Ensure convert() with tariff '96200' reaches convert_two_way_tariff
        dt = datetime(2027, 1, 15, 18, 5, tzinfo=BRISBANE)  # 18:05 → adjusted to 18:00 → peak
        price = energex.convert(dt, '96200', 100.0)
        self.assertAlmostEqual(price, 10.0 + 19.533, places=2)

    def test_convert_feed_in_tariff_96200x_dispatches(self):
        # Export via the public feed-in API must apply the seasonal reward/charge.
        summer = datetime(2027, 1, 15, 18, 5, tzinfo=BRISBANE)  # adjusted to 18:00 → reward
        self.assertAlmostEqual(energex.convert_feed_in_tariff(summer, '96200X', 100.0), 10.0 - 12.195, places=2)
        winter = datetime(2026, 7, 15, 12, 5, tzinfo=BRISBANE)  # adjusted to 12:00 → export charge
        self.assertAlmostEqual(energex.convert_feed_in_tariff(winter, '96200X', 100.0), 10.0 + 2.210, places=2)
        # Other tariffs remain spot-only.
        self.assertAlmostEqual(energex.convert_feed_in_tariff(summer, '6900X', 100.0), 10.0, places=2)
