import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from aemo_to_tariff.endeavour import convert, convert_feed_in_tariff, time_zone

class TestEndeavour(unittest.TestCase):
    def test_convert_feed_in(self):
        interval_time = datetime(2023, 1, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 100.0)
        self.assertAlmostEqual(feed_in_price, 10.00, places=1)
        
    def test_convert_N71_n61_feed_in(self):
        # 17:15	$55	Act	0.692 x 17.19¢	1189.88¢	0 x 31.98¢
        interval_time = datetime(2025, 11, 10, 17, 15, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N61'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 55.0)
        msg = f"Feed-in price for {tariff_code} at {interval_time} should be approximately 17.19"
        self.assertAlmostEqual(feed_in_price, 17.19 + 0.74, places=1, msg=msg)
        buyer_price = convert(interval_time, 'N71', 55.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 31.98"
        self.assertAlmostEqual(buyer_price, 31.98 - 4.68, places=1, msg=msg)
        
        # 17:15	$55	Act	0.692 x 17.19¢	1189.88¢	0 x 31.98¢
        interval_time = datetime(2025, 11, 15, 17, 15, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N61'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 55.0)
        msg = f"Feed-in price for {tariff_code} at {interval_time} should be approximately 5.5"
        self.assertAlmostEqual(feed_in_price, 5.5, places=1, msg=msg)
        buyer_price = convert(interval_time, 'N71', 55.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 31.98"
        self.assertAlmostEqual(buyer_price, 31.98 - 4.68, places=1, msg=msg)
        
        # 12:20	$-6	Act	0 x -0.67¢	0.00¢	0 x 4.55¢
        interval_time = datetime(2025, 11, 10, 12, 20, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N61'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, -6.0)
        msg = f"Feed-in price for {tariff_code} at {interval_time} should be approximately -11.04"
        self.assertAlmostEqual(feed_in_price, -2.569, places=1, msg=msg)
        buyer_price = convert(interval_time, 'N71', -6.0)
        msg = f"Buyer price for {tariff_code} at {interval_time} should be approximately 12.30"
        self.assertAlmostEqual(buyer_price, 4.55 + 0.41, places=1, msg=msg)
        
        # 00:10	$121	Act	0 x 13.03¢	0.00¢	0 x 27.40¢
        interval_time = datetime(2025, 11, 10, 0, 10, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N61'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 121.0)
        msg = f"Feed-in price for {tariff_code} at {interval_time} should be approximately 0.00"
        self.assertAlmostEqual(feed_in_price, 12.1, places=1, msg=msg)
        
    def test_N61_low_season_export(self):
        # Low season (Apr-Oct), business day, 16:00-20:00 -> spot + 3.6837
        interval_time = datetime(2025, 7, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, 'N61', 0.0)
        self.assertAlmostEqual(feed_in_price, 3.6837, places=4)

    def test_N61_high_season_export(self):
        # High season (Nov-Mar), business day, 16:00-20:00 -> spot + 12.4336
        interval_time = datetime(2025, 1, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, 'N61', 0.0)
        self.assertAlmostEqual(feed_in_price, 12.4336, places=4)

    def test_N61_solar_soak_charge_year_round(self):
        # Solar Soak block 2 charge (-1.9690 c/kWh at 10:00-14:00) applies all year
        # on business days, in both high and low season.
        from datetime import timedelta
        for month in range(1, 13):
            # find the first business day (Mon-Fri) of the month
            day = datetime(2025, month, 1, 11, 0, tzinfo=ZoneInfo(time_zone()))
            while day.weekday() >= 5:
                day = day + timedelta(days=1)
            feed_in_price = convert_feed_in_tariff(day, 'N61', 0.0)
            self.assertAlmostEqual(feed_in_price, -1.9690, places=4,
                                   msg=f"Solar soak charge wrong for month {month}")

    def test_convert_high_season_peak(self):
        interval_time = datetime(2023, 1, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 100.0
        expected_price = 31.7964
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price)

    def test_convert_low_season_peak(self):
        interval_time = datetime(2024, 8, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 100.0
        expected_price = 23.8419
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=4)

    def test_convert_off_peak(self):
        interval_time = datetime(2023, 7, 15, 10, 5, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 100.0
        expected_price = 15.97
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_convert_N71_solar_soak_10am(self):
        # The RRP in NSW on 2026-02-03 at 10:10am +10 looks to be $22 so the buy price was about 7.90¢ and sell was about 2.37¢
        interval_time = datetime(2026, 2, 3, 10, 10, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 22
        expected_price = 7.9 - 0.03 # for losses
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_convert_N71_solar_soak_1pm(self):
        # 2026-02-13 the RRP at 12:55 it was $46 so buy 4.91¢ and sell 10.51¢
        interval_time = datetime(2026, 2, 3, 12, 55, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 46
        expected_price = 10.51 - 0.149 # for losses
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_convert_unknown_tariff(self):
        interval_time = datetime(2023, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N999'
        rrp = 100.0
        with self.assertRaises(KeyError):
            convert(interval_time, tariff_code, rrp)
