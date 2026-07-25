import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
import aemo_to_tariff.evoenergy as evoenergy

class TestEvoenergy(unittest.TestCase):
    def test_some_evoenergy_functionality(self):
        interval_time = datetime(2025, 2, 20, 13, 45, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = '017'
        rrp = -27.14
        expected_price = 0.916755
        price = evoenergy.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.05, expected_price, places=2)

    def test_peak_evoenergy_functionality(self):
        interval_time = datetime(2025, 3, 28, 15, 55, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = '017'
        rrp = 119.63
        expected_price = 17.46672
        price = evoenergy.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 0.96, expected_price, places=1)

    def test_noon_evoenergy_april(self):
        interval_time = datetime(2025, 4, 30, 12, 00, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = '017'
        rrp = -23.5
        expected_price = 1.026793
        price = evoenergy.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        print(f"Loss factor: {loss_factor}")
        self.assertAlmostEqual(price * 0.83, expected_price, places=1)

    def test_peak_evoenergy_late_april(self):
        interval_time = datetime(2026, 4, 30, 7, 40, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = '017'
        rrp = -1.8
        expected_price = 18.82
        price = evoenergy.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        print(f"Loss factor: {loss_factor}")
        self.assertAlmostEqual(price * 1.06796, expected_price, places=1)

    def test_evoenergy_017_2026_27_peak(self):
        # Post-1-Jul-2026 New Residential TOU peak: 16.184 → 19.084 (incl 10% GST).
        # Was pinned at 16.049 against the original mis-transcribed table; re-based
        # once settled retail data showed every 2026-27 017 period 3.035 c/kWh low.
        interval_time = datetime(2026, 7, 20, 18, 0, tzinfo=ZoneInfo('Australia/Sydney'))
        price = evoenergy.convert(interval_time, '017', 100.0)
        self.assertAlmostEqual(price, 10.0 + 19.084 * 1.1, places=2)

    def test_evoenergy_090_midday(self):
        # Regression: tariff 090 has no peak_months. Previously is_peak_month
        # defaulted to False, so the 'Peak' period (7am–5pm) was always
        # skipped and any midday lookup fell through to the slope/intercept
        # default. Verify Peak now applies.
        interval_time = datetime(2025, 9, 16, 11, 0, tzinfo=ZoneInfo('Australia/Sydney'))
        price = evoenergy.convert(interval_time, '090', 0.0)
        # 2025–26 schedule peak rate 17.518 c/kWh × 1.1 GST = 19.27 c/kWh
        self.assertAlmostEqual(price, 17.518 * 1.1, places=2)

    def test_evoenergy_015_shoulder_month_morning(self):
        # Regression: 015 has peak_months [11,12,1,2,3,6,7,8]. In shoulder
        # months (Apr/May/Sep/Oct) at 8am Peak is skipped and previously no
        # other period covered 7-9, so the lookup fell through to the
        # slope/intercept default. Should now return Shoulder rate.
        interval_time = datetime(2025, 4, 15, 8, 0, tzinfo=ZoneInfo('Australia/Sydney'))
        price = evoenergy.convert(interval_time, '015', 0.0)
        self.assertAlmostEqual(price, 8.199 * 1.1, places=2)

    def test_evoenergy_018_shoulder_month_evening(self):
        # Same fix on 018: in shoulder months 17–21 should return Off-peak.
        interval_time = datetime(2025, 10, 15, 18, 0, tzinfo=ZoneInfo('Australia/Sydney'))
        price = evoenergy.convert(interval_time, '018', 0.0)
        self.assertAlmostEqual(price, 5.665 * 1.1, places=2)


class TestEvoenergy2026RateLevel(unittest.TestCase):
    """Guard the *absolute level* of the 2026-27 017 rates, not just their shape.

    The 2026-27 rates were originally transcribed 3.035 c/kWh too low on every
    period. Nothing in a relative check can see that: shift all periods of a
    tariff by the same amount and the period ratios, the shape of a priced day,
    and any "peak > off-peak > soak" ordering all still hold. The anchor has to
    come from outside the table.

    That anchor is settled retail data. On a pass-through (wholesale) retail plan
    the customer's settled price for an interval decomposes as::

        settled = k * spot + GST * network_rate + fee

    where ``spot`` is the RRP in c/kWh, ``k`` folds the network loss factors and
    GST into the spot term, and ``fee`` is the retailer's own flat per-kWh charge.
    ``k`` and ``fee`` are properties of the plan, not of the interval, so three
    intervals in three different network periods over-determine them: solve from
    two and the third must fall out.

    The intervals below are real settled (final, not forecast) data for one ACT
    tariff 017 site, deliberately carrying no site, meter, NMI or account
    identifier -- RRP is public market data and the settled price is a
    deterministic function of published rates plus the plan's flat fee.

    The decisive assertion is ``test_implied_retailer_fee_is_plausible``: with the
    rates too low, the arithmetic still closes perfectly, but it has to absorb the
    3.34 c/kWh error into ``fee``, pushing it to ~4.56 c/kWh -- far above any real
    pass-through retail margin, and ~3.3 c/kWh above what the same retailer
    charged the same site the month before under the 2025-26 rates.
    """

    # (period, interval, rrp $/MWh, settled retail c/kWh incl GST)
    SETTLED = [
        ('Peak', datetime(2026, 7, 24, 19, 10, tzinfo=ZoneInfo('Australia/Sydney')), 77.22, 31.01904113),
        ('Off-peak', datetime(2026, 7, 24, 16, 30, tzinfo=ZoneInfo('Australia/Sydney')), 81.00, 18.58223738),
        ('Solar Soak', datetime(2026, 7, 24, 11, 15, tzinfo=ZoneInfo('Australia/Sydney')), 42.80, 11.39746685),
    ]

    # Same site, same retailer, one month earlier under the 2025-26 rates. Recovered
    # by the identical solve; the fee is a plan property and should barely move
    # across a price-year boundary.
    FEE_2025_26 = 1.2220

    def _network_component(self, interval_time, rrp, settled, k, fee):
        """The GST-inclusive network charge the settled price implies."""
        return settled - k * (rrp / 10) - fee

    def _solve_k_and_fee(self):
        """Solve (k, fee) from the Peak and Off-peak intervals via the table rates."""
        rows = []
        for name, interval_time, rrp, settled in self.SETTLED[:2]:
            # convert() at rrp=0 isolates GST * network_rate for that period.
            network_c = evoenergy.convert(interval_time, '017', 0.0)
            rows.append((rrp / 10, settled - network_c))
        (x1, y1), (x2, y2) = rows
        k = (y1 - y2) / (x1 - x2)
        fee = y1 - k * x1
        return k, fee

    def test_implied_retailer_fee_is_plausible(self):
        # THE regression test. A flat level error in the table is pushed into the
        # solved fee, so bounding the fee bounds the level.
        _, fee = self._solve_k_and_fee()
        self.assertLess(
            fee, 2.0,
            msg=f'implied retailer fee {fee:.4f} c/kWh is too high to be a retail '
                f'margin -- the 017 network rates are most likely too low',
        )
        self.assertGreater(
            fee, 0.0,
            msg=f'implied retailer fee {fee:.4f} c/kWh is negative -- the 017 '
                f'network rates are most likely too high',
        )

    def test_implied_fee_is_stable_across_the_price_year_boundary(self):
        # A retailer's flat per-kWh charge does not jump when the AER rates change.
        _, fee = self._solve_k_and_fee()
        self.assertAlmostEqual(fee, self.FEE_2025_26, places=2)

    def test_third_period_is_predicted_by_the_other_two(self):
        # Structural check: confirms the *relative* spacing of the three periods.
        # Passes even when the level is wrong, which is exactly why it is not
        # sufficient on its own.
        k, fee = self._solve_k_and_fee()
        name, interval_time, rrp, settled = self.SETTLED[2]
        predicted = k * (rrp / 10) + evoenergy.convert(interval_time, '017', 0.0) + fee
        self.assertAlmostEqual(predicted, settled, places=3)

    def test_solved_spot_multiplier_is_a_loss_factor_times_gst(self):
        # Sanity on the other solved unknown: k = DLF * MLF * GST, so a little
        # over 1.1. Catches a solve that "fits" by distorting the spot term.
        k, _ = self._solve_k_and_fee()
        self.assertGreater(k, 1.1)
        self.assertLess(k, 1.25)

    def test_2026_27_rates_are_not_below_2025_26(self):
        # The 2026-27 AER update raised these rates. A transcription that lands
        # below the prior year is the signature of the original bug.
        for code in ('017', '018'):
            prior = {name: rate for name, _s, _e, rate in evoenergy.tariffs_2025_26[code]['periods']}
            for name, _s, _e, rate in evoenergy.tariffs_2026_27[code]['periods']:
                with self.subTest(tariff=code, period=name):
                    self.assertGreaterEqual(rate, prior[name])

    def test_017_period_rates_incl_gst(self):
        # Pin the corrected values directly, so a future edit has to be deliberate.
        for interval_time, expected_ex_gst in (
            (datetime(2026, 7, 24, 19, 10, tzinfo=ZoneInfo('Australia/Sydney')), 19.084),
            (datetime(2026, 7, 24, 16, 30, tzinfo=ZoneInfo('Australia/Sydney')), 7.386),
            (datetime(2026, 7, 24, 11, 15, tzinfo=ZoneInfo('Australia/Sydney')), 4.814),
        ):
            with self.subTest(interval=interval_time.isoformat()):
                self.assertAlmostEqual(
                    evoenergy.convert(interval_time, '017', 0.0), expected_ex_gst * 1.1, places=4)
