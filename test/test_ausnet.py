# test/test_ausnet.py

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from aemo_to_tariff.ausnet import convert_feed_in_tariff, time_zone, convert, calculate_demand_fee

class TestAusNet(unittest.TestCase):
    def test_nast11s_peak(self):
        interval_time = datetime(2025, 6, 12, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'NAST11S'
        rrp = 100.0  # $/MWh → 10 c/kWh
        expected_price = 10.0 + 14.6  # rrp + peak rate
        actual_price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(actual_price, expected_price, places=0)

    def test_nast11s_offpeak(self):
        interval_time = datetime(2025, 6, 12, 3, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'NAST11S'
        # amber_sell_price': 47.33081,
        # amber_buy_price': 63.83136,
        # amber_spot_per_kwh': 48.07081,
        rrp = 480.0  # $/MWh → 8 c/kWh
        expected_price = 63.0
        actual_price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(actual_price, expected_price, places=0)

    def test_nast11s_feed_in_passthrough(self):
        interval_time = datetime(2025, 6, 12, 14, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'NAST11S'
        rrp = 120.0
        expected = 12.0  # passthrough
        actual = convert_feed_in_tariff(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(actual, expected, places=2)

    def test_nast11s_demand_fee_default(self):
        tariff_code = 'NAST11S'
        demand_kw = 5
        fee = calculate_demand_fee(tariff_code, demand_kw, days=30)
        self.assertEqual(fee, 0.0)  # no demand charge defined

    def test_pre_peak_june(self):
        interval_time = datetime(2025, 6, 18, 16, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'NAST11S'
        sell_price = 21.16197
        expected = 48.84239
        rrp = 209
        actual = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(actual, expected, places=0)
        actual = convert_feed_in_tariff(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(actual, sell_price, places=0)

    def test_noon_peak_june(self):
        interval_time = datetime(2025, 6, 12, 11, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'NAST11S'
        expected = 28.43681
        rrp = 139.92
        actual = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(actual, expected, places=0)

    def test_nee11s_2026_27(self):
        # Post-1-Jul-2026: NEE11S anytime rate drops 13.6472 → 13.4297 c/kWh
        interval_time = datetime(2026, 7, 12, 10, 0, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'NEE11S', 100.0)
        self.assertAlmostEqual(price, 10.0 + 13.4297, places=2)