# Erin Williams (23072947)  
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.Request_Management import RegisterRequestPanel
import modules.Request_Management as request_management
from modules.Lifecycle_Management import MaintenanceDetailPanel
from database import maintaince_service


class DummyDropdown:
	def __init__(self, value):
		self.value = value

	def get(self):
		return self.value


class TestCase74MaintenancePriority:
	def test_maintenance_request_priority_is_saved_when_adding_request(self, monkeypatch):
		register_calls = []
		submitted_ids = []
		errors = []

		def fake_register_request(**kwargs):
			register_calls.append(kwargs)
			return 74

		monkeypatch.setattr(maintaince_service, "register_request", fake_register_request)
		monkeypatch.setattr(request_management.messagebox, "showerror", lambda title, message: errors.append((title, message)))

		panel = types.SimpleNamespace(
			issue_entry=DummyDropdown("Broken boiler in kitchen"),
			priority_var=DummyDropdown("High"),
			tenant_cb=DummyDropdown("Taylor Tenant"),
			apt_cb=DummyDropdown("Flat 4 - AB12 3CD"),
			_tenant_ids=[18],
			_tenant_names=["Taylor Tenant"],
			_apt_ids=[205],
			_apt_labels=["Flat 4 - AB12 3CD"],
			on_submit=lambda new_id: submitted_ids.append(new_id),
		)

		RegisterRequestPanel._submit(panel)

		assert errors == []
		assert register_calls == [{
			"apartment_id": 205,
			"tenant_id": 18,
			"issue": "Broken boiler in kitchen",
			"priority": "High",
		}]
		assert submitted_ids == [74]

	def test_maintenance_request_priority_is_saved_when_updating_request(self, monkeypatch):
		calls = []
		refreshed = []

		def fake_update_request_priority(request_id, new_priority):
			calls.append((request_id, new_priority))
			return True

		monkeypatch.setattr(maintaince_service, "update_request_priority", fake_update_request_priority)

		popup = types.SimpleNamespace(
			priority_update_dropdown=DummyDropdown("Low"),
			on_update_priority=lambda request_id: refreshed.append(request_id),
		)

		MaintenanceDetailPanel._handle_immediate_priority_update(popup, 74)

		assert calls == [(74, "Low")]
		assert refreshed == [74]