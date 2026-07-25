"""
Regression tests built from real Powston site decisions on 2026-07-09 (AEST winter).

Each case is one production interval for a distinct network/tariff pair, taken from
``inverter_action_values`` (what production actually computed), with LocalVolts
settled prices retained as independent ground truth where the site is on LocalVolts.

Conversion under test (matches production; the per-site market cost is added by the
caller, not the library):

    buy  = spot_to_tariff(t, network, import_tariff, rrp, dlf=DLF, mlf=1)   # market default
    sell = spot_to_feed_in_tariff(t, network, export_tariff, rrp, dlf=1, mlf=1, market=1)

``expected_c_kwh`` is the pure library output (no per-site market c/kWh added). The
production number a site actually sees is ``expected_c_kwh + market`` for buys; exports
carry no market adder.

``rrp`` is the decision-time next-interval price ($/MWh), not the settled 5-minute RRP,
so the LocalVolts comparison carries a little noise. ``dlf`` is the site loss factor
used in production (1.1 default; sapn 1.1678, powercor 1.3).

Not covered (no ground truth available):
  - ausnet (NAST11S) and united (URTOU): monitor-only rows, no values JSON.

Note: the sapn RESELEX evening export sits at 17.61 c/kWh here because the RESELE-family
Peak export credit is gated to SA summer (Nov-Mar); on a July interval no credit applies.
That seasonal gate is what closed the "export peak adder too big" gap flagged against the
LocalVolts actual (was 30.83 vs 19.8). See :class:`TestKnownDiscrepancies` for the spots
that still diverge from the LocalVolts ground truth beyond next-interval-price noise.
"""
import unittest
from collections import namedtuple
from datetime import datetime

from aemo_to_tariff.convert import spot_to_tariff, spot_to_feed_in_tariff, get_periods


Case = namedtuple(
    'Case',
    'network tariff interval rrp dlf expected lv direction market window',
)

BUY = 'buy'
SELL = 'sell'

# network, tariff, interval, rrp, dlf, expected_c_kwh, lv_observed, direction, market, window
OBSERVED_CASES = [
    # --- ausgrid: import EA025 / export EA029 -- site 478 (market 2.0)
    Case('ausgrid', 'EA025', '2026-07-09T09:00:00+10:00', 52.0, 1.1, 11.7008, 13.1, BUY, 2.0, 'Off-peak'),
    Case('ausgrid', 'EA025', '2026-07-09T18:00:00+10:00', 176.4, 1.1, 55.4709, 57.2, BUY, 2.0, 'Peak'),
    Case('ausgrid', 'EA029', '2026-07-09T12:30:00+10:00', 73.0, 1, 6.07, 6.2, SELL, 2.0, 'Day(09-16)'),
    Case('ausgrid', 'EA029', '2026-07-09T18:30:00+10:00', 160.9, 1, 19.94, 20.5, SELL, 2.0, 'Evening(16-21)'),
    Case('ausgrid', 'EA029', '2026-07-09T06:00:00+10:00', 115.4, 1, 11.54, 11.9, SELL, 2.0, 'Overnight(21-09)'),
    # --- endeavour: import N71 / export N61 -- site 169 (market 2.0)
    Case('endeavour', 'N71', '2026-07-09T18:00:00+10:00', 176.4, 1.1, 36.4274, 38.9, BUY, 2.0, 'High-season Peak'),
    Case('endeavour', 'N71', '2026-07-09T08:00:00+10:00', 89.1, 1.1, 22.8593, 24.8, BUY, 2.0, 'Off Peak'),
    Case('endeavour', 'N71', '2026-07-09T12:00:00+10:00', 78.6, 1.1, 13.7682, 15.6, BUY, 2.0, 'Solar Soak'),
    Case('endeavour', 'N61', '2026-07-09T12:30:00+10:00', 73.0, 1, 5.44, 7.8, SELL, 2.0, 'Day(09-16)'),
    Case('endeavour', 'N61', '2026-07-09T18:30:00+10:00', 160.9, 1, 19.5602, 20.8, SELL, 2.0, 'Evening(16-21)'),
    Case('endeavour', 'N61', '2026-07-09T06:00:00+10:00', 115.4, 1, 11.54, 12.4, SELL, 2.0, 'Overnight(21-09)'),
    # --- energex: import 6900 / export 9800 -- site 485 (market 4.25)
    Case('energex', '6900', '2026-07-09T13:30:00+10:00', 69.0, 1.1, 8.1843, 9.4, BUY, 4.25, 'Day'),
    Case('energex', '6900', '2026-07-09T18:30:00+10:00', 118.1, 1.1, 34.6774, 36.1, BUY, 4.25, 'Evening'),
    Case('energex', '6900', '2026-07-09T07:00:00+10:00', 101.6, 1.1, 18.024, 19.4, BUY, 4.25, 'Overnight'),
    Case('energex', '9800', '2026-07-09T12:30:00+10:00', 63.3, 1, 6.33, 6.7, SELL, 4.25, 'Day(09-16)'),
    Case('energex', '9800', '2026-07-09T18:30:00+10:00', 118.1, 1, 11.81, 12.6, SELL, 4.25, 'Evening(16-21)'),
    Case('energex', '9800', '2026-07-09T06:00:00+10:00', 102.8, 1, 10.28, 10.9, SELL, 4.25, 'Overnight(21-09)'),
    # --- energex: import 6970 / export 9870 -- site 98 (market 2.0)
    Case('energex', '6970', '2026-07-09T13:30:00+10:00', 69.0, 1.1, 8.1843, 9.4, BUY, 2.0, 'Day'),
    Case('energex', '6970', '2026-07-09T18:30:00+10:00', 118.1, 1.1, 34.6774, 36.1, BUY, 2.0, 'Evening'),
    Case('energex', '6970', '2026-07-09T07:00:00+10:00', 101.6, 1.1, 18.024, 19.4, BUY, 2.0, 'Overnight'),
    Case('energex', '9870', '2026-07-09T12:30:00+10:00', 61.4, 1, 6.14, 6.7, SELL, 2.0, 'Day(09-16)'),
    Case('energex', '9870', '2026-07-09T18:30:00+10:00', 118.1, 1, 11.81, 12.6, SELL, 2.0, 'Evening(16-21)'),
    Case('energex', '9870', '2026-07-09T06:00:00+10:00', 102.8, 1, 10.28, 10.9, SELL, 2.0, 'Overnight(21-09)'),
    # --- ergon: import ERTOUET1 / export NVG2 -- site 528 (market 2.0, no LocalVolts)
    Case('ergon', 'ERTOUET1', '2026-07-09T12:25:00+10:00', 61.4, 1.1, 7.1627, None, BUY, 2.0, 'Day(09-16)'),
    Case('ergon', 'ERTOUET1', '2026-07-09T19:05:00+10:00', 120.7, 1.1, 33.7072, None, BUY, 2.0, 'Evening(16-21)'),
    Case('ergon', 'ERTOUET1', '2026-07-09T06:30:00+10:00', 107.7, 1.1, 17.4447, None, BUY, 2.0, 'Overnight(21-09)'),
    Case('ergon', 'NVG2', '2026-07-09T12:25:00+10:00', 61.4, 1, 6.14, None, SELL, 2.0, 'Day(09-16)'),
    Case('ergon', 'NVG2', '2026-07-09T19:05:00+10:00', 120.7, 1, 12.07, None, SELL, 2.0, 'Evening(16-21)'),
    Case('ergon', 'NVG2', '2026-07-09T06:30:00+10:00', 107.7, 1, 10.77, None, SELL, 2.0, 'Overnight(21-09)'),
    # --- essential: import BLNRSS2 / export BLNREX2 -- site 223 (market 2.0)
    Case('essential', 'BLNRSS2', '2026-07-09T10:00:00+10:00', 70.7, 1.1, 27.649, 27.2, BUY, 2.0, 'Off-Peak'),
    Case('essential', 'BLNRSS2', '2026-07-09T17:00:00+10:00', 185.8, 1.1, 40.505, 38.9, BUY, 2.0, 'Peak'),
    Case('essential', 'BLNREX2', '2026-07-09T12:30:00+10:00', 73.0, 1, 6.4723, 5.9, SELL, 2.0, 'Day(09-16)'),
    Case('essential', 'BLNREX2', '2026-07-09T18:30:00+10:00', 160.9, 1, 27.8112, 26.7, SELL, 2.0, 'Evening(16-21)'),
    Case('essential', 'BLNREX2', '2026-07-09T06:00:00+10:00', 115.4, 1, 11.54, 10.7, SELL, 2.0, 'Overnight(21-09)'),
    # --- evoenergy: import 017 / export 1999 (market 2.0)
    # Expected values re-based when the 2026-27 017 rates were corrected (every
    # period was 3.035 c/kWh ex-GST low). That correction also closed these three
    # against the LocalVolts ground truth -- gaps went 2.6-2.9c -> 0.4-0.7c -- which
    # is an independent confirmation from a different day to the one that found it.
    Case('evoenergy', '017', '2026-07-09T09:00:00+10:00', 52.0, 1.1, 26.8005, 28.1, BUY, 2.0, 'Off-peak'),
    Case('evoenergy', '017', '2026-07-09T18:00:00+10:00', 176.4, 1.1, 40.6952, 42.3, BUY, 2.0, 'Peak'),
    Case('evoenergy', '017', '2026-07-09T13:00:00+10:00', 81.5, 1.1, 14.3985, 15.8, BUY, 2.0, 'Solar Soak'),
    Case('evoenergy', '1999', '2026-07-09T12:30:00+10:00', 73.0, 1, 7.3, 7.6, SELL, 2.0, 'Day(09-16)'),
    Case('evoenergy', '1999', '2026-07-09T18:30:00+10:00', 160.9, 1, 16.09, 16.7, SELL, 2.0, 'Evening(16-21)'),
    Case('evoenergy', '1999', '2026-07-09T06:00:00+10:00', 115.4, 1, 11.54, 12.0, SELL, 2.0, 'Overnight(21-09)'),
    # --- powercor: import PRDS / export GENR13 -- site 128 (market 4.25, Amber -- no LocalVolts)
    Case('powercor', 'PRDS', '2026-07-09T12:30:00+10:00', 101.0, 1.3, 13.3322, None, BUY, 4.25, 'Day'),
    Case('powercor', 'PRDS', '2026-07-09T07:00:00+10:00', 239.1, 1.3, 38.5617, None, BUY, 4.25, 'Off-peak'),
    Case('powercor', 'PRDS', '2026-07-09T18:30:00+10:00', 164.7, 1.3, 41.3507, None, BUY, 4.25, 'Peak'),
    Case('powercor', 'GENR13', '2026-07-09T12:30:00+10:00', 101.0, 1, 10.1, None, SELL, 4.25, 'Day(09-16)'),
    Case('powercor', 'GENR13', '2026-07-09T18:30:00+10:00', 164.7, 1, 16.47, None, SELL, 4.25, 'Evening(16-21)'),
    Case('powercor', 'GENR13', '2026-07-09T06:00:00+10:00', 123.9, 1, 12.39, None, SELL, 4.25, 'Overnight(21-09)'),
    # --- sapn: import RESELE / export RESELEX -- site 76 (market 2.0)
    Case('sapn', 'RESELE', '2026-07-09T19:00:00+09:30', 143.0, 1.1678, 56.5677, 58.2, BUY, 2.0, 'Peak'),
    Case('sapn', 'RESELE', '2026-07-09T06:30:00+09:30', 215.0, 1.1678, 37.2424, 39.2, BUY, 2.0, 'Shoulder'),
    Case('sapn', 'RESELE', '2026-07-09T13:00:00+09:30', 138.0, 1.1678, 19.8948, 21.5, BUY, 2.0, 'Solar Sponge'),
    Case('sapn', 'RESELEX', '2026-07-09T12:30:00+09:30', 135.1, 1, 12.51, 14.1, SELL, 2.0, 'Day(09-16)'),
    # Peak export credit is gated to SA summer, so this winter interval is uncredited.
    Case('sapn', 'RESELEX', '2026-07-09T18:30:00+09:30', 176.1, 1, 17.61, 19.8, SELL, 2.0, 'Evening(16-21)'),
    Case('sapn', 'RESELEX', '2026-07-09T05:30:00+09:30', 129.8, 1, 12.98, 14.6, SELL, 2.0, 'Overnight(21-09)'),
    # --- tasnetworks: import TAS94 / export TASX5I -- site 116 (market 2.0)
    # TAS94 Peak is weekdays 07-10 & 16-21 only; 2026-07-09 is a Thursday, so
    # both intervals below fall in Off-peak (2.670). The 04:30 case then lands on
    # the LV actual (13.43 + 2 market = 15.4). The 14:30 LV of 22.7 reflects a
    # settled spot well above the decision-time rrp here, so it is not reconciled.
    Case('tasnetworks', 'TAS94', '2026-07-09T14:30:00+10:00', 75.1, 1.1, 11.0582, 22.7, BUY, 2.0, 'Off-peak (weekday midday)'),
    Case('tasnetworks', 'TAS94', '2026-07-09T04:30:00+10:00', 96.3, 1.1, 13.4261, 15.4, BUY, 2.0, 'Off-peak (weekday overnight)'),
    Case('tasnetworks', 'TASX5I', '2026-07-09T12:30:00+10:00', 96.2, 1, 9.62, 10.5, SELL, 2.0, 'Day(09-16)'),
    Case('tasnetworks', 'TASX5I', '2026-07-09T18:30:00+10:00', 147.6, 1, 14.76, 16.2, SELL, 2.0, 'Evening(16-21)'),
    Case('tasnetworks', 'TASX5I', '2026-07-09T06:00:00+10:00', 112.2, 1, 11.22, 12.3, SELL, 2.0, 'Overnight(21-09)'),
]


def library_price(case):
    """Reproduce the production conversion for a case, without the market adder."""
    t = datetime.fromisoformat(case.interval)
    if case.direction == BUY:
        return spot_to_tariff(t, case.network, case.tariff, case.rrp, dlf=case.dlf, mlf=1)
    return spot_to_feed_in_tariff(t, case.network, case.tariff, case.rrp, dlf=1, mlf=1, market=1)


class TestObservedCases(unittest.TestCase):
    """Lock the library output for every real-site interval captured on 2026-07-09."""

    def test_all_observed_cases(self):
        for case in OBSERVED_CASES:
            with self.subTest(network=case.network, tariff=case.tariff,
                              window=case.window, direction=case.direction):
                self.assertAlmostEqual(library_price(case), case.expected, places=3)

    def test_every_network_and_tariff_is_covered(self):
        # Guard against a case being dropped during a future edit.
        self.assertEqual(len(OBSERVED_CASES), 57)
        pairs = {(c.network, c.tariff) for c in OBSERVED_CASES}
        self.assertEqual(len(pairs), 20)


class TestErgonPeriodsQuirk(unittest.TestCase):
    """ergon ERTOUET1 prices fine via spot_to_tariff but get_periods can't resolve it.

    Documented in the source data: get_periods() raises "Unknown tariff" for
    ERTOUET1 even though spot_to_tariff prices it, so the ergon windows above are
    coarse day-part buckets rather than real tariff periods.
    """

    def test_spot_to_tariff_prices_ertouet1(self):
        t = datetime.fromisoformat('2026-07-09T12:25:00+10:00')
        price = spot_to_tariff(t, 'ergon', 'ERTOUET1', 61.4, dlf=1.1, mlf=1)
        # 7.135 before GST was applied to the network component.
        self.assertAlmostEqual(price, 7.1627, places=3)

    def test_get_periods_raises_for_ertouet1(self):
        with self.assertRaises(ValueError):
            get_periods('ergon', 'ERTOUET1')


class TestKnownDiscrepancies(unittest.TestCase):
    """Spots where the production price diverges from LocalVolts settled ground truth.

    These are encoded as *expected failures*: each asserts the production price
    (library output + per-site market for buys) lands within GROUND_TRUTH_TOL of the
    LocalVolts actual. Unlike a library bug, both remaining gaps are driven by the
    caller-supplied ``dlf`` / ``market`` inputs, not by anything the library computes
    -- so they cannot be closed in this repo; the fix belongs in the site config that
    feeds those parameters. They stay here to document the gap and to alert (via an
    unexpected pass) if that config is corrected.

    (The TAS94 Peak/Shoulder window gaps that used to live here were real library
    bugs -- the Peak window ran 07:00-22:00 every day instead of weekdays
    07:00-10:00 & 16:00-21:00 -- and are now fixed, so those cases are locked in
    TestObservedCases. The sapn RESELEX evening export gap was likewise closed by
    gating the RESELE-family Peak export credit to SA summer.)
    """

    GROUND_TRUTH_TOL = 1.5  # c/kWh; comfortably above next-interval-price noise

    def _assert_matches_localvolts(self, case):
        prod = library_price(case)
        if case.direction == BUY:
            prod += case.market
        self.assertLessEqual(
            abs(prod - case.lv), self.GROUND_TRUTH_TOL,
            msg=f'{case.network} {case.tariff} {case.window}: '
                f'modelled {prod:.4f}c vs LocalVolts {case.lv}c',
        )

    def test_ausgrid_ea025_peak_buy_now_reconciles(self):
        # Was an expectedFailure blamed on the caller's dlf being too low (~54.2c
        # incl market vs LV 57.2c). The real cause was GST missing from the network
        # component: EA025 Peak is 32.516 c/kWh, so the 10% came to ~3.25 c/kWh and
        # swamped the loss-factor discrepancy it was attributed to. Now inside
        # tolerance, so it is asserted rather than expected to fail.
        self._assert_matches_localvolts(
            Case('ausgrid', 'EA025', '2026-07-09T18:00:00+10:00', 176.4, 1.1, 55.4709, 57.2, BUY, 2.0, 'Peak'))

    def test_evoenergy_017_reconciles_after_the_2026_27_rate_fix(self):
        """Not expectedFailure: all three evoenergy 017 windows now land inside
        GROUND_TRUTH_TOL of the LocalVolts settled price. Before the 2026-27 rate
        correction they were 2.6-2.9 c/kWh short, i.e. outside it. This locks the
        reconciliation so a future rate edit that reopens the gap fails here.
        """
        for case in OBSERVED_CASES:
            if case.network == 'evoenergy' and case.direction == BUY:
                with self.subTest(window=case.window):
                    self._assert_matches_localvolts(case)

    @unittest.expectedFailure
    def test_energex_6900_day_market_cost_too_high(self):
        # Not a library bug: the 6900 Day network rate is only 0.434c; the ~3c gap
        # (12.39c incl 4.25 market vs LV 9.4c) is the caller-supplied market cost.
        self._assert_matches_localvolts(
            Case('energex', '6900', '2026-07-09T13:30:00+10:00', 69.0, 1.1, 8.1843, 9.4, BUY, 4.25, 'Day'))


if __name__ == '__main__':
    unittest.main()
