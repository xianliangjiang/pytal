"""
Cost module
Author: Edward Oughton
Date: April 2019

Based off the repo pysim5g:
https://github.com/edwardoughton/pysim5g

"""
import math


def find_single_network_cost(country, region, sites_per_km2, strategy,
    geotype, costs, global_parameters, country_parameters, backhaul_lut):
    """
    Calculates the annual total cost using capex and opex.

    Parameters
    ----------
    region : dict
        The region being assessed and all associated parameters.
    sites_per_km2 : int
        The density of sites.
    strategy : str
        Infrastructure sharing strategy.
    costs : dict
        Contains the costs of each necessary equipment item.
    global_parameters : dict
        Contains all global_parameters.
    country_parameters :
        ???
    backhaul_lut : dict
        Backhaul distance by region.

    Returns
    -------
    output : list of dicts
        Contains a list of costs, with affliated discounted capex and
        opex costs.

    """

    generation, core, backhaul, sharing = get_strategy_options(strategy)

    cost_breakdown = get_costs(country, region, generation, core, backhaul, sharing,
        geotype, costs, sites_per_km2, global_parameters, country_parameters, backhaul_lut)

    network_cost_km2 = 0
    for key, value in cost_breakdown.items():
        network_cost_km2 += value

    cost_breakdown['network_cost_km2'] = network_cost_km2

    cost_breakdown['total_network_cost'] = network_cost_km2 * region['area_km2']

    return cost_breakdown


def get_costs(country, region, generation, core, backhaul, sharing, geotype, costs,
    sites_per_km2, global_parameters, country_parameters, backhaul_lut):

    if sharing == 'baseline':
        costs = baseline(country, region, generation, core, backhaul, sharing,
        geotype, costs, sites_per_km2, global_parameters, country_parameters, backhaul_lut)

    if sharing == 'passive':
        costs = passive(country, region, generation, core, backhaul, sharing,
        geotype, costs, sites_per_km2, global_parameters, country_parameters, backhaul_lut)

    if sharing == 'active':
        costs = active(country, region, generation, core, backhaul, sharing,
        geotype, costs, sites_per_km2, global_parameters, country_parameters, backhaul_lut)

    return costs


def baseline(country, region, generation, core, backhaul, sharing,
    geotype, costs, sites_per_km2, global_parameters, country_parameters, backhaul_lut):
    """
    No sharing takes place.
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    backhaul_cost = get_backhaul_costs(country, region, backhaul, geotype, costs, backhaul_lut)

    cost_breakdown = {
        'single_sector_antenna': (
            discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters) *
            sites_per_km2
        ),
        'tower': (
            costs['tower'] * sites_per_km2
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2
        ),
        'installation': (
            costs['installation'] * sites_per_km2
        ),
        'site_rental': (
            discount_opex(costs['site_rental'], global_parameters) * sites_per_km2
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'],
            global_parameters) *
            sites_per_km2
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], global_parameters) *
            sites_per_km2
        ),
        'router': (
            discount_capex_and_opex(costs['router'], global_parameters) * sites_per_km2
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(backhaul_cost, global_parameters) * sites_per_km2
        )
    }

    return cost_breakdown


def passive(country, region, generation, core, backhaul, sharing, geotype, costs,
    sites_per_km2, global_parameters, country_parameters, backhaul_lut):
    """
    Sharing of:
        - Mast
        - Site compound

    """
    backhaul_cost = get_backhaul_costs(country, region, backhaul, geotype, costs, backhaul_lut)

    cost_breakdown = {
        'single_sector_antenna': (
            discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters) *
            sites_per_km2
        ),
        'tower': (
            costs['tower'] * sites_per_km2 / global_parameters['networks']
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2 / global_parameters['networks']
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2 / global_parameters['networks']
        ),
        'installation': (
            costs['installation'] * sites_per_km2 / global_parameters['networks']
        ),
        'site_rental': (
            discount_opex(costs['site_rental'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'router': (
            discount_capex_and_opex(costs['router'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(backhaul_cost, global_parameters) *
            sites_per_km2 / global_parameters['networks']
        )
    }

    return cost_breakdown


def active(country, region, generation, core, backhaul, sharing, geotype, costs,
    sites_per_km2, global_parameters, country_parameters, backhaul_lut):
    """
    Sharing of:
        - RAN
        - Mast
        - Site compound

    """
    backhaul_cost = get_backhaul_costs(country, region, backhaul, geotype, costs, backhaul_lut)

    cost_breakdown = {
        'single_sector_antenna': (
            discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2 /
            global_parameters['networks']
        ),
        'single_remote_radio_unit': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2 /
            global_parameters['networks']
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'tower': (
            costs['tower'] *
            sites_per_km2 / global_parameters['networks']
        ),
        'civil_materials': (
            costs['civil_materials'] *
            sites_per_km2 / global_parameters['networks']
        ),
        'transportation': (
            costs['transportation'] *
            sites_per_km2 / global_parameters['networks']
        ),
        'installation': (
            costs['installation'] *
            sites_per_km2 / global_parameters['networks']
        ),
        'site_rental': (
            discount_opex(costs['site_rental'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'router': (
            discount_capex_and_opex(costs['router'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(backhaul_cost, global_parameters) *
            sites_per_km2 / global_parameters['networks']
        )
    }

    return cost_breakdown


def get_strategy_options(strategy):

    #strategy is 'generation_core_backhaul_sharing'
    generation = strategy.split('_')[0]
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    return generation, core, backhaul, sharing


def get_backhaul_costs(country, region, backhaul, geotype, costs, backhaul_lut):
    """
    Calculate backhaul costs.

    """
    distance_m = backhaul_lut[region['GID_id']]

    if backhaul == 'microwave':
        if distance_m < 2e4:
            tech = '{}_backhaul_{}'.format(backhaul, 'small')
            cost = costs[tech]
        elif 2e4 < distance_m < 4e4:
            tech = '{}_backhaul_{}'.format(backhaul, 'medium')
            cost = costs[tech]
        else:
            tech = '{}_backhaul_{}'.format(backhaul, 'large')
            cost = costs[tech]

    if backhaul == 'fiber':
        tech = '{}_backhaul_{}'.format(backhaul, geotype)
        cost_per_meter = costs[tech]
        cost = cost_per_meter * distance_m

    return cost


def discount_capex_and_opex(capex, global_parameters):
    """
    Discount costs based on return period.

    Parameters
    ----------
    cost : float
        Financial cost.
    global_parameters : dict
        All global model parameters.

    Returns
    -------
    discounted_cost : float
        The discounted cost over the desired time period.

    """
    return_period = global_parameters['return_period']
    discount_rate = global_parameters['discount_rate'] / 100

    costs_over_time_period = []

    costs_over_time_period.append(capex)

    opex = round(capex * (global_parameters['opex_percentage_of_capex'] / 100))

    for i in range(0, return_period):
        costs_over_time_period.append(
            opex / (1 + discount_rate)**i
        )

    discounted_cost = sum(costs_over_time_period)

    return discounted_cost


def discount_opex(opex, global_parameters):
    """
    Discount opex based on return period.

    """
    return_period = global_parameters['return_period']
    discount_rate = global_parameters['discount_rate'] / 100

    costs_over_time_period = []

    for i in range(0, return_period):
        costs_over_time_period.append(
            opex / (1 + discount_rate)**i
        )

    discounted_cost = sum(costs_over_time_period)

    return discounted_cost
