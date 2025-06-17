"""Tests for transform_incidents.py"""

import pytest
import pandas as pd

from transform_incidents import (is_paddington_to_bristol, transform)

# Test is_paddington_to_bristol


@pytest.mark.parametrize("text,expected", [
    ("between London Paddington and Bristol Temple Meads", True),
    ("Between London Paddington and Reading / Bristol Temple Meads / Cheltenham", True),
    ("between Reading and Bristol Temple Meads", False),
    ("Paddington to Bristol", False),
    ("from london paddington to bristol temple meads", True),
    ("from londong paddington to reading", False),
    ("From London Paddington to Reading / Bristol Temple Meads / Cheltenham", True),
])
def test_is_paddington_to_bristol_valid_input(text, expected):
    """Test that it correctly validates a paddington -> bristol line."""
    assert is_paddington_to_bristol(text) == expected


# Test transform


def test_transform_filters_correctly(sample_extracted_data):
    """Test that only Paddington to Bristol incidents are kept."""
    transformed = transform(sample_extracted_data)
    assert len(transformed) == 1
    assert transformed.iloc[0]["incident_number"] == "002"


def test_transform_types(sample_extracted_data):
    """Test that data types are converted properly."""
    transformed = transform(sample_extracted_data)

    assert pd.api.types.is_datetime64_any_dtype(transformed["start_time"])
    assert pd.api.types.is_datetime64_any_dtype(transformed["end_time"])
    assert pd.api.types.is_bool_dtype(transformed["is_planned"])


def test_transform_columns(sample_extracted_data):
    """Test that the transformed DataFrame contains the correct columns."""
    expected_columns = {
        "start_time",
        "end_time",
        "description",
        "incident_number",
        "version_number",
        "is_planned",
        "info_link",
        "summary",
        "operators"
    }

    transformed = transform(sample_extracted_data)
    actual_columns = set(transformed.columns)
    assert actual_columns == expected_columns
