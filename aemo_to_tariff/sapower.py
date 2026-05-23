# aemo_to_tariff/sapower.py
import logging
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

_logger = logging.getLogger(__name__)

def time_zone():
    return 'Australia/Adelaide'


def battery_tariffs(customer_type: str):
    """
    Get the battery tariff for a given customer type.

    Parameters:
    - customer_type (str): The customer type ('Residential' or 'Business').

    Returns:
    - str: The battery tariff code.
    """
    if customer_type == 'Residential':
        return {'import': ['RELE2W', 'RESELEX', 'RESELE'], 'export': ['RESELE', 'RESELEX', 'RELE2W']}
    elif customer_type == 'Business':
        return {'import': ['SBELE'], 'export': ['SBELE']}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")

feed_in_tariffs = {
    'RESELE': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 12.25),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'RESELEX': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 12.25),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'RELE2W': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 12.25),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'SBELE': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 12.25),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'SBELEX': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 12.25),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'B2R': {
        'name': 'Business Two Rate',
        'periods': [
            ('Solar Sponge', time(10, 0), time(16, 0), -0.76)
        ]
    },
}

tariffs = {
    'RSR': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), None, 14.51)
        ]
    },
    'RTOU': {
        'name': 'Residential Time of Use',
        'periods': [
            ('Peak', time(16, 0), time(0, 0), None, 18.95), # 12 hours per day not captured in the Off Peak
            ('Peak', time(6, 0), time(10, 0), None, 18.95), # or Solar Sponge windows.
            ('Off-peak', time(0, 0), time(6, 0), None, 9.47), # Six hour window of 12:00am – 6:00am.
            ('Solar Sponge', time(10, 0), time(16, 0), None, 4.74) # Six hour window of 10:00am – 4:00pm.
        ]
    },
    'RTOUNE': {
        'name': 'Residential Time of Use',
        'periods': [
            ('Peak', time(16, 0), time(0, 0), None, 18.95), # 12 hours per day not captured in the Off Peak
            ('Peak', time(6, 0), time(10, 0), None, 18.95), # or Solar Sponge windows.
            ('Off-peak', time(0, 0), time(6, 0), None, 9.47), # Six hour window of 12:00am – 6:00am.
            ('Solar Sponge', time(10, 0), time(16, 0), None, 4.74) # Six hour window of 10:00am – 4:00pm.
        ]
    },
    'RPRO': {
        'name': 'Residential Prosumer',
        'periods': [
            ('Peak', time(17, 0), time(20, 0), None, 18.95),
            ('Off-peak', time(16, 0), time(17, 0), None, 9.47),
            ('Off-peak', time(20, 0), time(10, 0), None, 9.47),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 4.74)
        ]
    },
    'RELE': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 31.98),
            ('Shoulder', time(21, 0), time(10, 0), None, 9.49),
            ('Shoulder', time(16, 0), time(17, 0), None, 9.49),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 2.84)
        ]
    },
    'RESELE': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 31.98),
            ('Shoulder', time(16, 0), time(17, 0), None, 9.49),
            ('Shoulder', time(21, 0), time(10, 0), None, 9.49),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 2.84)
        ]
    },
    'RELE2W': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 31.98),
            ('Shoulder', time(16, 0), time(17, 0), None, 9.49),
            ('Shoulder', time(21, 0), time(10, 0), None, 9.49),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 2.84)
        ]
    },
    'SBELE': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 34.83),
            ('Shoulder', time(16, 0), time(17, 0), None, 17.96),
            ('Shoulder', time(21, 0), time(10, 0), None, 17.96),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 10.26)
        ]
    },
    'B2R': { # 0.2065 0.1032 $ 0.0726 
        'name': 'Business Two Rate',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 20.65),
            ('Shoulder', time(16, 0), time(17, 0), None, 10.32),
            ('Off-peak', time(21, 0), time(10, 0), None, 7.26)
        ]
    },
    'SBTOU': { # 0.2750 0.1034 $ 0.1914
        'name': 'Small Business Time of Use',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), [11, 12, 1, 2, 3], 27.50), # 5:00pm – 9:00pm All days November – March
            ('Shoulder', time(7, 0), time(17, 0), [11, 12, 1, 2, 3], 19.14), # 7:00am – 5:00pm WD November – March and
            ('Shoulder', time(7, 0), time(17, 0), [4, 5, 6, 7, 8, 9, 10], 19.14), # 7:00am – 9:00pm WD April – October.
            ('Off-peak', None, None, None, 10.34) # All other times
        ]
    },
    'SBTOUNE': {
        'name': 'Small Business Time of Use',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), [11, 12, 1, 2, 3], 27.50), # 5:00pm – 9:00pm All days November – March
            ('Shoulder', time(7, 0), time(17, 0), [11, 12, 1, 2, 3], 19.14), # 7:00am – 5:00pm WD November – March and
            ('Shoulder', time(7, 0), time(17, 0), [4, 5, 6, 7, 8, 9, 10], 19.14), # 7:00am – 9:00pm WD April – October.
            ('Off-peak', None, None, None, 10.34) # All other times
        ]
    }
}

# $0.0255 Meter Charge
# $0.6185 Supply Rate
# 64.40c
daily_fees = {
    'RSR': 64.40,
    'RTOU': 64.40, 
    'RPRO': 64.40,
    'RELE': 64.40,
    'SBTOU': 72.59,
    'SBTOUE': 72.59
}

demand_charges = {
    'RESELE': None,
    'RELE2W': None,
    'SBELE': None,
    'SBTOU': None,
    'RTOU': None,
    'SBTOUNE': None,
    'RPRO': 83.39,  # $/kW/day
    'SBTOUD': 8.42  # $/kW/day
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
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10

    feed_in_tariff = feed_in_tariffs.get(tariff_code)
    if not feed_in_tariff:
        return rrp_c_kwh

    current_month = interval_datetime.month

    for period_name, start, end, rate in feed_in_tariff['periods']:

        if start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            total_price = rrp_c_kwh + rate
            return total_price

    return rrp_c_kwh

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for SA Power Networks.

    Parameters:
    - interval_datetime (datetime): The interval datetime.
    - tariff_code (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    _logger.debug("Interval Time: %s -> %s Tariff Code: %s RRP: %s", interval_datetime, interval_time, tariff_code, rrp)
    rrp_c_kwh = rrp / 10

    tariff = tariffs.get(tariff_code)

    # Handle unknown tariff codes
    slope = 1.037869032618134
    intercept = 5.586606750833143
    default_tariff = rrp_c_kwh * slope + intercept

    current_month = interval_datetime.month

    # Find the applicable period and rate
    for period, start, end, months, rate in tariff['periods']:
        if start is None and end is None:
            if months and current_month not in months:
                continue  # Skip period if not in applicable months
            default_tariff = rrp_c_kwh + rate
        elif start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            _logger.debug("Checking period: %s Start: %s End: %s Months: %s Rate: %s", period, start, end, months, rate)
            _logger.debug("Current month: %s Interval time: %s", current_month, interval_time)
            if months and current_month not in months:
                continue  # Skip period if not in applicable months
            total_price = rrp_c_kwh + rate
            _logger.debug("Found tariff match: %s in tariff code: %s %s Total Price: %s", period, tariff_code, rate, total_price)
            return total_price

    # If no period is found, use the first rate as default
    return default_tariff

def get_daily_fee(tariff_code: str):
    """
    Get the daily fee for a given tariff code.

    Parameters:
    - tariff_code (str): The tariff code.

    Returns:
    - float: The daily fee in dollars.
    """
    return daily_fees.get(tariff_code, 0.0)

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30):
    """
    Calculate the demand fee for a given tariff code, demand amount, and time period.

    Parameters:
    - tariff_code (str): The tariff code.
    - demand_kw (float): The maximum demand in kW.
    - days (int): The number of days for the billing period (default is 30).

    Returns:
    - float: The demand fee in dollars.
    """
    daily_charge = demand_charges.get(tariff_code, None)
    if daily_charge is None:
        return 0.0  # Return 0 if the tariff doesn't have a demand charge
    return daily_charge * demand_kw * days

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
    
    charge = demand_charges['RPRO']
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
