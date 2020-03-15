"""
Generate data for modeling.

Written by Ed Oughton.

Winter 2020

"""
import os
import csv
import configparser
import pandas as pd
import geopandas
from tqdm import tqdm
from collections import OrderedDict

from options import OPTIONS, COUNTRY_PARAMETERS
from pytal.demand import estimate_demand
from pytal.supply import estimate_supply

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def load_regions(path):
    """
    Load country regions.

    """
    regions = pd.read_csv(path)

    try:
        #[0,10,20,30,40,50,60,70,80,90,100] #labels=[100,90,80,70,60,50,40,30,20,10,0],
        regions['decile'] = pd.qcut(regions['population'], q=11, precision=0,
                            labels=[0,10,20,30,40,50,60,70,80,90,100], duplicates='drop')
    except:
        #[0,25,50,75,100] #labels=[100, 75, 50, 25, 0],
        regions['decile'] = pd.qcut(regions['population'], q=5, precision=0,
                            labels=[0,25,50,75,100], duplicates='drop')

    regions['geotype'] = regions.apply(define_geotype, axis=1)

    return regions


def define_geotype(x):
    """
    Allocate geotype given a specific population density.

    """
    if x['population_km2'] > 2000:
        return 'urban'
    elif x['population_km2'] > 1500:
        return 'suburban 1'
    elif x['population_km2'] > 1000:
        return 'suburban 2'
    elif x['population_km2'] > 500:
        return 'rural 1'
    elif x['population_km2'] > 100:
        return 'rural 2'
    elif x['population_km2'] > 50:
        return 'rural 3'
    elif x['population_km2'] > 10:
        return 'rural 4'
    else:
        return 'rural 5'


def read_capacity_lookup(path):
    """

    """
    capacity_lookup_table = {}

    with open(path, 'r') as capacity_lookup_file:
        reader = csv.DictReader(capacity_lookup_file)
        for row in reader:
            if float(row["capacity_mbps_km2_50ci"]) <= 0:
                continue
            environment = row["environment"].lower()
            ant_type = row["ant_type"]
            frequency_GHz = str(int(float(row["frequency_GHz"]) * 1e3))
            bandwidth_MHz = str(row["bandwidth_MHz"])
            generation = str(row["generation"])

            if (environment, ant_type, frequency_GHz, bandwidth_MHz, generation) \
                not in capacity_lookup_table:
                capacity_lookup_table[(
                    environment, ant_type, frequency_GHz, bandwidth_MHz, generation)
                    ] = []

            capacity_lookup_table[(
                environment,
                ant_type,
                frequency_GHz,
                bandwidth_MHz,
                generation)].append((
                    float(row["sites_per_km2"]),
                    {
                        'capacity_mbps_km2_1ci': float(row["capacity_mbps_km2_1ci"]),
                        'capacity_mbps_km2_10ci': float(row["capacity_mbps_km2_10ci"]),
                        'capacity_mbps_km2_50ci': float(row["capacity_mbps_km2_50ci"]),
                        'capacity_mbps_km2_90ci': float(row["capacity_mbps_km2_90ci"]),
                        'capacity_mbps_km2_99ci': float(row["capacity_mbps_km2_99ci"]),
                    }
                ))

        for key, value_list in capacity_lookup_table.items():
            value_list.sort(key=lambda tup: tup[0])

    return capacity_lookup_table


def lookup_cost(lookup, strategy, environment):
    """
    Find cost of network.

    """
    if (strategy, environment) not in lookup:
        raise KeyError("Combination %s not found in lookup table",
                       (strategy, environment))

    density_capacities = lookup[
        (strategy, environment)
    ]

    return density_capacities


def find_country_list(continent_list):
    """

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = geopandas.read_file(path_processed)

    subset = countries.loc[countries['continent'].isin(continent_list)]

    country_list = []
    country_regional_levels = []

    for name in subset.GID_0.unique():

        country_list.append(name)

        if name in ['ESH', 'LBY', 'LSO'] :
            regional_level =  1
        else:
            regional_level = 2

        country_regional_levels.append({
            'country': name,
            'regional_level': regional_level,
        })

    return country_list, country_regional_levels


def load_penetration(path):
    """
    Load penetration forecast.

    """
    output = {}

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            output[int(row['year'])] = float(row['penetration'])

    return output


def csv_writer(data, directory, filename):
    """
    Write data to a CSV file path.
    Parameters
    ----------
    data : list of dicts
        Data to be written.
    directory : string
        Path to export folder
    filename : string
        Desired filename.
    """
    # Create path
    if not os.path.exists(directory):
        os.makedirs(directory)

    fieldnames = []
    for name, value in data[0].items():
        fieldnames.append(name)

    with open(os.path.join(directory, filename), 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames, lineterminator = '\n')
        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':

    BASE_YEAR = 2020
    END_YEAR = 2030
    TIMESTEP_INCREMENT = 1
    TIMESTEPS = [t for t in range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)]

    COSTS = {
        #all costs in $USD
        'single_sector_antenna': 1500,
        'single_remote_radio_unit': 4000,
        'single_baseband_unit': 10000,
        'tower': 10000,
        'civil_materials': 5000,
        'transportation': 10000,
        'installation': 5000,
        'site_rental': 9600,
        'power_generator_battery_system': 5000,
        'high_speed_backhaul_hub': 15000,
        'router': 2000,
        'microwave_backhaul_urban': 10000,
        'microwave_backhaul_suburban': 15000,
        'microwave_backhaul_rural': 25000,
        'fiber_backhaul_urban': 20000,
        'fiber_backhaul_suburban': 35000,
        'fiber_backhaul_rural': 60000,
    }

    GLOBAL_PARAMETERS = {
        'overbooking_factor': 50,
        'return_period': 10,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'sectorization': 3,
        'confidence': [1, 10, 50]
        }

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency.csv')
    lookup = read_capacity_lookup(path)

    # country_list, country_regional_levels = find_country_list(['Africa', 'South America'])
    country_list = [
        # 'UGA',
        # 'ETH',
        # 'BGD',
        # 'PER',
        'MWI',
        # 'ZAF'
    ]

    decision_options = [
        'technology_options',
        # 'business_model_options'
    ]

    for decision_option in decision_options:

        options = OPTIONS[decision_option]

        data_to_write = []

        for country in country_list:

            country_parameters = COUNTRY_PARAMETERS[country]

            folder = os.path.join(DATA_INTERMEDIATE, country, 'subscriptions')
            filename = 'subs_forecast.csv'
            penetration_lut = load_penetration(os.path.join(folder, filename))

            print('-----')
            print('Working on {} in {}'.format(decision_option, country))
            print(' ')

            for option in options:

                if not option['strategy'] == '4G_epc_microwave_baseline':
                    continue

                print('Working on {} and {}'.format(option['scenario'], option['strategy']))

                # try:
                path = os.path.join(DATA_INTERMEDIATE, country, 'regional_data.csv')
                data = load_regions(path)[:1]

                data = data.to_dict('records')
                print(data)
                data = estimate_demand(
                    data,
                    option,
                    GLOBAL_PARAMETERS,
                    country_parameters,
                    TIMESTEPS,
                    penetration_lut
                )

                data = estimate_supply(
                    data,
                    lookup,
                    option,
                    GLOBAL_PARAMETERS,
                    country_parameters,
                    COSTS
                )

                data_to_write = data_to_write + data

                # except:
                #     print('Unable to process {} for {} and {}'.format(
                #         country, option['scenario'], option['strategy']))
                #     pass

        path_results = os.path.join(BASE_PATH, '..', 'results')

        csv_writer(data_to_write, path_results, 'results_{}_{}.csv'.format(
            decision_option, len(country_list)))
