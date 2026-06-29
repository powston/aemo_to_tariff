# aemo_to_tariff/victoria.py
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

def time_zone():
    # Victoria uses Australia/Melbourne time
    return 'Australia/Melbourne'

###############################################################################
# Daily Fees
###############################################################################
# These might be daily supply charges ($/day).
# In some Victorian DNSP areas, there may be multiple "bands"


daily_fees = {
    'VICR_SINGLE': 1.00,  # Residential single rate
    'VICR_TOU': 1.20,  # Residential time-of-use
    'VICS_SINGLE': 2.50,  # Small business single rate
    'VICS_TOU': {
        'band1': 2.50,   # Up to 20 MWh/year
        'band2': 3.00,   # 20–40 MWh/year
        'band3': 3.50,   # 40–60 MWh/year
        'band4': 4.00,   # 60–80 MWh/year
        'band5': 4.50    # >80 MWh/year
    },
    'VICR_DEMAND': 1.10,  # Residential demand
    'VICS_DEMAND': 3.00   # Small business demand
}

###############################################################################
# Tariff Schedules
###############################################################################
# These define how usage charges (c/kWh) vary by time of day.
# Some Victorian tariffs have Peak/Off-Peak only; others have Peak/Shoulder/Off-Peak.

tariffs = {
    'VICR_SINGLE': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 20.0)  # c/kWh
        ],
        'rate': 20.0
    },
    'VICR_TOU': {
        'name': 'Residential Time of Use',
        'periods': [
            # Example: Peak 7am–11pm, Off-Peak 11pm–7am
            ('Peak', time(7, 0), time(23, 0), 30.0),
            ('Off-Peak', time(23, 0), time(7, 0), 15.0)
        ],
        'rate': {'Peak': 30.0, 'Off-Peak': 15.0},
        # Classic Victorian ToU peak (7am–11pm) applies on business days only;
        # weekends are entirely off-peak. See convert().
        'weekend_offpeak': True
    },
    'VICS_SINGLE': {
        'name': 'Small Business Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 22.0)
        ],
        'rate': 22.0
    },
    'VICS_TOU': {
        'name': 'Small Business Time of Use',
        'periods': [
            # Example: Peak 7am–10pm, Off-Peak 10pm–7am
            ('Peak', time(7, 0), time(22, 0), 35.0),
            ('Off-Peak', time(22, 0), time(7, 0), 18.0)
        ],
        'rate': {'Peak': 35.0, 'Off-Peak': 18.0},
        # Classic Victorian ToU peak (7am–10pm) applies on business days only;
        # weekends are entirely off-peak. See convert().
        'weekend_offpeak': True
    },
    'VICR_DEMAND': {
        'name': 'Residential Demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 15.0)
        ],
        'rate': 15.0
    },
    'VICS_DEMAND': {
        'name': 'Small Business Demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 25.0)
        ],
        'rate': 25.0
    }
}

###############################################################################
# Demand Charges
###############################################################################
# These are the monthly $/kW (or $/kVA) charges for demand-based tariffs.
# Multiply by the measured maximum demand, then prorate for the billing period.

demand_charges = {
    'VICR_DEMAND': 15.00,  # Residential Demand
    'VICS_DEMAND': 30.00   # Small Business Demand
}

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30):
    """
    Calculate the demand fee for a given tariff code, demand amount (kW),
    and number of days in the billing period.
    """
    # Strip down to the first part of the code if needed, or just use the full code:
    tariff_code = str(tariff_code)

    if tariff_code not in demand_charges:
        return 0.0

    charge_per_kw_per_month = demand_charges[tariff_code]

    # Convert the charge to a daily rate
    daily_rate = charge_per_kw_per_month / 30
    total_charge = demand_kw * daily_rate * days
    return total_charge

def get_daily_fee(tariff_code: str, annual_usage: float = None):
    """
    Calculate the daily fee ($/day) for a given tariff code.

    If the daily fee is tiered by annual usage, pass in `annual_usage`.
    Otherwise, return the simple daily fee from the dictionary.
    """
    fee = daily_fees.get(tariff_code)

    # If the fee is a dict, we assume it's usage-based or capacity-based
    if isinstance(fee, dict):
        if annual_usage is None:
            raise ValueError("Annual usage is required for this tariff.")
        if annual_usage <= 20000:
            return fee['band1']
        elif annual_usage <= 40000:
            return fee['band2']
        elif annual_usage <= 60000:
            return fee['band3']
        elif annual_usage <= 80000:
            return fee['band4']
        else:
            return fee['band5']

    # If the fee is just a number, return it as-is
    return fee if fee else 0.0

def get_periods(tariff_code: str):
    """
    Retrieve the time-of-use periods for a given tariff code.
    """
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

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for a Victorian network.

    Parameters:
    - interval_datetime (datetime): The interval datetime object.
    - tariff_code (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    # Convert local time
    interval_datetime = interval_datetime - timedelta(minutes=5)
    local_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()

    # Convert $/MWh to c/kWh: 1 $/MWh = 0.1 c/kWh
    # e.g. 100 $/MWh = 10 c/kWh
    rrp_c_kwh = rrp / 10

    # Lookup tariff
    tariff = tariffs.get(tariff_code)
    if not tariff:
        # If unknown, apply some default linear function
        slope = 1.0
        intercept = 5.0
        return rrp_c_kwh * slope + intercept

    # The classic Victorian ToU tariffs (VICR_TOU 7am–11pm, VICS_TOU 7am–10pm)
    # define the peak as Monday–Friday only; weekends fall entirely to off-peak
    # (CitiPower/United Energy legacy ToU definition: "weekends" listed under
    # off-peak). Short-circuit weekends to the Off-Peak rate before the period
    # scan. Public holidays are not handled — same limitation as the feed-in
    # side. NOTE: the current default Victorian residential ToU (CRTOU/URTOU)
    # uses a 3pm–9pm peak that applies *every day*; this module models the
    # legacy 7am–11pm weekday-only definition.
    if interval_datetime.weekday() >= 5 and tariff.get('weekend_offpeak'):
        off_peak_rate = next((rate for name, start, end, rate in tariff['periods']
                              if 'off' in name.lower()), None)
        if off_peak_rate is not None:
            return rrp_c_kwh + off_peak_rate

    # Identify which period the local_time falls in
    for period_name, start, end, rate in tariff['periods']:
        # Handle periods that wrap past midnight (if start > end)
        if start < end:
            if start <= local_time < end:
                return rrp_c_kwh + rate
        else:
            # For example, if the period is 22:00 to 07:00
            if local_time >= start or local_time < end:
                return rrp_c_kwh + rate

    # Fallback to the "default" rate if no period matched
    if isinstance(tariff['rate'], dict):
        # Use the first key from the dictionary as default
        rate = list(tariff['rate'].values())[0]
    else:
        rate = tariff['rate']
    return rrp_c_kwh + rate

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
    
    if tariff_code not in demand_charges:
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
