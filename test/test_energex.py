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
        self.assertAlmostEqual(price, 15.3548, places=2)

    def test_convert_2026_27(self):
        # On/after 1 July 2026: uses 2026–27 prices (Overnight 6.069 c/kWh)
        interval_time = datetime(2026, 7, 15, 10, 0, tzinfo=BRISBANE)
        price = energex.convert(interval_time, '6900', 100.0)
        self.assertAlmostEqual(price, 16.6759, places=2)

    def test_get_daily_fee_2025_26(self):
        interval_time = datetime(2025, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('6900', 20000, interval_time=interval_time), 55.6, 3)

    def test_get_daily_fee_2026_27(self):
        interval_time = datetime(2026, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('6900', 20000, interval_time=interval_time), 65.1, 3)


class TestLargeTouEnergy(unittest.TestCase):
    # NTC 94300 (SAC Large TOU Energy) — rates from the AER consolidated
    # stakeholder reports: 2025-26 peak 24.736 / off-peak 0.476 / shoulder
    # 20.136 c/kWh, $7.544/day; 2026-27 peak 25.876 / off-peak 1.627 /
    # shoulder 19.540 c/kWh, $7.777/day.

    def test_translate_tariff_94300(self):
        # 5-digit code must not be truncated
        self.assertEqual(energex.translate_tariff('94300'), '94300')

    def test_convert_peak_2025_26(self):
        # 18:05 → adjusted to 18:00 → Peak 24.736
        dt = datetime(2025, 8, 15, 18, 5, tzinfo=BRISBANE)
        price = energex.convert(dt, '94300', 100.0)
        self.assertAlmostEqual(price, 10.0 + 24.736 * 1.1, places=3)

    def test_convert_offpeak_2025_26(self):
        # 12:00 → Off-Peak 0.476 (was mistranscribed as 0.00476 in $/kWh)
        dt = datetime(2025, 8, 15, 12, 0, tzinfo=BRISBANE)
        price = energex.convert(dt, '94300', 100.0)
        self.assertAlmostEqual(price, 10.0 + 0.476 * 1.1, places=3)

    def test_convert_shoulder_afternoon_gap_2025_26(self):
        # 15:00 sits in the 14:00-16:00 window that used to be an uncovered gap
        dt = datetime(2025, 8, 15, 15, 0, tzinfo=BRISBANE)
        price = energex.convert(dt, '94300', 100.0)
        self.assertAlmostEqual(price, 10.0 + 20.136 * 1.1, places=3)

    def test_convert_shoulder_overnight_2025_26(self):
        dt = datetime(2025, 8, 15, 22, 0, tzinfo=BRISBANE)
        price = energex.convert(dt, '94300', 100.0)
        self.assertAlmostEqual(price, 10.0 + 20.136 * 1.1, places=3)

    def test_convert_peak_2026_27(self):
        dt = datetime(2026, 8, 15, 18, 5, tzinfo=BRISBANE)
        price = energex.convert(dt, '94300', 100.0)
        self.assertAlmostEqual(price, 10.0 + 25.876 * 1.1, places=3)

    def test_convert_shoulder_afternoon_gap_2026_27(self):
        dt = datetime(2026, 8, 15, 15, 0, tzinfo=BRISBANE)
        price = energex.convert(dt, '94300', 100.0)
        self.assertAlmostEqual(price, 10.0 + 19.540 * 1.1, places=3)

    def test_periods_cover_full_day(self):
        # Every minute of the day must match a period in both price years
        # (the old entries left 14:00-16:00 uncovered).
        from datetime import time as t
        for year in (2025, 2026):
            when = datetime(year, 8, 15, 12, 0, tzinfo=BRISBANE)
            periods = energex.get_periods('94300', interval_time=when)
            for minutes in range(0, 24 * 60):
                now = t(minutes // 60, minutes % 60)
                matched = any(
                    start <= now < end or (start > end and (now >= start or now < end))
                    for _, start, end, _ in periods
                )
                self.assertTrue(matched, f"no period covers {now} in {year}")

    def test_daily_fee_94300_2025_26(self):
        # Fee table is $/day; get_daily_fee returns cents/day.
        interval_time = datetime(2025, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('94300', interval_time=interval_time), 754.4, 3)

    def test_daily_fee_94300_2026_27(self):
        interval_time = datetime(2026, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('94300', interval_time=interval_time), 777.7, 3)

    def test_get_periods_94300(self):
        interval_time = datetime(2025, 9, 1, 12, 0, tzinfo=BRISBANE)
        names = {p[0] for p in energex.get_periods('94300', interval_time=interval_time)}
        self.assertEqual(names, {'Peak', 'Off-Peak', 'Shoulder'})

    def test_estimate_demand_fee_94300(self):
        # Energy-only tariff: must not fall back to the 3700 demand charge.
        interval_time = datetime(2025, 9, 1, 18, 0, tzinfo=BRISBANE)
        self.assertEqual(energex.estimate_demand_fee(interval_time, '94300', 5.0), 0.0)


class TestLargeDynamicFlexStorage(unittest.TestCase):
    # NTC 94000 (SAC Large Dynamic Flex Storage) — per the Energex TSS
    # 2025-30 Table 9 and the AER consolidated stakeholder reports, the only
    # volume charge is Peak 17:00-20:00 (1.736 c/kWh 2025-26, 1.876 c/kWh
    # 2026-27); off-peak (11:00-13:00) and shoulder are zero. Daily fees are
    # $7.544/day (2025-26) and $8.382/day (2026-27).

    def test_translate_tariff_94000(self):
        # 5-digit code must not be truncated
        self.assertEqual(energex.translate_tariff('94000'), '94000')

    def test_convert_peak_2025_26(self):
        # 18:05 → adjusted to 18:00 → Peak 1.736
        dt = datetime(2025, 8, 15, 18, 5, tzinfo=BRISBANE)
        price = energex.convert(dt, '94000', 100.0)
        self.assertAlmostEqual(price, 10.0 + 1.736 * 1.1, places=3)

    def test_convert_peak_2026_27(self):
        dt = datetime(2026, 8, 15, 18, 5, tzinfo=BRISBANE)
        price = energex.convert(dt, '94000', 100.0)
        self.assertAlmostEqual(price, 10.0 + 1.876 * 1.1, places=3)

    def test_convert_zero_network_outside_peak(self):
        # Off-peak and shoulder carry no volume charge: spot only
        for year in (2025, 2026):
            for hour in (0, 6, 12, 15, 22):
                dt = datetime(year, 8, 15, hour, 30, tzinfo=BRISBANE)
                price = energex.convert(dt, '94000', 100.0)
                self.assertAlmostEqual(price, 10.0, places=3, msg=f"{year} {hour}:30")

    def test_daily_fee_94000_2025_26(self):
        # Fee table is $/day; get_daily_fee returns cents/day.
        interval_time = datetime(2025, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('94000', interval_time=interval_time), 754.4, 3)

    def test_daily_fee_94000_2026_27(self):
        interval_time = datetime(2026, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('94000', interval_time=interval_time), 838.2, 3)

    def test_get_periods_94000(self):
        interval_time = datetime(2025, 9, 1, 12, 0, tzinfo=BRISBANE)
        names = {p[0] for p in energex.get_periods('94000', interval_time=interval_time)}
        self.assertEqual(names, {'Peak', 'Off-Peak', 'Shoulder'})

    def test_estimate_demand_fee_94000(self):
        # Energy-only tariff: must not fall back to the 3700 demand charge.
        interval_time = datetime(2025, 9, 1, 18, 0, tzinfo=BRISBANE)
        self.assertEqual(energex.estimate_demand_fee(interval_time, '94000', 5.0), 0.0)


class TestTwoWayTariff(unittest.TestCase):

    def test_import_peak_summer(self):
        # Summer peak: Jan 15, 18:00 → Peak rate 19.533
        dt = datetime(2027, 1, 15, 18, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 19.533 * 1.1, places=2)

    def test_import_offpeak_summer(self):
        # Summer off-peak: Jan 15, 12:00 → Off-Peak 0.434
        dt = datetime(2027, 1, 15, 12, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 0.434 * 1.1, places=2)

    def test_import_shoulder_summer(self):
        # Summer shoulder: Jan 15, 21:00 → Shoulder 6.069
        dt = datetime(2027, 1, 15, 21, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 6.069 * 1.1, places=2)

    def test_import_offpeak_nonsummer(self):
        # Non-summer off-peak: Jul 15, 12:00 → Off-Peak 0.434
        dt = datetime(2026, 7, 15, 12, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 0.434 * 1.1, places=2)

    def test_import_shoulder_nonsummer(self):
        # Non-summer shoulder (no peak period): Jul 15, 18:00 → Shoulder 6.069
        dt = datetime(2026, 7, 15, 18, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0 + 6.069 * 1.1, places=2)

    def test_export_reward_summer(self):
        # Summer export reward raises the sell price: Jan 15, 18:00 → +12.195
        dt = datetime(2027, 1, 15, 18, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0 + 12.195, places=2)

    def test_export_charge_nonsummer(self):
        # Non-summer export charge 11:00-13:00 lowers the sell price: Jul 15, 12:00 → -2.210
        dt = datetime(2026, 7, 15, 12, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0 - 2.210, places=2)

    def test_export_bel_exempt(self):
        # BEL exempt window 10:00-11:00: Jul 15, 10:30 → 0 network
        dt = datetime(2026, 7, 15, 10, 30, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0 + 0.0, places=2)

    def test_export_no_charge_nonsummer_evening(self):
        # Non-summer evening export: no charge
        dt = datetime(2026, 7, 15, 20, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0, places=2)

    def test_pre_july_2026_returns_spot_only(self):
        # Before 1 July 2026 — tariff doesn't exist, should return spot only
        dt = datetime(2025, 12, 15, 18, 0, tzinfo=BRISBANE)  # summer but pre-2026-27
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=False)
        self.assertAlmostEqual(price, 10.0, places=2)  # spot only, no network

    def test_pre_july_2026_export_returns_spot_only(self):
        # Before 1 July 2026 — export, should return spot only
        dt = datetime(2025, 12, 15, 18, 0, tzinfo=BRISBANE)
        price = energex.convert_two_way_tariff(dt, 100.0, is_export=True)
        self.assertAlmostEqual(price, 10.0, places=2)  # spot only, no network

    def test_daily_fee_96200(self):
        # Fee table is $/day; get_daily_fee returns cents/day.
        interval_time = datetime(2026, 9, 1, 12, 0, tzinfo=BRISBANE)
        self.assertAlmostEqual(energex.get_daily_fee('96200', interval_time=interval_time), 65.1, 3)

    def test_translate_tariff_96200(self):
        # 96200 must not be truncated
        self.assertEqual(energex.translate_tariff('96200'), '96200')

    def test_convert_96200_dispatches(self):
        # Ensure convert() with tariff '96200' reaches convert_two_way_tariff
        dt = datetime(2027, 1, 15, 18, 5, tzinfo=BRISBANE)  # 18:05 → adjusted to 18:00 → peak
        price = energex.convert(dt, '96200', 100.0)
        self.assertAlmostEqual(price, 10.0 + 19.533 * 1.1, places=2)

    def test_convert_feed_in_tariff_96200x_dispatches(self):
        # Export via the public feed-in API must apply the seasonal reward/charge.
        summer = datetime(2027, 1, 15, 18, 5, tzinfo=BRISBANE)  # adjusted to 18:00 → reward
        self.assertAlmostEqual(energex.convert_feed_in_tariff(summer, '96200X', 100.0), 10.0 + 12.195, places=2)
        winter = datetime(2026, 7, 15, 12, 5, tzinfo=BRISBANE)  # adjusted to 12:00 → export charge
        self.assertAlmostEqual(energex.convert_feed_in_tariff(winter, '96200X', 100.0), 10.0 - 2.210, places=2)
        # Other tariffs remain spot-only.
        self.assertAlmostEqual(energex.convert_feed_in_tariff(summer, '6900X', 100.0), 10.0, places=2)

    def test_get_periods_96200_seasonal(self):
        # get_periods must return season-specific periods: the 17:00-20:00
        # Peak only exists Nov-Mar; outside summer that window is Shoulder.
        summer = datetime(2027, 1, 15, 12, 0, tzinfo=BRISBANE)
        names = {p[0] for p in energex.get_periods('96200', interval_time=summer)}
        self.assertEqual(names, {'Peak', 'Off-Peak', 'Shoulder'})
        non_summer = datetime(2026, 9, 1, 12, 0, tzinfo=BRISBANE)
        names = {p[0] for p in energex.get_periods('96200', interval_time=non_summer)}
        self.assertEqual(names, {'Off-Peak', 'Shoulder'})

    def test_estimate_demand_fee_96200_is_zero(self):
        # Energy-only trial tariff must not fall back to the 3700 demand charge.
        interval_time = datetime(2026, 9, 1, 18, 0, tzinfo=BRISBANE)
        self.assertEqual(energex.estimate_demand_fee(interval_time, '96200', 5.0), 0.0)
