# aemo_to_tariff/essential.py
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

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
    if customer_type.lower() == 'residential':
        return {'import': ['BLNRSS2'], 'export': ['BLNREX2']}  # was 'BLNT3AL' — obsolete since 1 Jul 2025
    elif customer_type.lower() == 'business':
        return {'import': ['BLNBSS1'], 'export': ['BLNBEX1']}
    else:
        raise ValueError("Invalid customer type.")


feed_in_tariffs_2025_26 = {
    'BLNREX2': {
        'name': 'LV Residential Solar Export',
        'periods': [
            ('Peak', time(17, 0), time(20, 0), 11.5725),
            ('Solar Soaker', time(10, 0), time(14, 59), -0.8172)
        ]
    },
    'BLNBEX1': {
        'name': 'LV Residential Business Solar Export',
        'periods': [
            ('Peak', time(16, 0), time(20, 0), 12.0871),
            ('Off Peak', time(0, 0), time(10, 0), -0.8172)
        ]
    }
}

# AER 2026–27: residential export rebate 11.7212 c/kWh (peak), export
# consumption >7.5 kWh +0.8277 c/kWh (solar soak); business rebate 12.2425.
feed_in_tariffs_2026_27 = {
    'BLNREX2': {
        'name': 'LV Residential Solar Export',
        'periods': [
            ('Peak', time(17, 0), time(20, 0), 11.7212),
            ('Solar Soaker', time(10, 0), time(14, 59), -0.8277)
        ]
    },
    'BLNBEX1': {
        'name': 'LV Residential Business Solar Export',
        'periods': [
            ('Peak', time(16, 0), time(20, 0), 12.2425),
            ('Off Peak', time(0, 0), time(10, 0), -0.8277)
        ]
    }
}


tariffs_2025_26 = {
    'BLNN2AU': {
        'name': 'LV Residential Anytime',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 12.6808),
        ]
    },
    'BLNT3AU': {
        'name': 'LV Residential TOU (Basic Meter)',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 17.7676),
            ('Shoulder', time(9, 0), time(17, 0), 13.8149),
            ('Peak', time(17, 0), time(20, 0), 17.7676),
            ('Shoulder', time(20, 0), time(22, 0), 13.8149),
            ('Off-Peak', time(22, 0), time(7, 0), 5.4026),
        ]
    },
    'BLNT3AL': {
        'name': 'LV Residential TOU (Interval Meter)',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 13.3044),
            ('Peak', time(17, 0), time(20, 0), 18.4298),
            ('Shoulder', time(20, 0), time(22, 0), 13.3044),
            ('Off-Peak', time(22, 0), time(7, 0), 5.4026),
        ]
    },
    'BLNRSS2': {
        'name': 'LV Residential Sun Soaker',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 16.9522),
            ('Peak', time(15, 0), time(22, 0), 16.9522),
            ('Off-Peak', time(10, 0), time(15, 0), 5.8530),
            ('Off-Peak', time(22, 0), time(7, 0), 5.8530),
        ]
    },
    'BLND1AR': {
        'name': 'LV Residential Demand',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 5.9050),
            ('Peak', time(17, 0), time(20, 0), 8.8434),
            ('Shoulder', time(20, 0), time(22, 0), 5.9050),
            ('Off-Peak', time(22, 0), time(7, 0), 3.5188),
        ]
    },
    'BLNC1AU': {
        'name': 'Controlled Load 1',
        'periods': [
            ('Controlled Load 1', time(0, 0), time(23, 59), 2.7130),
        ]
    },
    'BLNC2AU': {
        'name': 'Controlled Load 2',
        'periods': [
            ('Controlled Load 2', time(0, 0), time(23, 59), 5.7748),
        ]
    },
    'BLNN1AU': {
        'name': 'LV Small Business Anytime',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 17.4231),
        ]
    },
    'BLNT2AU': {
        'name': 'LV Small Business TOU (Basic Meter)',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 18.8112),
            ('Shoulder', time(9, 0), time(17, 0), 14.7236),
            ('Peak', time(17, 0), time(20, 0), 18.8112),
            ('Shoulder', time(20, 0), time(22, 0), 14.7236),
            ('Off-Peak', time(22, 0), time(7, 0), 7.8256),
        ]
    },
    'BLNT2AL': {
        'name': 'LV Small Business TOU (Interval Meter)',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 14.1904),
            ('Peak', time(17, 0), time(20, 0), 19.5029),
            ('Shoulder', time(20, 0), time(22, 0), 14.1904),
            ('Off-Peak', time(22, 0), time(7, 0), 7.5707),
        ]
    },
    'BLNT1AO': {
        'name': 'LV Small Business TOU (100–160 MWh)',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 14.7236),
            ('Peak', time(17, 0), time(20, 0), 18.8112),
            ('Shoulder', time(20, 0), time(22, 0), 14.7236),
            ('Off-Peak', time(22, 0), time(7, 0), 7.8256),
        ]
    },
    'BLND1AB': {
        'name': 'LV Small Business Demand',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 8.6714),
            ('Peak', time(17, 0), time(20, 0), 12.3583),
            ('Shoulder', time(20, 0), time(22, 0), 8.6714),
            ('Off-Peak', time(22, 0), time(7, 0), 5.1286),
        ]
    },
    'BLNBSS1': {
        # SS window per the 2025-26 Network Price List: Peak 7am-10am and
        # 3pm-10pm every day, Off-Peak all other times (same shape as BLNRSS2).
        'name': 'LV Small Business TOU - Sun Soaker',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 17.9646),
            ('Peak', time(15, 0), time(22, 0), 17.9646),
            ('Off-Peak', time(10, 0), time(15, 0), 8.1015),
            ('Off-Peak', time(22, 0), time(7, 0), 8.1015),
        ]
    },
}

# AER 2026–27 consolidated stakeholder report (8 May 2026).
tariffs_2026_27 = {
    'BLNN2AU': {
        'name': 'LV Residential Anytime',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 14.5489),
        ]
    },
    'BLNT3AU': {
        'name': 'LV Residential TOU (Basic Meter)',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 20.5470),
            ('Shoulder', time(9, 0), time(17, 0), 15.9751),
            ('Peak', time(17, 0), time(20, 0), 20.5470),
            ('Shoulder', time(20, 0), time(22, 0), 15.9751),
            ('Off-Peak', time(22, 0), time(7, 0), 6.4301),
        ]
    },
    'BLNT3AL': {
        'name': 'LV Residential TOU (Interval Meter)',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 15.1672),
            ('Peak', time(17, 0), time(20, 0), 20.9051),
            ('Shoulder', time(20, 0), time(22, 0), 15.1672),
            ('Off-Peak', time(22, 0), time(7, 0), 6.3486),
        ]
    },
    'BLNRSS2': {
        'name': 'LV Residential Sun Soaker',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 17.9566),
            ('Peak', time(15, 0), time(22, 0), 17.9566),
            ('Off-Peak', time(10, 0), time(15, 0), 6.3275),
            ('Off-Peak', time(22, 0), time(7, 0), 6.3275),
        ]
    },
    'BLND1AR': {
        'name': 'LV Residential Demand',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 7.3713),
            ('Peak', time(17, 0), time(20, 0), 10.8399),
            ('Shoulder', time(20, 0), time(22, 0), 7.3713),
            ('Off-Peak', time(22, 0), time(7, 0), 4.3811),
        ]
    },
    'BLNC1AU': {
        'name': 'Controlled Load 1',
        'periods': [
            ('Controlled Load 1', time(0, 0), time(23, 59), 3.5046),
        ]
    },
    'BLNC2AU': {
        'name': 'Controlled Load 2',
        'periods': [
            ('Controlled Load 2', time(0, 0), time(23, 59), 7.0007),
        ]
    },
    'BLNN1AU': {
        'name': 'LV Small Business Anytime',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 19.6765),
        ]
    },
    'BLNT2AU': {
        'name': 'LV Small Business TOU (Basic Meter)',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 21.6514),
            ('Shoulder', time(9, 0), time(17, 0), 16.9328),
            ('Peak', time(17, 0), time(20, 0), 21.6514),
            ('Shoulder', time(20, 0), time(22, 0), 16.9328),
            ('Off-Peak', time(22, 0), time(7, 0), 9.0349),
        ]
    },
    'BLNT2AL': {
        'name': 'LV Small Business TOU (Interval Meter)',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 16.0890),
            ('Peak', time(17, 0), time(20, 0), 22.0254),
            ('Shoulder', time(20, 0), time(22, 0), 16.0890),
            ('Off-Peak', time(22, 0), time(7, 0), 8.6314),
        ]
    },
    'BLNT1AO': {
        'name': 'LV Small Business TOU (100–160 MWh)',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 16.9328),
            ('Peak', time(17, 0), time(20, 0), 21.6514),
            ('Shoulder', time(20, 0), time(22, 0), 16.9328),
            ('Off-Peak', time(22, 0), time(7, 0), 9.0349),
        ]
    },
    'BLND1AB': {
        'name': 'LV Small Business Demand',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 8.6714),
            ('Peak', time(17, 0), time(20, 0), 12.3583),
            ('Shoulder', time(20, 0), time(22, 0), 8.6714),
            ('Off-Peak', time(22, 0), time(7, 0), 5.1286),
        ]
    },
    'BLNBSS1': {
        # Same SS window as 2025-26 (Peak 7-10 and 15-22 every day).
        'name': 'LV Small Business TOU - Sun Soaker',
        'periods': [
            ('Peak', time(7, 0), time(10, 0), 18.9741),
            ('Peak', time(15, 0), time(22, 0), 18.9741),
            ('Off-Peak', time(10, 0), time(15, 0), 8.5988),
            ('Off-Peak', time(22, 0), time(7, 0), 8.5988),
        ]
    },
}


daily_fees_2025_26 = {
    'BLNN2AU': 1.2788,
    'BLNT3AU': 1.2788,
    'BLNT3AL': 1.2788,
    'BLNRSS2': 1.2788,
    'BLND1AR': 1.2788,
    'BLNC1AU': 0.1148,
    'BLNC2AU': 0.1148,
    'BLNN1AU': 2.0579,
    'BLNT2AU': 2.0579,
    'BLNT2AL': 2.0579,
    'BLNT1AO': 2.0579,
    'BLNBSS1': 2.0579,
    'BLND1AB': 2.0579,
}

# AER 2026–27: residential $473.36/year ≈ $1.2969/day, business
# $804.77/year ≈ $2.2049/day, controlled $48.85/year ≈ $0.1339/day.
daily_fees_2026_27 = {
    'BLNN2AU': 1.2969,
    'BLNT3AU': 1.2969,
    'BLNT3AL': 1.2969,
    'BLNRSS2': 1.2969,
    'BLND1AR': 1.2969,
    'BLNC1AU': 0.1338,
    'BLNC2AU': 0.1338,
    'BLNN1AU': 2.2049,
    'BLNT2AU': 2.2049,
    'BLNT2AL': 2.2049,
    'BLNT1AO': 2.2049,
    'BLNBSS1': 2.2049,
    'BLND1AB': 2.2049,
}


demand_charges_2025_26 = {
    'BLNRSS2': None,
    'BLND1AR': {'peak': 8.998},
    'BLND1AB': {'peak': 8.998},
}

# AER 2026–27 demand: BLND1AR peak demand 5.193 $/kVA (col 13).
# BLND1AB (LV Small Business Demand) not separately rated in 2026–27 spreadsheet;
# preserved from 2025–26.
demand_charges_2026_27 = {
    'BLNRSS2': None,
    'BLND1AR': {'peak': 5.193},
    'BLND1AB': {'peak': 8.998},
}


def get_tariffs(interval_time=None):
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_feed_in_tariffs(interval_time=None):
    return feed_in_tariffs_2026_27 if _use_2026_prices(interval_time) else feed_in_tariffs_2025_26


def get_daily_fees(interval_time=None):
    return daily_fees_2026_27 if _use_2026_prices(interval_time) else daily_fees_2025_26


def get_demand_charges(interval_time=None):
    return demand_charges_2026_27 if _use_2026_prices(interval_time) else demand_charges_2025_26


def get_periods(tariff_code: str, interval_time=None):
    """
    Retrieve the list of TOU periods for the given tariff code.
    Each period is (period_name, start_time, end_time, rate_cents_kwh).
    """
    tariff = get_tariffs(interval_time).get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")
    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh including any feed-in adjustment.

    Parameters:
    - interval_datetime (datetime): The interval datetime.
    - tariff_code (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    local_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10
    feed_in_tariffs = get_feed_in_tariffs(interval_datetime)
    tariff = feed_in_tariffs.get(tariff_code, {})
    if not tariff:
        return rrp_c_kwh  # Fallback if unknown tariff code
    for period, start, end, rate in tariff['periods']:
        if start <= local_time < end:
            total_price = rrp_c_kwh + rate
            return total_price
    return rrp_c_kwh  # Fallback if no specific feed-in tariff found


# Essential Energy standard ToU tariffs whose Peak (and Shoulder) periods apply
# on business days only. On weekends the entire weekday Peak/Shoulder window is
# billed at the Off-Peak rate — the Essential 2025-26 Network Price List period
# table shows the "Weekend" row as a single off-peak band spanning the whole
# weekday peak/shoulder window. Public holidays are deliberately NOT handled:
# Essential's price list states the periods "are unchanged when a public holiday
# falls on a weekday" (i.e. a weekday public holiday is still a peak day), so the
# Mon–Fri gate matches their rule exactly. The Sun Soaker tariffs (BLNRSS2,
# BLNBSS1) are "Everyday" — their peak applies 7 days a week — so they are
# excluded from this set.
WEEKDAY_PEAK_TARIFFS = {
    'BLNT3AU', 'BLNT3AL', 'BLNT2AU', 'BLNT2AL', 'BLNT1AO', 'BLND1AR', 'BLND1AB',
}


def convert(interval_datetime: datetime, tariff_code: str, rrp: float) -> float:
    """
    Convert RRP from $/MWh to c/kWh for an Essential Energy tariff.

    Parameters:
    - interval_datetime (datetime): The interval datetime in UTC or any tz.
    - tariff_code (str): The tariff code (e.g. 'BLNT3AL', 'BLNRSS2').
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The total price in c/kWh.
    """
    # Convert interval time to Australia/Sydney
    interval_datetime = interval_datetime - timedelta(minutes=5)
    local_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10.0  # $/MWh => c/kWh

    tariff = get_tariffs(interval_datetime).get(tariff_code)
    if not tariff:
        # Fallback if unknown tariff code
        slope = 1.037869032618134
        intercept = 5.586606750833143
        return rrp_c_kwh * slope + intercept

    # Weekend: standard ToU tariffs have no Peak/Shoulder — the whole day is
    # off-peak. Short-circuit to the Off-Peak rate before the period scan.
    if interval_datetime.weekday() >= 5 and tariff_code in WEEKDAY_PEAK_TARIFFS:
        off_peak_rate = next((rate for name, start, end, rate in tariff['periods']
                              if 'off' in name.lower()), None)
        if off_peak_rate is not None:
            return rrp_c_kwh + off_peak_rate

    # Match the period whose start-end covers local_time
    for period_name, start, end, rate_cents in tariff['periods']:
        # Handle normal range if start < end
        if start < end:
            if start <= local_time < end:
                return rrp_c_kwh + rate_cents
        else:
            # Period crosses midnight
            if local_time >= start or local_time < end:
                return rrp_c_kwh + rate_cents

    # Default to first period’s rate if none matched
    return rrp_c_kwh + tariff['periods'][0][3]

def get_daily_fee(tariff_code: str, interval_time=None) -> float:
    """
    Get the daily fixed fee for the given tariff code (in cents per day).
    Fee tables are transcribed in $/day; the package contract is cents/day.
    """
    return get_daily_fees(interval_time).get(tariff_code, 0.0) * 100


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
    demand_charges = get_demand_charges(interval_time)

    charge = demand_charges.get('BLND1AR')
    if tariff_code in demand_charges:
        charge = demand_charges[tariff_code]
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

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30, tou='Peak', interval_time=None) -> float:
    """
    Calculate the demand charge for a given tariff code, maximum demand (kW), and billing period (days).

    Returns:
    - float: The demand fee in dollars (i.e. demand_charge $/kW/day * demand_kw * days).
    """
    demand_charges = get_demand_charges(interval_time)
    daily_charge = demand_charges.get(tariff_code, {}).get(tou.lower(), 0.0)
    return daily_charge * demand_kw * days
