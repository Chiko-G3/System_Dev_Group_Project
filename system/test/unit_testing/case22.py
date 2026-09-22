# Ava Abtin (23039373)   
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.Lifecycle_Management import StaffAssignmentPanel
import modules.Lifecycle_Management as lifecycle_management
from database import maintaince_service


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


def test_availability_logic_returns_only_the_available_time_slots(monkeypatch):
	monkeypatch.setattr(maintaince_service, "get_staff_task_count_for_date", lambda staff_name, date_str: {"09:00": 1})
	monkeypatch.setattr(lifecycle_management, "clear_frame", lambda frame: None)
	monkeypatch.setattr(lifecycle_management, "create_button", lambda *args, **kwargs: DummyButton())

	panel = StaffAssignmentPanel.__new__(StaffAssignmentPanel)
	panel.parent = None
	panel.date_entry = DummyField("2026-04-08")
	panel.staff_dropdown = DummyField("Sam Worker")
	panel.slots_frame = object()
	panel.selected_slot = None
	panel._available_slots = []

	StaffAssignmentPanel._check_availability(panel)

	assert panel._available_slots == ["13:00", "17:00"]