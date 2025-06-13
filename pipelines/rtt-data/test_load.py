"""Test for load script that loads data to the RDS."""

from unittest.mock import patch

from load import (get_connection)


def test_get_db_connection_called_once():
    """Test that connect is called once when get_connection is invoked."""
    with patch("load.connect") as mock_connect, \
            patch.dict("os.environ", {
                "DB_USER": "USER",
                "DB_PASSWORD": "PASSWORD",
                "DB_HOST": "HOST",
                "DB_PORT": "PORT",
                "DB_NAME": "NAME"
            }):
        get_connection()
        mock_connect.assert_called_once()
