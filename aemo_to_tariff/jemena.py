# aemo_to_tariff/jemena.py
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
    'PRTOU': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(16, 0), 4.8700),
            ('Peak', time(16, 0), time(21, 0), 18.3400),
            ('Off-peak', time(21, 0), time(23, 59), 4.8700),
        ]
    }
}

# AER 2026–27: D1↔A100 (Residential Single Rate), PRTOU↔A130 (Residential
# Time of Use Daytime Saver).
tariffs_2026_27 = {
    'D1': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.486)
        ]
    },
    'A100': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.486)
        ]
    },
    'PRTOU': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(16, 0), 4.551),
            ('Peak', time(16, 0), time(21, 0), 18.208),
            ('Off-peak', time(21, 0), time(23, 59), 4.551),
        ]
    },
    'A130': {
        'name': 'Residential TOU Daytime Saver',
        'periods': [
            ('Off-peak', time(0, 0), time(16, 0), 4.551),
            ('Peak', time(16, 0), time(21, 0), 18.208),
            ('Off-peak', time(21, 0), time(23, 59), 4.551),
        ]
    },
    'A200': {
        'name': 'Small Business Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 13.107)
        ]
    },
    'A210': {
        'name': 'Small Business TOU Weekdays',
        'periods': [
            ('Off-peak', time(0, 0), time(16, 0), 3.713),
            ('Peak', time(16, 0), time(21, 0), 17.020),
            ('Off-peak', time(21, 0), time(23, 59), 3.713),
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

# AER 2026–27 large business demand: A30C 97.107 $/kW/year, A32C 85.127, etc.
# Existing legacy codes preserved at the same rate as 2025–26 since they
# don't appear in the new AER schedule.
demand_charges_2026_27 = {
    'PRDEMD': { 'Peak': 10.0},
    'PSTDEMD': { 'Peak': 10.0},
    'PSTCTD': { 'Peak': 10.0},
    'PSTNPD': { 'Peak': 10.0},
    'PSTNCD': { 'Peak': 10.0},
    'PSTNDD': { 'Peak': 10.0},
    'A230': { 'Peak': 77.889},
    'A270': { 'Peak': 77.889},
    'A30C': { 'Peak': 97.107},
    'A32C': { 'Peak': 85.127},
    'A34C': { 'Peak': 81.705},
    'A37T': { 'Peak': 60.995},
    'A40C': { 'Peak': 72.564},
}


daily_fees_2025_26 = {
    # Legacy: 1.2 hardcoded for all
}

# AER 2026–27 standing charges ($/year → $/day). Residential A100 $120.77/yr
# ≈ $0.3309/day; small business A200 $246.75/yr ≈ $0.6760/day; large business
# A30C $4079.85/yr ≈ $11.18/day.
daily_fees_2026_27 = {
    'D1': 120.774 / 365,
    'A100': 120.774 / 365,
    'PRTOU': 120.754 / 365,
    'A130': 120.754 / 365,
    'A10E': 121.014 / 365,
    'A200': 246.75 / 365,
    'A210': 250.196 / 365,
    'A230': 494.463 / 365,
    'A270': 532.556 / 365,
    'A30B': 4079.849 / 365,
    'A30C': 4145.116 / 365,
    'A32C': 7397.195 / 365,
    'A34C': 13709.068 / 365,
    'A37T': 17401.314 / 365,
    'A40C': 32255.677 / 365,
}


def get_tariffs(interval_time=None):
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_demand_charges(interval_time=None):
    return demand_charges_2026_27 if _use_2026_prices(interval_time) else demand_charges_2025_26


def get_daily_fees(interval_time=None):
    return daily_fees_2026_27 if _use_2026_prices(interval_time) else daily_fees_2025_26


def get_daily_fee(tariff_code: str, interval_time=None):
    # Fee tables are transcribed in $/day; the package contract is cents/day.
    if _use_2026_prices(interval_time):
        fees = get_daily_fees(interval_time)
        return fees.get(tariff_code, 1.2) * 100
    return 120.0  # 2025–26 placeholder behaviour preserved

def get_periods(tariff_code: str, interval_time=None):
    tariff = get_tariffs(interval_time).get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return tariff['periods']

def estimate_demand_fee(interval_time: datetime, tariff_code: str, demand_kw: float):
    """
    Estimate the demand fee for a given tariff code, demand amount, and time period.
    """
    time_of_day = interval_time.astimezone(ZoneInfo(time_zone())).time()
    demand_charges = get_demand_charges(interval_time)

    if tariff_code not in demand_charges:
        return 0.0  # Return 0 if the tariff doesn't have a demand charge

    charge = demand_charges[tariff_code]
    if isinstance(charge, dict):
        # Determine the time period
        if 'Peak' in charge and time(17, 0) <= time_of_day < time(20, 0):
            charge_per_kw_per_month = charge['Peak']
        elif 'Off-Peak' in charge and time(11, 0) <= time_of_day < time(13, 0):
            charge_per_kw_per_month = charge['Off-Peak']
        else:
            charge_per_kw_per_month = charge.get('Shoulder', 0.0)
    else:
        charge_per_kw_per_month = charge

    return charge_per_kw_per_month * demand_kw

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh.
    """
    rrp_c_kwh = rrp / 10

    return rrp_c_kwh

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for Jemena.

    Parameters:
    - interval_time (str): The interval time.
    - tariff (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
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
