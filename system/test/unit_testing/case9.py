# Momchil Georgiev (24033989) 
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.Request_Management import RegisterRequestPanel
import modules.Request_Management as request_management
from database import maintaince_service


class DummyField:
	def __init__(self, value):
		self.value = value

	def get(self):
		return self.value


def test_maintenance_request_missing_required_fields_show_validation_error_and_request_not_saved(monkeypatch):
	errors = []
	register_called = {"value": False}

	monkeypatch.setattr(request_management.messagebox, "showerror", lambda title, message: errors.append((title, message)))
	monkeypatch.setattr(maintaince_service, "register_request", lambda **kwargs: register_called.update({"value": True}))

	panel = types.SimpleNamespace(
		issue_entry=DummyField(""),
		priority_var=DummyField(""),
		tenant_cb=DummyField(""),
		apt_cb=DummyField(""),
		_tenant_ids=[],
		_tenant_names=[],
		_apt_ids=[],
		_apt_labels=[],
		on_submit=None,
	)

	RegisterRequestPanel._submit(panel)

	assert errors
	assert errors[0][0] == "Validation Error"
	assert register_called["value"] is False