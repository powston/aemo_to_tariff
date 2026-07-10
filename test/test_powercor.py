import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo
from datetime import datetime
from aemo_to_tariff.powercor import time_zone, convert, get_daily_fee
from aemo_to_tariff.convert import spot_to_feed_in_tariff

class TestPowercor(unittest.TestCase):
    def test_convert(self):
        interval_time = datetime(2025, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'PRDS'
        rrp = 100.0
        expected_price = 17.0
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_get_daily_fee(self):
        tariff_code = 'PRDS'
        annual_usage = 20000
        expected_fee = 43.84  # cents/day
        fee = get_daily_fee(tariff_code)
        self.assertEqual(fee, expected_fee)

    def test_convert_2026_27_peak(self):
        # PRTOU post-1-Jul-2026: peak 20.17 → 22.09 c/kWh
        interval_time = datetime(2026, 7, 15, 18, 0, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'PRTOU', 100.0)
        self.assertAlmostEqual(price, 10.0 + 22.09, places=2)

    def test_feed_in_dispatches_to_powercor_module(self):
        # Regression: spot_to_feed_in_tariff used to route powercor exports through
        # united.convert_feed_in_tariff (a copy-paste bug). Both modules currently
        # return rrp/10, so patch powercor's feed-in with a sentinel to prove the
        # wrapper actually dispatches to the powercor module.
        interval_time = datetime(2026, 7, 9, 12, 30, tzinfo=ZoneInfo(time_zone()))
        with patch('aemo_to_tariff.powercor.convert_feed_in_tariff', return_value=42.0) as m:
            result = spot_to_feed_in_tariff(interval_time, 'powercor', 'GENR13', 100.0, dlf=1, mlf=1, market=1)
        self.assertEqual(result, 42.0)
        m.assert_called_once()

    def test_feed_in_value(self):
        # Behavioural lock: powercor export is a straight rrp/10 pass-through.
        interval_time = datetime(2026, 7, 9, 12, 30, tzinfo=ZoneInfo(time_zone()))
        price = spot_to_feed_in_tariff(interval_time, 'powercor', 'GENR13', 100.0, dlf=1, mlf=1, market=1)
        self.assertAlmostEqual(price, 10.0, places=6)
