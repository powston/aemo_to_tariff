import unittest
from datetime import datetime, time
from zoneinfo import ZoneInfo

from aemo_to_tariff.ergon import (
    estimate_demand_fee,
    time_zone,
    get_daily_fee,
    calculate_demand_fee,
    get_periods,
    convert_feed_in_tariff,
    convert,
)

BRISBANE = ZoneInfo('Australia/Brisbane')
BEFORE_TRANSITION = datetime(2025, 9, 1, 12, 0, tzinfo=BRISBANE)
AFTER_TRANSITION = datetime(2026, 9, 1, 12, 0, tzinfo=BRISBANE)


class TestErgonFunctions(unittest.TestCase):
    def test_time_zone(self):
        self.assertEqual(time_zone(), 'Australia/Brisbane')

    def test_get_daily_fee_2025_26(self):
        self.assertAlmostEqual(get_daily_fee('WRTOUET1', interval_time=BEFORE_TRANSITION), 721.0, 3)
        self.assertAlmostEqual(get_daily_fee('ERTOUET1', interval_time=BEFORE_TRANSITION), 180.8, 3)

    def test_get_daily_fee_2026_27(self):
        self.assertAlmostEqual(get_daily_fee('WRTOUET1', interval_time=AFTER_TRANSITION), 746.4, 3)
        self.assertAlmostEqual(get_daily_fee('ERTOUET1', interval_time=AFTER_TRANSITION), 173.0, 3)
        # New 2026–27 tariff
        self.assertAlmostEqual(get_daily_fee('ERTDEMT1', interval_time=AFTER_TRANSITION), 160.3, 3)

    def test_get_periods_2025_26(self):
        periods = get_periods('WRTOUET1', interval_time=BEFORE_TRANSITION)
        self.assertEqual(len(periods), 3)
        self.assertEqual(periods[0], ('Off-Peak', time(11, 0), time(16, 0), 0.524))
        with self.assertRaises(ValueError):
            get_periods('UNKNOWN', interval_time=BEFORE_TRANSITION)

    def test_get_periods_2026_27(self):
        periods = get_periods('WRTOUET1', interval_time=AFTER_TRANSITION)
        self.assertEqual(periods[0], ('Off-Peak', time(11, 0), time(16, 0), 0.277))

    def test_convert_feed_in_tariff(self):
        interval_datetime = datetime(2023, 1, 1, 12, 0, tzinfo=BRISBANE)
        self.assertEqual(convert_feed_in_tariff(interval_datetime, 'WRTOUET1', 100), 10.0)

    def test_ERTDEMCT1_tariff_2025_26(self):
        # 11:30 RRP $-31.99/MWh — falls back to ERTOUET1 off-peak (0.524 c/kWh in 2025–26)
        interval_datetime = datetime(2025, 4, 5, 11, 30, tzinfo=BRISBANE)
        self.assertAlmostEqual(convert(interval_datetime, 'ERTDEMCT1', rrp=-31.99), -2.6226, places=2)

    def test_ERTDEMCT1_tariff_2026_27(self):
        # After transition off-peak rate drops to 0.277 c/kWh
        interval_datetime = datetime(2026, 7, 5, 11, 30, tzinfo=BRISBANE)
        self.assertAlmostEqual(convert(interval_datetime, 'ERTDEMCT1', rrp=-31.99), -2.8943, places=2)

    def test_ERTDEMXT1_tariff(self):
        interval_datetime = datetime(2025, 4, 5, 11, 30, tzinfo=BRISBANE)
        self.assertAlmostEqual(convert(interval_datetime, 'ERTDEMXT1', rrp=-31.99), -2.6226, places=2)

    def test_ERTDEMXT1_demand_fee(self):
        # $7/kW demand applies in both schedules (residential demand unchanged)
        interval_datetime = datetime(2025, 4, 5, 18, 30, tzinfo=BRISBANE)
        self.assertAlmostEqual(estimate_demand_fee(interval_datetime, 'ERTDEMXT1', demand_kw=5), 35, places=2)
        self.assertAlmostEqual(estimate_demand_fee(interval_datetime, 'ERTDEMCT1', demand_kw=5), 35, places=2)

    def test_ERTOUET1_tariff_2025_26(self):
        # Off-peak window, 2025–26
        interval_datetime = datetime(2025, 4, 5, 11, 30, tzinfo=BRISBANE)
        self.assertAlmostEqual(convert(interval_datetime, 'ERTOUET1', rrp=-31.99), -2.6226, places=2)
        # Peak window, 2025–26: 18.564 c/kWh
        interval_datetime = datetime(2025, 4, 5, 18, 30, tzinfo=BRISBANE)
        self.assertAlmostEqual(convert(interval_datetime, 'ERTOUET1', rrp=31.99), 23.6194, places=2)

    def test_ERTOUET1_tariff_2026_27(self):
        # Peak window, 2026–27: 18.387 c/kWh
        interval_datetime = datetime(2026, 7, 5, 18, 30, tzinfo=BRISBANE)
        self.assertAlmostEqual(convert(interval_datetime, 'ERTOUET1', rrp=31.99), 23.4247, places=2)

    def test_WRTOUET1_tariff(self):
        interval_datetime = datetime(2025, 4, 5, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(convert(interval_datetime, 'WRTOUET1', -31.99), -2.6226, places=2)

    def test_MRTOUET4_tariff(self):
        interval_datetime = datetime(2025, 4, 5, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(convert(interval_datetime, 'MRTOUET4', -31.99), -2.6226, places=2)
    