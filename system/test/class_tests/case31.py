# Leyla Ahmed (24060594)   

from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.Lifecycle_Management import MaintenanceDetailPanel
import modules.Lifecycle_Management as lifecycle_management


class DummyField:
	def __init__(self, value):
		self.value = value

	def get(self, *_args):
		return self.value


class TestCase78ResolutionValidation:
	def test_resolution_submission_accepts_valid_entries_and_passes_numeric_values(self):
		resolved_calls = []

		panel = types.SimpleNamespace(
			parent=None,
			resolve_notes=DummyField("Replaced damaged pipe and tested water flow"),
			cost_entry=DummyField("125.50"),
			time_entry=DummyField("2"),
			on_resolve=lambda notes, repair_cost, repair_time: resolved_calls.append((notes, repair_cost, repair_time)),
		)

		MaintenanceDetailPanel._submit_resolution(panel)

		assert resolved_calls == [(
			"Replaced damaged pipe and tested water flow",
			125.5,
			2.0,
		)]

	def test_resolution_note_validation_blocks_invalid_submission(self, monkeypatch):
		errors = []
		resolved_calls = []

		monkeypatch.setattr(lifecycle_management.messagebox, "showerror", lambda title, message, parent=None: errors.append((title, message)))

		panel = types.SimpleNamespace(
			parent=None,
			resolve_notes=DummyField(""),
			cost_entry=DummyField("-5"),
			time_entry=DummyField("abc"),
			on_resolve=lambda notes, repair_cost, repair_time: resolved_calls.append((notes, repair_cost, repair_time)),
		)

		MaintenanceDetailPanel._submit_resolution(panel)

		assert resolved_calls == []
		assert errors
		assert errors[0][0] == "Validation Error"
		assert "Resolution notes are required" in errors[0][1]
		assert "Repair time must be a valid number" in errors[0][1]
		assert "Repair cost cannot be negative" in errors[0][1]