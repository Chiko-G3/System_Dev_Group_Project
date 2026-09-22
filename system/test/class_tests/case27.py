# Leyla Ahmed (24060594)   

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import validations


class TestCase51TenantValidation:
	def test_invalid_national_insurance_number_format_raises_value_error(self):
		invalid_ni_number = "123456789"

		with pytest.raises(ValueError, match="National Insurance Number format is invalid"):
			validations.validate_national_insurance_number(invalid_ni_number)

	def test_invalid_tenant_email_format_raises_value_error(self):
		assert hasattr(validations, "validate_email_address"), "validate_email_address is missing"

		with pytest.raises(ValueError, match="Email format is invalid"):
			validations.validate_email_address("invalid-email")

	def test_invalid_tenant_phone_number_format_raises_value_error(self):
		assert hasattr(validations, "validate_phone_number"), "validate_phone_number is missing"

		with pytest.raises(ValueError, match="Telephone format is invalid"):
			validations.validate_phone_number("12AB")