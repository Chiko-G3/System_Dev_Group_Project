# Leyla Ahmed (24060594)   
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import databaseConnection, db_utils, maintaince_service
from modules.Lifecycle_Management import StaffAssignmentPanel
import modules.Lifecycle_Management as lifecycle_management


def _use_temp_database(tmp_path, monkeypatch):
	db_path = tmp_path / "case92.db"
	schema_path = Path(__file__).resolve().parents[2] / "database" / "schema.sql"

	conn = sqlite3.connect(db_path)
	conn.executescript(schema_path.read_text(encoding="utf-8"))
	conn.close()

	def _connect(_db_path="database/database.db"):
		return sqlite3.connect(db_path)

	monkeypatch.setattr(databaseConnection, "check_connection", _connect)
	monkeypatch.setattr(db_utils, "check_connection", _connect)
	monkeypatch.setattr(maintaince_service, "check_connection", _connect, raising=False)


class DummyField:
	def __init__(self, value):
		self.value = value

	def get(self, *_args):
		return self.value


class DummyButton:
	def pack_forget(self):
		return None

	def pack(self, **_kwargs):
		return None


class TestCase92SchedulingCapacity:
	def test_scheduling_slots_reduce_after_booking_is_saved(self, tmp_path, monkeypatch):
		_use_temp_database(tmp_path, monkeypatch)

		assert maintaince_service.assign_and_schedule(
			16,
			10,
			"High",
			"2026-09-01 09:00:00",
			"Urgent boiler pressure check",
		) is True

		task_counts = maintaince_service.get_staff_task_count_for_date("Troy Dixon", "2026-09-01")
		assert task_counts == {"09:00": 1}

		monkeypatch.setattr(lifecycle_management, "clear_frame", lambda frame: None)
		monkeypatch.setattr(lifecycle_management, "create_button", lambda *args, **kwargs: DummyButton())

		panel = StaffAssignmentPanel.__new__(StaffAssignmentPanel)
		panel.parent = None
		panel.date_entry = DummyField("2026-09-01")
		panel.staff_dropdown = DummyField("Troy Dixon")
		panel.slots_frame = object()
		panel.selected_slot = None
		panel._available_slots = []

		StaffAssignmentPanel._check_availability(panel)

		assert panel._available_slots == ["13:00", "17:00"]