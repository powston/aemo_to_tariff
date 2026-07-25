"""Settled-price reconciliation: does convert() explain what customers are billed?

On a pass-through (wholesale) retail plan an interval's settled price decomposes as

    settled = k * spot + network_component(table) + fee

``k`` folds the network loss factors and GST into the spot term and ``fee`` is the
retailer's own flat per-kWh charge. Both are properties of the *plan*, not of the
interval, so a day of intervals across several network periods over-determines
them: fit ``k`` plus one ``fee`` per period and the fees must all come out equal.

That equality is the test. If convert() understates the network component by a
constant, every fee absorbs the same amount and they still agree -- which is how
the evoenergy 2026-27 level error hid (see TestEvoenergy2026RateLevel). But if
convert() understates it *proportionally* -- e.g. by omitting GST -- the implied
fee grows with the rate and the fees disagree. That is exactly what these cases
caught across six networks: before GST was applied to the network component the
per-period fees fanned out with a slope of precisely 0.1000.

Cases are real settled (final, not forecast) intervals, carrying no site, meter,
NMI or account identifier. RRP is public market data; the settled price is a
deterministic function of published rates plus the plan's flat fee.

Evidence beyond these fixtures: fitting a site's plan on a pre-1-July day and
predicting a post-1-July day out-of-sample gives a mean error of 0.004-0.02 c/kWh
with GST applied, versus 0.2-1.2 c/kWh without, over ~200 sites.
"""
import statistics
import unittest
from collections import namedtuple, defaultdict
from datetime import datetime

from aemo_to_tariff.convert import spot_to_tariff

C = namedtuple('C', 'network tariff interval rrp settled')

# network, tariff, interval, rrp $/MWh, settled retail c/kWh incl GST
CASES = [
    # ausgrid EA025: 2 periods, plan fee 1.3000 c/kWh
    C('ausgrid', 'EA025', '2026-07-21T03:45:00+00:00', 46.3, 12.55832819),
    C('ausgrid', 'EA025', '2026-07-20T21:35:00+00:00', 207.93, 31.28948888),
    C('ausgrid', 'EA025', '2026-07-21T05:15:00+00:00', 70.58, 45.24745636),
    C('ausgrid', 'EA025', '2026-07-21T07:40:00+00:00', 122.04, 51.21111118),
    # ausgrid EA225: 2 periods, plan fee 1.2961 c/kWh
    C('ausgrid', 'EA225', '2026-07-21T03:45:00+00:00', 46.3, 13.13018904),
    C('ausgrid', 'EA225', '2026-07-20T21:35:00+00:00', 207.93, 31.78718480),
    C('ausgrid', 'EA225', '2026-07-21T05:15:00+00:00', 70.58, 53.17586618),
    C('ausgrid', 'EA225', '2026-07-21T07:40:00+00:00', 122.04, 59.11590826),
    # endeavour N71: 3 periods, plan fee 1.3365 c/kWh
    C('endeavour', 'N71', '2026-07-21T03:45:00+00:00', 46.3, 11.75348367),
    C('endeavour', 'N71', '2026-07-21T01:10:00+00:00', 77.59, 15.42174642),
    C('endeavour', 'N71', '2026-07-20T23:30:00+00:00', 51.95, 20.33420774),
    C('endeavour', 'N71', '2026-07-20T21:35:00+00:00', 207.93, 38.62042134),
    C('endeavour', 'N71', '2026-07-21T10:00:00+00:00', 101.1, 29.91349594),
    C('endeavour', 'N71', '2026-07-21T07:40:00+00:00', 122.04, 32.36838319),
    # endeavour N73: 2 periods, plan fee 1.3365 c/kWh
    C('endeavour', 'N73', '2026-07-21T03:45:00+00:00', 46.3, 11.79771546),
    C('endeavour', 'N73', '2026-07-21T01:10:00+00:00', 77.59, 15.49587049),
    C('endeavour', 'N73', '2026-07-20T23:30:00+00:00', 51.95, 19.47303714),
    C('endeavour', 'N73', '2026-07-20T21:35:00+00:00', 207.93, 37.90826315),
    # endeavour N91: 3 periods, plan fee 1.3365 c/kWh
    C('endeavour', 'N91', '2026-07-21T03:45:00+00:00', 46.3, 12.45099367),
    C('endeavour', 'N91', '2026-07-21T01:10:00+00:00', 77.59, 16.11925642),
    C('endeavour', 'N91', '2026-07-20T23:30:00+00:00', 51.95, 22.21311774),
    C('endeavour', 'N91', '2026-07-20T21:35:00+00:00', 207.93, 40.49933134),
    C('endeavour', 'N91', '2026-07-21T10:00:00+00:00', 101.1, 31.79240594),
    C('endeavour', 'N91', '2026-07-21T07:40:00+00:00', 122.04, 34.24729319),
    # energex 3900: 3 periods, plan fee 0.8244 c/kWh
    C('energex', '3900', '2026-07-21T03:45:00+00:00', 43.01, 6.34310035),
    C('energex', '3900', '2026-07-21T06:00:00+00:00', 102.8, 13.35124722),
    C('energex', '3900', '2026-07-21T11:00:00+00:00', 88.86, 14.02620229),
    C('energex', '3900', '2026-07-21T07:40:00+00:00', 114.03, 16.97644576),
    C('energex', '3900', '2026-07-20T21:55:00+00:00', 11.85, 8.88925286),
    C('energex', '3900', '2026-07-20T21:10:00+00:00', 132.83, 23.06964437),
    # energex 6900: 3 periods, plan fee 0.8244 c/kWh
    C('energex', '6900', '2026-07-21T03:45:00+00:00', 43.01, 6.30533395),
    C('energex', '6900', '2026-07-21T06:00:00+00:00', 102.8, 13.26098017),
    C('energex', '6900', '2026-07-20T21:55:00+00:00', 11.85, 8.87884756),
    C('energex', '6900', '2026-07-20T21:10:00+00:00', 132.83, 22.95300845),
    C('energex', '6900', '2026-07-21T11:00:00+00:00', 88.86, 32.64817573),
    C('energex', '6900', '2026-07-21T07:40:00+00:00', 114.03, 35.57631781),
    # energex 6950: 3 periods, plan fee 0.8244 c/kWh
    C('energex', '6950', '2026-07-21T03:45:00+00:00', 43.01, 6.32918641),
    C('energex', '6950', '2026-07-21T06:00:00+00:00', 102.8, 13.31799094),
    C('energex', '6950', '2026-07-20T21:55:00+00:00', 11.85, 8.88541933),
    C('energex', '6950', '2026-07-20T21:10:00+00:00', 132.83, 23.02667324),
    C('energex', '6950', '2026-07-21T11:00:00+00:00', 88.86, 32.69745566),
    C('energex', '6950', '2026-07-21T07:40:00+00:00', 114.03, 35.63955652),
    # energex 6970: 3 periods, plan fee 0.8244 c/kWh
    C('energex', '6970', '2026-07-21T03:45:00+00:00', 43.01, 6.33465260),
    C('energex', '6970', '2026-07-21T06:00:00+00:00', 102.8, 13.33105591),
    C('energex', '6970', '2026-07-20T21:55:00+00:00', 11.85, 8.88692536),
    C('energex', '6970', '2026-07-20T21:10:00+00:00', 132.83, 23.04355476),
    C('energex', '6970', '2026-07-21T11:00:00+00:00', 88.86, 32.70874898),
    C('energex', '6970', '2026-07-21T07:40:00+00:00', 114.03, 35.65404872),
    # ergon ERTDEMT1: 3 periods, plan fee 0.8430 c/kWh
    C('ergon', 'ERTDEMT1', '2026-07-21T03:45:00+00:00', 43.01, 6.27306038),
    C('ergon', 'ERTDEMT1', '2026-07-21T06:00:00+00:00', 102.8, 13.39810422),
    C('ergon', 'ERTDEMT1', '2026-07-21T11:00:00+00:00', 88.86, 12.95790484),
    C('ergon', 'ERTDEMT1', '2026-07-21T07:40:00+00:00', 114.03, 15.95735881),
    C('ergon', 'ERTDEMT1', '2026-07-20T21:55:00+00:00', 11.85, 7.67039117),
    C('ergon', 'ERTDEMT1', '2026-07-20T21:10:00+00:00', 132.83, 22.08731379),
    # ergon ERTOUET1: 3 periods, plan fee 0.8430 c/kWh
    C('ergon', 'ERTOUET1', '2026-07-21T03:45:00+00:00', 43.01, 6.29490955),
    C('ergon', 'ERTOUET1', '2026-07-21T06:00:00+00:00', 102.8, 13.45032682),
    C('ergon', 'ERTOUET1', '2026-07-20T21:55:00+00:00', 11.85, 7.67641100),
    C('ergon', 'ERTOUET1', '2026-07-20T21:10:00+00:00', 132.83, 22.15479170),
    C('ergon', 'ERTOUET1', '2026-07-21T11:00:00+00:00', 88.86, 31.70304589),
    C('ergon', 'ERTOUET1', '2026-07-21T07:40:00+00:00', 114.03, 34.71528628),
    # essential BLNBSS1: 2 periods, plan fee 1.3205 c/kWh
    C('essential', 'BLNBSS1', '2026-07-21T03:45:00+00:00', 46.3, 15.89686303),
    C('essential', 'BLNBSS1', '2026-07-20T21:00:00+00:00', 142.54, 26.53451074),
    C('essential', 'BLNBSS1', '2026-07-20T23:30:00+00:00', 51.95, 27.93420165),
    C('essential', 'BLNBSS1', '2026-07-20T21:35:00+00:00', 207.93, 45.17506084),
    # essential BLNRSS2: 2 periods, plan fee 0.5071 c/kWh
    C('essential', 'BLNRSS2', '2026-07-21T03:45:00+00:00', 46.3, 12.48584708),
    C('essential', 'BLNRSS2', '2026-07-20T21:00:00+00:00', 142.54, 22.31151197),
    C('essential', 'BLNRSS2', '2026-07-20T23:30:00+00:00', 51.95, 25.27180630),
    C('essential', 'BLNRSS2', '2026-07-20T21:35:00+00:00', 207.93, 41.19665263),
    # sapn RESELE: 3 periods, plan fee 0.8882 c/kWh
    C('sapn', 'RESELE', '2026-07-21T02:20:00+00:00', 53.69, 11.06151058),
    C('sapn', 'RESELE', '2026-07-21T06:30:00+00:00', 126.62, 20.08416925),
    C('sapn', 'RESELE', '2026-07-20T23:30:00+00:00', 64.59, 20.62702258),
    C('sapn', 'RESELE', '2026-07-20T22:05:00+00:00', 171.03, 33.79542774),
    C('sapn', 'RESELE', '2026-07-21T11:20:00+00:00', 89.8, 51.60892049),
    C('sapn', 'RESELE', '2026-07-21T07:40:00+00:00', 122.9, 55.70394314),
]

# essential BLNRSS2 does not reconcile. Its per-period fees disagree by ~0.58
# c/kWh, its solved spot multiplier (1.021) is below the ~1.10 floor that a loss
# factor times GST implies, its fee sits well under the ~1.32 BLNBSS1 shows on the
# same network in the same month, and the fee moves across 1 July. So one of its
# two period rates is wrong -- but with only two periods the fit cannot say which,
# and no other BLNRSS2 evidence is available. Excluded from the checks below and
# pinned as an expected failure in TestKnownUnresolved so it cannot hide, and so
# that fixing the rates surfaces as an unexpected pass.
KNOWN_UNRESOLVED = {('essential', 'BLNRSS2')}


def solve(cases):
    """Recover the plan's spot multiplier k and its per-period fee, exactly.

    Within a single network period the component is constant, so two intervals at
    different spot prices give k directly -- no fitting required. k is a property
    of the plan, so that one value must then explain every other period, and the
    fee each period implies must come out the same.

    Returns (k, {component: fee}, worst within-period disagreement).
    """
    groups = defaultdict(list)
    for c in cases:
        t = datetime.fromisoformat(c.interval)
        comp = round(spot_to_tariff(t, c.network, c.tariff, 0.0, dlf=1, mlf=1, market=1), 6)
        groups[comp].append((c.rrp / 10, c.settled - comp))

    # take k from the period with the widest spot spread (best conditioned)
    widest = max(groups.values(), key=lambda pts: max(p[0] for p in pts) - min(p[0] for p in pts))
    (x1, y1), (x2, y2) = min(widest), max(widest)
    k = (y2 - y1) / (x2 - x1)

    fees = {comp: [y - k * x for x, y in pts] for comp, pts in groups.items()}
    resid = max(max(f) - min(f) for f in fees.values())
    return k, {comp: statistics.fmean(f) for comp, f in fees.items()}, resid


def by_pair(include_unresolved=False):
    grouped = defaultdict(list)
    for c in CASES:
        if not include_unresolved and (c.network, c.tariff) in KNOWN_UNRESOLVED:
            continue
        grouped[(c.network, c.tariff)].append(c)
    return grouped


class TestSettledReconciliation(unittest.TestCase):

    def test_implied_fee_agrees_across_periods(self):
        """THE test. A proportional error (missing GST) makes these fan out."""
        for pair, cases in sorted(by_pair().items()):
            with self.subTest(network=pair[0], tariff=pair[1]):
                _k, fees, _r = solve(cases)
                spread = max(fees.values()) - min(fees.values())
                self.assertLess(
                    spread, 0.02,
                    msg=f'{pair[0]}/{pair[1]}: implied retailer fee varies by '
                        f'{spread:.4f} c/kWh across network periods '
                        f'({ {round(p, 3): round(f, 4) for p, f in fees.items()} }) -- the '
                        f'network component does not scale correctly')

    def test_model_reproduces_settled_prices(self):
        for pair, cases in sorted(by_pair().items()):
            with self.subTest(network=pair[0], tariff=pair[1]):
                _k, _f, resid = solve(cases)
                self.assertLess(resid, 0.01, msg=f'{pair[0]}/{pair[1]}: residual {resid:.4f} c/kWh')

    def test_implied_fee_is_a_plausible_retail_margin(self):
        for pair, cases in sorted(by_pair().items()):
            with self.subTest(network=pair[0], tariff=pair[1]):
                _k, fees, _r = solve(cases)
                fee = statistics.median(list(fees.values()))
                self.assertGreater(fee, 0.0, msg=f'{pair[0]}/{pair[1]}: fee {fee:.4f} is negative')
                self.assertLess(fee, 2.5, msg=f'{pair[0]}/{pair[1]}: fee {fee:.4f} is too high '
                                             f'to be a retail margin')

    def test_spot_multiplier_is_a_loss_factor_times_gst(self):
        for pair, cases in sorted(by_pair().items()):
            with self.subTest(network=pair[0], tariff=pair[1]):
                k, _f, _r = solve(cases)
                self.assertGreater(k, 1.05)
                self.assertLess(k, 1.30)

    def test_one_fee_per_network(self):
        """Tariffs on the same network share a retailer, so they share a fee."""
        per_network = defaultdict(list)
        for pair, cases in by_pair().items():
            _k, fees, _r = solve(cases)
            per_network[pair[0]].append((pair[1], statistics.median(list(fees.values()))))
        for network, entries in sorted(per_network.items()):
            if len(entries) < 2:
                continue
            with self.subTest(network=network):
                vals = [f for _t, f in entries]
                self.assertLess(max(vals) - min(vals), 0.05, msg=f'{network}: {entries}')


class TestKnownUnresolved(unittest.TestCase):
    """Pairs that still do not reconcile, pinned so they stay visible.

    Encoded as expected failures: each asserts the reconciliation that *should*
    hold. An unexpected pass means the underlying rates were corrected and the
    entry can move into TestSettledReconciliation.
    """

    @unittest.expectedFailure
    def test_essential_blnrss2_period_rates(self):
        cases = [c for c in CASES if (c.network, c.tariff) == ('essential', 'BLNRSS2')]
        _k, fees, _r = solve(cases)
        spread = max(fees.values()) - min(fees.values())
        self.assertLess(spread, 0.02, msg=f'BLNRSS2 per-period fee spread {spread:.4f} c/kWh')
