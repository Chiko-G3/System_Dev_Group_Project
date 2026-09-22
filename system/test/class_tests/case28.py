# Erin Williams (23072947)  

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import tenant_service, user_service


class TestCase53DuplicateEmailValidation:
	def test_duplicate_tenant_email_is_rejected(self, monkeypatch):
		def fake_execute_query(query, params=(), fetch_mode='all'):
			assert params[0] == "tenant@example.com"
			return (1,)

		monkeypatch.setattr(tenant_service, "execute_query", fake_execute_query)

		with pytest.raises(ValueError, match="Tenant email already exists"):
			tenant_service.ensure_unique_tenant_email(" Tenant@Example.com ")

	def test_duplicate_user_email_is_rejected(self, monkeypatch):
		def fake_execute_query(query, params=(), fetch_mode='all'):
			assert params[0] == "staff@example.com"
			assert fetch_mode == 'one'
			return (1,)

		monkeypatch.setattr(user_service, "execute_query", fake_execute_query)

		with pytest.raises(ValueError, match="Email already exists"):
			user_service.create_user("Jane", "Doe", " staff@example.com ", "Password1", 1)