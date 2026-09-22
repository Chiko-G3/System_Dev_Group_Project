# Leyla Ahmed (24060594)   

from pathlib import Path
import sys
import types

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import main.lease_page as lease_page
from database import lease_service


class DummyField:
	def __init__(self, value):
		self.value = value

	def get(self):
		return self.value


class TestCase65LeaseCreationValidation:
	def test_lease_creation_missing_tenant_or_apartment_is_blocked(self, monkeypatch):
		errors = []
		create_called = {"value": False}

		monkeypatch.setattr(lease_page.messagebox, "showerror", lambda title, message: errors.append((title, message)))
		monkeypatch.setattr(lease_page, "create_lease", lambda *args, **kwargs: create_called.update({"value": True}))

		page = types.SimpleNamespace(
			tenant_cb=DummyField(""),
			apt_cb=DummyField(""),
			start_entry=DummyField("2026-05-01"),
			end_entry=DummyField("2026-06-01"),
			rent_entry=DummyField("1200"),
			tenant_map={},
			available_map={},
			_clear_form=lambda: None,
			_load_leases=lambda: None,
		)

		lease_page.LeaseManagerPage._add_lease(page)

		assert errors
		assert errors[0] == ("Validation Error", "Please choose tenant and apartment.")
		assert create_called["value"] is False

	def test_lease_creation_invalid_dates_are_rejected_before_save(self, monkeypatch):
		connection_checked = {"value": False}

		monkeypatch.setattr(lease_service, "check_connection", lambda: connection_checked.update({"value": True}))

		with pytest.raises(ValueError, match="End date must be on or after start date"):
			lease_service.create_lease(1, 2, "2026-06-01", "2026-05-01", "1200")

		assert connection_checked["value"] is False

	def test_lease_creation_invalid_rent_is_rejected_before_save(self, monkeypatch):
		connection_checked = {"value": False}

		monkeypatch.setattr(lease_service, "check_connection", lambda: connection_checked.update({"value": True}))

		with pytest.raises(ValueError, match="Rent must be greater than 0"):
			lease_service.create_lease(1, 2, "2026-05-01", "2026-06-01", "0")

		assert connection_checked["value"] is False