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
