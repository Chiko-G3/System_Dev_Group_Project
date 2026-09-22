# Momchil Georgiev (24033989) 
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from main.Lifecycle_page import MaintenanceManagementPage
from database import maintaince_service


class DummyButton:
	def __init__(self):
		self.calls = []

	def config(self, **kwargs):
		self.calls.append(kwargs)


def test_lifecycle_restriction_blocks_assignment_until_request_is_approved():
	page = types.SimpleNamespace(
		selected_request_id=77,
		request_status={"77": "Open"},
		assign_btn=DummyButton(),
	)

	MaintenanceManagementPage._update_assign_button(page)

	assert page.assign_btn.calls[-1] == {"bg": "#dc3545", "state": "disabled"}

	page.request_status = {"77": "Approved"}
	MaintenanceManagementPage._update_assign_button(page)

	assert page.assign_btn.calls[-1] == {"bg": "#28a745", "state": "normal"}


def test_lifecycle_restriction_enforces_city_rules_for_staff_queries(monkeypatch):
	captured = {}

	def fake_execute_query(query, params=(), fetch_mode="all"):
		captured["query"] = query
		captured["params"] = params
		captured["fetch_mode"] = fetch_mode
		return []

	monkeypatch.setattr(maintaince_service, "execute_query", fake_execute_query)

	maintaince_service.get_maintenance_staff(user_info=(1, "Pat", "Lee", "pat@example.com", "Staff", 9))

	assert "u.city_id = ?" in captured["query"]
	assert captured["params"] == (9,)
	assert captured["fetch_mode"] == "all"