# Leyla Ahmed (24060594)   
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from validations import validate_tenant_form


def test_reference_email_can_be_blank_when_other_fields_are_valid():
	data = (
		"John",
		"Smith",
		"tenant@example.com",
		"+44 7700 900123",
		"Ref Person",
		"",
		"QQ123456C",
		"",
		"",
		"Engineer",
	)

	assert validate_tenant_form(data) is True


def test_reference_email_invalid_format_is_rejected():
	data = (
		"John",
		"Smith",
		"tenant@example.com",
		"+44 7700 900123",
		"Ref Person",
		"bad-reference-email",
		"QQ123456C",
		"",
		"",
		"Engineer",
	)

	with pytest.raises(ValueError, match="Reference Email format"):
		validate_tenant_form(data)