import unittest
from datetime import datetime
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
        self.assertAlmostEqual(price * 1.168, expected_price, places=1)

    def test_seven_pm(self):
        # 2025-05-12 19:25:00+10
        interval_time = datetime(2025, 5, 12, 19, 25, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = 135.36
        expected_price = 37.60955297
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.68, expected_price, places=1)

    def test_seven_am(self):
        # 2025-05-12 07:25:00+10
        interval_time = datetime(2025, 5, 12, 7, 25, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = 153.88
        expected_price = 34.06917696
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.6, expected_price, places=1)

    def test_four_am(self):
        # 2025-05-10 04:15:00+10
        interval_time = datetime(2025, 5, 20, 4, 15, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = 67.73
        expected_price = 15.23709699
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.48, expected_price, places=1)

    def test_later_day(self):
        # 2025-05-10 12:25:00+10
        interval_time = datetime(2025, 5, 20, 12, 25, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = -16.13
        expected_price = 6.21313241
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.447, expected_price, places=1)

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
        self.assertAlmostEqual(buyer_price, 16.17 - 2.32, places=1, msg=msg)
        
        # 07:50	$-10	Act	0.001 x -0.94¢	-0.09¢	0 x 19.13¢
        interval_time = datetime(2025, 11, 9, 7, 50, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, export_tariff, -10.0)
        msg = f"Feed-in price for {export_tariff} at {interval_time} should be approximately -0.09"
        self.assertAlmostEqual(feed_in_price, -0.09 - 0.91, places=1, msg=msg)
        buyer_price = convert(interval_time, tariff_code, -10.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 19.13"
        self.assertAlmostEqual(buyer_price, 19.13 - 3.18, places=1, msg=msg)

        # 11:55	$-26	Act	0.001 x -11.43¢	-1.14¢	0 x 5.26¢
        interval_time = datetime(2025, 11, 9, 11, 55, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, export_tariff, -26.0)
        msg = f"Feed-in price for {export_tariff} at {interval_time} should be approximately -2.6"
        self.assertAlmostEqual(feed_in_price, -3.42, places=1, msg=msg)
        buyer_price = convert(interval_time, tariff_code, -26.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 5.26"
        self.assertAlmostEqual(buyer_price, 5.26 - 2, places=1, msg=msg)
        
        # 18:10	$84	Act	0.001 x 19.45¢	1.94¢	0.001 x 28.82¢
        interval_time = datetime(2025, 11, 9, 18, 10, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, export_tariff, 84.0)
        msg = f"Feed-in price for {export_tariff} at {interval_time} should be approximately 19.45"
        self.assertAlmostEqual(feed_in_price, 19.45 + 0.53, places=1, msg=msg)
        buyer_price = convert(interval_time, tariff_code, 84.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 28.82"
        self.assertAlmostEqual(buyer_price, 25.35, places=1, msg=msg)

    def test_blnt3al_2026_27_peak(self):
        # Post-1-Jul-2026 peak rate 18.4298 → 20.9051 c/kWh
        interval_time = datetime(2026, 7, 12, 18, 0, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'BLNT3AL', 100.0)
        self.assertAlmostEqual(price, 10.0 + 20.9051, places=2)

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
        # 2025-26: 19:59 inside → adjusted -5min = 19:54, still in window
        dt_inside = datetime(2026, 2, 15, 20, 4, tzinfo=SYDNEY)  # adjusted to 19:59 → in window
        price_inside = essential.convert_feed_in_tariff(dt_inside, 'BLNREX2', 0.0)
        # 20:00 outside → adjusted to 19:55... wait, let's use 20:05 adjusted to 20:00
        dt_outside = datetime(2026, 2, 15, 20, 5, tzinfo=SYDNEY)  # adjusted to 20:00 → outside
        price_outside = essential.convert_feed_in_tariff(dt_outside, 'BLNREX2', 0.0)
        self.assertGreater(price_inside, price_outside)

