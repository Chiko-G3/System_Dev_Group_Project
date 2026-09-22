# Erin Williams (23072947)  
from pathlib import Path
import sys
from datetime import date, timedelta
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.Lease_Management import RemoveLeaseStepper
import modules.Lease_Management as lease_management


def test_staff_lease_removal_confirmation_shows_penalty_and_one_month_notice(monkeypatch):
	updated = {}
	confirmation = {}

	future_end_date = str(date.today() + timedelta(days=45))
	expected_vacate_by = str(date.today() + timedelta(days=30))

	monkeypatch.setattr(lease_management.messagebox, "askyesno", lambda title, message: confirmation.update({"title": title, "message": message}) or True)
	monkeypatch.setattr(lease_management.messagebox, "showinfo", lambda *args, **kwargs: None)
	monkeypatch.setattr(lease_management, "update_lease_early_termination", lambda lease_id, fee: updated.update({"lease_id": lease_id, "fee": fee}))

	stepper = types.SimpleNamespace(
		leases=[(9, "Jane Doe", "Apartment 4A", "2026-01-01", future_end_date, 1200.0, "London", "Active")],
		refresh_callback=lambda: updated.update({"refreshed": True}),
	)

	RemoveLeaseStepper.step_confirm(stepper, "#9 - Jane Doe (Apartment 4A) - Active")

	assert updated["lease_id"] == 9
	assert updated["fee"] == 60.0
	assert updated["refreshed"] is True
	assert confirmation["title"] == "Confirm Removal"
	assert "Penalty (5%): £60.00" in confirmation["message"]
	assert f"Vacate By: {expected_vacate_by}" in confirmation["message"]
	assert "Notice: A minimum 1 month notice applies." in confirmation["message"]