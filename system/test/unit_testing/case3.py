# Erin Williams (23072947)  
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from validations import validate_email_address


def test_invalid_email_address_is_rejected():
	with pytest.raises(ValueError, match="Email format is invalid"):
		validate_email_address("invalid-email")