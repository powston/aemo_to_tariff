import unittest
from zoneinfo import ZoneInfo
from datetime import datetime
from aemo_to_tariff.jemena import time_zone, convert, get_daily_fee

class TestJemena(unittest.TestCase):
    # peak 3pm: 2025-08-13 15:05:00+10	26.29598	0.00004
    # night 9pm: 2025-08-12 21:05:00+10	31.49869	19.19978	180.61
    def test_convert(self):
        interval_time = datetime(2023, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'PRTOU'
        rrp = 100.0
        expected_price = 14.870
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_get_daily_fee(self):
        tariff_code = 'PRTOU'
        expected_fee = 120.754 / 365 * 100  # cents/day (PRTOU annual charge)
        fee = get_daily_fee(tariff_code)
        self.assertEqual(fee, expected_fee)

    def test_convert_2026_27_peak(self):
        # Post-1-Jul-2026 PRTOU peak: 18.34 → 18.208 c/kWh
        interval_time = datetime(2026, 7, 15, 18, 0, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'PRTOU', 100.0)
        self.assertAlmostEqual(price, 10.0 + 18.208, places=2)
