# aemo_to_tariff/ausnet.py

from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

def time_zone():
    return 'Australia/Melbourne'

# AusNet Services tariffs
# Rates from AER-approved Schedule of Tariffs 2024-25
tariffs = {
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

# Optional daily fees if available
daily_fees = {
    'NAST11S': 3.00,
    'NEE11S': 0.3795,  # $138.51/year = 37.95 c/day
}

# Optional demand charges if needed
demand_charges = {
    'NAST11D': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 33.2942),  # ¢/kW/day
        ]
    },
}

def get_periods(tariff_code: str):
    tariff = tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")
    return tariff['periods']

def convert(interval_datetime: datetime, tariff_code: str, rrp: float) -> float:
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10.0  # Convert $/MWh to c/kWh

    tariff = tariffs.get(tariff_code)
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

def get_daily_fee(tariff_code: str, annual_usage: float = None) -> float:
    return daily_fees.get(tariff_code, 0.0)

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

    charge = demand_charges['NAST11D']
    if tariff_code in demand_charges:
        charge = demand_charges[tariff_code]
    if charge is None:
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

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30) -> float:
    if tariff_code not in demand_charges:
        return 0.0
    rate = demand_charges[tariff_code] / 30  # Convert monthly rate to daily
    return rate * demand_kw * days
