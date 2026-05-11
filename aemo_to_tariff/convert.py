# aemo_to_tariff/convert.py

import aemo_to_tariff.energex as energex
import aemo_to_tariff.ergon as ergon
import aemo_to_tariff.ausgrid as ausgrid
import aemo_to_tariff.evoenergy as evoenergy
import aemo_to_tariff.sapower as sapower
import aemo_to_tariff.tasnetworks as tasnetworks
import aemo_to_tariff.endeavour as endeavour
import aemo_to_tariff.powercor as powercor
import aemo_to_tariff.united as united
import aemo_to_tariff.jemena as jemena
import aemo_to_tariff.essential as essential
import aemo_to_tariff.victoria as victoria
import aemo_to_tariff.ausnet as ausnet

def spot_to_tariff(interval_time, network, tariff, rrp,
                   dlf=1.05905, mlf=1.0154, market=1.0154):
    """
    Convert spot price from $/MWh to c/kWh for a given network and tariff.

    Parameters:
    - interval_time (str): The interval time.
    - network (str): The name of the network (e.g., 'Energex', 'Ausgrid', 'Evoenergy').
    - tariff (str): The tariff code (e.g., '6970', '017').
    - rrp (float): The Regional Reference Price in $/MWh.
    - dlf (float): The Distribution Loss Factor.
    - mlf (float): The Metering Loss Factor.
    - market (float): The market factor.

    Returns:
    - float: The price in c/kWh.
    """
    adjusted_rrp = rrp * dlf * mlf * market
    network = network.lower()

    if network == 'energex':
        return energex.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'ergon':
        return ergon.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'ausgrid':
        return ausgrid.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'evoenergy':
        return evoenergy.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'sapn':
        return sapower.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'tasnetworks':
        return tasnetworks.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'endeavour':
        return endeavour.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'powercor':
        return powercor.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'united':
        return united.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'jemena':
        return jemena.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'essential':
        return essential.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'victoria':
        return victoria.convert(interval_time, tariff, adjusted_rrp)
    elif network == 'ausnet':
        return ausnet.convert(interval_time, tariff, adjusted_rrp)
    else:
        slope = 1.05
        intercept = 7.5
        # This is a terrible approximation
        # for unknown networks, but it should be close enough
        # for most cases.
        return adjusted_rrp * slope + intercept

def spot_to_feed_in_tariff(interval_time, network, tariff, rrp,
                           dlf=1.05905, mlf=1.0154, market=1.0154):
    """
    Convert spot price from $/MWh to c/kWh for a given network and tariff.

    Parameters:
    - interval_time (str): The interval time.
    - network (str): The name of the network (e.g., 'Energex', 'Ausgrid', 'Evoenergy').
    - tariff (str): The tariff code (e.g., '6970', '017').
    - rrp (float): The Regional Reference Price in $/MWh.
    - dlf (float): The Distribution Loss Factor.
    - mlf (float): The Metering Loss Factor.
    - market (float): The market factor.

    Returns:
    - float: The price in c/kWh.
    """
    adjusted_rrp = rrp * dlf * mlf * market
    network = network.lower()

    if network == 'energex':
        return energex.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'ergon':
        return ergon.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'ausgrid':
        return ausgrid.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'evoenergy':
        return evoenergy.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'sapn':
        return sapower.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'tasnetworks':
        return tasnetworks.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'endeavour':
        return endeavour.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'evoenergy':
        return evoenergy.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'jemena':
        return jemena.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'powercor':
        return united.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'united':
        return united.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'essential':
        return essential.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'victoria':
        return victoria.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    elif network == 'ausnet':
        return ausnet.convert_feed_in_tariff(interval_time, tariff, adjusted_rrp)
    else:
        return adjusted_rrp / 10

def get_daily_fee(network, tariff, annual_usage=None, interval_time=None):
    """
    Calculate the daily fee for a given network and tariff.

    Parameters:
    - network (str): The name of the network (e.g., 'Energex', 'Ausgrid', 'Evoenergy').
    - tariff (str): The tariff code.
    - annual_usage (float): Annual usage in kWh, required for some tariffs.
    - interval_time (datetime, optional): Selects the price schedule for networks
      that publish more than one (e.g. Energex/Ergon switch on 1 July 2026).
      Defaults to the current date.

    Returns:
    - float: The daily fee in dollars.
    """
    network = network.lower()

    if network == 'energex':
        return energex.get_daily_fee(tariff, annual_usage, interval_time=interval_time)
    elif network == 'ergon':
        return ergon.get_daily_fee(tariff, annual_usage, interval_time=interval_time)
    elif network == 'ausgrid':
        return ausgrid.get_daily_fee(tariff, annual_usage, interval_time=interval_time)
    elif network == 'evoenergy':
        # Placeholder for Evoenergy daily fee calculation
        return 0.0
    elif network == 'sapn':
        return sapower.get_daily_fee(tariff)
    elif network == 'tasnetworks':
        return tasnetworks.get_daily_fee(tariff)
    elif network == 'victoria':
        return victoria.get_daily_fee(tariff)
    elif network == 'essential':
        return essential.get_daily_fee(tariff)
    elif network == 'powercor':
        return powercor.get_daily_fee(tariff)
    elif network == 'united':
        return united.get_daily_fee(tariff)
    elif network == 'jemena':
        return jemena.get_daily_fee(tariff)
    elif network == 'endeavour':
        return endeavour.get_daily_fee(tariff)
    elif network == 'ausnet':
        return ausnet.get_daily_fee(tariff, annual_usage)
    else:
        return 1

def calculate_demand_fee(network, tariff, demand_kw, days=30, interval_time=None):
    """
    Calculate the demand fee for a given network, tariff, demand amount, and time period.

    Parameters:
    - network (str): The name of the network (e.g., 'Energex', 'Ausgrid', 'Evoenergy').
    - tariff (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for some tariffs).
    - days (int): The number of days for the billing period (default is 30).
    - interval_time (datetime, optional): Selects the price schedule for networks
      that publish more than one. Defaults to the current date.

    Returns:
    - float: The demand fee in dollars.
    """
    network = network.lower()

    if network == 'energex':
        return energex.calculate_demand_fee(tariff, demand_kw, days, interval_time=interval_time)
    elif network == 'ergon':
        return ergon.calculate_demand_fee(tariff, demand_kw, days, interval_time=interval_time)
    elif network == 'ausgrid':
        return ausgrid.calculate_demand_fee(tariff, demand_kw, days, interval_time=interval_time)
    elif network == 'evoenergy':
        # Placeholder for Evoenergy demand fee calculation
        return 0.0
    elif network == 'sapn':
        return sapower.calculate_demand_fee(tariff, demand_kw, days)
    elif network == 'tasnetworks':
        return tasnetworks.calculate_demand_fee(tariff, demand_kw, days)
    elif network == 'endeavour':
        return endeavour.calculate_demand_fee(tariff, demand_kw, days)
    elif network == 'victoria':
        return victoria.calculate_demand_fee(tariff, demand_kw, days)
    elif network == 'ausnet':
        return ausnet.calculate_demand_fee(tariff, demand_kw, days)
    elif network == 'essential':
        return essential.calculate_demand_fee(tariff, demand_kw, days)
    else:
        return 0.0


def estimate_demand_fee(interval_time, network, tariff, demand_kw):
    """
    Estimate the demand fee for a given network, tariff, interval time, and demand amount.

    Parameters:
    - interval_time (datetime): The interval time.
    - network (str): The name of the network (e.g., 'Energex', 'Ausgrid', 'Evoenergy').
    - tariff (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for some tariffs).

    Returns:
    - float: The estimated demand fee in dollars.
    """
    network = network.lower()

    if network == 'energex':
        return energex.estimate_demand_fee(interval_time, tariff, demand_kw)
    elif network == 'ergon':
        return ergon.estimate_demand_fee(interval_time, tariff, demand_kw)
    elif network == 'ausgrid':
        return ausgrid.estimate_demand_fee(interval_time, tariff, demand_kw)
    elif network == 'evoenergy':
        # Placeholder for Evoenergy demand fee estimation
        return 0.0
    elif network == 'sapn':
        return sapower.estimate_demand_fee(interval_time, tariff, demand_kw)
    elif network == 'tasnetworks':
        return tasnetworks.estimate_demand_fee(interval_time, tariff, demand_kw)
    elif network == 'endeavour':
        return endeavour.estimate_demand_fee(interval_time, tariff, demand_kw)
    elif network == 'victoria':
        return victoria.estimate_demand_fee(interval_time, tariff, demand_kw)
    elif network == 'ausnet':
        return ausnet.estimate_demand_fee(interval_time, tariff, demand_kw)
    elif network == 'essential':
        return essential.estimate_demand_fee(interval_time, tariff, demand_kw)
    else:
        return 0.0

def get_periods(network, tariff: str):
    """
    Get the periods for a given network and tariff.

    Parameter:
    - network (str): The name of the network (e.g., 'Energex', 'Ausgrid', 'Evoenergy').
    - tariff (str): The tariff code.

    Returns:
    - list: A list of periods for the given tariff.
    """
    network = network.lower()

    if network == 'energex':
        return energex.get_periods(tariff)
    elif network == 'ausgrid':
        return ausgrid.get_periods(tariff)
    elif network == 'ergon':
        return ausgrid.get_periods(tariff)
    elif network == 'evoenergy':
        return evoenergy.get_periods(tariff)
    elif network == 'sapn':
        return sapower.get_periods(tariff)
    elif network == 'tasnetworks':
        return tasnetworks.get_periods(tariff)
    elif network == 'endeavour':
        return endeavour.get_periods(tariff)
    elif network == 'essential':
        return essential.get_periods(tariff)
    elif network == 'victoria':
        return victoria.get_periods(tariff)
    elif network == 'jemena':
        return jemena.get_periods(tariff)
    elif network == 'powercor':
        return powercor.get_periods(tariff)
    elif network == 'united':
        return united.get_periods(tariff)
    elif network == 'ausnet':
        return ausnet.get_periods(tariff)
    else:
        return energex.get_periods(tariff)


def battery_tariffs(network, customer_type: str):
    """
    Get the battery tariffs for a given network and customer type.
    Parameters:
    - network (str): The name of the network (e.g., 'Energex', 'Ausgrid', 'Evoenergy').
    - customer_type (str): The customer type ('Residential' or 'Business').
    Returns:
    - dict: A dictionary with 'import' and 'export' tariff codes.
    """
    network = network.lower()

    if network == 'energex':
        return energex.battery_tariffs(customer_type)
    elif network == 'ausgrid':
        return ausgrid.battery_tariffs(customer_type)
    elif network == 'ergon':
        return ergon.battery_tariffs(customer_type)
    elif network == 'evoenergy':
        return evoenergy.battery_tariffs(customer_type)
    elif network == 'sapn':
        return sapower.battery_tariffs(customer_type)
    elif network == 'tasnetworks':
        return tasnetworks.battery_tariffs(customer_type)
    elif network == 'endeavour':
        return endeavour.battery_tariffs(customer_type)
    elif network == 'essential':
        return essential.battery_tariffs(customer_type)
    else:
        return energex.battery_tariffs(customer_type)
