import unittest
from zoneinfo import ZoneInfo
from datetime import datetime
from aemo_to_tariff.united import time_zone, convert, get_daily_fee

class TestUnited(unittest.TestCase):
    def test_convert(self):
        interval_time = datetime(2023, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'URTOU'
        rrp = 100.0
        expected_price = 14.76
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_get_daily_fee(self):
        tariff_code = 'URTOU'
        expected_fee = 31.51  # cents/day
        fee = get_daily_fee(tariff_code)
        self.assertEqual(fee, expected_fee)

    def test_convert_2026_27_peak(self):
        # Post-1-Jul-2026 URTOU peak: 19.13 → 20.92 c/kWh
        interval_time = datetime(2026, 7, 15, 18, 0, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'URTOU', 100.0)
        self.assertAlmostEqual(price, 10.0 + 20.92, places=2)

    def test_convert_2026_27_saver_window(self):
        # 2026-27 URSTOU adds an 11:00-16:00 Saver rate at 1.0 c/kWh; the
        # closed URDS/FURDS tariffs migrate to the same schedule.
        interval_time = datetime(2026, 7, 15, 13, 0, tzinfo=ZoneInfo(time_zone()))
        for code in ('URTOU', 'URSTOU', 'URDS', 'FURDS'):
            price = convert(interval_time, code, 100.0)
            self.assertAlmostEqual(price, 10.0 + 1.0, places=2, msg=code)
        # Off-peak resumes outside the Saver window.
        off_peak = datetime(2026, 7, 15, 8, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertAlmostEqual(convert(off_peak, 'URSTOU', 100.0), 10.0 + 5.22, places=2)

    def test_reskw1r_migrates_to_urstou(self):
        # RESKW1R closed in 2026-27 and migrates to URSTOU; it must price and
        # return a daily fee rather than raising KeyError.
        interval_time = datetime(2026, 7, 15, 18, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertAlmostEqual(convert(interval_time, 'RESKW1R', 100.0), 10.0 + 20.92, places=2)
        self.assertEqual(get_daily_fee('RESKW1R', interval_time=interval_time), 31.51)
