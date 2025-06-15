"""Fixtures for testing report files."""

import datetime

from pytest import fixture
from psycopg2.extras import RealDictRow


@fixture
def test_valid_past_day_data():
    """List of dictionaries with valid data for get_days_data_per_station function."""
    return [
        RealDictRow({
            'train_stop_id': 108,
            'train_service_id': 65,
            'station_id': 11,
            'scheduled_arr_time': datetime.time(21, 20),
            'actual_arr_time': datetime.time(21, 18),
            'scheduled_dep_time': datetime.time(21, 21),
            'actual_dep_time': datetime.time(21, 21),
            'platform': '2',
            'platform_changed': False,
            'station_name': 'Didcot Parkway',
            'station_crs': 'DID',
            'service_uid': 'G04992',
            'train_identity': '1L90',
            'service_date': datetime.date(2025, 6, 14),
            'route_id': 9,
            'cancellation_id': 13,
            'reason': 'a problem with the train'
        }),
        RealDictRow({
            'train_stop_id': 119,
            'train_service_id': 73,
            'station_id': 11,
            'scheduled_arr_time': datetime.time(22, 20),
            'actual_arr_time': datetime.time(22, 18),
            'scheduled_dep_time': datetime.time(23, 45),
            'actual_dep_time': datetime.time(23, 45),
            'platform': '5',
            'platform_changed': False,
            'station_name': 'Didcot Parkway',
            'station_crs': 'DID',
            'service_uid': 'G05996',
            'train_identity': '2P86',
            'service_date': datetime.date(2025, 6, 14),
            'route_id': 6,
            'cancellation_id': None,
            'reason': None
        }),
        RealDictRow({
            'train_stop_id': 20,
            'train_service_id': 27,
            'station_id': 11,
            'scheduled_arr_time': datetime.time(16, 26),
            'actual_arr_time': datetime.time(16, 35),
            'scheduled_dep_time': datetime.time(17, 8),
            'actual_dep_time': datetime.time(17, 15),
            'platform': '5', 'platform_changed': False,
            'station_name': 'Didcot Parkway',
            'station_crs': 'DID',
            'service_uid': 'G05985',
            'train_identity': '2P61',
            'service_date': datetime.date(2025, 6, 14),
            'route_id': 6,
            'cancellation_id': None,
            'reason': None
        }),
        RealDictRow({
            'train_stop_id': 25,
            'train_service_id': 29,
            'station_id': 11,
            'scheduled_arr_time': datetime.time(17, 20),
            'actual_arr_time': datetime.time(17, 25),
            'scheduled_dep_time': datetime.time(18, 38),
            'actual_dep_time': datetime.time(18, 38),
            'platform': '5',
            'platform_changed': False,
            'station_name': 'Didcot Parkway',
            'station_crs': 'DID',
            'service_uid': 'G05988',
            'train_identity': '2P67',
            'service_date': datetime.date(2025, 6, 14),
            'route_id': 6,
            'cancellation_id': None,
            'reason': None
        })
    ]
