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
        return {'import': ['N71'], 'export': ['N61']}
    elif customer_type == 'Business':
        return {'import': ['N91'], 'export': []}
    elif customer_type == 'Battery':
        return {'import': ['N95'], 'export': ['N95']}
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")


# 2025–26 reference: Endeavour NUOS Price List 2025-26 v1.1
tariffs_2025_26 = {
    'N70': {
        'name': 'Residential Flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.8173)
        ],
        'fixed_daily_charge': 63.1270,
    },
    'N71': {
        'name': 'Residential Seasonal TOU',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 21.7964),
            ('Low-season Peak', time(16, 0), time(20, 0),  13.8419),
            ('Solar Soak', time(10, 0), time(14, 0), 3.4252),
            ('Off Peak', time(0, 0), time(10, 0), 10.4931),
            ('Off Peak', time(14, 0), time(16, 0), 10.4931),
            ('Off Peak', time(20, 0), time(23, 59), 10.4931)
        ],
        'fixed_daily_charge': 63.1270,
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N90': {
        'name': 'General Supply Block',
        'periods': [
            ('Block 1', time(0, 0), time(23, 59), 11.2803),
            ('Block 2', time(0, 0), time(23, 59), 13.5302)
        ],
        'fixed_daily_charge': 88.8470,
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
        'fixed_daily_charge': 88.8470,
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N19': {
        # LV demand tariff. The 10:00–14:00 window has no energy charge per
        # the AER 2025–26 schedule (Solar Soak column blank); add an explicit
        # period at rate 0 so convert() doesn't fall through to the default
        # slope/intercept approximation.
        'name': 'LV Seasonal STOU Demand',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 5.4400),
            ('Low-season Peak', time(16, 0), time(20, 0), 4.8861),
            ('Solar Soak', time(10, 0), time(14, 0), 0.0),
            ('Off Peak', time(0, 0), time(10, 0), 3.6458),
            ('Off Peak', time(14, 0), time(16, 0), 3.6458),
            ('Off Peak', time(20, 0), time(23, 59), 3.6458)
        ],
        'fixed_daily_charge': 2612.00,
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N95': {
        'name': 'Storage',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 13.1329),
            ('Low-season Peak', time(16, 0), time(20, 0), 5.1784),
            ('Solar Soak', time(10, 0), time(14, 0), 0.0),
            ('Off Peak', time(0, 0), time(10, 0), 1.8296),
            ('Off Peak', time(14, 0), time(16, 0), 1.8296),
            ('Off Peak', time(20, 0), time(23, 59), 1.8296)
        ],
        'fixed_daily_charge': 161.1570,
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N73': {
        'name': 'Residential Demand Transitional',
        'periods': [
            ('Solar Soak', time(10, 0), time(14, 0), 3.4252),
            ('Off Peak', time(0, 0), time(10, 0), 9.5389),
            ('Off Peak', time(14, 0), time(23, 59), 9.5389)
        ],
        'fixed_daily_charge': 63.1270,
    }
}

# AER 2026–27 consolidated stakeholder report (8 May 2026).
tariffs_2026_27 = {
    'N70': {
        'name': 'Residential Flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 12.0348)
        ],
        'fixed_daily_charge': 66.55,
    },
    'N71': {
        'name': 'Residential Seasonal TOU',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 23.4471),
            ('Low-season Peak', time(16, 0), time(20, 0), 15.2042),
            ('Solar Soak', time(10, 0), time(14, 0), 4.5355),
            ('Off Peak', time(0, 0), time(10, 0), 11.734),
            ('Off Peak', time(14, 0), time(16, 0), 11.734),
            ('Off Peak', time(20, 0), time(23, 59), 11.734)
        ],
        'fixed_daily_charge': 66.55,
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N90': {
        'name': 'General Supply Block',
        'periods': [
            ('Block 1', time(0, 0), time(23, 59), 12.5753),
            ('Block 2', time(0, 0), time(23, 59), 15.0103)
        ],
        'fixed_daily_charge': 95.24,
    },
    'N91': {
        'name': 'GS Seasonal TOU',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 25.1552),
            ('Low-season Peak', time(16, 0), time(20, 0), 16.9123),
            ('Solar Soak', time(10, 0), time(14, 0), 5.1696),
            ('Off Peak', time(0, 0), time(10, 0), 13.4421),
            ('Off Peak', time(14, 0), time(16, 0), 13.4421),
            ('Off Peak', time(20, 0), time(23, 59), 13.4421)
        ],
        'fixed_daily_charge': 95.24,
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N19': {
        # AER 2026–27 lists no Solar Soak energy charge (column blank); add
        # a 10:00–14:00 period at rate 0 to prevent fall-through.
        'name': 'LV Seasonal STOU Demand',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 6.1024),
            ('Low-season Peak', time(16, 0), time(20, 0), 5.5284),
            ('Solar Soak', time(10, 0), time(14, 0), 0.0),
            ('Off Peak', time(0, 0), time(10, 0), 4.2432),
            ('Off Peak', time(14, 0), time(16, 0), 4.2432),
            ('Off Peak', time(20, 0), time(23, 59), 4.2432)
        ],
        'fixed_daily_charge': 2414.00,
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N95': {
        'name': 'Storage',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 13.7294),
            ('Low-season Peak', time(16, 0), time(20, 0), 5.4865),
            ('Solar Soak', time(10, 0), time(14, 0), 0.0),
            ('Off Peak', time(0, 0), time(10, 0), 2.0163),
            ('Off Peak', time(14, 0), time(16, 0), 2.0163),
            ('Off Peak', time(20, 0), time(23, 59), 2.0163)
        ],
        'fixed_daily_charge': 169.69,
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N73': {
        'name': 'Residential Demand Transitional',
        'periods': [
            ('Solar Soak', time(10, 0), time(14, 0), 4.5355),
            ('Off Peak', time(0, 0), time(10, 0), 10.906),
            ('Off Peak', time(14, 0), time(23, 59), 10.906)
        ],
        'fixed_daily_charge': 66.55,
    }
}

demand_charges_2025_26 = {
    'N71': None,
    'N91': None,
    'N19': {
        'Peak': 49.42,
        'Shoulder': 0.0,
        'Off-Peak': 0.0
    },
    'N73': {
        'Peak': 14.2700,
        'Peak_Low': 7.3800,
        'Off-Peak': 0.0,
        'Shoulder': 0.0
    }
}

demand_charges_2026_27 = {
    'N71': None,
    'N91': None,
    'N19': {
        'Peak': 53.11,
        'Peak_Low': 48.33,
        'Shoulder': 0.0,
        'Off-Peak': 0.0
    },
    'N72': {
        'Peak': 18.18,
        'Peak_Low': 9.27,
        'Off-Peak': 0.0,
        'Shoulder': 0.0
    },
    'N73': {
        'Peak': 16.36,
        'Peak_Low': 8.34,
        'Off-Peak': 0.0,
        'Shoulder': 0.0
    },
    'N92': {
        'Peak': 24.18,
        'Peak_Low': 11.92,
        'Off-Peak': 0.0,
        'Shoulder': 0.0
    },
    'N93': {
        'Peak': 21.76,
        'Peak_Low': 10.73,
        'Off-Peak': 0.0,
        'Shoulder': 0.0
    },
}

feed_in_tariffs_2025_26 = {
    'N61': {
        # GST-inclusive values from Endeavour 2025-26 Network Price List (page 34).
        # HS export reward = 12.4336 c/kWh (Nov–Mar weekdays 16:00–20:00).
        # LS export reward = 3.6837 c/kWh (Apr–Oct weekdays 16:00–20:00).
        # Solar Soak Block 2 charge = 1.9690 c/kWh (every day 10:00–14:00, after
        # 730 kWh/quarter); stored as -1.9690 so spot + rate = spot - 1.969.
        'name': 'Residential Electrify',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 12.4336),
            ('Low-season Peak', time(16, 0), time(20, 0), 3.6837),
            ('Solar Soak', time(10, 0), time(14, 0), -1.9690)
        ],
        'weekdays': [0, 1, 2, 3, 4],
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N95': {
        'name': 'Storage',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 12.4336),
            ('Low-season Peak', time(16, 0), time(20, 0), 3.6837),
            ('Solar Soak', time(10, 0), time(14, 0), -1.9690)
        ],
        'weekdays': [0, 1, 2, 3, 4],
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    }
}

# AER 2026–27 export reward (col 21/22) — values stored as positive c/kWh added
# to the spot price, matching the 2025–26 convention.
feed_in_tariffs_2026_27 = {
    'N61': {
        'name': 'Residential Electrify',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 11.7131),
            ('Low-season Peak', time(16, 0), time(20, 0), 3.4702),
            ('Solar Soak', time(10, 0), time(14, 0), -1.86)
        ],
        'weekdays': [0, 1, 2, 3, 4],
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    },
    'N95': {
        'name': 'Storage',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 11.7131),
            ('Low-season Peak', time(16, 0), time(20, 0), 3.4702),
            ('Solar Soak', time(10, 0), time(14, 0), -1.86)
        ],
        'weekdays': [0, 1, 2, 3, 4],
        'peak_months': [11, 12, 1, 2, 3]  # High season: Nov–Mar
    }
}


def get_tariffs(interval_time=None):
    return tariffs_2026_27 if _use_2026_prices(interval_time) else tariffs_2025_26


def get_demand_charges(interval_time=None):
    return demand_charges_2026_27 if _use_2026_prices(interval_time) else demand_charges_2025_26


def get_feed_in_tariffs(interval_time=None):
    return feed_in_tariffs_2026_27 if _use_2026_prices(interval_time) else feed_in_tariffs_2025_26


def get_daily_fee(tariff_code: str, interval_time=None):
    """
    Get the daily fee for a given tariff.

    Parameters:
    - tariff_code (str): The tariff code.
    - interval_time (datetime, optional): Selects the price schedule. Defaults to now.

    Returns:
    - float: The daily fee in cents per day.
    """
    tariff = get_tariffs(interval_time).get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return tariff.get('fixed_daily_charge', 0.0)  # already in cents/day, matching the package contract


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
    charge = demand_charges.get('N19')
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

def calculate_demand_fee(tariff: str, demand_kw: float, days=30, interval_time=None):
    """
    Calculate the demand fee for a given tariff, demand amount, and time period.

    Parameters:
    - tariff (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for some tariffs).
    - days (int): The number of days for the billing period (default is 30).
    - interval_time (datetime, optional): Selects the price schedule. Defaults to now.

    Returns:
    - float: The demand fee in dollars.
    """
    tariff_data = get_tariffs(interval_time)[tariff]

    # Find the applicable rate
    for period, start, end, rate in tariff_data['periods']:
        if start <= demand_kw < end:
            return rate * days

    raise ValueError(f"Unknown demand amount: {demand_kw}")

def get_periods(tariff_code: str, interval_time=None):
    tariff = get_tariffs(interval_time).get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh including any feed-in tariff adjustment.

    Parameters:
    - interval_datetime (datetime): The interval datetime.
    - tariff_code (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    rrp_c_kwh = rrp / 10
    interval_datetime = interval_datetime - timedelta(minutes=5)
    feed_in_tariffs = get_feed_in_tariffs(interval_datetime)

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
                elif 'solar' in period.lower():
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
    tariff = get_tariffs(interval_datetime)[tariff_code]

    # Determine if it's high season (November to March) or low season (April to October)
    current_month = interval_datetime.month
    is_high_season = current_month in [11, 12, 1, 2, 3]

    # Endeavour ToU peak (16:00–20:00) only applies on business days (Mon–Fri).
    # On weekends that window is billed at the off-peak rate. Solar Soak
    # (10:00–14:00) and Off Peak apply every day. This mirrors the weekday gate
    # already used on the feed-in side (convert_feed_in_tariff). Public holidays
    # are not handled here — same limitation as the feed-in side. The peak window
    # has no Off Peak period covering it, so keep the off-peak rate as the
    # weekend fallback.
    is_business_day = interval_datetime.weekday() < 5
    off_peak_rate = next((rate for period, start, end, rate in tariff['periods']
                          if 'off' in period.lower()), None)

    # Find the applicable period and rate. Seasonal selection is driven by
    # the period name, not the tariff name — N95 'Storage' has 'High-season
    # Peak' / 'Low-season Peak' periods but its name doesn't contain
    # 'season', so the previous tariff-name check let the HS rate win in
    # both seasons.
    for period, start, end, rate in tariff['periods']:
        if start <= interval_time < end:
            period_lower = period.lower()
            if 'high' in period_lower:
                if is_high_season and is_business_day:
                    return rrp_c_kwh + rate * GST
                continue  # Skip HS period in low season / on weekends
            if 'low' in period_lower:
                if (not is_high_season) and is_business_day:
                    return rrp_c_kwh + rate * GST
                continue  # Skip LS period in high season / on weekends
            # Solar Soak, Off Peak, Anytime, Block N etc. apply year-round
            return rrp_c_kwh + rate * GST

    # Weekend peak window (peak periods skipped above): bill at the off-peak rate.
    if off_peak_rate is not None:
        return rrp_c_kwh + off_peak_rate * GST

    # Otherwise, this terrible approximation
    slope = 1.037869032618134
    intecept = 5.586606750833143
    return rrp_c_kwh * slope + intecept
