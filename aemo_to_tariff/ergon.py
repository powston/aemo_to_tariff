# aemo_to_tariff/ergon.py
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo


# GST on the network component. Settled retail data shows the distributor's
# c/kWh rate is billed GST-inclusive, so convert() grosses it up here (matching
# evoenergy, which has always done so). Confirmed out-of-sample for this network:
# fitting a site's plan on a pre-1-July day and predicting a post-1-July day
# drops the mean error to <0.15 c/kWh with GST and leaves it at 0.2-1.2 without.
# Not applied to convert_feed_in_tariff -- export credits do not carry GST --
# nor to the unknown-tariff slope/intercept fallbacks.
GST = 1.1


def time_zone():
    return 'Australia/Brisbane'

# AER-approved price years take effect on 1 July. Ergon 2026–27 prices apply
# from 1 July 2026; before that, the 2025–26 schedule applies.
PRICE_TRANSITION_DATE = datetime(2026, 7, 1, 0, 0, tzinfo=ZoneInfo('Australia/Brisbane'))


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
        return {'import':['ERTOUET1'], 'export':['NVGC2', 'NVGX2']}
    elif customer_type == 'Business':
        return {'import':['EBTOUET1'], 'export':['NVGC2', 'NVGX2']}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")


daily_fees_2025_26 = {
    'ERTOUET1': 1.808,
    'WRTOUET1': 7.210,
    'MRTOUET4': 1.698,
    'EBTOUET1': 3.337,
    'WBTOUET1': 13.675,
    'MBTOUET4': 3.149,
}

daily_fees_2026_27 = {
    'ERTOUET1': 1.730,
    'WRTOUET1': 7.464,
    'MRTOUET4': 1.743,
    'ERTDEMT1': 1.603,
    'WRTDEMT1': 6.768,
    'MRTDEMT4': 1.561,
    'EBTOUET1': 3.329,
    'WBTOUET1': 14.490,
    'MBTOUET4': 3.434,
    'EBTDEMT1': 2.687,
    'WBTDEMT1': 11.555,
    'MBTDEMT4': 2.659,
}


tariffs_2025_26 = {
    'ERTOUET1': {
        'name': 'Residential Battery ToU',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.524),
            ('Peak', time(16, 0), time(21, 0), 18.564),
            ('Shoulder', time(21, 0), time(11, 0), 4.065)
        ],
        'rate': {'Off-Peak': 0.524, 'Peak': 18.564, 'Shoulder': 4.065}
    },
    'WRTOUET1': {
        'name': 'Residential Wide ToU',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.524),
            ('Peak', time(16, 0), time(21, 0), 18.564),
            ('Shoulder', time(21, 0), time(11, 0), 4.065)
        ],
        'rate': {'Off-Peak': 0.524, 'Peak': 18.564, 'Shoulder': 4.065}
    },
    'MRTOUET4': {
        'name': 'Residential Multi ToU',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.524),
            ('Peak', time(16, 0), time(21, 0), 0.17671),
            ('Shoulder', time(21, 0), time(11, 0), 0.03172)
        ],
        'rate': {'Off-Peak': 0.524, 'Peak': 0.17671, 'Shoulder': 0.03172}
    },
    '6900': {
        'name': 'Residential Time of Use Energy',
        'periods': [
            ('Evening', time(16, 0), time(21, 0), 19.367),
            ('Overnight', time(21, 0), time(11, 0), 4.868),
            ('Day', time(11, 0), time(16, 0), 0.00476)
        ],
        'rate': {'Evening': 19.367, 'Overnight': 4.868, 'Day': 0.00476}
    },
}

tariffs_2026_27 = {
    'ERTOUET1': {
        'name': 'East Residential TOU Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.277),
            ('Peak', time(16, 0), time(21, 0), 18.387),
            ('Shoulder', time(21, 0), time(11, 0), 4.923)
        ],
        'rate': {'Off-Peak': 0.277, 'Peak': 18.387, 'Shoulder': 4.923}
    },
    'WRTOUET1': {
        'name': 'West Residential TOU Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.277),
            ('Peak', time(16, 0), time(21, 0), 18.387),
            ('Shoulder', time(21, 0), time(11, 0), 4.923)
        ],
        'rate': {'Off-Peak': 0.277, 'Peak': 18.387, 'Shoulder': 4.923}
    },
    'MRTOUET4': {
        'name': 'Mt Isa Residential TOU Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.277),
            ('Peak', time(16, 0), time(21, 0), 17.447),
            ('Shoulder', time(21, 0), time(11, 0), 3.983)
        ],
        'rate': {'Off-Peak': 0.277, 'Peak': 17.447, 'Shoulder': 3.983}
    },
    'ERTDEMT1': {
        'name': 'East Residential TOU Demand & Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.277),
            ('Peak', time(16, 0), time(21, 0), 1.387),
            ('Shoulder', time(21, 0), time(11, 0), 4.923)
        ],
        'rate': {'Off-Peak': 0.277, 'Peak': 1.387, 'Shoulder': 4.923}
    },
    'WRTDEMT1': {
        'name': 'West Residential TOU Demand & Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.277),
            ('Peak', time(16, 0), time(21, 0), 1.387),
            ('Shoulder', time(21, 0), time(11, 0), 4.923)
        ],
        'rate': {'Off-Peak': 0.277, 'Peak': 1.387, 'Shoulder': 4.923}
    },
    'MRTDEMT4': {
        'name': 'Mt Isa Residential TOU Demand & Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.277),
            ('Peak', time(16, 0), time(21, 0), 0.447),
            ('Shoulder', time(21, 0), time(11, 0), 3.983)
        ],
        'rate': {'Off-Peak': 0.277, 'Peak': 0.447, 'Shoulder': 3.983}
    },
    'EBTOUET1': {
        'name': 'East Small Business TOU Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 1.470),
            ('Peak', time(16, 0), time(21, 0), 25.594),
            ('Shoulder', time(21, 0), time(11, 0), 6.971)
        ],
        'rate': {'Off-Peak': 1.470, 'Peak': 25.594, 'Shoulder': 6.971}
    },
    'WBTOUET1': {
        'name': 'West Small Business TOU Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 1.470),
            ('Peak', time(16, 0), time(21, 0), 25.594),
            ('Shoulder', time(21, 0), time(11, 0), 6.971)
        ],
        'rate': {'Off-Peak': 1.470, 'Peak': 25.594, 'Shoulder': 6.971}
    },
    'MBTOUET4': {
        'name': 'Mt Isa Small Business TOU Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 1.470),
            ('Peak', time(16, 0), time(21, 0), 24.384),
            ('Shoulder', time(21, 0), time(11, 0), 5.761)
        ],
        'rate': {'Off-Peak': 1.470, 'Peak': 24.384, 'Shoulder': 5.761}
    },
    'EBTDEMT1': {
        'name': 'East Small Business TOU Demand & Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 1.470),
            ('Peak', time(16, 0), time(21, 0), 1.594),
            ('Shoulder', time(21, 0), time(11, 0), 7.496)
        ],
        'rate': {'Off-Peak': 1.470, 'Peak': 1.594, 'Shoulder': 7.496}
    },
    'WBTDEMT1': {
        'name': 'West Small Business TOU Demand & Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 1.470),
            ('Peak', time(16, 0), time(21, 0), 1.594),
            ('Shoulder', time(21, 0), time(11, 0), 7.496)
        ],
        'rate': {'Off-Peak': 1.470, 'Peak': 1.594, 'Shoulder': 7.496}
    },
    'MBTDEMT4': {
        'name': 'Mt Isa Small Business TOU Demand & Energy',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 1.470),
            ('Peak', time(16, 0), time(21, 0), 0.384),
            ('Shoulder', time(21, 0), time(11, 0), 6.286)
        ],
        'rate': {'Off-Peak': 1.470, 'Peak': 0.384, 'Shoulder': 6.286}
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
}


demand_charges_2025_26 = {
    'ERTOUET1': None,
    'ERTDEMXT1': { 'Peak': 7},
    'ERTDEMCT1': { 'Peak': 7},
    '3900': { 'Peak': 5.127},
    '3600': { 'Peak': 10.289},
    '3800': { 'Peak': 4.975},
    '7200': {
        'Off-Peak': 0.000,
        'Peak': 14.919,
        'Shoulder': 3.333
    },
    '8100': 15.773,
    '8300': 15.704,
}

demand_charges_2026_27 = {
    'ERTOUET1': None,
    'WRTOUET1': None,
    'MRTOUET4': None,
    'EBTOUET1': None,
    'WBTOUET1': None,
    'MBTOUET4': None,
    'ERTDEMT1': { 'Peak': 7},  # East Residential TOU Demand
    'WRTDEMT1': { 'Peak': 7},  # West Residential TOU Demand
    'MRTDEMT4': { 'Peak': 7},  # Mt Isa Residential TOU Demand
    'EBTDEMT1': { 'Peak': 7},  # East Small Business TOU Demand
    'WBTDEMT1': { 'Peak': 7},  # West Small Business TOU Demand
    'MBTDEMT4': { 'Peak': 7},  # Mt Isa Small Business TOU Demand
    'ERTDEMXT1': { 'Peak': 7},  # legacy alias
    'ERTDEMCT1': { 'Peak': 7},  # legacy alias
    '3900': { 'Peak': 7.000},
    '3600': { 'Peak': 10.289},
    '3800': { 'Peak': 7.000},
    '7200': {
        'Off-Peak': 0.000,
        'Peak': 15.459,
        'Shoulder': 4.080
    },
    '8100': 15.773,
    '8300': 13.913,
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
    if len(code) == 4:
        prefix = code[:2]
        return prefix + '00'
    return code

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

    charge = charges['ERTDEMXT1']
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
    daily_rate = charge_per_kw_per_month / 30
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
    fees = get_daily_fees(interval_time)
    fee = fees.get(tariff_code)
    if fee is None:
        fee = fees.get('ERTOUET1')  # Default to ERTOUET1 if unknown

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

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for Ergon.

    Parameters:
    - interval_time (str): The interval time.
    - tariff (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10

    tariffs = get_tariffs(interval_datetime)
    tariff = tariffs.get(tariff_code)

    if not tariff:
        # Handle unknown tariff codes
        tariff = tariffs.get('ERTOUET1')  # Default to ERTOUET1 if unknown

    # Find the applicable period and rate
    for period, start, end, rate in tariff['periods']:
        if start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            total_price = rrp_c_kwh + rate * GST
            return total_price

    # If no period is found, use the default rate
    if isinstance(tariff['rate'], dict):
        # For Time-of-Use tariffs, use the first rate as default
        rate = list(tariff['rate'].values())[0]
    else:
        rate = tariff['rate']

    return rrp_c_kwh + rate * GST
