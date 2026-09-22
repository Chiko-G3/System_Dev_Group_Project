# Mohamed Hamouda (23077543)   
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from main.Lifecycle_page import MaintenanceManagementPage
import main.Lifecycle_page as lifecycle_page


def test_mark_as_resolved_on_submit_updates_request_status(monkeypatch):
	resolve_calls = []
	info_messages = []
	load_calls = []
	row_select_calls = []

	monkeypatch.setattr(lifecycle_page, "resolve_request", lambda request_id, notes, repair_cost, repair_time: resolve_calls.append((request_id, notes, repair_cost, repair_time)) or True)
	monkeypatch.setattr(lifecycle_page.messagebox, "showinfo", lambda title, message, parent=None: info_messages.append((title, message)))

	page = types.SimpleNamespace(
		selected_request_id=79,
		frame=None,
		_load_requests=lambda reselect_id=None: load_calls.append(reselect_id),
		_on_row_select=lambda: row_select_calls.append(True),
	)

	MaintenanceManagementPage._on_resolved(page, "Replaced damaged pipe and tested water flow", 125.5, 2.0)

	assert resolve_calls == [(79, "Replaced damaged pipe and tested water flow", 125.5, 2.0)]
	assert info_messages == [("Resolved", "Request marked as Resolved.")]
	assert load_calls == [79]
	assert row_select_calls == [True]