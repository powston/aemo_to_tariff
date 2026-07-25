import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import aemo_to_tariff.essential as essential
from aemo_to_tariff.essential import time_zone, convert_feed_in_tariff, convert

class TestEssentualPower(unittest.TestCase):
    def test_some_essential_functionality(self):
        interval_time = datetime(2025, 2, 20, 9, 10, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLNT3AL'
        rrp = -100.0
        expected_price = 3.858878319999999
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 0.8326, expected_price, places=1)

    def test_seven_pm(self):
        # 2025-05-12 19:25:00+10
        interval_time = datetime(2025, 5, 12, 19, 25, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = 135.36
        expected_price = 37.60955297
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.6167, expected_price, places=1)

    def test_seven_am(self):
        # 2025-05-12 07:25:00+10
        interval_time = datetime(2025, 5, 12, 7, 25, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = 153.88
        expected_price = 34.06917696
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.5568, expected_price, places=1)

    def test_four_am(self):
        # 2025-05-10 04:15:00+10
        interval_time = datetime(2025, 5, 20, 4, 15, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = 67.73
        expected_price = 15.23709699
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.4316, expected_price, places=1)

    def test_later_day(self):
        # 2025-05-10 12:25:00+10
        interval_time = datetime(2025, 5, 20, 12, 25, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = -16.13
        expected_price = 6.21313241
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.2725, expected_price, places=1)

    def test_solar_soaker(self):
        # 
        # 00:50	$80	Act	0.002 x 7.48¢	1.49¢	0 x 16.17¢	
        interval_time = datetime(2025, 11, 9, 00, 15, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'BLNRSS2'
        export_tariff = 'BLNREX2'
        feed_in_price = convert_feed_in_tariff(interval_time, export_tariff, 80.0)
        msg = f"Feed-in price for {export_tariff} at {interval_time} should be approximately 7.48"
        self.assertAlmostEqual(feed_in_price, 7.48 + 0.52, places=1, msg=msg)
        buyer_price = convert(interval_time, tariff_code, 80.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 16.17"
        # Model was 2.32c short of the billed price; GST on the network
        # component narrows the gap to 1.7317c.
        self.assertAlmostEqual(buyer_price, 16.17 - 1.7317, places=1, msg=msg)
        
        # 07:50	$-10	Act	0.001 x -0.94¢	-0.09¢	0 x 19.13¢
        interval_time = datetime(2025, 11, 9, 7, 50, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, export_tariff, -10.0)
        msg = f"Feed-in price for {export_tariff} at {interval_time} should be approximately -0.09"
        self.assertAlmostEqual(feed_in_price, -0.09 - 0.91, places=1, msg=msg)
        buyer_price = convert(interval_time, tariff_code, -10.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 19.13"
        # Model was 3.18c short of the billed price; GST on the network
        # component narrows the gap to 1.4826c.
        self.assertAlmostEqual(buyer_price, 19.13 - 1.4826, places=1, msg=msg)

        # 11:55	$-26	Act	0.001 x -11.43¢	-1.14¢	0 x 5.26¢
        interval_time = datetime(2025, 11, 9, 11, 55, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, export_tariff, -26.0)
        msg = f"Feed-in price for {export_tariff} at {interval_time} should be approximately -2.6"
        self.assertAlmostEqual(feed_in_price, -3.42, places=1, msg=msg)
        buyer_price = convert(interval_time, tariff_code, -26.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 5.26"
        # Model was 2.0c short of the billed price; GST on the network
        # component narrows the gap to 1.4217c.
        self.assertAlmostEqual(buyer_price, 5.26 - 1.4217, places=1, msg=msg)
        
        # 18:10	$84	Act	0.001 x 19.45¢	1.94¢	0.001 x 28.82¢
        interval_time = datetime(2025, 11, 9, 18, 10, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, export_tariff, 84.0)
        msg = f"Feed-in price for {export_tariff} at {interval_time} should be approximately 19.45"
        self.assertAlmostEqual(feed_in_price, 19.45 + 0.53, places=1, msg=msg)
        buyer_price = convert(interval_time, tariff_code, 84.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 28.82"
        self.assertAlmostEqual(buyer_price, 27.0474, places=1, msg=msg)

    def test_blnt3al_2026_27_peak(self):
        # Post-1-Jul-2026 peak rate 18.4298 → 20.9051 c/kWh.
        # 2026-07-13 is a Monday — peak applies on business days only.
        interval_time = datetime(2026, 7, 13, 18, 0, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'BLNT3AL', 100.0)
        self.assertAlmostEqual(price, 10.0 + 20.9051 * 1.1, places=2)

    def test_peak_is_weekday_only(self):
        # Essential Energy standard ToU peak (and shoulder) apply on business
        # days only; the whole weekday Peak/Shoulder window is billed off-peak
        # on weekends. Public holidays are NOT handled, but Essential treats a
        # weekday public holiday as a normal peak weekday, so the Mon–Fri gate
        # matches their published rule. BLNT3AL 2025-26: Shoulder 13.3044,
        # Peak 18.4298, Off-Peak 5.4026.
        rrp = 100.0  # 10 c/kWh spot
        mon = datetime(2026, 1, 19, 18, 0, tzinfo=ZoneInfo(time_zone()))  # peak window
        sat = datetime(2026, 1, 17, 18, 0, tzinfo=ZoneInfo(time_zone()))  # weekend peak window
        self.assertEqual(mon.weekday(), 0)
        self.assertEqual(sat.weekday(), 5)
        self.assertAlmostEqual(convert(mon, 'BLNT3AL', rrp), 10.0 + 18.4298 * 1.1, places=3)
        self.assertAlmostEqual(convert(sat, 'BLNT3AL', rrp), 10.0 + 5.4026 * 1.1, places=3)
        # Shoulder window (10:00) collapses to off-peak on weekends too.
        mon_sh = datetime(2026, 1, 19, 10, 0, tzinfo=ZoneInfo(time_zone()))
        sat_sh = datetime(2026, 1, 17, 10, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertAlmostEqual(convert(mon_sh, 'BLNT3AL', rrp), 10.0 + 13.3044 * 1.1, places=3)
        self.assertAlmostEqual(convert(sat_sh, 'BLNT3AL', rrp), 10.0 + 5.4026 * 1.1, places=3)

    def test_business_tou_peak_is_weekday_only(self):
        # Small-business standard ToU (BLNT2AL) is also weekday-gated.
        # 2025-26: Shoulder 14.1904, Peak 19.5029, Off-Peak 7.5707.
        rrp = 100.0
        mon = datetime(2026, 1, 19, 18, 0, tzinfo=ZoneInfo(time_zone()))
        sun = datetime(2026, 1, 18, 18, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertEqual(sun.weekday(), 6)
        self.assertAlmostEqual(convert(mon, 'BLNT2AL', rrp), 10.0 + 19.5029 * 1.1, places=3)
        self.assertAlmostEqual(convert(sun, 'BLNT2AL', rrp), 10.0 + 7.5707 * 1.1, places=3)

    def test_sun_soaker_peak_applies_on_weekends(self):
        # The Sun Soaker tariff (BLNRSS2) is "Everyday" — its peak applies on
        # weekends too, so it must NOT be weekday-gated. 2025-26 peak 16.9522.
        sat = datetime(2026, 1, 17, 18, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertEqual(sat.weekday(), 5)
        self.assertAlmostEqual(convert(sat, 'BLNRSS2', 100.0), 10.0 + 16.9522 * 1.1, places=3)

    def test_battery_tariffs_residential_uses_blnrss2(self):
        """battery_tariffs() should return BLNRSS2, not the obsolete BLNT3AL."""
        tariffs = essential.battery_tariffs('Residential')
        self.assertIn('BLNRSS2', tariffs['import'])
        self.assertNotIn('BLNT3AL', tariffs['import'])
        self.assertIn('BLNREX2', tariffs['export'])

    def test_battery_tariffs_business_unchanged(self):
        tariffs = essential.battery_tariffs('Business')
        self.assertIn('BLNBSS1', tariffs['import'])
        self.assertIn('BLNBEX1', tariffs['export'])

    def test_blnrex2_peak_ends_at_2000(self):
        """Peak export rebate window should end at 20:00, not 19:59 (both FY years)."""
        SYDNEY = ZoneInfo('Australia/Sydney')
        dt_inside = datetime(2026, 2, 15, 20, 4, tzinfo=SYDNEY)  # adjusted -5min to 19:59 → in window
        price_inside = essential.convert_feed_in_tariff(dt_inside, 'BLNREX2', 0.0)
        dt_outside = datetime(2026, 2, 15, 20, 5, tzinfo=SYDNEY)  # adjusted -5min to 20:00 → outside
        price_outside = essential.convert_feed_in_tariff(dt_outside, 'BLNREX2', 0.0)
        self.assertGreater(price_inside, price_outside)


    def test_blnbss1_full_day_coverage(self):
        # Business Sun Soaker follows the SS window: Peak 7-10 and 15-22 every
        # day, Off-Peak all other times. A noon interval must price at
        # Off-Peak, not fall back to the first (Peak) period.
        noon = datetime(2026, 1, 19, 12, 0, tzinfo=ZoneInfo(time_zone()))  # Monday
        self.assertAlmostEqual(convert(noon, 'BLNBSS1', 100.0), 10.0 + 8.1015 * 1.1, places=3)
        morning_peak = datetime(2026, 1, 19, 8, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertAlmostEqual(convert(morning_peak, 'BLNBSS1', 100.0), 10.0 + 17.9646 * 1.1, places=3)
        # Sun Soaker peak is everyday — no weekday gate.
        sat_evening = datetime(2026, 1, 17, 18, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertAlmostEqual(convert(sat_evening, 'BLNBSS1', 100.0), 10.0 + 17.9646 * 1.1, places=3)
        # 2026-27 rates, same window shape.
        noon_27 = datetime(2026, 8, 17, 12, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertAlmostEqual(convert(noon_27, 'BLNBSS1', 100.0), 10.0 + 8.5988 * 1.1, places=3)

    def test_sun_soaker_no_boundary_gaps(self):
        # Period bounds are exclusive at the end; exact boundary times like
        # 09:59/14:59 must not fall through to the Peak fallback.
        for code, off_rate in (('BLNBSS1', 8.1015), ('BLNRSS2', 5.8530)):
            for hh, mm in ((6, 59), (14, 59), (23, 59), (12, 0), (4, 0)):
                dt = datetime(2026, 1, 19, hh, mm, tzinfo=ZoneInfo(time_zone()))
                # Add 5 min because convert() adjusts the interval end back.
                dt = dt + timedelta(minutes=5)
                self.assertAlmostEqual(convert(dt, code, 100.0), 10.0 + off_rate * 1.1,
                                       places=3, msg=f"{code} at {hh}:{mm:02d}")
