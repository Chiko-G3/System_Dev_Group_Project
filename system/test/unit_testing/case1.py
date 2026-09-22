# Mohamed Hamouda (23077543)   
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import tenant_service


def test_duplicate_national_insurance_number_raises_value_error(monkeypatch):
	def fake_execute_query(query, params=(), fetch_mode='all'):
		assert params[0] == "QQ123456C"
		return (1,)

	monkeypatch.setattr(tenant_service, "execute_query", fake_execute_query)

	with pytest.raises(ValueError, match="already exists"):
		tenant_service.ensure_unique_national_insurance_number("qq 12 34 56 c")