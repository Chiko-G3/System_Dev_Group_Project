# Momchil Georgiev (24033989) 
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import user_service


def test_login_with_valid_credentials_is_allowed(monkeypatch):
	stored_password = user_service._hash_password_with_name_key("StrongPass1", "Jane", "Doe")

	def fake_execute_query(query, params=(), fetch_mode='all'):
		return (stored_password, "Jane", "Doe", "Administrators")

	monkeypatch.setattr(user_service, "ensure_tenant_contact_schema", lambda: None)
	monkeypatch.setattr(user_service, "execute_query", fake_execute_query)

	assert user_service.check_user("jane@example.com", "StrongPass1") == 1


def test_login_with_wrong_credentials_is_denied(monkeypatch):
	stored_password = user_service._hash_password_with_name_key("StrongPass1", "Jane", "Doe")

	def fake_execute_query(query, params=(), fetch_mode='all'):
		return (stored_password, "Jane", "Doe", "Administrators")

	monkeypatch.setattr(user_service, "ensure_tenant_contact_schema", lambda: None)
	monkeypatch.setattr(user_service, "execute_query", fake_execute_query)

	assert user_service.check_user("jane@example.com", "WrongPass9") is None