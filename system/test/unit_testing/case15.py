# Momchil Georgiev (24033989) 
from pathlib import Path
import sys
from datetime import date, timedelta
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import main.lease_page as lease_page


def test_early_termination_penalty_is_calculated_from_rent(monkeypatch):
	updated = {}
	confirmation = {}

	future_end_date = str(date.today() + timedelta(days=45))

	monkeypatch.setattr(lease_page.messagebox, "askyesno", lambda title, message: confirmation.update({"title": title, "message": message}) or True)
	monkeypatch.setattr(lease_page, "update_lease_early_termination", lambda lease_id, fee: updated.update({"lease_id": lease_id, "fee": fee}))

	page = types.SimpleNamespace(
		selected_lease_id="9",
		selected_lease_row=("9", "Jane Doe", "Apartment 4A", "2026-01-01", future_end_date, "£1,200.00", "London", "Active"),
		_load_leases=lambda: updated.update({"reloaded": True}),
	)

	lease_page.LeaseManagerPage._remove_lease(page)

	assert updated["lease_id"] == 9
	assert updated["fee"] == 60.0
	assert updated["reloaded"] is True
	assert "Penalty (5%): £60.00" in confirmation["message"]
