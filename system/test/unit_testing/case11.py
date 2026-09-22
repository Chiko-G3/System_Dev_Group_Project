# Ava Abtin (23039373)   
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.Property_Management import AddApartmentStepper
import modules.Property_Management as property_management


def test_invalid_apartment_details_are_rejected_and_apartment_not_saved(monkeypatch):
	errors = []
	create_called = {"value": False}

	monkeypatch.setattr(property_management.messagebox, "showerror", lambda title, message, parent=None: errors.append((title, message)))
	monkeypatch.setattr(property_management, "create_apartment", lambda *args, **kwargs: create_called.update({"value": True}))

	stepper = types.SimpleNamespace(
		box_frame=None,
		display_to_id={"221B Baker Street": 5},
		city_map={"London": 2},
		refresh_callback=lambda: None,
		_show_success_state=lambda *args, **kwargs: None,
	)

	AddApartmentStepper._submit(stepper, "abc", "Wrong Type", "Vacant", "London", "221B Baker Street")

	assert errors
	assert errors[0][0] == "Validation Error"
	assert create_called["value"] is False