# aemo_to_tariff/energex.py
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

def time_zone():
    return 'Australia/Brisbane'

# AER-approved price years take effect on 1 July. Energex 2026–27 prices apply
# from 1 July 2026; before that, the 2025–26 schedule applies.
PRICE_TRANSITION_DATE = datetime(2026, 7, 1, 0, 0, tzinfo=ZoneInfo('Australia/Brisbane'))


def _use_2026_prices(interval_time=None) -> bool:
    if interval_time is None:
        interval_time = datetime.now(tz=ZoneInfo(time_zone()))
    if interval_time.tzinfo is None:
        interval_time = interval_time.replace(tzinfo=ZoneInfo(time_zone()))
    return interval_time >= PRICE_TRANSITION_DATE


def _is_summer(interval_time: datetime) -> bool:
    """Return True if the interval falls in the summer season (Nov–Mar)."""
    local_time = interval_time.astimezone(ZoneInfo(time_zone()))
    return local_time.month in (11, 12, 1, 2, 3)


def battery_tariffs(customer_type: str):
    """
    Get the battery tariff for a given customer type.

    Parameters:
    - customer_type (str): The customer type ('Residential' or 'Business').

    Returns:
    - str: The battery tariff code.
    """
    if customer_type == 'Residential':
        return {'import': ['6900', '96200'], 'export': ['6900X', '96200X']}
    elif customer_type == 'Business':
        return {'import': ['6800'], 'export': ['6800X']}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")


daily_fees_2025_26 = {
    '8400': 0.556,
    '3900': 0.556,
    '3700': 0.556,
    '6900': 0.556,
    '8500': 0.739,
    '3600': 0.739,
    '3800': 0.739,
    '6000': {
        'band1': 0.739,
        'band2': 1.033,
        'band3': 1.322,
        'band4': 1.608,
        'band5': 1.888
    },
    '6800': {
        'band1': 0.739,
        'band2': 1.041,
        'band3': 1.343,
        'band4': 1.647,
        'band5': 1.950
    },
    '6600': 5.273,
    '6700': 5.273,
    '7200': 7.665,
    '8100': 37.740,
    '8300': 5.273,
}

daily_fees_2026_27 = {
    '8400': 0.871,  # Residential Flat
    '3900': 0.451,  # Residential TOU Demand & Energy
    '3700': 0.556,  # Residential Demand (legacy, not in AER 2026–27)
    '6900': 0.651,  # Residential Time of Use Energy
    '8500': 1.224,  # Small Business Flat
    '3600': 0.739,  # Small Business Demand (legacy)
    '3800': 0.863,  # Small Business TOU Demand & Energy
    '6000': {        # Small Business Wide IFT (legacy)
        'band1': 0.739,
        'band2': 1.033,
        'band3': 1.322,
        'band4': 1.608,
        'band5': 1.888
    },
    '6800': {        # Small Business ToU Energy
        'band1': 1.221,
        'band2': 1.720,
        'band3': 2.219,
        'band4': 2.721,
        'band5': 3.222
    },
    '6600': 5.273,  # Large Residential Energy (legacy)
    '6700': 8.759,  # Large Business Energy
    '7200': 9.134,  # LV Demand Time-of-Use
    '8100': 37.740,  # Demand Large (legacy)
    '8300': 10.317,  # Demand Small
    '96200': 0.651,  # Residential Two-Way Tariff Trial
}


tariffs_2025_26 = {
    '8400': {
        'name': 'Residential Flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.648)
        ],
        'rate': 9.648
    },
    '3900': {
        'name': 'Residential Transitional Demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 4.085)
        ],
        'rate': 4.085
    },
    '3700': {
        'name': 'Residential Demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 3.320)
        ],
        'rate': 3.320
    },
    '6900': {
        'name': 'Residential Time of Use Energy',
        'periods': [
            ('Evening', time(16, 0), time(21, 0), 19.367),
            ('Overnight', time(21, 0), time(11, 0), 4.868),
            ('Day', time(11, 0), time(16, 0), 0.476)
        ],
        'rate': {'Evening': 19.367, 'Overnight': 4.868, 'Day': 0.476}
    },
    '3600': {
        'name': 'Small Business Demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 5.616)
        ],
        'rate': 5.616
    },
    '3800': {
        'name': 'Small Business Transitional Demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 6.558)
        ],
        'rate': 6.558
    },
    '6000': {
        'name': 'Small Business Wide IFT',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.359)
        ],
        'rate': 10.359
    },
    '8500': {
        'name': 'Small Business Flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.359)
        ],
        'rate': 10.195
    },
    '8900': {
        'name': 'Small 8900 TOU',
        'periods': [
            ('Evening', time(16, 0), time(21, 0), 22.98),
            ('Overnight', time(21, 0), time(11, 0), 11.02),
            ('Day', time(11, 0), time(16, 0), 8.37)
        ],
        'rate': 10.195
    },
    '8800': {
        'name': 'Small 8800 TOU',
        'periods': [
            ('Evening', time(7, 0), time(21, 0), 14.58),
            ('Overnight', time(21, 0), time(23, 59), 9.59),
            ('Day', time(0, 0), time(7, 0), 9.59)
        ],
        'rate': 10.195
    },
    '6800': {
        'name': 'Small Business ToU Energy',
        'periods': [
            ('Day', time(11, 0), time(16, 0), 4.356),
            ('Evening', time(16, 0), time(21, 0), 19.219),
            ('Overnight', time(21, 0), time(11, 0), 14.097)
        ],
        'rate': {'Day': 4.356, 'Evening': 19.219, 'Overnight': 14.097}
    },
    '6600': {
        'name': 'Large Residential Energy',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.648)
        ],
        'rate': 9.648
    },
    '6700': {
        'name': 'Large Business Energy',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.195)
        ],
        'rate': 10.195
    },
    '7200': {
        'name': 'LV Demand Time-of-Use',
        'periods': [
            ('Off-Peak', time(11, 0), time(13, 0), 0.00476),
            ('Peak', time(17, 0), time(20, 0), 0.01736),
            ('Shoulder', time(20, 0), time(23, 59), 0.02611),
            ('Shoulder', time(0, 0), time(10, 59), 0.02611),
            ('Shoulder', time(13, 1), time(16, 59), 0.02611),
            ('Shoulder', time(14, 0), time(16, 59), 0.02611)
        ],
        'rate': 2.484
    },
    '8100': {
        'name': 'Demand Large',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 1.301)
        ],
        'rate': 1.301
    },
    '8300': {
        'name': 'SAC Demand Small',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 0.01736)
        ],
        'rate': 1.799
    },
    '94300': {
        'name': 'Large TOU Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(13, 59), 0.00476),
            ('Peak', time(16, 0), time(20, 59), 0.24736),
            ('Shoulder', time(21, 0), time(23, 59), 0.20136),
            ('Shoulder', time(0, 0), time(10, 59), 0.20136)
        ],
    },
}

tariffs_2026_27 = {
    '8400': {
        'name': 'Residential Flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.391)
        ],
        'rate': 9.391
    },
    '3900': {
        'name': 'Residential TOU Demand & Energy',
        'periods': [
            ('Evening', time(16, 0), time(21, 0), 2.533),
            ('Overnight', time(21, 0), time(11, 0), 6.069),
            ('Day', time(11, 0), time(16, 0), 0.434)
        ],
        'rate': {'Evening': 2.533, 'Overnight': 6.069, 'Day': 0.434}
    },
    '3700': {
        'name': 'Residential Demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 3.320)
        ],
        'rate': 3.320
    },
    '6900': {
        'name': 'Residential Time of Use Energy',
        'periods': [
            ('Evening', time(16, 0), time(21, 0), 19.533),
            ('Overnight', time(21, 0), time(11, 0), 6.069),
            ('Day', time(11, 0), time(16, 0), 0.434)
        ],
        'rate': {'Evening': 19.533, 'Overnight': 6.069, 'Day': 0.434}
    },
    '3600': {
        'name': 'Small Business Demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 5.616)
        ],
        'rate': 5.616
    },
    '3800': {
        'name': 'Small Business TOU Demand & Energy',
        'periods': [
            ('Evening', time(16, 0), time(21, 0), 2.318),
            ('Overnight', time(21, 0), time(11, 0), 8.220),
            ('Day', time(11, 0), time(16, 0), 1.627)
        ],
        'rate': {'Evening': 2.318, 'Overnight': 8.220, 'Day': 1.627}
    },
    '6000': {
        'name': 'Small Business Wide IFT',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.359)
        ],
        'rate': 10.359
    },
    '8500': {
        'name': 'Small Business Flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.760)
        ],
        'rate': 10.760
    },
    '8900': {
        'name': 'Small 8900 TOU',
        'periods': [
            ('Evening', time(16, 0), time(21, 0), 22.98),
            ('Overnight', time(21, 0), time(11, 0), 11.02),
            ('Day', time(11, 0), time(16, 0), 8.37)
        ],
        'rate': 10.195
    },
    '8800': {
        'name': 'Small 8800 TOU',
        'periods': [
            ('Evening', time(7, 0), time(21, 0), 14.58),
            ('Overnight', time(21, 0), time(23, 59), 9.59),
            ('Day', time(0, 0), time(7, 0), 9.59)
        ],
        'rate': 10.195
    },
    '6800': {
        'name': 'Small Business ToU Energy',
        'periods': [
            ('Day', time(11, 0), time(16, 0), 1.627),
            ('Evening', time(16, 0), time(21, 0), 26.318),
            ('Overnight', time(21, 0), time(11, 0), 7.695)
        ],
        'rate': {'Day': 1.627, 'Evening': 26.318, 'Overnight': 7.695}
    },
    '6600': {
        'name': 'Large Residential Energy',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.648)
        ],
        'rate': 9.648
    },
    '6700': {
        'name': 'Large Business Energy',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 11.191)
        ],
        'rate': 11.191
    },
    '7200': {
        'name': 'LV Demand Time-of-Use',
        'periods': [
            ('Off-Peak', time(11, 0), time(13, 0), 1.627),
            ('Peak', time(17, 0), time(20, 0), 1.876),
            ('Shoulder', time(20, 0), time(23, 59), 2.947),
            ('Shoulder', time(0, 0), time(10, 59), 2.947),
            ('Shoulder', time(13, 1), time(16, 59), 2.947),
            ('Shoulder', time(14, 0), time(16, 59), 2.947)
        ],
        'rate': 2.947
    },
    '8100': {
        'name': 'Demand Large',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 1.301)
        ],
        'rate': 1.301
    },
    '8300': {
        'name': 'SAC Demand Small',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 3.365)
        ],
        'rate': 3.365
    },
    '94300': {
        'name': 'Large TOU Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(13, 59), 1.627),
            ('Peak', time(16, 0), time(20, 59), 25.876),
            ('Shoulder', time(21, 0), time(23, 59), 19.540),
            ('Shoulder', time(0, 0), time(10, 59), 19.540)
        ],
    },
    '96200': {
        'name': 'Residential Two-Way Tariff Trial',
        'seasonal': True,
        'rate': {
            'Peak': 19.533,
            'Shoulder': 6.069,
            'Off-Peak': 0.434,
            'ExportCharge': 2.210,
            'ExportReward': -12.195,
        }
    },
}


demand_charges_2025_26 = {
    '3700': { 'Peak': 8.998},
    '3900': { 'Peak': 5.127},
    '3600': { 'Peak': 10.289},
    '3800': { 'Peak': 4.975},
    '6900': None,
    '8900': None,
    '8800': None,
    '7200': {
        'Off-Peak': 0.000,
        'Peak': 14.919,
        'Shoulder': 3.333
    },
    '8100': 15.773,
    '8300': 15.704,
}

demand_charges_2026_27 = {
    '3700': { 'Peak': 8.998},  # Residential Demand (legacy)
    '3900': { 'Peak': 7.000},  # Residential TOU Demand & Energy
    '3600': { 'Peak': 10.289},  # Small Business Demand (legacy)
    '3800': { 'Peak': 7.000},  # Small Business TOU Demand & Energy
    '6900': None,  # Residential Time of Use Energy
    '8900': None,  # Small 8900 TOU
    '8800': None,  # Small 8800 TOU
    '7200': {
        'Off-Peak': 0.000,    # 11:00 to 13:00
        'Peak': 15.459,       # 17:00 to 20:00
        'Shoulder': 4.080     # Other times
    },
    '8100': 15.773,  # Demand Large (legacy)
    '8300': 13.913,  # Demand Small
}


def get_tariffs(interval_time=None):
    """Return the tariff schedule that applies at ``interval_time``."""
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_daily_fees(interval_time=None):
    """Return the daily-fee schedule that applies at ``interval_time``."""
    return daily_fees_2026_27 if _use_2026_prices(interval_time) else daily_fees_2025_26


def get_demand_charges(interval_time=None):
    """Return the demand-charge schedule that applies at ``interval_time``."""
    return demand_charges_2026_27 if _use_2026_prices(interval_time) else demand_charges_2025_26


def translate_tariff(tariff_code: str):
    """
    Translate a tariff code to its canonical form for lookup.

    Parameters:
    - tariff_code (str): The input tariff code.

    Returns:
    - str: The canonical tariff code for lookup.
    """
    code = str(tariff_code)
    if code == '96200':  # Two-Way Tariff Trial — do not truncate
        return code
    if len(code) == 4:
        prefix = code[:2]
        return prefix + '00'
    return code

def days_in_month(interval_time: datetime) -> int:
    year = interval_time.year
    month = interval_time.month
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    days_in_month = (datetime(next_year, next_month, 1) - datetime(year, month, 1)).days
    return days_in_month


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
    tariff_code = translate_tariff(str(tariff_code))
    time_of_day = interval_time.astimezone(ZoneInfo(time_zone())).time()
    charges = get_demand_charges(interval_time)

    charge = charges['3700']
    if tariff_code in charges:
        charge = charges[tariff_code]
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

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30, tou='peak', interval_time=None):
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
    charges = get_demand_charges(interval_time)

    if tariff_code not in charges:
        return 0.0  # Return 0 if the tariff doesn't have a demand charge

    charge = charges[tariff_code]
    if isinstance(charge, dict):
        charge_per_kw_per_month = charge.get(tou, 0.0)
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
    tariff_code = translate_tariff(str(tariff_code))
    fee = get_daily_fees(interval_time).get(tariff_code)

    if isinstance(fee, dict):
        if annual_usage is None:
            raise ValueError("Annual usage is required for this tariff.")

        if annual_usage <= 20000:
            fee = fee['band1']
        elif annual_usage <= 40000:
            fee = fee['band2']
        elif annual_usage <= 60000:
            fee = fee['band3']
        elif annual_usage <= 80000:
            fee = fee['band4']
        else:
            fee = fee['band5']

    # Fee tables are transcribed in $/day; the package contract is cents/day.
    return fee * 100 if fee is not None else None


def get_periods(tariff_code: str, interval_time=None):
    tariff_code = translate_tariff(str(tariff_code))
    tariff = get_tariffs(interval_time).get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for Energex feed-in (export).

    Parameters:
    - interval_datetime (datetime): The interval datetime.
    - tariff_code (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    if str(tariff_code) in ('96200', '96200X'):
        # Two-Way Tariff Trial export — seasonal reward/charge applies.
        adjusted = interval_datetime - timedelta(minutes=5)
        return convert_two_way_tariff(adjusted, rrp, is_export=True)

    rrp_c_kwh = rrp / 10

    return rrp_c_kwh

def convert_two_way_tariff(interval_datetime: datetime, rrp: float, is_export: bool = False) -> float:
    """
    Convert RRP to c/kWh for the Energex Residential Two-Way Tariff Trial (NTC 96200).

    Import periods:
      Summer (Nov-Mar):
        Peak:     17:00-20:00  → 19.533 c/kWh
        Off-Peak: 09:00-15:00  → 0.434 c/kWh
        Shoulder: all other    → 6.069 c/kWh
      Non-Summer (Apr-Oct):
        Off-Peak: 09:00-15:00  → 0.434 c/kWh
        Shoulder: all other    → 6.069 c/kWh  (no peak period)

    Export periods:
      Summer:     17:00-20:00  → -12.195 c/kWh (reward/credit)
      Non-Summer: 11:00-13:00  → +2.210 c/kWh (charge)
                  10:00-11:00  → 0 (BEL exempt)
      All other:               → 0 c/kWh

    Parameters:
    - interval_datetime: The dispatch interval datetime (tz-aware), already adjusted.
    - rrp: AEMO Regional Reference Price in $/MWh.
    - is_export: True for export (feed-in), False for import.

    Returns:
    - float: Price in c/kWh. For import: spot + network. For export: spot + network adjustment.
    """
    rrp_c_kwh = rrp / 10

    if not _use_2026_prices(interval_datetime):
        # NTC 96200 does not exist before 1 July 2026 — return spot-only
        return rrp_c_kwh

    local = interval_datetime.astimezone(ZoneInfo(time_zone()))
    t = local.time()
    summer = _is_summer(local)

    if is_export:
        if summer and time(17, 0) <= t < time(20, 0):
            network = -12.195  # export reward (credit)
        elif not summer and time(11, 0) <= t < time(13, 0):
            network = 2.210   # export charge
        else:
            network = 0.0     # no charge/reward
        return rrp_c_kwh + network

    # Import
    if summer and time(17, 0) <= t < time(20, 0):
        network = 19.533  # Peak
    elif time(9, 0) <= t < time(15, 0):
        network = 0.434   # Off-Peak (all year)
    else:
        network = 6.069   # Shoulder (summer: 20-09 + 15-17; non-summer: 15-09)

    return rrp_c_kwh + network


def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for Energex.

    Parameters:
    - interval_time (str): The interval time.
    - tariff (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    tariff_code = translate_tariff(str(tariff_code))

    # Two-Way Tariff Trial — delegate to seasonal handler. interval_datetime is
    # already adjusted by 5 minutes above, so pass it directly.
    if tariff_code == '96200':
        return convert_two_way_tariff(interval_datetime, rrp, is_export=False)

    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10

    tariff_code = str(tariff_code)[:4]
    tariff = get_tariffs(interval_datetime).get(tariff_code)

    if not tariff:
        # Handle unknown tariff codes
        slope = 1.037869032618134
        intercept = 5.586606750833143
        return rrp_c_kwh * slope + intercept

    # Find the applicable period and rate
    for period, start, end, rate in tariff['periods']:
        if start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            total_price = rrp_c_kwh + rate
            return total_price

    # If no period is found, use the default rate
    if isinstance(tariff['rate'], dict):
        # For Time-of-Use tariffs, use the first rate as default
        rate = list(tariff['rate'].values())[0]
    else:
        rate = tariff['rate']

    return rrp_c_kwh + rate
