# test/test_convert.py
import unittest
from datetime import datetime
from aemo_to_tariff import (spot_to_tariff, get_daily_fee, calculate_demand_fee,
                            spot_to_feed_in_tariff, estimate_demand_fee, battery_tariffs)

class TestTariffConversions(unittest.TestCase):

    def test_battery_tariff(self):
        expected_includes = 'BLNREX2'
        self.assertIn(expected_includes, battery_tariffs(network='Essential', customer_type='Residential')['export'])
        expected_includes = 'EA029'
        self.assertIn(expected_includes, battery_tariffs(network='Ausgrid', customer_type='Residential')['export'])
        expected_includes = 'RESELE'
        self.assertIn(expected_includes, battery_tariffs(network='SAPN', customer_type='Residential')['export'])
        expected_includes = 'N61'
        self.assertIn(expected_includes, battery_tariffs(network='Endeavour', customer_type='Residential')['export'])
        
    def test_energex_tariff_6970(self):
        # Off peak (Day, solar window) — 2024 uses 2025–26 schedule
        interval_time = datetime.strptime('2024-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Energex', '6900', 100, 1, 1), 10.63, 2)

        # Peak (Evening)
        interval_time = datetime.strptime('2024-07-05 18:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Energex', '6970', 100, 1, 1), 29.521, 2)

        # Shoulder (Overnight)
        interval_time = datetime.strptime('2024-07-05 02:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Energex', '6900', 100, 1, 1), 15.022, 2)

        # With loss factor
        interval_time = datetime.strptime('2024-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Energex', '6900', 200, 1.05, 1.01), 22.0126, 2)

        # Demand estimate (2025–26: 3900 peak demand = 5.127 $/kW)
        interval_time = datetime.strptime('2024-07-05 18:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Energex', '6900', 5.5), 0.0, 2)
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Energex', '3950', 5.5), 28.1985, 2)

    def test_energex_tariff_6900_2026_27(self):
        # Post-transition: Day rate drops 0.476 → 0.434, Evening 19.367 → 19.533
        interval_time = datetime.strptime('2026-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Energex', '6900', 100, 1, 1), 10.588, 2)
        # Demand for 3950 jumps from 5.127 to 7.0 $/kW
        interval_time = datetime.strptime('2026-07-05 18:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Energex', '3950', 5.5), 38.5, 2)

    def test_powercor_tariff_017(self):
        # With loss factor 6.2516935 -44.75
        interval_time = datetime.strptime('2024-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Powercor', 'PRDS', -18.79, 1.058, 1.01), -2.08574, 1)

        # PRDS estimate
        interval_time = datetime.strptime('2024-09-05 15:05+10:00', '%Y-%m-%d %H:%M%z')
        expected_price = (17.95919 * 0.99) - 2.25 - 3.9606291203999966
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Powercor', 'PRDS', 42.53, 1.058, 1.00), expected_price, 2)
    
    def test_ergon_tariff_017(self):
        # With loss factor (Off-Peak solar window) — 2024 uses 2025–26 schedule (0.524 c/kWh)
        interval_time = datetime.strptime('2024-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Ergon', 'ERTOUET1', 200, 1.05, 1.01), 22.06, 2)

        # Demand estimate
        interval_time = datetime.strptime('2024-07-05 18:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Ergon', 'ERTOUET1', 5.5), 0.0, 2)
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Ergon', 'ERTDEMCT1', 5.5), 38.5, 2)

    def test_ergon_tariff_017_2026_27(self):
        # Post-transition off-peak drops 0.524 → 0.277
        interval_time = datetime.strptime('2026-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Ergon', 'ERTOUET1', 200, 1.05, 1.01), 21.8136, 2)

    def test_evoenergy_tariff_017(self):
        # Off peak
        interval_time = datetime.strptime('2024-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Evoenergy', '017', 100, 1, 1), 13.7411, 2)

        # Peak
        interval_time = datetime.strptime('2024-07-05 17:05+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Evoenergy', '017', 100, 1, 1), 27.9564, 2)

        # Shoulder
        interval_time = datetime.strptime('2024-07-05 02:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Evoenergy', '017', 100, 1, 1), 16.3855, 2)

        interval_time = datetime.strptime('2024-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Evoenergy', '017', 200), 25.4255, 2)

    def test_ausgrid_tariff_EA116(self):
        interval_time = datetime.strptime('2024-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Ausgrid', 'EA116', 100, 1, 1), 12.491, 2)
        interval_time = datetime.strptime('2024-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Ausgrid', 'EA116', 200, 1, 1), 22.645, 2)
        # Demand estimate
        interval_time = datetime.strptime('2024-07-05 18:00+11:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Ausgrid', 'EA025', 5.5), 0.0, 2)
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Ausgrid', 'EA116', 5.5), 49.489, 2)

    def test_essential_demand_fee(self):
        # Demand estimate
        interval_time = datetime.strptime('2024-07-05 18:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Essential', 'BLNRSS2', 5.5), 0.0, 2)
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Essential', 'Other', 5.5), 49.489, 2)

    def test_endeavour_demand_fee(self):
        # Demand estimate
        interval_time = datetime.strptime('2024-07-05 18:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Endeavour', 'N71', 5.5), 0.0, 2)
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Endeavour', 'N73', 5.5), 78.485, 2)
        interval_time = datetime.strptime('2024-07-05 11:30+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'Endeavour', 'N73', 5.5), 0.0, 2)

    def test_energex_daily_fee(self):
        before = datetime.strptime('2025-09-01 12:00+10:00', '%Y-%m-%d %H:%M%z')
        after = datetime.strptime('2026-09-01 12:00+10:00', '%Y-%m-%d %H:%M%z')
        # 2025–26
        self.assertAlmostEqual(get_daily_fee('Energex', '3900', interval_time=before), 55.6, 3)
        self.assertAlmostEqual(get_daily_fee('Energex', '7200', interval_time=before), 766.5, 3)
        # 2026–27
        self.assertAlmostEqual(get_daily_fee('Energex', '3900', interval_time=after), 45.1, 3)
        self.assertAlmostEqual(get_daily_fee('Energex', '7200', interval_time=after), 913.4, 3)
        # Banded fee unchanged in either schedule
        self.assertAlmostEqual(get_daily_fee('Energex', '6000', annual_usage=15000, interval_time=after), 73.9, 3)
        self.assertAlmostEqual(get_daily_fee('Energex', '6000', annual_usage=30000, interval_time=after), 103.3, 3)

    def test_energex_demand_fee(self):
        self.assertAlmostEqual(calculate_demand_fee('Energex', '3700', 5.5, 31), 0.0, 2)
        self.assertAlmostEqual(calculate_demand_fee('Energex', '3900', 5.5, 31), 0.0, 2)

    def test_ausgrid_daily_fee(self):
        # Placeholder test - update when Ausgrid is implemented
        self.assertAlmostEqual(get_daily_fee('Ausgrid', 'EA116'), 67.0054, 3)  # cents/day

    def test_ausgrid_demand_fee(self):
        # Placeholder test - update when Ausgrid is implemented
        self.assertAlmostEqual(calculate_demand_fee('Ausgrid', 'EA116', 5.5, 31), 217.17, 1)

    def test_evoenergy_daily_fee(self):
        # Placeholder test - update when Evoenergy is implemented
        self.assertEqual(get_daily_fee('Evoenergy', '017'), 0.0)

    def test_evoenergy_demand_fee(self):
        # Placeholder test - update when Evoenergy is implemented
        self.assertEqual(calculate_demand_fee('Evoenergy', '017', 5.5, 31), 0.0)

    def test_sapn_daily_fee(self):
        self.assertAlmostEqual(get_daily_fee('SAPN', 'RTOU'), 65.53, 2)  # cents/day
        self.assertAlmostEqual(get_daily_fee('SAPN', 'SBTOU'), 66.45, 2)  # cents/day
        # Demand estimate
        interval_time = datetime.strptime('2024-07-05 18:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'SAPN', 'SBTOU', 5.5), 0.0, 2)
        self.assertAlmostEqual(estimate_demand_fee(interval_time, 'SAPN', 'RTOU', 5.5), 0, 2)

    def test_evo_battery_trial(self):
        interval_time = datetime.strptime('2024-07-05 14:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'Evoenergy', '026', 100), 14.506, 2)
        self.assertAlmostEqual(spot_to_feed_in_tariff(interval_time, 'Evoenergy', '026', 200), 20.84, 2)
        interval_time = datetime.strptime('2024-07-05 19:00+10:00', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_feed_in_tariff(interval_time, 'Evoenergy', '026', 200), 34.2, 2)

    def test_sapn_demand_fee(self):
        self.assertAlmostEqual(calculate_demand_fee('SAPN', 'RTOU', 5.5, 31), 0, 4)
        self.assertAlmostEqual(calculate_demand_fee('SAPN', 'SBTOU', 5.5, 31), 0, 4)

    def test_sapn_tariff_RTOU(self):
        # Peak
        interval_time = datetime.strptime('2024-07-05 18:00+09:30', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'SAPN', 'RTOU', 100), 29.8692, 2)

        # Off-peak
        interval_time = datetime.strptime('2024-07-05 02:00+09:30', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'SAPN', 'RTOU', 100), 20.3892, 2)

    def test_tasnetworks_daily_fee(self):
        self.assertAlmostEqual(get_daily_fee('tasnetworks', 'TAS93'), 80.544, 3)  # cents/day
        self.assertAlmostEqual(get_daily_fee('tasnetworks', 'TAS94'), 96.355, 3)  # cents/day

    def test_tasnetworks_demand_fee(self):
        self.assertAlmostEqual(calculate_demand_fee('tasnetworks', '75', 5.5, 31), 0.0, 2)
        self.assertAlmostEqual(calculate_demand_fee('tasnetworks', '31', 5.5, 31), 0.0, 2)

    def test_tasnetworks_tariff_93(self):
        # Peak
        interval_time = datetime.strptime('2024-07-05 18:00+09:30', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'tasnetworks', 'TAS93', 100), 28.148, 2)

        # Off-peak
        interval_time = datetime.strptime('2024-07-05 02:00+09:30', '%Y-%m-%d %H:%M%z')
        self.assertAlmostEqual(spot_to_tariff(interval_time, 'tasnetworks', 'TAS93', 100), 14.537, 2)


if __name__ == '__main__':
    unittest.main()

    def test_get_periods_threads_interval_time(self):
        # Package-level get_periods must pass interval_time through so
        # seasonal tariffs (Energex 96200) return the right season.
        from aemo_to_tariff import get_periods
        from zoneinfo import ZoneInfo
        summer = datetime(2027, 1, 15, 12, 0, tzinfo=ZoneInfo('Australia/Brisbane'))
        names = {p[0] for p in get_periods('Energex', '96200', summer)}
        self.assertIn('Peak', names)
        winter = datetime(2026, 9, 1, 12, 0, tzinfo=ZoneInfo('Australia/Brisbane'))
        names = {p[0] for p in get_periods('Energex', '96200', winter)}
        self.assertNotIn('Peak', names)
