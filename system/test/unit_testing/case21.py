# Erin Williams (23072947)  
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.Lifecycle_Management import StaffAssignmentPanel
from database import maintaince_service


class DummyField:
	def __init__(self, value):
		self.value = value

	def get(self, *_args):
		return self.value


class DummyButton:
	def __init__(self):
		self.calls = []

	def config(self, **kwargs):
		self.calls.append(kwargs)


def test_employee_selection_logic_assigns_selected_employee_id_to_request(monkeypatch):
	assign_calls = []
	submitted = []

	def fake_assign_and_schedule(request_id, employee_id, priority, scheduled_dt, comment):
		assign_calls.append((request_id, employee_id, priority, scheduled_dt, comment))
		return True

	monkeypatch.setattr(maintaince_service, "assign_and_schedule", fake_assign_and_schedule)

	panel = types.SimpleNamespace(
		parent=None,
		assignment_completed=False,
		staff_dropdown=DummyField("Sam Worker"),
		priority_dropdown=DummyField("High"),
		date_entry=DummyField("2026-04-08"),
		selected_slot="13:00",
		comment_text=DummyField("Check leak in bathroom"),
		_staff_ids=[41],
		_staff_names=["Sam Worker"],
		request_id=75,
		assign_button=DummyButton(),
		on_submit=lambda request_id, staff_name, comment: submitted.append((request_id, staff_name, comment)),
	)

	StaffAssignmentPanel._submit(panel)

	assert assign_calls == [(75, 41, "High", "2026-04-08 13:00:00", "Check leak in bathroom")]
	assert submitted == [(75, "Sam Worker", "Check leak in bathroom")]
	assert panel.assignment_completed is True
	assert panel.assign_button.calls[-1] == {"state": "disabled", "bg": "#95a5a6"}