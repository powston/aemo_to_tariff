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
        
        # 2025-11-15 is a SATURDAY: peak applies on business days only, so on the
        # weekend both the feed-in reward (no 16:00–20:00 export bonus) and the
        # buy price fall back to off-peak. N71 2025-26 off-peak = 10.4931 c/kWh.
        interval_time = datetime(2025, 11, 15, 17, 15, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N61'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 55.0)
        msg = f"Feed-in price for {tariff_code} at {interval_time} (Sat) should be spot only, ~5.5"
        self.assertAlmostEqual(feed_in_price, 5.5, places=1, msg=msg)
        buyer_price = convert(interval_time, 'N71', 55.0)
        msg = f"Buyer price for N71 at {interval_time} (Sat) should be off-peak: 5.5 + 10.4931"
        self.assertAlmostEqual(buyer_price, 5.5 + 10.4931, places=2, msg=msg)
        
        # 12:20 $-6 — N71 Solar Soak window, rate 3.4252 c/kWh
        # Feed-in N61 Solar Soak block 2 charge -1.969 c/kWh
        interval_time = datetime(2025, 11, 10, 12, 20, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N61'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, -6.0)
        msg = f"Feed-in price for {tariff_code} at {interval_time} should be approximately -2.569"
        self.assertAlmostEqual(feed_in_price, -0.6 + (-1.9690), places=2, msg=msg)
        buyer_price = convert(interval_time, 'N71', -6.0)
        msg = f"Buyer price for N71 at {interval_time} should be approximately 2.83"
        self.assertAlmostEqual(buyer_price, -0.6 + 3.4252, places=2, msg=msg)
        
        # 00:10	$121	Act	0 x 13.03¢	0.00¢	0 x 27.40¢
        interval_time = datetime(2025, 11, 10, 0, 10, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N61'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 121.0)
        msg = f"Feed-in price for {tariff_code} at {interval_time} should be approximately 0.00"
        self.assertAlmostEqual(feed_in_price, 12.1, places=1, msg=msg)
        
    def test_convert_high_season_peak(self):
        # 2023-01-16 is a Monday (peak applies on business days only).
        interval_time = datetime(2023, 1, 16, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 100.0
        expected_price = 31.7964
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price)

    def test_peak_is_weekday_only(self):
        # Endeavour ToU peak (16:00–20:00) applies on business days only; on
        # weekends that window is billed at off-peak. N71 2025-26: HS peak
        # 21.7964, LS peak 13.8419, off-peak 10.4931.
        rrp = 100.0  # 10 c/kWh spot
        # High season (January) — Saturday vs the following Monday:
        sat_hs = datetime(2026, 1, 17, 17, 0, tzinfo=ZoneInfo(time_zone()))
        mon_hs = datetime(2026, 1, 19, 17, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertEqual(sat_hs.weekday(), 5)
        self.assertAlmostEqual(convert(sat_hs, 'N71', rrp), 10.0 + 10.4931, places=3)
        self.assertAlmostEqual(convert(mon_hs, 'N71', rrp), 10.0 + 21.7964, places=3)
        # Low season (July) — Sunday vs the following Monday:
        sun_ls = datetime(2025, 7, 13, 17, 0, tzinfo=ZoneInfo(time_zone()))
        mon_ls = datetime(2025, 7, 14, 17, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertEqual(sun_ls.weekday(), 6)
        self.assertAlmostEqual(convert(sun_ls, 'N71', rrp), 10.0 + 10.4931, places=3)
        self.assertAlmostEqual(convert(mon_ls, 'N71', rrp), 10.0 + 13.8419, places=3)

    def test_solar_soak_applies_on_weekends(self):
        # Solar Soak (10:00–14:00) applies every day, including weekends.
        # N71 2025-26 Solar Soak = 3.4252 c/kWh.
        sat = datetime(2026, 1, 17, 11, 30, tzinfo=ZoneInfo(time_zone()))
        self.assertEqual(sat.weekday(), 5)
        self.assertAlmostEqual(convert(sat, 'N71', 22.0), 2.2 + 3.4252, places=3)

    def test_N91_peak_is_weekday_only(self):
        # N91 (GS STOU) 2025-26: LS peak 15.5462, off-peak 12.1974.
        rrp = 100.0
        sat_ls = datetime(2025, 7, 12, 17, 0, tzinfo=ZoneInfo(time_zone()))
        mon_ls = datetime(2025, 7, 14, 17, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertEqual(sat_ls.weekday(), 5)
        self.assertAlmostEqual(convert(sat_ls, 'N91', rrp), 10.0 + 12.1974, places=3)
        self.assertAlmostEqual(convert(mon_ls, 'N91', rrp), 10.0 + 15.5462, places=3)

    def test_convert_low_season_peak(self):
        interval_time = datetime(2024, 8, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 100.0
        expected_price = 23.8419
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=4)

    def test_convert_off_peak(self):
        # 2023-07-15 10:05 — N71 Solar Soak window (10:00–14:00); rate 3.4252 c/kWh
        interval_time = datetime(2023, 7, 15, 10, 5, tzinfo=ZoneInfo(time_zone()))
        rrp = 100.0
        expected_price = 10.0 + 3.4252
        price = convert(interval_time, 'N71', rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_convert_N71_solar_soak_10am(self):
        # N71 Solar Soak 10:00–14:00. 2025–26 rate = 3.4252 c/kWh ex-GST.
        # RRP $22/MWh → 2.2 c/kWh; final = 2.2 + 3.4252 = 5.6252 c/kWh.
        interval_time = datetime(2026, 2, 3, 10, 10, tzinfo=ZoneInfo(time_zone()))
        rrp = 22
        expected_price = 2.2 + 3.4252
        price = convert(interval_time, 'N71', rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_convert_N71_solar_soak_1pm(self):
        # N71 Solar Soak at 12:55. RRP $46/MWh → 4.6 c/kWh; final = 4.6 + 3.4252.
        interval_time = datetime(2026, 2, 3, 12, 55, tzinfo=ZoneInfo(time_zone()))
        rrp = 46
        expected_price = 4.6 + 3.4252
        price = convert(interval_time, 'N71', rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_convert_unknown_tariff(self):
        interval_time = datetime(2023, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N999'
        rrp = 100.0
        with self.assertRaises(KeyError):
            convert(interval_time, tariff_code, rrp)

    def test_convert_2026_27_high_season_peak(self):
        # Post-transition N71 high-season peak: 21.7964 → 23.4471 c/kWh
        interval_time = datetime(2027, 1, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'N71', 100.0)
        self.assertAlmostEqual(price, 10.0 + 23.4471, places=4)

    def test_N61_low_season_export(self):
        # Regression: peak_months previously contained all 12 months which made
        # is_high_season always True and paid the HS rate year-round.
        # July is low season — should return spot + 3.6837 (not + 12.4336).
        interval_time = datetime(2025, 7, 14, 17, 0, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, 'N61', 50.0)
        self.assertAlmostEqual(feed_in_price, 5.0 + 3.6837, places=2)

    def test_N61_high_season_export(self):
        # January is high season — should return spot + 12.4336.
        interval_time = datetime(2026, 1, 14, 17, 0, tzinfo=ZoneInfo(time_zone()))
        feed_in_price = convert_feed_in_tariff(interval_time, 'N61', 50.0)
        self.assertAlmostEqual(feed_in_price, 5.0 + 12.4336, places=2)

    def test_N61_solar_soak_charge_year_round(self):
        # Solar Soak block 2 charge (1.969 c/kWh penalty) applies in both seasons.
        # Winter weekday, solar-soak window:
        winter = datetime(2025, 7, 14, 11, 30, tzinfo=ZoneInfo(time_zone()))
        self.assertAlmostEqual(
            convert_feed_in_tariff(winter, 'N61', 50.0), 5.0 - 1.969, places=2
        )
        # Summer weekday, solar-soak window:
        summer = datetime(2026, 1, 14, 11, 30, tzinfo=ZoneInfo(time_zone()))
        self.assertAlmostEqual(
            convert_feed_in_tariff(summer, 'N61', 50.0), 5.0 - 1.969, places=2
        )

    def test_N71_solar_soak_winter_buy(self):
        # Regression: Solar Soak previously fell through to a linear approximation
        # because the convert() loop's 'high/low/off' branches don't match 'Solar Soak'.
        # Winter solar-soak buy should be spot + 3.4252 (not the default approx).
        interval_time = datetime(2025, 7, 14, 11, 30, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'N71', 22.0)
        self.assertAlmostEqual(price, 2.2 + 3.4252, places=2)

    def test_N19_solar_soak_zero_energy(self):
        # Regression: N19 LV demand previously had no period covering 10–14, so
        # midday lookups fell through to the slope/intercept default. The AER
        # 2025–26 schedule has no Solar Soak energy charge (blank column); we
        # model it as an explicit Solar Soak period at rate 0.
        interval_time = datetime(2025, 9, 1, 11, 30, tzinfo=ZoneInfo(time_zone()))
        price = convert(interval_time, 'N19', 22.0)
        self.assertAlmostEqual(price, 2.2 + 0.0, places=2)

    def test_N95_seasonality(self):
        # Regression: N95 'Storage' has seasonal periods but its tariff name
        # doesn't contain 'season', which previously caused the convert() loop
        # to fall back to the simple "first matching period" branch and apply
        # the HS rate year-round. Verify HS rate in Jan, LS rate in Jul.
        hs = datetime(2026, 1, 14, 18, 0, tzinfo=ZoneInfo(time_zone()))
        ls = datetime(2025, 7, 14, 18, 0, tzinfo=ZoneInfo(time_zone()))
        self.assertAlmostEqual(convert(hs, 'N95', 0.0), 13.1329, places=4)
        self.assertAlmostEqual(convert(ls, 'N95', 0.0), 5.1784, places=4)
