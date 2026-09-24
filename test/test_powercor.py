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


class TestPowercorPRCER(unittest.TestCase):
    """Residential CER two-way tariff, Powercor 2026-27 Tariff Summary (7 May 2026)."""

    @staticmethod
    def _at(month, hour, minute=0, day=15):
        # Interval END; convert() steps back 5 minutes for the period lookup.
        return datetime(2026 if month >= 7 else 2027, month, day, hour, minute, tzinfo=ZoneInfo(time_zone()))

    def test_import_peak_is_seasonal(self):
        from aemo_to_tariff.powercor import get_periods
        # Dec-Feb and Jun-Aug: 27.86; Mar-May and Sep-Nov: 20.80. Interval ending
        # 16:05 is the first peak interval; ending 16:00 is the last saver one.
        self.assertAlmostEqual(convert(self._at(7, 16, 5), 'PRCER', 100.0), 10.0 + 27.86, places=6)
        self.assertAlmostEqual(convert(self._at(1, 20, 55), 'PRCER', 100.0), 10.0 + 27.86, places=6)
        self.assertAlmostEqual(convert(self._at(9, 16, 5), 'PRCER', 100.0), 10.0 + 20.80, places=6)
        self.assertAlmostEqual(convert(self._at(4, 18, 0), 'PRCER', 100.0), 10.0 + 20.80, places=6)
        # Saver and off-peak do not move with the season.
        for month in (7, 9):
            self.assertAlmostEqual(convert(self._at(month, 16, 0), 'PRCER', 100.0), 10.0 + 1.00, places=6)
            self.assertAlmostEqual(convert(self._at(month, 11, 5), 'PRCER', 100.0), 10.0 + 1.00, places=6)
            self.assertAlmostEqual(convert(self._at(month, 11, 0), 'PRCER', 100.0), 10.0 + 4.20, places=6)
            self.assertAlmostEqual(convert(self._at(month, 21, 5), 'PRCER', 100.0), 10.0 + 4.20, places=6)
            self.assertAlmostEqual(convert(self._at(month, 3, 0), 'PRCER', 100.0), 10.0 + 4.20, places=6)
        self.assertEqual([r[3] for r in get_periods('PRCER', self._at(12, 12))], [4.20, 1.00, 27.86, 4.20])
        self.assertEqual([r[3] for r in get_periods('PRCER', self._at(10, 12))], [4.20, 1.00, 20.80, 4.20])

    def test_export_credit_and_charge_windows(self):
        from aemo_to_tariff.powercor import convert_feed_in_tariff as feed_in
        # Peak export credit 7 c/kWh, 16:00-21:00, Dec-Feb and Jun-Aug only.
        self.assertAlmostEqual(feed_in(self._at(7, 18, 0), 'PRCER', 100.0), 10.0 + 7.00, places=6)
        self.assertAlmostEqual(feed_in(self._at(2, 16, 5), 'PRCER', 100.0), 10.0 + 7.00, places=6)
        self.assertAlmostEqual(feed_in(self._at(9, 18, 0), 'PRCER', 100.0), 10.0, places=6)
        # Saver export charge 1 c/kWh, 11:00-16:00, Sep-May (so December carries both).
        self.assertAlmostEqual(feed_in(self._at(9, 13, 0), 'PRCER', 100.0), 10.0 - 1.00, places=6)
        self.assertAlmostEqual(feed_in(self._at(12, 13, 0), 'PRCER', 100.0), 10.0 - 1.00, places=6)
        self.assertAlmostEqual(feed_in(self._at(12, 18, 0), 'PRCER', 100.0), 10.0 + 7.00, places=6)
        self.assertAlmostEqual(feed_in(self._at(7, 13, 0), 'PRCER', 100.0), 10.0, places=6)
        # Outside both windows the export is spot.
        self.assertAlmostEqual(feed_in(self._at(7, 22, 0), 'PRCER', 100.0), 10.0, places=6)
        # Other codes are unchanged pass-throughs.
        self.assertAlmostEqual(feed_in(self._at(7, 18, 0), 'PRTOU', 100.0), 10.0, places=6)

    def test_public_api_routes_prcer(self):
        from aemo_to_tariff import battery_tariffs, get_periods, spot_to_feed_in_tariff, spot_to_tariff
        when = self._at(7, 18, 0)
        self.assertAlmostEqual(spot_to_tariff(when, 'powercor', 'PRCER', 100.0, dlf=1, mlf=1, market=1), 37.86, places=6)
        self.assertAlmostEqual(spot_to_feed_in_tariff(when, 'powercor', 'PRCER', 100.0, dlf=1, mlf=1, market=1), 17.0, places=6)
        self.assertEqual(battery_tariffs('powercor', 'Residential'), {'import': ['PRCER'], 'export': ['PRCER']})
        self.assertEqual(len(get_periods('powercor', 'PRCER', when)), 4)
        self.assertEqual(get_daily_fee('PRCER'), 43.84)

    def test_prcer_is_a_2026_27_tariff(self):
        from aemo_to_tariff.powercor import get_feed_in_tariffs, get_tariffs
        before = datetime(2026, 6, 30, 12, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertNotIn('PRCER', get_tariffs(before))
        self.assertEqual(get_feed_in_tariffs(before), {})
        self.assertIn('PRCER', get_tariffs(self._at(7, 12)))
