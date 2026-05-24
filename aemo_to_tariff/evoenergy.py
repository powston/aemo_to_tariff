# aemo_to_tariff/evoenergy.py
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

def time_zone():
    return 'Australia/ACT'

# AER-approved prices change at the start of each financial year (1 July).
# 2026–27 prices apply from 1 July 2026; before that, 2025–26 applies.
PRICE_TRANSITION_DATE = datetime(2026, 7, 1, 0, 0, tzinfo=ZoneInfo('Australia/ACT'))


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
        return {'import': ['017'], 'export': []}
    elif customer_type == 'Business':
        return {'import': ['090'], 'export': []}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")


tariffs_2025_26 = {
    '015': {
        'name': 'Residential TOU Network (closed)',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.095),
            ('Peak', time(17, 0), time(20, 0), 16.095),
            ('Shoulder', time(9, 0), time(17, 0), 8.199),
            ('Shoulder', time(20, 0), time(22, 0), 8.199),
            ('Off-peak', time(22, 0), time(7, 0), 4.828)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
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
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
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
        'fixed_daily_charge': 34.984,
        'peak_months': [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
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
        'fixed_daily_charge': 48.257,
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
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
        'fixed_daily_charge': 32.757,
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    '090': {
        'name': 'Component Charge Applicability',
        'periods': [
            ('Peak', time(7, 0), time(17, 0), 17.518),
            ('Shoulder', time(17, 0), time(22, 0), 10.990),
            ('Off-peak', time(22, 0), time(7, 0), 5.110),
        ],
        'fixed_daily_charge': 76.676
    }
}

# AER 2026–27 consolidated stakeholder report (8 May 2026).
tariffs_2026_27 = {
    '015': {
        'name': 'Residential TOU Network (closed)',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 15.877),
            ('Peak', time(17, 0), time(20, 0), 15.877),
            ('Shoulder', time(9, 0), time(17, 0), 7.030),
            ('Shoulder', time(20, 0), time(22, 0), 7.030),
            ('Off-peak', time(22, 0), time(7, 0), 3.442)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    '016': {
        'name': 'Residential TOU Network (closed) XMC',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 15.877),
            ('Peak', time(17, 0), time(20, 0), 15.877),
            ('Shoulder', time(9, 0), time(17, 0), 7.030),
            ('Shoulder', time(20, 0), time(22, 0), 7.030),
            ('Off-peak', time(22, 0), time(7, 0), 3.442)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    '017': {
        'name': 'New Residential TOU Network',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.049),
            ('Peak', time(17, 0), time(21, 0), 16.049),
            ('Solar Soak', time(11, 0), time(15, 0), 1.779),
            ('Off-peak', time(21, 0), time(7, 0), 4.351),
            ('Off-peak', time(9, 0), time(11, 0), 4.351),
            ('Off-peak', time(15, 0), time(17, 0), 4.351)
        ],
        'fixed_daily_charge': 39.331,
        'peak_months': [11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    },
    '018': {
        'name': 'New Residential TOU Network XMC',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.049),
            ('Peak', time(17, 0), time(21, 0), 16.049),
            ('Solar Soak', time(11, 0), time(15, 0), 1.779),
            ('Off-peak', time(21, 0), time(7, 0), 4.351),
            ('Off-peak', time(9, 0), time(11, 0), 4.351),
            ('Off-peak', time(15, 0), time(17, 0), 4.351)
        ],
        'fixed_daily_charge': 39.331,
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    '026': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.049),
            ('Peak', time(17, 0), time(21, 0), 16.049),
            ('Solar Soak', time(11, 0), time(15, 0), 1.630),
            ('Off-peak', time(21, 0), time(7, 0), 3.534),
            ('Off-peak', time(9, 0), time(11, 0), 3.534),
            ('Off-peak', time(15, 0), time(17, 0), 3.534)
        ],
        'fixed_daily_charge': 39.391,
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    '090': {
        'name': 'Component Charge Applicability',
        'periods': [
            ('Peak', time(7, 0), time(17, 0), 19.920),
            ('Shoulder', time(17, 0), time(22, 0), 12.996),
            ('Off-peak', time(22, 0), time(7, 0), 5.875),
        ],
        'fixed_daily_charge': 73.453
    }
}


feed_in_tariffs_2025_26 = {
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

# AER 2026–27 doesn't publish a separate 026 export feed-in. Preserve 2025–26.
feed_in_tariffs_2026_27 = dict(feed_in_tariffs_2025_26)


demand_charges_2025_26 = {
    '017': None,
    '026': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 33.2942),
        ]
    },
    '090': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 33.2942),
        ]
    },
}

# AER 2026–27: 023/024 (New residential demand) Peak demand HS 21.808
# c/kW/highsn, LS 13.083 c/kW/lowsn, off-peak demand 2.076 c/kW/day.
demand_charges_2026_27 = {
    '017': None,
    '026': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 21.808),
        ]
    },
    '090': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 33.2942),
        ]
    },
}


def get_tariffs(interval_time=None):
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_feed_in_tariffs(interval_time=None):
    return feed_in_tariffs_2026_27 if _use_2026_prices(interval_time) else feed_in_tariffs_2025_26


def get_demand_charges(interval_time=None):
    return demand_charges_2026_27 if _use_2026_prices(interval_time) else demand_charges_2025_26


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
    charge = demand_charges.get('026')
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
    tariff = get_tariffs(interval_datetime)[tariff_code]
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
    feed_in_tariffs = get_feed_in_tariffs(interval_datetime)

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
