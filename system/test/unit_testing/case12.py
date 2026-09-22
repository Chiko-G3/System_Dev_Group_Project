# Mohamed Hamouda (23077543)   
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from validations import validate_building_form, validate_city_name


def test_invalid_city_name_is_rejected():
	with pytest.raises(ValueError, match="only contain letters"):
		validate_city_name("London2")


def test_missing_or_invalid_building_data_is_rejected():
	with pytest.raises(ValueError, match="City is required|Postcode must be exactly 7 characters"):
		validate_building_form("", "Main Street", "ABC123")