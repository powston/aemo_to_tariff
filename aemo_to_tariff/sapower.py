# aemo_to_tariff/sapower.py
import logging
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

_logger = logging.getLogger(__name__)

def time_zone():
    return 'Australia/Adelaide'

# AER-approved prices change at the start of each financial year (1 July).
# 2026–27 prices apply from 1 July 2026; before that, 2025–26 applies.
PRICE_TRANSITION_DATE = datetime(2026, 7, 1, 0, 0, tzinfo=ZoneInfo('Australia/Adelaide'))


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
        return {'import': ['RELE2W', 'RESELEX', 'RESELE'], 'export': ['RESELE', 'RESELEX', 'RELE2W']}
    elif customer_type == 'Business':
        return {'import': ['SBELE'], 'export': ['SBELE']}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")


feed_in_tariffs_2025_26 = {
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
        'name': 'Small Business Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 12.25),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'SBELEX': {
        'name': 'Small Business Electrify',
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

# AER 2026–27: Export Credit (col 22) for RESELE = -0.1322 $/kWh = -13.22 c/kWh
# applied during peak; values stored as positive c/kWh to be added to the
# spot price, matching the 2025–26 convention.
feed_in_tariffs_2026_27 = {
    'RESELE': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 13.22),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'RESELEX': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 13.22),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'RELE2W': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 13.22),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'SBELE': {
        'name': 'Small Business Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 13.22),
            ('Off-peak', time(21, 0), time(10, 0), 0),
            ('Off-peak', time(16, 0), time(17, 0), 0),
            ('Solar Sponge', time(10, 0), time(16, 0), -1)
        ]
    },
    'SBELEX': {
        'name': 'Small Business Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 13.22),
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


tariffs_2025_26 = {
    'RSR': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), None, 14.51)
        ]
    },
    'RTOU': {
        'name': 'Residential Time of Use',
        'periods': [
            ('Peak', time(16, 0), time(0, 0), None, 18.95),
            ('Peak', time(6, 0), time(10, 0), None, 18.95),
            ('Off-peak', time(0, 0), time(6, 0), None, 9.47),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 4.74)
        ]
    },
    'RTOUNE': {
        'name': 'Residential Time of Use',
        'periods': [
            ('Peak', time(16, 0), time(0, 0), None, 18.95),
            ('Peak', time(6, 0), time(10, 0), None, 18.95),
            ('Off-peak', time(0, 0), time(6, 0), None, 9.47),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 4.74)
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
        'name': 'Small Business Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 34.83),
            ('Shoulder', time(16, 0), time(17, 0), None, 17.96),
            ('Shoulder', time(21, 0), time(10, 0), None, 17.96),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 10.26)
        ]
    },
    'B2R': {
        # Two-rate business tariff. Previously the periods only covered 16:00–
        # 10:00 next day, leaving 10:00–16:00 falling through to the slope/
        # intercept default. Added an explicit 'Solar Sponge' window at the
        # off-peak rate (AER 2026–27 lists no separate solar-sponge usage rate
        # for B2R, so it matches off-peak).
        'name': 'Business Two Rate',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 20.65),
            ('Shoulder', time(16, 0), time(17, 0), None, 10.32),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 7.26),
            ('Off-peak', time(21, 0), time(10, 0), None, 7.26)
        ]
    },
    'SBTOU': {
        'name': 'Small Business Time of Use',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), [11, 12, 1, 2, 3], 27.50),
            ('Shoulder', time(7, 0), time(17, 0), [11, 12, 1, 2, 3], 19.14),
            ('Shoulder', time(7, 0), time(17, 0), [4, 5, 6, 7, 8, 9, 10], 19.14),
            ('Off-peak', None, None, None, 10.34)
        ]
    },
    'SBTOUNE': {
        'name': 'Small Business Time of Use',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), [11, 12, 1, 2, 3], 27.50),
            ('Shoulder', time(7, 0), time(17, 0), [11, 12, 1, 2, 3], 19.14),
            ('Shoulder', time(7, 0), time(17, 0), [4, 5, 6, 7, 8, 9, 10], 19.14),
            ('Off-peak', None, None, None, 10.34)
        ]
    }
}

# AER 2026–27: RSR anytime 16.34 c/kWh; RTOU peak 21.33, shoulder/off-peak
# 10.67, solar sponge 5.35; RESELE peak 36.01 + shoulder 10.68 + solar 3.21;
# SBTOU peak 28.72, shoulder 19.98, off-peak 10.79.
tariffs_2026_27 = {
    'RSR': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), None, 16.34)
        ]
    },
    'RTOU': {
        'name': 'Residential Time of Use',
        'periods': [
            ('Peak', time(16, 0), time(0, 0), None, 21.33),
            ('Peak', time(6, 0), time(10, 0), None, 21.33),
            ('Off-peak', time(0, 0), time(6, 0), None, 10.67),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 5.35)
        ]
    },
    'RTOUNE': {
        'name': 'Residential Time of Use',
        'periods': [
            ('Peak', time(16, 0), time(0, 0), None, 21.33),
            ('Peak', time(6, 0), time(10, 0), None, 21.33),
            ('Off-peak', time(0, 0), time(6, 0), None, 10.67),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 5.35)
        ]
    },
    'RPRO': {
        'name': 'Residential Prosumer',
        'periods': [
            ('Peak', time(17, 0), time(20, 0), None, 21.33),
            ('Off-peak', time(16, 0), time(17, 0), None, 10.67),
            ('Off-peak', time(20, 0), time(10, 0), None, 10.67),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 5.35)
        ]
    },
    'RELE': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 36.01),
            ('Shoulder', time(21, 0), time(10, 0), None, 10.68),
            ('Shoulder', time(16, 0), time(17, 0), None, 10.68),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 3.21)
        ]
    },
    'RESELE': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 36.01),
            ('Shoulder', time(16, 0), time(17, 0), None, 10.68),
            ('Shoulder', time(21, 0), time(10, 0), None, 10.68),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 3.21)
        ]
    },
    'RELE2W': {
        'name': 'Residential Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 36.01),
            ('Shoulder', time(16, 0), time(17, 0), None, 10.68),
            ('Shoulder', time(21, 0), time(10, 0), None, 10.68),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 3.21)
        ]
    },
    'SBELE': {
        'name': 'Small Business Electrify',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 36.36),
            ('Shoulder', time(16, 0), time(17, 0), None, 18.75),
            ('Shoulder', time(21, 0), time(10, 0), None, 18.75),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 10.72)
        ]
    },
    'B2R': {
        # See 2025–26 dict for the rationale on the Solar Sponge window.
        'name': 'Business Two Rate',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), None, 21.57),
            ('Shoulder', time(16, 0), time(17, 0), None, 10.78),
            ('Solar Sponge', time(10, 0), time(16, 0), None, 7.26),
            ('Off-peak', time(21, 0), time(10, 0), None, 7.26)
        ]
    },
    'SBTOU': {
        'name': 'Small Business Time of Use',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), [11, 12, 1, 2, 3], 28.72),
            ('Shoulder', time(7, 0), time(17, 0), [11, 12, 1, 2, 3], 19.98),
            ('Shoulder', time(7, 0), time(17, 0), [4, 5, 6, 7, 8, 9, 10], 19.98),
            ('Off-peak', None, None, None, 10.79)
        ]
    },
    'SBTOUNE': {
        'name': 'Small Business Time of Use',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), [11, 12, 1, 2, 3], 28.72),
            ('Shoulder', time(7, 0), time(17, 0), [11, 12, 1, 2, 3], 19.98),
            ('Shoulder', time(7, 0), time(17, 0), [4, 5, 6, 7, 8, 9, 10], 19.98),
            ('Off-peak', None, None, None, 10.79)
        ]
    }
}


daily_fees_2025_26 = {
    'RSR': 64.40,
    'RTOU': 64.40,
    'RPRO': 64.40,
    'RELE': 64.40,
    'SBTOU': 72.59,
    'SBTOUE': 72.59
}

# AER 2026–27: RSR/RTOU/RESELE fixed $0.6553/day (65.53 c/day);
# BSR/B2R/SBTOU/SBELE fixed $0.6645/day (66.45 c/day).
daily_fees_2026_27 = {
    'RSR': 65.53,
    'RTOU': 65.53,
    'RTOUNE': 65.53,
    'RESELE': 65.53,
    'RPRO': 65.53,
    'RELE': 65.53,
    'B2R': 66.45,
    'SBTOU': 66.45,
    'SBTOUE': 66.45,
    'SBTOUNE': 66.45,
    'SBELE': 66.45,
}


demand_charges_2025_26 = {
    'RESELE': None,
    'RELE2W': None,
    'SBELE': None,
    'SBTOU': None,
    'RTOU': None,
    'SBTOUNE': None,
    'RPRO': 83.39,
    'SBTOUD': 8.42,
}

# AER 2026–27: MBTOUD annual kVA demand 0.0861 $/kVA = 8.61 c/kVA/day.
demand_charges_2026_27 = {
    'RESELE': None,
    'RELE2W': None,
    'SBELE': None,
    'SBTOU': None,
    'RTOU': None,
    'SBTOUNE': None,
    'RPRO': 83.39,
    'SBTOUD': 8.61,
    'MBTOUD': 8.61,
}


def get_tariffs(interval_time=None):
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_feed_in_tariffs(interval_time=None):
    return feed_in_tariffs_2026_27 if _use_2026_prices(interval_time) else feed_in_tariffs_2025_26


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
    Convert RRP from $/MWh to c/kWh for SA Power Networks.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10
    feed_in_tariffs = get_feed_in_tariffs(interval_datetime)

    feed_in_tariff = feed_in_tariffs.get(tariff_code)
    if not feed_in_tariff:
        return rrp_c_kwh

    for period_name, start, end, rate in feed_in_tariff['periods']:

        if start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            total_price = rrp_c_kwh + rate
            return total_price

    return rrp_c_kwh

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for SA Power Networks.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    _logger.debug("Interval Time: %s -> %s Tariff Code: %s RRP: %s", interval_datetime, interval_time, tariff_code, rrp)
    rrp_c_kwh = rrp / 10

    tariff = get_tariffs(interval_datetime).get(tariff_code)

    # Handle unknown tariff codes
    slope = 1.037869032618134
    intercept = 5.586606750833143
    default_tariff = rrp_c_kwh * slope + intercept

    current_month = interval_datetime.month

    if tariff is None:
        return default_tariff

    # Find the applicable period and rate
    for period, start, end, months, rate in tariff['periods']:
        if start is None and end is None:
            if months and current_month not in months:
                continue
            default_tariff = rrp_c_kwh + rate
        elif start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            _logger.debug("Checking period: %s Start: %s End: %s Months: %s Rate: %s", period, start, end, months, rate)
            _logger.debug("Current month: %s Interval time: %s", current_month, interval_time)
            if months and current_month not in months:
                continue
            total_price = rrp_c_kwh + rate
            _logger.debug("Found tariff match: %s in tariff code: %s %s Total Price: %s", period, tariff_code, rate, total_price)
            return total_price

    return default_tariff

def get_daily_fee(tariff_code: str, interval_time=None):
    """
    Get the daily fee for a given tariff code.
    """
    return get_daily_fees(interval_time).get(tariff_code, 0.0)

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30, interval_time=None):
    """
    Calculate the demand fee for a given tariff code, demand amount, and time period.
    """
    demand_charges = get_demand_charges(interval_time)
    daily_charge = demand_charges.get(tariff_code, None)
    if daily_charge is None:
        return 0.0
    return daily_charge * demand_kw * days

def estimate_demand_fee(interval_time: datetime, tariff_code: str, demand_kw: float):
    """
    Estimate the demand fee for a given tariff code, demand amount, and time period.
    """
    time_of_day = interval_time.astimezone(ZoneInfo(time_zone())).time()
    demand_charges = get_demand_charges(interval_time)

    charge = demand_charges.get('RPRO')
    if tariff_code in demand_charges:
        charge = demand_charges[tariff_code]
    if charge is None:
        return 0.0
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
