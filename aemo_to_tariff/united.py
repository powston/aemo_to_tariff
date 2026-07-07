# aemo_to_tariff/united.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from datetime import time

def time_zone():
    return 'Australia/Melbourne'

# AER-approved prices change at the start of each financial year (1 July).
# 2026–27 prices apply from 1 July 2026; before that, 2025–26 applies.
PRICE_TRANSITION_DATE = datetime(2026, 7, 1, 0, 0, tzinfo=ZoneInfo('Australia/Melbourne'))


def _use_2026_prices(interval_time=None) -> bool:
    if interval_time is None:
        interval_time = datetime.now(tz=ZoneInfo(time_zone()))
    if interval_time.tzinfo is None:
        interval_time = interval_time.replace(tzinfo=ZoneInfo(time_zone()))
    return interval_time >= PRICE_TRANSITION_DATE


tariffs_2025_26 = {
    'D1': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.6700)
        ]
    },
    'URTOU': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 4.76),
            ('Peak', time(15, 0), time(21, 0), 19.13),
            ('Off-peak', time(21, 0), time(23, 59), 4.76),
        ]
    },
    'FURTOU': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 4.76),
            ('Peak', time(15, 0), time(21, 0), 19.13),
            ('Off-peak', time(21, 0), time(23, 59), 4.76),
        ]
    },
    'FURDS': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 6.71),
            ('Solar-Soaker', time(10, 0), time(15, 0), 0.0),
            ('Off-peak', time(15, 0), time(16, 0), 6.71),
            ('Peak', time(16, 0), time(21, 0), 18.82),
            ('Off-peak', time(21, 0), time(23, 59), 6.71),
        ]
    },
    'URDS': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 6.71),
            ('Solar-Soaker', time(10, 0), time(15, 0), 0.0),
            ('Off-peak', time(15, 0), time(16, 0), 6.71),
            ('Peak', time(16, 0), time(21, 0), 18.82),
            ('Off-peak', time(21, 0), time(23, 59), 6.71),
        ]
    },
    'NDMO21': {
        'name': 'NDMO21 TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 5.61),
            ('Peak', time(15, 0), time(21, 0), 19.29),
            ('Off-peak', time(21, 0), time(23, 59), 5.61),
        ]
    },
    'NDTOU': {
        'name': 'NDTOU TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 4.58),
            ('Peak', time(15, 0), time(21, 0), 20.60),
            ('Off-peak', time(21, 0), time(23, 59), 4.58),
        ]
    },
    'PRDS': {
        'name': 'Residential daytime saver',
        'periods': [
            ('Off-peak', time(0, 0), time(10, 0), 7.0),
            ('Day', time(10, 0), time(15, 0), 0.0),
            ('Off-peak', time(15, 0), time(16, 0), 7.0),
            ('Peak', time(16, 0), time(21, 0), 19.61),
            ('Off-peak', time(21, 0), time(23, 59), 7.0),
        ]
    }
}

# AER 2026–27 consolidated stakeholder report (8 May 2026).
tariffs_2026_27 = {
    'D1': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.720)
        ]
    },
    'LVS1R': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.720)
        ]
    },
    'URTOU': {
        'name': 'Residential TOU (URSTOU)',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 5.220),
            ('Peak', time(15, 0), time(21, 0), 20.920),
            ('Off-peak', time(21, 0), time(23, 59), 5.220),
        ]
    },
    'URSTOU': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 5.220),
            ('Peak', time(15, 0), time(21, 0), 20.920),
            ('Off-peak', time(21, 0), time(23, 59), 5.220),
        ]
    },
    'FURTOU': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 5.220),
            ('Peak', time(15, 0), time(21, 0), 20.920),
            ('Off-peak', time(21, 0), time(23, 59), 5.220),
        ]
    },
    'FURDS': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 6.71),
            ('Solar-Soaker', time(10, 0), time(15, 0), 0.0),
            ('Off-peak', time(15, 0), time(16, 0), 6.71),
            ('Peak', time(16, 0), time(21, 0), 18.82),
            ('Off-peak', time(21, 0), time(23, 59), 6.71),
        ]
    },
    'URDS': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 6.71),
            ('Solar-Soaker', time(10, 0), time(15, 0), 0.0),
            ('Off-peak', time(15, 0), time(16, 0), 6.71),
            ('Peak', time(16, 0), time(21, 0), 18.82),
            ('Off-peak', time(21, 0), time(23, 59), 6.71),
        ]
    },
    'NDMO21': {
        'name': 'NDMO21 TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 6.000),
            ('Peak', time(15, 0), time(21, 0), 19.510),
            ('Off-peak', time(21, 0), time(23, 59), 6.000),
        ]
    },
    'NDTOU': {
        'name': 'NDTOU TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 3.890),
            ('Peak', time(15, 0), time(21, 0), 15.540),
            ('Off-peak', time(21, 0), time(23, 59), 3.890),
        ]
    },
    'LVTOU': {
        'name': 'Small Business ToU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 3.890),
            ('Peak', time(15, 0), time(21, 0), 15.540),
            ('Off-peak', time(21, 0), time(23, 59), 3.890),
        ]
    },
    'LVM1R': {
        'name': 'Small Business Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.400)
        ]
    },
    'PRDS': {
        'name': 'Residential daytime saver',
        'periods': [
            ('Off-peak', time(0, 0), time(10, 0), 7.0),
            ('Day', time(10, 0), time(15, 0), 0.0),
            ('Off-peak', time(15, 0), time(16, 0), 7.0),
            ('Peak', time(16, 0), time(21, 0), 19.61),
            ('Off-peak', time(21, 0), time(23, 59), 7.0),
        ]
    }
}


demand_charges_2025_26 = {
    'PRDEMD': { 'Peak': 10.0},
    'PSTDEMD': { 'Peak': 10.0},
    'PSTCTD': { 'Peak': 10.0},
    'PSTNPD': { 'Peak': 10.0},
    'PSTNCD': { 'Peak': 10.0},
    'PSTNDD': { 'Peak': 10.0},
}

# AER 2026–27 demand: LVMKW1R/UMBD Summer 63.86 / Non-summer 31.36 c/kW/day.
# LVkVATOU 38.91 / 35.28; HVkVATOU 26.15 / 28.93; Subtransmission 7.8.
demand_charges_2026_27 = {
    'PRDEMD': { 'Peak': 10.0},
    'PSTDEMD': { 'Peak': 10.0},
    'PSTCTD': { 'Peak': 10.0},
    'PSTNPD': { 'Peak': 10.0},
    'PSTNCD': { 'Peak': 10.0},
    'PSTNDD': { 'Peak': 10.0},
    'LVMKW1R': { 'Peak': 63.86, 'Off-Peak': 31.36 },
    'UMBD': { 'Peak': 63.86, 'Off-Peak': 31.36 },
    'LVkVATOU': { 'Peak': 38.91, 'Off-Peak': 35.28 },
    'HVkVATOU': { 'Peak': 26.15, 'Off-Peak': 28.93 },
    'SUBTkVATOU': { 'Peak': 7.8 },
}


daily_fees_2025_26 = {
    # Legacy: 41.10 hardcoded for all
}

# AER 2026–27 standing charges (cents/day). Residential D1/URSTOU/URCER:
# 31.51 c/day. Small business LVM1R/LVTOU/LVMKW1R: 61.64. Medium UMBD/UMBO:
# 123.29.
daily_fees_2026_27 = {
    'D1': 31.51,
    'LVS1R': 31.51,
    'URTOU': 31.51,
    'URSTOU': 31.51,
    'URCER': 31.51,
    'URDS': 31.51,
    'FURTOU': 31.51,
    'FURDS': 31.51,
    'LVM1R': 61.64,
    'LVTOU': 61.64,
    'LVMKW1R': 61.64,
    'NDTOU': 61.64,
    'UMBD': 123.29,
    'UMBO': 123.29,
    'NDMO21': 123.29,
}


def get_tariffs(interval_time=None):
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_demand_charges(interval_time=None):
    return demand_charges_2026_27 if _use_2026_prices(interval_time) else demand_charges_2025_26


def get_daily_fees(interval_time=None):
    return daily_fees_2026_27 if _use_2026_prices(interval_time) else daily_fees_2025_26


def get_daily_fee(tariff_code: str, interval_time=None):
    # Fee tables are transcribed in c/day; the package contract is dollars/day.
    if _use_2026_prices(interval_time):
        return get_daily_fees(interval_time).get(tariff_code, 41.10) / 100
    return 41.10 / 100  # 2025–26 placeholder behaviour preserved

def get_periods(tariff_code: str, interval_time=None):
    tariff = get_tariffs(interval_time).get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh.
    """
    rrp_c_kwh = rrp / 10

    return rrp_c_kwh

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for United Energy.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()

    rrp_c_kwh = rrp / 10
    tariff = get_tariffs(interval_datetime)[tariff_code]

    # Find the applicable period and rate
    for period, start, end, rate in tariff['periods']:
        if start <= interval_time < end:
            total_price = rrp_c_kwh + rate
            return total_price

        # Handle overnight periods (e.g., 22:00 to 07:00)
        if start > end and (interval_time >= start or interval_time < end):
            total_price = rrp_c_kwh + rate
            return total_price

    # Otherwise, this terrible approximation
    slope = 1.037869032618134
    intercept = 5.586606750833143
    return rrp_c_kwh * slope + intercept


def estimate_demand_fee(interval_time: datetime, tariff_code: str, demand_kw: float):
    """
    Estimate the demand fee for a given tariff code, demand amount, and time period.
    """
    time_of_day = interval_time.astimezone(ZoneInfo(time_zone())).time()
    demand_charges = get_demand_charges(interval_time)

    if tariff_code not in demand_charges:
        return 0.0

    charge = demand_charges[tariff_code]
    if isinstance(charge, dict):
        if 'Peak' in charge and time(17, 0) <= time_of_day < time(20, 0):
            charge_per_kw_per_month = charge['Peak']
        elif 'Off-Peak' in charge and time(11, 0) <= time_of_day < time(13, 0):
            charge_per_kw_per_month = charge['Off-Peak']
        else:
            charge_per_kw_per_month = charge.get('Shoulder', 0.0)
    else:
        charge_per_kw_per_month = charge

    return charge_per_kw_per_month * demand_kw
