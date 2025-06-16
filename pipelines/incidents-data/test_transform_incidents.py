"""Tests for extract.py"""

import pytest

from transform_incidents import (is_paddington_to_bristol)

# Test is_paddington_to_bristol


@pytest.mark.parametrize("text,expected", [
    ("between London Paddington and Bristol Temple Meads", True),
    ("Between London Paddington and Reading / Bristol Temple Meads / Cheltenham", True),
    ("between Reading and Bristol Temple Meads", False),
    ("Paddington to Bristol", False),
    ("from london paddington to bristol temple meads", True)
])
def test_is_paddington_to_bristol_valid_input(text, expected):
    """Test that it correctly validates a paddington -> bristol line."""
    assert is_paddington_to_bristol(text) == expected
