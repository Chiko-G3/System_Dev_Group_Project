# Momchil Georgiev (24033989) 
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import databaseConnection, db_utils, maintaince_service
import main.Lifecycle_page as lifecycle_page


def _use_temp_database(tmp_path, monkeypatch):
	db_path = tmp_path / "case91.db"
	schema_path = Path(__file__).resolve().parents[2] / "database" / "schema.sql"

	conn = sqlite3.connect(db_path)
	conn.executescript(schema_path.read_text(encoding="utf-8"))
	conn.close()

	def _connect(_db_path="database/database.db"):
		return sqlite3.connect(db_path)

	monkeypatch.setattr(databaseConnection, "check_connection", _connect)
	monkeypatch.setattr(db_utils, "check_connection", _connect)
	monkeypatch.setattr(maintaince_service, "check_connection", _connect, raising=False)


class DummyButton:
	def __init__(self):
		self.state = {}

	def config(self, **kwargs):
		self.state.update(kwargs)


class TestCase91ApprovalBeforeAssignment:
	def test_assignment_remains_blocked_until_request_is_approved(self, tmp_path, monkeypatch):
		_use_temp_database(tmp_path, monkeypatch)

		page = type("Page", (), {})()
		page.selected_request_id = 16
		page.assign_btn = DummyButton()

		open_status = maintaince_service.viewFull(16)[5]
		page.request_status = {"16": open_status}

		lifecycle_page.MaintenanceManagementPage._update_assign_button(page)

		assert page.assign_btn.state["state"] == "disabled"
		assert page.assign_btn.state["bg"] == "#dc3545"

		assert maintaince_service.update_request_status(16, "approve") is True
		approved_status = maintaince_service.viewFull(16)[5]
		page.request_status = {"16": approved_status}

		lifecycle_page.MaintenanceManagementPage._update_assign_button(page)

		assert approved_status == "Approved"
		assert page.assign_btn.state["state"] == "normal"
		assert page.assign_btn.state["bg"] == "#28a745"