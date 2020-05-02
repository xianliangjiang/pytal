from pytest import fixture


@fixture(scope='function')
def setup_region():
    return [{
    'GID_0': 'MWI',
    'GID_id': 'MWI.1.1.1_1',
    'mean_luminosity_km2': 26.736407691655717,
    'population': 10000,
    'area_km2': 2,
    'population_km2': 5000,
    'decile': 100,
    'geotype': 'urban',
    'demand_mbps_km2': 5000
    }]


@fixture(scope='function')
def setup_region_rural():
    return [{
    'GID_0': 'MWI',
    'GID_id': 'MWI.1.1.1_1',
    'mean_luminosity_km2': 26.736407691655717,
    'population': 10000,
    'area_km2': 2,
    'population_km2': 5000,
    'decile': 100,
    'geotype': 'rural'
    }]


@fixture(scope='function')
def setup_option():
    return {
        'scenario': 'S1_50_5_1',
        'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'
    }


@fixture(scope='function')
def setup_option_high():
    return {
        'scenario': 'S1_50_5_1',
        'strategy': '4G_epc_microwave_baseline_high_high_high'
    }


@fixture(scope='function')
def setup_global_parameters():
    return {
        'overbooking_factor': 100,
        'return_period': 2,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'sectorization': 3,
        'confidence': [1, 10, 50],
        'networks': 2,
        'cots_processing_split_urban': 2,
        'cots_processing_split_suburban': 4,
        'cots_processing_split_rural': 16,
        'io_n2_n3_split': 7,
        'low_latency_switch_split': 7,
        'rack_split': 7,
        'cloud_power_supply_converter_split': 7,
        'software_split': 7,
        'cloud_backhaul_split': 7,
    }


@fixture(scope='function')
def setup_country_parameters():
    return {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 15,
            'medium': 5,
            'low': 2,
        },
        # also GSMA, 2019 (same report as above)
        # smartphone pen was 10% in 2017, so assume 15% in 2020
        'smartphone_pen': 0.5,
        # Access Comm, Airtel, TNM
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'networks': 3,
        # https://en.wikipedia.org/wiki/List_of_LTE_networks_in_Africa
        'proportion_of_sites': 50,
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': 10,
                },
                {
                    'frequency': 3500,
                    'bandwidth': 50,
                },
                {
                    'frequency': 26000,
                    'bandwidth': 500,
                },
            ]
        },
        'financials': {
            'profit_margin': 20,
            'subsidy_low': 10,
            'subsidy_baseline': 25,
            'subsidy_high': 40,
            'spectrum_coverage_low_usd_mhz_pop': 0.25,
            'spectrum_capacity_low_usd_mhz_pop': 0.05,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.5,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'spectrum_coverage_high_usd_mhz_pop': 1,
            'spectrum_capacity_high_usd_mhz_pop': 0.2,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        }


@fixture(scope='function')
def setup_timesteps():
    return [
        2020,
        # 2021,
        # 2022,
        # 2023,
        # 2024,
        # 2025,
        # 2026,
        # 2027,
        # 2028,
        # 2029,
        # 2030
    ]


@fixture(scope='function')
def setup_penetration_lut():
    return {
        2020: 50,
        # 2021: 75,
    }


@fixture(scope='function')
def setup_costs():
    return {
        #all costs in $USD
        'single_sector_antenna': 1500,
        'single_remote_radio_unit': 4000,
        'io_fronthaul': 1500,
        'processing': 1500,
        'io_s1_x2': 1500,
        'control_unit': 1500,
        'cooling_fans': 250,
        'distributed_power_supply_converter': 250,
        'power_generator_battery_system': 5000,
        'bbu_cabinet': 500,
        'fiber_fronthaul_urban_m': 10,
        'fiber_fronthaul_suburban_m': 5,
        'fiber_fronthaul_rural_m': 2,
        'cots_processing': 500,
        'io_n2_n3': 1500,
        'low_latency_switch': 500,
        'rack': 500,
        'cloud_power_supply_converter': 1000,
        'software': 50,
        'tower': 10000,
        'civil_materials': 5000,
        'transportation': 5000,
        'installation': 5000,
        'site_rental_urban': 9600,
        'site_rental_suburban': 4000,
        'site_rental_rural': 2000,
        'router': 2000,
        'microwave_backhaul_small': 10000,
        'microwave_backhaul_medium': 20000,
        'microwave_backhaul_large': 40000,
        'fiber_backhaul_urban_m': 10,
        'fiber_backhaul_suburban_m': 5,
        'fiber_backhaul_rural_m': 2,
        'core_node_epc': 100000,
        'core_node_nsa': 150000,
        'core_node_sa': 200000,
        'core_edge': 20,
        'regional_node_epc': 100000,
        'regional_node_nsa': 150000,
        'regional_node_sa': 200000,
        'regional_edge': 10,
        'regional_node_lower_epc': 10000,
        'regional_node_lower_nsa': 10000,
        'regional_node_lower_sa': 10000,
    }


# @fixture(scope='function')
# def setup_costs():
#     return {
#         #all costs in $USD
#         'single_sector_antenna': 1500,
#         'single_remote_radio_unit': 4000,
#         'io_fronthaul': 1500,
#         'processing': 1500,
#         'io_s1_x2': 1500,
#         'control_unit': 1500,
#         'cooling_fans': 250,
#         'distributed_power_supply_converter': 250,
#         'power_generator_battery_system': 5000,
#         'bbu_cabinet': 500,
#         'fiber_fronthaul_urban_m': 10,
#         'fiber_fronthaul_suburban_m': 5,
#         'fiber_fronthaul_rural_m': 2,
#         'cots_processing': 500,
#         'io_n2_n3': 1500,
#         'low_latency_switch': 500,
#         'rack': 500,
#         'cloud_power_supply_converter': 1000,
#         'software': 50,
#         'tower': 10000,
#         'civil_materials': 5000,
#         'transportation': 5000,
#         'installation': 5000,
#         'site_rental_urban': 9600,
#         'site_rental_suburban': 4000,
#         'site_rental_rural': 2000,
#         'router': 2000,
#         'microwave_backhaul_small': 5000,
#         'microwave_backhaul_medium': 10000,
#         'microwave_backhaul_large': 15000,
#         'fiber_backhaul_urban_m': 25,
#         'fiber_backhaul_suburban_m': 15,
#         'fiber_backhaul_rural_m': 10,
#         'core_node_epc': 50000,
#         'core_node_nsa': 50000,
#         'core_node_sa': 50000,
#         'core_edge': 10,
#         'regional_node_epc': 25000,
#         'regional_node_nsa': 25000,
#         'regional_node_sa': 25000,
#         'regional_edge': 5,
#         'regional_node_lower_epc': 5000,
#         'regional_node_lower_nsa': 5000,
#         'regional_node_lower_sa': 10000,
#     }


@fixture(scope='function')
def setup_lookup():
    return {
        ('urban', 'macro', '800', '4G', '50'): [
            (0.01, 1),
            (0.02, 2),
            (0.05, 5),
            (0.15, 15),
            (2, 100)
        ],
        ('urban', 'macro', '1800', '4G', '50'): [
            (0.01, 5),
            (0.02, 10),
            (0.05, 20),
            (0.15, 40),
            (2, 1000)
        ],

    }


@fixture(scope='function')
def setup_ci():
    return 50


@fixture(scope='function')
def setup_backhaul_lut():
    return [
        {'node_density_km2': 0.00000001, 'average_distance_m': 5242880},
        {'node_density_km2': 0.0000001, 'average_distance_m': 1638400},
        {'node_density_km2': 0.000001, 'average_distance_m': 512000},
        {'node_density_km2': 0.00001, 'average_distance_m': 160000},
        {'node_density_km2': 0.0001, 'average_distance_m': 50000},
        {'node_density_km2': 0.001, 'average_distance_m': 16000},
        {'node_density_km2': 0.01, 'average_distance_m': 5000},
        {'node_density_km2': 0.1, 'average_distance_m': 1500},
        {'node_density_km2': 1.0,	'average_distance_m': 500},
    ]


@fixture(scope='function')
def setup_core_lut():
    return {
        'core_edge': {
            'MWI.1.1.1_1': 1000
        },
        'core_node': {
            'MWI.1.1.1_1': 2
        },
        'regional_edge': {
            'MWI.1.1.1_1': 1000
        },
        'regional_node': {
            'MWI.1.1.1_1': 2
        },
    }
