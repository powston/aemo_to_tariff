from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo


def time_zone():
    return 'Australia/Sydney'

def battery_tariffs(customer_type: str):
    """
    Get the battery tariff for a given customer type.

    Parameters:
    - customer_type (str): The customer type ('Residential' or 'Business').

    Returns:
    - str: The battery tariff code.
    """
    if customer_type == 'Residential':
        return {'import': ['N71'], 'export': ['N61']}
    elif customer_type == 'Business':
        return {'import': ['N91'], 'export': []}
    elif customer_type == 'Battery':
        return {'import': ['N95'], 'export': ['N95']}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")


# below reference page numbers are from this doc: https://www.endeavourenergy.com.au/__data/assets/pdf_file/0014/35024/NUOS-Price-List-202526-v1.1.pdf
tariffs = {
    'N70': {
        'name': 'Residential Flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.8173)
        ],
        'fixed_daily_charge': 63.1270,  # see page 34 
    },
    'N71': {
        'name': 'Residential Seasonal TOU', # 21.7964 13.8419 3.4252 10.4931
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 21.7964),
            ('Low-season Peak', time(16, 0), time(20, 0),  13.8419),
            ('Solar Soak', time(10, 0), time(14, 0), 3.4252),
            ('Off Peak', time(0, 0), time(10, 0), 10.4931),
            ('Off Peak', time(14, 0), time(16, 0), 10.4931),
            ('Off Peak', time(20, 0), time(23, 59), 10.4931)
        ],
        'fixed_daily_charge': 63.1270,  # see page 34 
        'peak_months': [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # November–March and April-October - see page 19
    },
    'N90': {
        'name': 'General Supply Block',
        'periods': [
            ('Block 1', time(0, 0), time(23, 59), 11.2803),
            ('Block 2', time(0, 0), time(23, 59), 13.5302)
        ],
        'fixed_daily_charge': 88.8470,  # see page 34 
    },
    'N91': {
        'name': 'GS Seasonal TOU',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 23.5007),
            ('Low-season Peak', time(16, 0), time(20, 0), 15.5462),
            ('Solar Soak', time(10, 0), time(14, 0), 4.1635),
            ('Off Peak', time(0, 0), time(10, 0), 12.1974),
            ('Off Peak', time(14, 0), time(16, 0), 12.1974),
            ('Off Peak', time(20, 0), time(23, 59), 12.1974)
        ],
        'fixed_daily_charge': 88.8470,  # see page 34 
        'peak_months': [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # November–March and April-October - see page 19
    },
    'N19': {
        'name': 'LV Seasonal STOU Demand',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 5.4400),
            ('Low-season Peak', time(16, 0), time(20, 0), 4.8861),
            ('Off Peak', time(0, 0), time(10, 0), 3.6458),
            ('Off Peak', time(14, 0), time(16, 0), 3.6458),
            ('Off Peak', time(20, 0), time(23, 59), 3.6458)
        ],
        'fixed_daily_charge': 2612.00,  # see page 34 
        'peak_months': [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # November–March and April-October - see page 19
    },
    'N95': {  # below from page 34 of https://www.endeavourenergy.com.au/__data/assets/pdf_file/0014/35024/NUOS-Price-List-202526-v1.1.pdf
        'name': 'Storage',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 13.1329),
            ('Low-season Peak', time(16, 0), time(20, 0), 5.1784),
            ('Solar Soak', time(10, 0), time(14, 0), 0.0),
            ('Off Peak', time(0, 0), time(10, 0), 1.8296),
            ('Off Peak', time(14, 0), time(16, 0), 1.8296),
            ('Off Peak', time(20, 0), time(23, 59), 1.8296)
        ],
        'fixed_daily_charge': 161.1570,  # see page 34  
        'peak_months': [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # November–March and April-October - see page 19
    }
}

demand_charges = {
    'N71': None,
    'N91': None,
    'N19': {
        'Peak': 49.42,  # $/kW/day see page 34, low-season is 44.80
        'Shoulder': 0.0,  # $/kW/day
        'Off-Peak': 0.0  # $/kW/day
    },
    'N73': {
        'Peak': 14.27,  # $/kW/day - see page 34, low-season demand is 9.23
        'Off-Peak': 0.0,  # $/kW/day
        'Shoulder': 0.0  # $/kW/day
    }
}

feed_in_tariffs = {
    'N61': {
        'name': 'Residential Electrify',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 12.4336),  # inc GST - correct?
            ('Low-season Peak', time(16, 0), time(20, 0), 3.6837),  # inc GST - correct?
            ('Off Peak', time(10, 0), time(14, 0), -1.9690)  # inc GST - correct?
        ],
        'weekdays': [0, 1, 2, 3, 4],
        'peak_months': [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # November–March and April-October - see page 19
    },
    'N95': {
        'name': 'Storage',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 12.4336),  # inc GST - correct?
            ('Low-season Peak', time(16, 0), time(20, 0), 3.6837),  # inc GST - correct?
            ('Off Peak', time(10, 0), time(14, 0), -1.9690)  # inc GST - correct?
        ],
        'weekdays': [0, 1, 2, 3, 4],
        'peak_months': [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # November–March and April-October - see page 19
    }
}

def get_daily_fee(tariff_code: str):
    """
    Get the daily fee for a given tariff.

    Parameters:
    - tariff_code (str): The tariff code.

    Returns:
    - float: The daily fee in dollars.
    """
    tariff = tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return 39.7300


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
    charge = demand_charges['N19']
    if tariff_code in demand_charges:
        charge = demand_charges[tariff_code]
    if charge is None:
        return 0.0  # Return 0 if the tariff doesn't have a demand charge
    if isinstance(charge, dict):
        # Determine the time period
        if 'Peak' in charge and time(16, 0) <= time_of_day < time(21, 0):
            charge_per_kw_per_month = charge['Peak']
        elif 'Off-Peak' in charge and time(11, 0) <= time_of_day < time(13, 0):
            charge_per_kw_per_month = charge['Off-Peak']
        else:
            charge_per_kw_per_month = charge.get('Shoulder', 0.0)
    else:
        charge_per_kw_per_month = charge

    return charge_per_kw_per_month * demand_kw

def calculate_demand_fee(tariff: str, demand_kw: float, days=30):
    """
    Calculate the demand fee for a given tariff, demand amount, and time period.

    Parameters:
    - tariff (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for some tariffs).
    - days (int): The number of days for the billing period (default is 30).

    Returns:
    - float: The demand fee in dollars.
    """
    tariff = tariffs[tariff]

    # Find the applicable rate
    for period, start, end, rate in tariff['periods']:
        if start <= demand_kw < end:
            return rate * days

    raise ValueError(f"Unknown demand amount: {demand_kw}")

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
    interval_datetime = interval_datetime - timedelta(minutes=5)
    
    if tariff_code in feed_in_tariffs:
        interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
        tariff = feed_in_tariffs[tariff_code]
        current_month = interval_datetime.month
        is_high_season = current_month in tariff['peak_months']
        if 'weekdays' in tariff:
            if interval_datetime.weekday() not in tariff['weekdays']:
                return rrp_c_kwh

        for period, start, end, rate in tariff['periods']:
            if start <= interval_time < end:
                if 'high' in period.lower() and is_high_season:
                    total_price = rrp_c_kwh +  rate
                    return total_price
                elif 'low' in period.lower() and not is_high_season:
                    total_price = rrp_c_kwh + rate
                    return total_price
                elif 'off' in period.lower():
                    total_price = rrp_c_kwh + rate
                    return total_price
    
    
    return rrp_c_kwh

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for endeavour.

    Parameters:
    - interval_datetime (datetime): The interval time.
    - tariff (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10
    tariff = tariffs[tariff_code]

    # Determine if it's high season (November to March) or low season (April to October)
    current_month = interval_datetime.month
    is_high_season = current_month in [11, 12, 1, 2, 3]

    # Find the applicable period and rate
    for period, start, end, rate in tariff['periods']:
        if start <= interval_time < end:
            if 'season' in tariff['name'].lower():
                if is_high_season and 'high' in period.lower():
                    total_price = rrp_c_kwh + rate
                    return total_price
                elif 'low' in period.lower() and not is_high_season:
                    total_price = rrp_c_kwh + rate
                    return total_price
                elif 'off' in period.lower():
                    total_price = rrp_c_kwh + rate
                    return total_price
                else:
                    continue
            else:
                total_price = rrp_c_kwh + rate
                return total_price

    # Otherwise, this terrible approximation
    slope = 1.037869032618134
    intecept = 5.586606750833143
    return rrp_c_kwh * slope + intecept
