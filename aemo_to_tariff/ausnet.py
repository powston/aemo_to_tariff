# aemo_to_tariff/ausnet.py

from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

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


# AusNet Services tariffs
tariffs_2025_26 = {
    'NAST11S': {
        'name': 'Small Business Time of Use',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 5.5+22.4055),
            ('Off-Peak', time(0, 0), time(15, 0), 14.6394),
            ('Off-Peak', time(21, 0), time(0, 0), 14.6394)
        ]
    },
    'NEE11S': {
        'name': 'Small Residential Single Rate (Standard Feed-in)',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 13.6472)
        ]
    }
}

# AER 2026–27 consolidated stakeholder report (8 May 2026). Off-Peak rate
# for NAST11S/NASS11S drops sharply (was ~14.6, now 5.33 c/kWh) reflecting
# the AER's separately-tariffed solar soak window.
tariffs_2026_27 = {
    'NAST11S': {
        'name': 'Small Residential Time of Use',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 26.9556),
            ('Off-Peak', time(0, 0), time(15, 0), 5.3299),
            ('Off-Peak', time(21, 0), time(0, 0), 5.3299)
        ]
    },
    'NEE11S': {
        'name': 'Small Residential Single Rate (Standard Feed-in)',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 13.4297)
        ]
    },
    'NEE11': {
        'name': 'Small Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 13.4297)
        ]
    },
    'NEE12': {
        'name': 'Small Business Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 17.6073)
        ]
    },
    'NAST12': {
        'name': 'Small Business Time of Use',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 20.7731),
            ('Off-Peak', time(0, 0), time(15, 0), 4.8791),
            ('Off-Peak', time(21, 0), time(0, 0), 4.8791)
        ]
    }
}

# Optional daily fees if available
daily_fees_2025_26 = {
    'NAST11S': 3.00,
    'NEE11S': 0.3795,  # $138.51/year = 37.95 c/day
}

# AER 2026–27: NEE11S/NEE11 standing $145.305/year ≈ $0.3981/day.
daily_fees_2026_27 = {
    'NAST11S': 145.30522170722094 / 365,
    'NEE11': 145.30522170722094 / 365,
    'NEE11S': 145.30522170722094 / 365,
    'NEE12': 148.93785224990143 / 365,
    'NAST12': 148.93785224990143 / 365,
}

# Optional demand charges if needed
demand_charges_2025_26 = {
    'NAST11D': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 33.2942),  # ¢/kW/day
        ]
    },
}

demand_charges_2026_27 = {
    'NAST11D': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 33.2942),
        ]
    },
    # Small business single-rate demand from AER 2026–27 ($/kW)
    'NASN12': {'Peak': 11.4725, 'Off-Peak': 2.8622},
    'NASN19': {'Peak': 9.1933, 'Off-Peak': 2.2936},
}


def get_tariffs(interval_time=None):
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_daily_fees(interval_time=None):
    return daily_fees_2026_27 if _use_2026_prices(interval_time) else daily_fees_2025_26


def get_demand_charges(interval_time=None):
    return demand_charges_2026_27 if _use_2026_prices(interval_time) else demand_charges_2025_26


def get_periods(tariff_code: str, interval_time=None):
    tariff = get_tariffs(interval_time).get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")
    return tariff['periods']

def convert(interval_datetime: datetime, tariff_code: str, rrp: float) -> float:
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10.0  # Convert $/MWh to c/kWh

    tariff = get_tariffs(interval_datetime).get(tariff_code)
    if not tariff:
        return rrp_c_kwh * 1.0 + 5.0  # fallback approximation

    for period_name, start, end, rate in tariff['periods']:
        if start < end and start <= interval_time < end:
            return rrp_c_kwh + rate
        elif start > end and (interval_time >= start or interval_time < end):  # overnight window
            return rrp_c_kwh + rate

    return rrp_c_kwh + tariff['periods'][0][3]

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float) -> float:
    return rrp / 10.0  # Simple passthrough unless AusNet has special FiT windows

def get_daily_fee(tariff_code: str, annual_usage: float = None, interval_time=None) -> float:
    return get_daily_fees(interval_time).get(tariff_code, 0.0)

def estimate_demand_fee(interval_time: datetime, tariff_code: str, demand_kw: float):
    """
    Estimate the demand fee for a given tariff code, demand amount, and time period.

    Parameters:
    - interval_time (datetime): The interval datetime.
    - tariff_code (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for 8100 and 8300 tariffs).

    Returns:
    - float: The estimated demand fee in dollars.
    """
    time_of_day = interval_time.astimezone(ZoneInfo(time_zone())).time()
    demand_charges = get_demand_charges(interval_time)

    charge = demand_charges.get('NAST11D')
    if tariff_code in demand_charges:
        charge = demand_charges[tariff_code]
    if charge is None:
        return 0.0  # Return 0 if the tariff doesn't have a demand charge
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

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30, interval_time=None) -> float:
    demand_charges = get_demand_charges(interval_time)
    if tariff_code not in demand_charges:
        return 0.0
    rate = demand_charges[tariff_code]
    if isinstance(rate, dict):
        rate = rate.get('Peak', 0)
    return (rate / 30) * demand_kw * days
