# Ava Abtin (23039373)   
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import user_service, tenant_service


class TestCase85DataIntegrity:
	def test_data_integrity_blocks_user_creation_in_conflicting_city_scope(self):
		with pytest.raises(ValueError, match="assigned location"):
			user_service.create_user(
				"Jamie",
				"Smith",
				"jamie@example.com",
				"StrongPass1",
				2,
				city_id=9,
				scope_city_id=3,
			)

	def test_data_integrity_blocks_conflicting_duplicate_identifiers(self, monkeypatch):
		monkeypatch.setattr(tenant_service, "execute_query", lambda query, params=(), fetch_mode="all": (99,))

		with pytest.raises(ValueError, match="National Insurance Number already exists"):
			tenant_service.ensure_unique_national_insurance_number("QQ123456C")