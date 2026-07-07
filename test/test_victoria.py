import unittest
from zoneinfo import ZoneInfo
from datetime import datetime
from aemo_to_tariff.victoria import time_zone, convert, get_daily_fee

class TestVictoria(unittest.TestCase):
    def test_convert(self):
        # 2023-07-14 is a Friday — the classic VIC ToU peak (7am–11pm) applies
        # on business days, so 10:00 is peak.
        interval_time = datetime(2023, 7, 14, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'VICR_TOU'
        rrp = 100.0
        expected_price = 40.0
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_peak_is_weekday_only(self):
        # Classic Victorian ToU peak (VICR_TOU 7am–11pm, VICS_TOU 7am–10pm)
        # applies Mon–Fri only; weekends are entirely off-peak. Public holidays
        # are not handled — a known limitation matching the feed-in side.
        rrp = 100.0  # 10 c/kWh spot
        # VICR_TOU: peak 30.0, off-peak 15.0.
        fri = datetime(2023, 7, 14, 10, 0, tzinfo=ZoneInfo(time_zone()))
        sat = datetime(2023, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        sun = datetime(2023, 7, 16, 18, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertEqual(fri.weekday(), 4)
        self.assertEqual(sat.weekday(), 5)
        self.assertEqual(sun.weekday(), 6)
        self.assertAlmostEqual(convert(fri, 'VICR_TOU', rrp), 10.0 + 30.0, places=2)
        self.assertAlmostEqual(convert(sat, 'VICR_TOU', rrp), 10.0 + 15.0, places=2)
        self.assertAlmostEqual(convert(sun, 'VICR_TOU', rrp), 10.0 + 15.0, places=2)
        # VICS_TOU: peak 35.0, off-peak 18.0.
        self.assertAlmostEqual(convert(fri, 'VICS_TOU', rrp), 10.0 + 35.0, places=2)
        self.assertAlmostEqual(convert(sat, 'VICS_TOU', rrp), 10.0 + 18.0, places=2)

    def test_weekend_overnight_still_off_peak(self):
        # The overnight off-peak band is unchanged on weekends (sanity check
        # that the weekend short-circuit returns the same off-peak rate).
        sat_night = datetime(2023, 7, 15, 2, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertEqual(sat_night.weekday(), 5)
        self.assertAlmostEqual(convert(sat_night, 'VICR_TOU', 100.0), 10.0 + 15.0, places=2)

    def test_get_daily_fee(self):
        tariff_code = 'VICR_TOU'
        annual_usage = 20000
        expected_fee = 120.0  # cents/day
        fee = get_daily_fee(tariff_code, annual_usage)
        self.assertAlmostEqual(fee, expected_fee, 3)
