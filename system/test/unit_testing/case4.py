# Ava Abtin (23039373)   
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from validations import validate_password_strength


def test_weak_password_is_rejected_for_user_creation():
	with pytest.raises(ValueError, match="Password is too weak"):
		validate_password_strength("weak")


def test_password_with_lowercase_numbers_and_symbols_is_accepted():
	assert validate_password_strength("momo1234!") == "momo1234!"


def test_password_with_uppercase_lowercase_and_numbers_is_accepted():
	assert validate_password_strength("StrongPass1") == "StrongPass1"