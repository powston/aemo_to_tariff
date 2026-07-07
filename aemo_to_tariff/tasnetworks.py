# aemo_to_tariff/tasnetworks.py
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

def time_zone():
    return 'Australia/Hobart'

# AER-approved prices change at the start of each financial year (1 July).
# 2026–27 prices apply from 1 July 2026; before that, 2025–26 applies.
PRICE_TRANSITION_DATE = datetime(2026, 7, 1, 0, 0, tzinfo=ZoneInfo('Australia/Hobart'))


def _use_2026_prices(interval_time=None) -> bool:
    if interval_time is None:
        interval_time = datetime.now(tz=ZoneInfo(time_zone()))
    if interval_time.tzinfo is None:
        interval_time = interval_time.replace(tzinfo=ZoneInfo(time_zone()))
    return interval_time >= PRICE_TRANSITION_DATE


def battery_tariffs(customer_type: str):
    """
    Get the battery tariff for a given customer type.

    Parameters:
    - customer_type (str): The customer type ('Residential' or 'Business').

    Returns:
    - str: The battery tariff code.
    """
    if customer_type == 'Residential':
        return {'import': ['TAS93']}
    elif customer_type == 'Business':
        return {'import': ['TAS94']}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")


tariffs_2025_26 = {
    'TAS93': {
        'name': 'Residential time of use consumption',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 17.229),
            ('Peak', time(16, 0), time(21, 0), 17.229),
            ('Off-peak', time(21, 0), time(7, 0), 3.618),
            ('Off-peak', time(10, 0), time(16, 0), 3.618),
        ]
    },
    'TAS87': {
        'name': 'Residential time of use demand',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 30.133),
            ('Peak', time(16, 0), time(21, 0), 30.133),
            ('Off-peak', time(21, 0), time(7, 0), 10.034),
            ('Off-peak', time(10, 0), time(16, 0), 10.034),
        ]
    },
    'TAS97': {
        'name': 'Residential time of use CER',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 18.090),
            ('Peak', time(16, 0), time(21, 0), 18.090),
            ('Off-peak', time(21, 0), time(7, 0), 2.714),
            ('Off-peak', time(10, 0), time(16, 0), 2.714),
            ('Super off-peak', time(10, 0), time(16, 0), 0.090),
        ]
    },
    'TAS94': {
        'name': 'Small business time of use consumption',
        'periods': [
            ('Peak', time(7, 0), time(22, 0), 16.784),
            ('Shoulder', time(22, 0), time(23, 59), 9.886),
            ('Shoulder', time(0, 0), time(7, 0), 9.886),
            ('Off-peak', time(0, 0), time(23, 59), 2.426),
        ]
    },
    'TAS88': {
        'name': 'Small business time of use demand',
        'periods': [
            ('Peak', time(7, 0), time(22, 0), 68.628),
            ('Off-peak', time(22, 0), time(7, 0), 22.853),
        ]
    },
}

# AER 2026–27 consolidated stakeholder report (8 May 2026).
tariffs_2026_27 = {
    'TAS93': {
        'name': 'Residential time of use consumption',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 19.860),
            ('Peak', time(16, 0), time(21, 0), 19.860),
            ('Off-peak', time(21, 0), time(7, 0), 4.369),
            ('Off-peak', time(10, 0), time(16, 0), 4.369),
        ]
    },
    'TAS87': {
        'name': 'Residential time of use demand',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 34.772),
            ('Peak', time(16, 0), time(21, 0), 34.772),
            ('Off-peak', time(21, 0), time(7, 0), 11.579),
            ('Off-peak', time(10, 0), time(16, 0), 11.579),
        ]
    },
    'TAS97': {
        'name': 'Residential time of use CER',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 20.853),
            ('Peak', time(16, 0), time(21, 0), 20.853),
            ('Off-peak', time(21, 0), time(7, 0), 3.128),
            ('Off-peak', time(10, 0), time(16, 0), 3.128),
            ('Super off-peak', time(10, 0), time(16, 0), 0.104),
        ]
    },
    'TAS94': {
        'name': 'Small business time of use consumption',
        'periods': [
            ('Peak', time(7, 0), time(22, 0), 19.766),
            ('Shoulder', time(22, 0), time(23, 59), 11.643),
            ('Shoulder', time(0, 0), time(7, 0), 11.643),
            ('Off-peak', time(0, 0), time(23, 59), 2.670),
        ]
    },
    'TAS88': {
        'name': 'Small business time of use demand',
        'periods': [
            ('Peak', time(7, 0), time(22, 0), 80.837),
            ('Off-peak', time(22, 0), time(7, 0), 26.919),
        ]
    },
    'TAS22': {
        'name': 'Low voltage small business general',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 11.892),
        ]
    },
    'TAS31': {
        'name': 'Low voltage residential general light and power',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.001),
        ]
    }
}


demand_charges_2025_26 = {
    'TAS87': {
        'peak': 30.133,
        'off_peak': 10.034
    },
    'TAS97': {
        'peak': 25.613
    },
    'TAS88': {
        'peak': 68.628,
        'off_peak': 22.853
    },
    'TAS98': {
        'peak': 68.628,
        'off_peak': 22.853
    },
    'TAS89': {
        'peak': 52.542,
        'off_peak': 17.496
    },
    'TAS82': {
        'all': 40.211
    }
}

# AER 2026–27 demand (cents/kVA/day).
demand_charges_2026_27 = {
    'TAS87': {
        'peak': 34.772,
        'off_peak': 11.579
    },
    'TAS97': {
        'peak': 29.556
    },
    'TAS88': {
        'peak': 80.837,
        'off_peak': 26.919
    },
    'TAS98': {
        'peak': 80.837,
        'off_peak': 26.919
    },
    'TAS89': {
        'peak': 60.490,
        'off_peak': 20.143
    },
    'TAS82': {
        'all': 46.616
    }
}


daily_fees_2025_26 = {
    'TAS93': 70.032,
    'TAS87': 71.258,
    'TAS97': 70.032,
    'TAS94': 83.780,
    'TAS88': 92.661,
    'TAS98': 92.661,
    'TAS89': 619.613,
    'TAS82': 439.841,
}

# AER 2026–27 standing charges (cents/day).
daily_fees_2026_27 = {
    'TAS93': 80.544,
    'TAS87': 81.954,
    'TAS97': 80.544,
    'TAS94': 96.355,
    'TAS88': 106.569,
    'TAS98': 106.569,
    'TAS89': 732.692,
    'TAS82': 520.112,
    'TAS22': 73.254,
    'TAS31': 73.674,
}


def get_tariffs(interval_time=None):
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_demand_charges(interval_time=None):
    return demand_charges_2026_27 if _use_2026_prices(interval_time) else demand_charges_2025_26


def get_daily_fees(interval_time=None):
    return daily_fees_2026_27 if _use_2026_prices(interval_time) else daily_fees_2025_26


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
    Convert RRP from $/MWh to c/kWh for TasNetworks.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10

    tariff = get_tariffs(interval_datetime).get(tariff_code)
    if not tariff:
        # Handle unknown tariff codes
        slope = 1.037869032618134
        intercept = 5.586606750833143
        return rrp_c_kwh * slope + intercept

    # Check if it's a weekend for TAS94
    is_weekend = interval_datetime.weekday() >= 5

    # Find the applicable period and rate
    for period, start, end, rate in tariff['periods']:
        if tariff_code == 'TAS94' and period == 'Off-peak' and is_weekend:
            return rrp_c_kwh + rate
        elif start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            return rrp_c_kwh + rate

    # If no period is found, use the default rate (first rate in the list)
    return rrp_c_kwh + tariff['periods'][0][3]


def calculate_demand_fee(tariff_code: str, demand_kw: float, peak_demand_kw: float = None, days: int = 30, interval_time=None):
    """
    Calculate the demand fee for a given tariff code, demand amount, and time period.
    """
    demand_charges = get_demand_charges(interval_time)
    if tariff_code not in demand_charges:
        return 0.0

    charges = demand_charges[tariff_code]
    daily_rate = days / 30

    if 'peak' in charges and 'off_peak' in charges:
        if peak_demand_kw is None:
            raise ValueError("Peak demand is required for this tariff.")
        peak_charge = charges['peak'] * peak_demand_kw * daily_rate
        off_peak_charge = charges['off_peak'] * (demand_kw - peak_demand_kw) * daily_rate
        return peak_charge + off_peak_charge
    elif 'peak' in charges:
        return charges['peak'] * demand_kw * daily_rate
    elif 'all' in charges:
        return charges['all'] * demand_kw * daily_rate
    else:
        return 0.0

def get_daily_fee(tariff_code: str, interval_time=None):
    """
    Get the daily fee in dollars for a given tariff code.
    Fee tables are transcribed in c/day; the package contract is dollars/day.
    """
    return get_daily_fees(interval_time).get(tariff_code, 0.0) / 100

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
