import importlib
import pkgutil
import unittest

import aemo_to_tariff

# Networks that define a feed_in_tariffs_* dict alongside tariffs_*.
NETWORKS = ['endeavour', 'essential', 'evoenergy', 'sapower']

CUSTOMER_TYPES = ['Residential', 'Business', 'Battery']


def _battery_tariff_modules():
    """Every network module exposing battery_tariffs()."""
    for info in pkgutil.iter_modules(aemo_to_tariff.__path__):
        module = importlib.import_module(f'aemo_to_tariff.{info.name}')
        # convert.py re-exports battery_tariffs as a dispatcher, not a network.
        if info.name != 'convert' and hasattr(module, 'battery_tariffs'):
            yield info.name, module

# Export-only tariff codes: assigned in addition to an import tariff rather than
# instead of one, so they legitimately have no entry in tariffs_*. Each is priced
# purely on export in the network's own schedule (no fixed daily charge, all
# import energy columns blank/zero). Anything NOT listed here that appears in
# feed_in_tariffs_* but not tariffs_* is a real gap and fails below.
#
#   endeavour N61   'Prosumer' — AER 2026-27 consolidated stakeholder report
#                   (8 May 2026), 'Tariff schedule' row 267: fixed charge and
#                   every import energy column are 0; only the export reward and
#                   solar soak export columns are populated. Paired with an
#                   import tariff (N71/N73) — see endeavour.battery_tariffs.
#   essential BLNREX2 / BLNBEX1  'LV Residential/Business Solar Export' — paired
#                   with BLNRSS2 / BLNBSS1 import; see essential.battery_tariffs.
#   sapower  RESELEX / SBELEX    export components of the Electrify tariffs,
#                   paired with RESELE / SBELE import.
EXPORT_ONLY = {
    'endeavour': {'N61'},
    'essential': {'BLNREX2', 'BLNBEX1'},
    'sapower': {'RESELEX', 'SBELEX'},
    'evoenergy': set(),
}


class TestTariffSymmetry(unittest.TestCase):
    def test_feed_in_codes_have_import_entry_or_are_export_only(self):
        """Every feed-in code must either price on import too, or be declared export-only.

        Guards the gap where a code is added to feed_in_tariffs_* but forgotten in
        tariffs_*, which surfaces at runtime as get_daily_fee/get_periods raising
        ValueError and convert() KeyError-ing.
        """
        for network in NETWORKS:
            module = importlib.import_module(f'aemo_to_tariff.{network}')
            for attr in dir(module):
                if not attr.startswith('feed_in_tariffs_'):
                    continue
                year = attr[len('feed_in_tariffs_'):]
                import_tariffs = getattr(module, f'tariffs_{year}', None)
                self.assertIsNotNone(
                    import_tariffs,
                    f'{network}.{attr} has no matching tariffs_{year}')

                for code in getattr(module, attr):
                    if code in EXPORT_ONLY[network]:
                        continue
                    with self.subTest(network=network, year=year, code=code):
                        self.assertIn(
                            code, import_tariffs,
                            f'{network}: {code} is in {attr} but missing from '
                            f'tariffs_{year}. Add its import periods and '
                            f'fixed_daily_charge, or declare it export-only in '
                            f'EXPORT_ONLY with a source citation.')

    def test_export_only_codes_are_actually_export_only(self):
        """Keep EXPORT_ONLY honest: if a code gains an import entry, stop exempting it."""
        for network in NETWORKS:
            module = importlib.import_module(f'aemo_to_tariff.{network}')
            for code in EXPORT_ONLY[network]:
                for attr in dir(module):
                    if not attr.startswith('tariffs_'):
                        continue
                    with self.subTest(network=network, code=code, table=attr):
                        self.assertNotIn(
                            code, getattr(module, attr),
                            f'{network}: {code} is declared export-only but now has '
                            f'an import entry in {attr}. Remove it from EXPORT_ONLY.')

    def test_export_only_codes_exist_on_the_feed_in_side(self):
        """A stale EXPORT_ONLY entry would silently exempt nothing."""
        for network in NETWORKS:
            module = importlib.import_module(f'aemo_to_tariff.{network}')
            feed_in_codes = set()
            for attr in dir(module):
                if attr.startswith('feed_in_tariffs_'):
                    feed_in_codes |= set(getattr(module, attr))
            for code in EXPORT_ONLY[network]:
                with self.subTest(network=network, code=code):
                    self.assertIn(
                        code, feed_in_codes,
                        f'{network}: {code} is declared export-only but appears in no '
                        f'feed_in_tariffs_* table. Remove the stale EXPORT_ONLY entry.')


class TestBatteryTariffCodesResolve(unittest.TestCase):
    def test_import_codes_have_import_entry(self):
        """Codes battery_tariffs() offers for import must actually price on import.

        Checked against the *current* schedule only: battery_tariffs() is a
        present-tense recommendation, and codes introduced in a later price year
        (e.g. energex 96200, a 2026-27 trial tariff) are legitimately absent from
        earlier tables.

        sapower listed export-only RESELEX under 'import', so a caller iterating
        the import codes hit ValueError from get_periods().
        """
        for network, module in _battery_tariff_modules():
            current = module.get_tariffs()
            for customer_type in CUSTOMER_TYPES:
                try:
                    codes = module.battery_tariffs(customer_type)['import']
                except ValueError:
                    continue  # network doesn't offer this customer type
                for code in codes:
                    with self.subTest(network=network, customer=customer_type, code=code):
                        self.assertIn(
                            code, current,
                            f'{network}.battery_tariffs({customer_type!r}) offers '
                            f'{code} for import, but it has no entry in the current '
                            f'tariffs table. Either add its import rates or move it '
                            f'to the export list.')

    def test_import_codes_survive_get_periods(self):
        """The end-to-end symptom: get_periods() must not raise for an import code."""
        for network, module in _battery_tariff_modules():
            for customer_type in CUSTOMER_TYPES:
                try:
                    codes = module.battery_tariffs(customer_type)['import']
                except ValueError:
                    continue
                for code in codes:
                    with self.subTest(network=network, customer=customer_type, code=code):
                        try:
                            module.get_periods(code)
                        except ValueError as exc:
                            self.fail(
                                f'{network}.get_periods({code!r}) raised "{exc}" for an '
                                f'import code offered by battery_tariffs({customer_type!r}).')


if __name__ == '__main__':
    unittest.main()
