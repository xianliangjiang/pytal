"""
Assessment Module

Written by Ed Oughton.

Winter 2020

"""

def assess(country, regions, option, global_parameters, country_parameters, costs):
    """
    For each region, assess the viability level.

    Parameters
    ----------
    country : dict
        Country information.
    regions : list of dicts
        Data for all regions (one dict per region).
    option : dict
        Contains the scenario and strategy. The strategy string controls
        the strategy variants being testes in the model and is defined based
        on the type of technology generation, core and backhaul, and the level
        of sharing, subsidy, spectrum and tax.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.
    costs : dict
        All equipment costs.

    Returns
    -------
    output : list of dicts
        Contains all output data (one dict per region).

    """
    interim = []

    strategy = option['strategy']
    available_for_cross_subsidy = 0

    for region in regions:

        # add administration cost
        region = get_administration_cost(region, country_parameters)

        # npv spectrum cost
        region['spectrum_cost'] = get_spectrum_costs(region, option['strategy'],
            global_parameters, country_parameters)

        #tax on investment
        region['tax'] = calculate_tax(region, strategy, country_parameters)

        #profit margin value calculated on all costs + taxes
        region['profit_margin'] = calculate_profit(region, country_parameters)

        region['total_cost'] = (
            region['network_cost'] +
            region['administration'] +
            region['spectrum_cost'] +
            region['tax'] +
            region['profit_margin']
        )

        #avoid zero division
        if region['total_cost'] > 0 and region['smartphones_on_network'] > 0:
            region['cost_per_sp_user'] = (
                region['total_cost'] / region['smartphones_on_network'])
        else:
            region['cost_per_sp_user'] = 0

        #apply cross subsidy
        region = allocate_available_excess(region)
        available_for_cross_subsidy += region['available_cross_subsidy']

        interim.append(region)

    interim = sorted(interim, key=lambda k: k['deficit'], reverse=False)

    output = []

    for region in interim:

        region, available_for_cross_subsidy = estimate_subsidies(
            region, available_for_cross_subsidy)

        output.append(region)

    return output


def get_administration_cost(region, country_parameters):
    """
    There is an administration cost to deploying and operating all assets.

    Parameters
    ----------
    regions : list of dicts
        Data for all regions (one dict per region).
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    region : dict
        Contains all regional data.

    """
    region['administration'] = (
        region['network_cost'] *
        (country_parameters['financials']['administration_percentage_of_network_cost'] /
        100))

    return region


def get_spectrum_costs(region, strategy, global_parameters, country_parameters):
    """
    Calculate spectrum costs.

    Parameters
    ----------
    region : dict
        Contains all regional data.
    strategy : dict
        Controls the strategy variants being tested in the model and is
        defined based on the type of technology generation, core and
        backhaul, and the level of sharing, subsidy, spectrum and tax.
        of sharing, subsidy, spectrum and tax.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.

    Output
    ------
    region : dict
        Contains all regional data.

    """
    population = int(round(region['population']))
    frequencies = country_parameters['frequencies']
    generation = strategy.split('_')[0]
    frequencies = frequencies[generation]

    spectrum_cost = strategy.split('_')[5]

    coverage_spectrum_cost = 'spectrum_coverage_baseline_usd_mhz_pop'
    capacity_spectrum_cost = 'spectrum_capacity_baseline_usd_mhz_pop'

    coverage_cost_usd_mhz_pop = country_parameters['financials'][coverage_spectrum_cost]
    capacity_cost_usd_mhz_pop = country_parameters['financials'][capacity_spectrum_cost]

    if spectrum_cost == 'low':
        coverage_cost_usd_mhz_pop = (
            coverage_cost_usd_mhz_pop *
            (country_parameters['financials']['spectrum_cost_low'] /100))
        capacity_cost_usd_mhz_pop = (
            capacity_cost_usd_mhz_pop *
            (country_parameters['financials']['spectrum_cost_low'] /100))

    if spectrum_cost == 'high':
        coverage_cost_usd_mhz_pop = (
            coverage_cost_usd_mhz_pop *
            1 + (country_parameters['financials']['spectrum_cost_high'] / 100))
        capacity_cost_usd_mhz_pop = (
            capacity_cost_usd_mhz_pop *
            1 + (country_parameters['financials']['spectrum_cost_high'] / 100))

    all_costs = []

    for frequency in frequencies:

        channel_number = int(frequency['bandwidth'].split('x')[0])
        channel_bandwidth = int(frequency['bandwidth'].split('x')[1])
        bandwidth_total = channel_number * channel_bandwidth

        if frequency['frequency'] < 1000:
            cost = (
                coverage_cost_usd_mhz_pop * bandwidth_total *
                population)
            all_costs.append(cost)
        else:
            cost = (
                capacity_cost_usd_mhz_pop * bandwidth_total *
                population)
            all_costs.append(cost)

    return sum(all_costs)


def calculate_tax(region, strategy, country_parameters):
    """
    Estimate the quantity of tax.

    Parameters
    ----------
    region : dict
        Contains all regional data.
    strategy : dict
        Controls the strategy variants being tested in the model and is
        defined based on the type of technology generation, core and
        backhaul, and the level of sharing, subsidy, spectrum and tax.
        of sharing, subsidy, spectrum and tax.
    country_parameters : dict
        All country specific parameters.

    Return
    ------
    tax : int
        Quantity of tax.

    """
    tax_rate = strategy.split('_')[6]
    tax_rate = 'tax_{}'.format(tax_rate)

    tax_rate = country_parameters['financials'][tax_rate]

    investment = region['network_cost']

    tax = investment * (tax_rate / 100)

    return int(tax)


def calculate_profit(region, country_parameters):
    """
    Estimate the quantity of profit.

    Parameters
    ----------
    region : dict
        Contains all regional data.
    country_parameters : dict
        All country specific parameters.

    Return
    ------
    profit : int
        Quantity of profit.

    """
    investment = (
        region['network_cost'] +
        region['spectrum_cost'] +
        region['tax']
    )

    profit = investment * (country_parameters['financials']['profit_margin'] / 100)

    return profit


def allocate_available_excess(region):
    """
    Allocate available excess capital (if any).

    Parameters
    ----------
    region : dict
        Contains all regional data.

    Output
    ------
    region : dict
        Contains all regional data.

    """
    difference = region['total_revenue'] - region['total_cost']

    if difference > 0:
        region['available_cross_subsidy'] = difference
        region['deficit'] = 0
    else:
        region['available_cross_subsidy'] = 0
        region['deficit'] = abs(difference)

    return region


def estimate_subsidies(region, available_for_cross_subsidy):
    """
    Estimates either the contribution to cross-subsidies, or the
    quantity of subsidy required.

    Parameters
    ----------
    region : dict
        Contains all regional data.
    available_for_cross_subsidy : int
        The amount of capital available for cross-subsidization.

    Output
    ------
    region : dict
        Contains all regional data.
    available_for_cross_subsidy : int
        The amount of capital available for cross-subsidization.

    """
    if region['deficit'] > 0:

        if available_for_cross_subsidy >= region['deficit']:
            region['used_cross_subsidy'] = region['deficit']
            available_for_cross_subsidy -= region['deficit']
        elif 0 < available_for_cross_subsidy < region['deficit']:
            region['used_cross_subsidy'] = available_for_cross_subsidy
            available_for_cross_subsidy = 0
        else:
            region['used_cross_subsidy'] = 0

    else:
        region['used_cross_subsidy'] = 0

    required_state_subsidy = (region['total_cost'] -
        (region['total_revenue'] + region['used_cross_subsidy']))

    if required_state_subsidy > 0:
        region['required_state_subsidy'] = required_state_subsidy
    else:
        region['required_state_subsidy'] = 0

    return region, available_for_cross_subsidy
