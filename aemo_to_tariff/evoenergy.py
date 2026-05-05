# aemo_to_tariff/evoenergy.py
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

def time_zone():
    return 'Australia/ACT'

def battery_tariffs(customer_type: str):
    """
    Get the battery tariff for a given customer type.

    Parameters:
    - customer_type (str): The customer type ('Residential' or 'Business').

    Returns:
    - str: The battery tariff code.
    """
    if customer_type == 'Residential':
        return {'import': ['017'], 'export': []}
    elif customer_type == 'Business':
        return {'import': ['090'], 'export': []}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")

tariffs = {
    '015': {
        'name': 'Residential TOU Network (closed)',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.095),
            ('Peak', time(17, 0), time(20, 0), 16.095),
            ('Shoulder', time(9, 0), time(17, 0), 8.199),
            ('Shoulder', time(20, 0), time(22, 0), 8.199),
            ('Off-peak', time(22, 0), time(7, 0), 4.828)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]  # November–March and June–August
    },
    '016': {
        'name': 'Residential TOU Network (closed) XMC',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.095),
            ('Peak', time(17, 0), time(20, 0), 16.095),
            ('Shoulder', time(9, 0), time(17, 0), 8.199),
            ('Shoulder', time(20, 0), time(22, 0), 8.199),
            ('Off-peak', time(22, 0), time(7, 0), 4.828)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]  # November–March and June–August
    },
    '017': {
        'name': 'New Residential TOU Network',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.184),
            ('Peak', time(17, 0), time(21, 0), 16.184),
            ('Solar Soak', time(11, 0), time(15, 0), 3.261),
            ('Off-peak', time(21, 0), time(7, 0), 5.665),
            ('Off-peak', time(9, 0), time(11, 0), 5.665),
            ('Off-peak', time(15, 0), time(17, 0), 5.665)
        ],
        'fixed_daily_charge': 34.984,  # Fixed daily charge in c/day
        'peak_months': [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # All year
    },
    '018': {
        'name': 'New Residential TOU Network XMC',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.184),
            ('Peak', time(17, 0), time(21, 0), 16.184),
            ('Solar Soak', time(11, 0), time(15, 0), 3.261),
            ('Off-peak', time(21, 0), time(7, 0), 5.665),
            ('Off-peak', time(9, 0), time(11, 0), 5.665),
            ('Off-peak', time(15, 0), time(17, 0), 5.665)
        ],
        'fixed_daily_charge': 48.257,  # Fixed daily charge in c/day
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]  # November–March and June–August
    },
    '026': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.184),
            ('Peak', time(17, 0), time(21, 0), 16.184),
            ('Solar Soak', time(11, 0), time(15, 0), 3.261),
            ('Off-peak', time(21, 0), time(7, 0), 5.665),
            ('Off-peak', time(9, 0), time(11, 0), 5.665),
            ('Off-peak', time(15, 0), time(17, 0), 5.665)
        ],
        'fixed_daily_charge': 32.757,  # same as 017
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    '090': {
        'name': 'Component Charge Applicability',
        'periods': [
            ('Peak', time(7, 0), time(17, 0), 17.518),  # 7am-5pm weekdays
            ('Shoulder', time(17, 0), time(22, 0), 10.990),  # 5pm-10pm weekdays
            ('Off-peak', time(22, 0), time(7, 0), 5.110),  # All other times
        ],
        'fixed_daily_charge': 76.676  # Fixed daily charge in c/day
    }
}

feed_in_tariffs = {
    '026': {
        'name': 'Battery Feed-in Trial',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 12.36),
            ('Off-peak', time(21, 0), time(7, 0), 0.0),
            ('Solar Soak', time(10, 0), time(15, 0), -1.0)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    }
}

demand_charges = {
    '017': None,
    '026': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 33.2942),  # ¢/kW/day
        ]
    },  # $/kW/day
    '090': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 33.2942),  # ¢/kW/day
        ]
    },   # $/kW/day
}

def get_periods(tariff_code: str):
    tariff = tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for SA Power Networks.

    Parameters:
    - interval_datetime (datetime): The interval datetime.
    - tariff_code (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    rrp_c_kwh = rrp / 10
    
    return rrp_c_kwh


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
    
    charge = demand_charges['026']
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

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for Evoenergy.

    Parameters:
    - interval_time (str): The interval time.
    - tariff (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    current_month = interval_datetime.month

    rrp_c_kwh = rrp / 10
    tariff = tariffs[tariff_code]
    gst = 1.1
    is_peak_month = current_month in tariff.get('peak_months', [])

    # Find the applicable period and rate
    for period_name, start, end, rate in tariff['periods']:
        if period_name == 'Peak' and not is_peak_month:
            continue  # Skip peak period if not in peak months

        if start <= interval_time < end:
            total_price = rrp_c_kwh + (rate * gst)
            return total_price

        # Handle overnight periods (e.g., 22:00 to 07:00)
        if start > end and (interval_time >= start or interval_time < end):
            total_price = rrp_c_kwh + (rate * gst)
            return total_price

    # Otherwise, this terrible approximation
    slope = 1.037869032618134
    intercept = 5.586606750833143
    return rrp_c_kwh * slope + intercept

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for Evoenergy feed-in tariffs.

    Parameters:
    - interval_datetime (datetime): The interval datetime.
    - tariff_code (str): The feed-in tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The total feed-in price in c/kWh.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10

    feed_in_tariff = feed_in_tariffs.get(tariff_code)
    if not feed_in_tariff:
        return rrp_c_kwh

    current_month = interval_datetime.month
    is_peak_month = current_month in feed_in_tariff.get('peak_months', [])

    for period_name, start, end, rate in feed_in_tariff['periods']:
        if period_name == 'Peak' and not is_peak_month:
            continue

        if start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            return rrp_c_kwh + rate

    return rrp_c_kwh
