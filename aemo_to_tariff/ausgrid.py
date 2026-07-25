from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

from aemo_to_tariff.energex import translate_tariff


# GST on the network component. Settled retail data shows the distributor's
# c/kWh rate is billed GST-inclusive, so convert() grosses it up here (matching
# evoenergy, which has always done so). Confirmed out-of-sample for this network:
# fitting a site's plan on a pre-1-July day and predicting a post-1-July day
# drops the mean error to <0.15 c/kWh with GST and leaves it at 0.2-1.2 without.
# Not applied to convert_feed_in_tariff -- export credits do not carry GST --
# nor to the unknown-tariff slope/intercept fallbacks.
GST = 1.1


def time_zone():
    return 'Australia/Sydney'

# AER-approved prices change at the start of each financial year (1 July).
# 2026–27 prices apply from 1 July 2026; before that, 2025–26 applies.
PRICE_TRANSITION_DATE = datetime(2026, 7, 1, 0, 0, tzinfo=ZoneInfo('Australia/Sydney'))


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
        return {'import': ['EA025'], 'export': ['EA029']}
    elif customer_type == 'Business':
        return {'import': ['EA225'], 'export': ['EA029']}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")


tariffs_2025_26 = {
    'EA010': {
        'name': 'Residential flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.8007)
        ]
    },
    'EA025': {
        'name': 'Residential ToU',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 29.2450),
            # Off-peak covers all 24 hours so it remains the rate during
            # shoulder months (Apr/May/Sep/Oct) when Peak is skipped. The
            # Peak entry above wins when its window matches during a peak
            # month because periods are evaluated in order.
            ('Off-peak', time(0, 0), time(23, 59), 5.1535)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    'EA111': {
        'name': 'Residential demand (introductory)',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.7805)
        ]
    },
    'EA116': {
        'name': 'Residential demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 2.3370)
        ]
    },
    'EA225': {
        'name': 'Small Business ToU',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 34.8921),
            ('Off-peak', time(0, 0), time(23, 59), 5.7619)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    'EA305': {
        'name': 'Small Business LV',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 7.3723),
            ('Off-Peak', time(21, 0), time(14, 59), 1.6800)
        ]
    }
}

tariffs_2026_27 = {
    'EA010': {
        'name': 'Residential flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 12.7029)
        ]
    },
    'EA025': {
        'name': 'Residential ToU',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 32.5164),
            ('Off-peak', time(0, 0), time(23, 59), 5.3570)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    'EA111': {
        'name': 'Residential demand (introductory)',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 11.8010)
        ]
    },
    'EA116': {
        'name': 'Residential demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 2.8061)
        ]
    },
    'EA225': {
        'name': 'Small Business ToU',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 39.7570),
            ('Off-peak', time(0, 0), time(23, 59), 5.8997)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]
    },
    'EA305': {
        'name': 'Small Business LV',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 8.2347),
            ('Off-Peak', time(21, 0), time(14, 59), 1.8459)
        ]
    }
}


demand_tariffs_2025_26 = {
    'EA025': None,
    'EA225': None,
    'EA116': { 'peak': 8.998},
    'EA305': { 'peak': 8.998},
}

demand_tariffs_2026_27 = {
    'EA025': None,
    'EA225': None,
    'EA111': { 'peak': 1.4584},
    'EA116': { 'peak': 39.4850},
    'EA251': { 'peak': 1.3817},
    'EA256': { 'peak': 44.5311},
    'EA305': { 'peak': 8.998},
}


daily_fixed_charges_2025_26 = {
    'EA010': 47,
    'EA025': 57,
    'EA111': 51,
    'EA116': 60,
    'EA225': 184,
    'EA305': 2047.0434,
}

daily_fixed_charges_2026_27 = {
    'EA010': 50.8550,
    'EA025': 63.2330,
    'EA111': 57.2945,
    'EA116': 67.0054,
    'EA225': 218.6472,
    'EA305': 2546.5371,
}


def get_tariffs(interval_time=None):
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_demand_tariffs(interval_time=None):
    return demand_tariffs_2026_27 if _use_2026_prices(interval_time) else demand_tariffs_2025_26


def get_daily_fixed_charges(interval_time=None):
    return daily_fixed_charges_2026_27 if _use_2026_prices(interval_time) else daily_fixed_charges_2025_26


def get_periods(tariff_code: str, interval_time=None):
    tariff = get_tariffs(interval_time).get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")
    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone()))
    rrp_c_kwh = rrp / 10
    if tariff_code in ['EA029']:
        if interval_time.hour >= 16 and interval_time.hour < 21:
            reward = 3.85
            return rrp_c_kwh + reward
        elif interval_time.hour >= 10 and interval_time.hour < 15:
            penalty = -1.23
            return rrp_c_kwh + penalty
    return rrp_c_kwh

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10
    tariff = get_tariffs(interval_datetime).get(tariff_code)

    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    current_month = interval_datetime.month

    # Tariffs that don't declare 'peak_months' have non-seasonal peaks (e.g.
    # EA305 LV business). Only skip the Peak period when the tariff explicitly
    # restricts it to certain months.
    peak_months = tariff.get('peak_months')
    is_peak_month = peak_months is None or current_month in peak_months

    for period_name, start, end, rate in tariff['periods']:
        if period_name == 'Peak' and not is_peak_month:
            continue  # Skip peak period if not in peak months

        if start <= end:
            if start <= interval_time < end:
                return rrp_c_kwh + rate * GST
        else:
            # Over midnight
            if interval_time >= start or interval_time < end:
                return rrp_c_kwh + rate * GST

    # If no period matches, apply default approximation
    slope = 1.037869032618134
    intercept = 5.586606750833143
    return rrp_c_kwh * slope + intercept

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
    demand_tariffs = get_demand_tariffs(interval_time)

    charge = demand_tariffs['EA116']
    if tariff_code in demand_tariffs:
        charge = demand_tariffs[tariff_code]
    if charge is None:
        return 0.0  # Return 0 if the tariff doesn't have a demand charge
    if isinstance(charge, dict):
        # Determine the time period
        if 'peak' in charge and time(17, 0) <= time_of_day < time(20, 0):
            charge_per_kw_per_month = charge['peak']
        elif 'off-peak' in charge and time(11, 0) <= time_of_day < time(13, 0):
            charge_per_kw_per_month = charge['off-peak']
        else:
            charge_per_kw_per_month = charge.get('shoulder', 0.0)
    else:
        charge_per_kw_per_month = charge

    return charge_per_kw_per_month * demand_kw

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30, tou='Peak', interval_time=None):
    """
    Calculate the demand fee for a given tariff code, demand amount, and time period.

    Parameters:
    - tariff_code (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for 8100 and 8300 tariffs).
    - days (int): The number of days for the billing period (default is 30).
    - interval_time (datetime, optional): Selects the price schedule. Defaults to now.

    Returns:
    - float: The demand fee in dollars.
    """
    tariff_code = translate_tariff(str(tariff_code))
    demand_tariffs = get_demand_tariffs(interval_time)

    charge = demand_tariffs['EA116']
    if tariff_code in demand_tariffs:
        charge = demand_tariffs[tariff_code]
    if charge is None:
        return 0.0  # Return 0 if the tariff doesn't have a demand charge
    if isinstance(charge, dict):
        charge_per_kw_per_month = charge.get(tou.lower(), 0.0)
    else:
        charge_per_kw_per_month = charge

    # Convert the charge to a daily rate and then calculate for the given number of days
    daily_rate = charge_per_kw_per_month / days
    total_charge = demand_kw * daily_rate * days

    return total_charge

def get_daily_fee(tariff_code: str, annual_usage: float = None, interval_time=None):
    """
    Calculate the daily fee for a given tariff code.

    Parameters:
    - tariff_code (str): The tariff code.
    - annual_usage (float): Annual usage in kWh, required for Wide IFT and ToU Energy tariffs.
    - interval_time (datetime, optional): Selects the price schedule. Defaults to now.

    Returns:
    - float: The daily fee in cents per day.
    """
    fee = get_daily_fixed_charges(interval_time).get(tariff_code)
    if fee is None:
        raise ValueError(f"Unknown tariff code: {tariff_code}")
    return fee  # Table is transcribed in ¢/day, matching the package contract (cents/day)
