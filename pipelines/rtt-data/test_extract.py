"""Unit testing for the functions in extract.py."""
from unittest.mock import patch

from extract import get_station_name, get_trains, extract_train_info, make_train_info_list

### Testing get_station_name() ###


def test_get_station_name_returns_name_when_location_is_present():
    """Tests that get_station_name correctly returns the station name."""
    response = {"location": {"name": "test"}}
    assert get_station_name(response) == "test"


def test_get_station_name_returns_none_when_name_is_none():
    """Tests that get_station_name returns None when station name is missing."""
    response = {"location": {}}
    assert get_station_name(response) is None


def test_get_station_name_returns_none_when_location_is_none():
    """Tests that get_station_name returns None when location is None."""
    response = {"location": None}
    assert get_station_name(response) is None


@patch('extract.logger')
def test_logs_info_when_location_is_present(mock_logger):
    """Tests that the info log is correctly called."""
    response = {'location': {'name': 'test'}}
    get_station_name(response)
    mock_logger.info.assert_called_once_with(
        "Extracted station name: %s", 'test')


@patch('extract.logger')
def test_logs_warning_when_location_is_missing(mock_logger):
    """Tests that the warning log is correctly called."""
    response = {}
    get_station_name(response)
    mock_logger.warning.assert_called_once_with(
        "No location data found in response.")

### Testing get_trains() ###


def test_get_trains_returns_empty_list_when_no_services():
    """Tests that an empty list is returned when response is empty."""
    response = {}
    assert get_trains(response) == []


def test_get_trains_returns_services_when_present():
    """Tests that get_trains correctly returns services."""
    response = {'services': [{'service': 1}, {'service': 2}]}
    assert get_trains(response) == [{'service': 1}, {'service': 2}]


@patch('extract.logger')
def test_logs_info_when_services_are_retrieved(mock_logger):
    """Tests that the info log is correctly called."""
    response = {'services': [{'service': 1}]}
    get_trains(response)
    mock_logger.info.assert_called_once_with(
        "Train services successfully retrieved from API.")


@patch('extract.logger')
def test_logs_info_when_no_services_in_response(mock_logger):
    """Tests that the debug log is correctly called."""
    response = {}
    get_trains(response)
    mock_logger.debug.assert_called_once_with("No services to retrieve.")

### Testing extract_train_info() ###


def test_extract_train_info_with_valid_service():
    """Tests that extract_train_info correctly processes response data."""
    service = {
        'serviceUid': '123',
        'trainIdentity': '234',
        'atocName': 'test',
        'runDate': '0000-00-00',
        'serviceType': 'train',
        'locationDetail': {
            'origin': [{'description': 'arr_description'}],
            'destination': [{'description': 'des_description'}],
            'gbttBookedArrival': '1000',
            'realtimeArrival': '2000',
            'gbttBookedDeparture': '3000',
            'realtimeDeparture': '4000',
            'platform': '1',
            'platformChanged': False
        }
    }

    name = 'station'
    crs = 'ABC'
    expected = {
        'service_uid': '123',
        'train_identity': '234',
        'station_name': 'station',
        'station_crs': 'ABC',
        'origin_name': 'arr_description',
        'destination_name': 'des_description',
        'scheduled_arr_time': '1000',
        'actual_arr_time': '2000',
        'scheduled_dep_time': '3000',
        'actual_dep_time': '4000',
        'operator_name': 'test',
        'service_date': '0000-00-00',
        'platform': '1',
        'platform_changed': False,
        'cancelled': False,
        'cancel_reason': None,
        'service_type': 'train'
    }
    result = extract_train_info(service, name, crs)
    assert result == expected


def test_extract_train_info_with_cancelled_service():
    """Tests that extract_train_info correctly processes cancellation data."""
    service = {
        'serviceUid': '123',
        'trainIdentity': '234',
        'atocName': 'test',
        'serviceType': 'train',
        'runDate': '0000-00-00',
        'locationDetail': {
            'origin': [{'description': 'arr_description'}],
            'destination': [{'description': 'des_description'}],
            'gbttBookedArrival': '1000',
            'realtimeArrival': '2000',
            'gbttBookedDeparture': '3000',
            'realtimeDeparture': '4000',
            'platform': '1',
            'platformChanged': False,
            'cancelReasonCode': 'abc',
            'cancelReasonLongText': 'cancelled'
        }
    }

    name = 'station'
    crs = 'ABC'
    expected = {
        'service_uid': '123',
        'train_identity': '234',
        'station_name': 'station',
        'station_crs': 'ABC',
        'origin_name': 'arr_description',
        'destination_name': 'des_description',
        'scheduled_arr_time': '1000',
        'actual_arr_time': '2000',
        'scheduled_dep_time': '3000',
        'actual_dep_time': '4000',
        'operator_name': 'test',
        'service_date': '0000-00-00',
        'platform': '1',
        'platform_changed': False,
        'cancelled': True,
        'cancel_reason': 'cancelled',
        'service_type': 'train'
    }
    result = extract_train_info(service, name, crs)
    assert result == expected


@patch('extract.logger')
def test_logs_info_when_extracting_train_info_initial(mock_logger):
    """Tests that the initial info log is correctly called."""
    service = {'serviceUid': '123'}
    name = 'station1'
    crs = 'ABC'
    extract_train_info(service, name, crs)
    mock_logger.info.assert_any_call(
        "Extracting train info for services from %s", "ABC")


@patch('extract.logger')
def test_logs_info_when_extracting_train_info(mock_logger):
    """Tests that the info log is correctly called."""
    service = {'serviceUid': '123'}
    name = 'station1'
    crs = 'ABC'
    extract_train_info(service, name, crs)
    mock_logger.info.assert_any_call(
        "Extracted train info for service '%s'", '123')

### Testing make_train_info_list() ###


def test_make_train_info_list():
    """Tests that make_train_info_list returns correct data."""
    train_list = [{'serviceUid': '123'}, {'serviceUid': '456'}]
    name = 'station1'
    crs = 'st1'

    with patch('extract.extract_train_info') as mock_extract_train_info:
        mock_extract_train_info.side_effect = [{'serviceUid': '123', 'station_name': 'Station A'},
                                               {'serviceUid': '456',
                                                   'station_name': 'Station A'}
                                               ]
        result = make_train_info_list(train_list, name, crs)

        assert len(result) == 2
        assert result[0]['serviceUid'] == '123'
        assert result[1]['serviceUid'] == '456'
