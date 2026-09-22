# Momchil Georgiev (24033989) 
from pathlib import Path
from datetime import date, timedelta
import sqlite3
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import databaseConnection, db_utils, lease_service
import main.lease_page as lease_page


def _use_temp_database(tmp_path, monkeypatch):
	db_path = tmp_path / "case90.db"
	schema_path = Path(__file__).resolve().parents[2] / "database" / "schema.sql"

	conn = sqlite3.connect(db_path)
	conn.executescript(schema_path.read_text(encoding="utf-8"))
	conn.close()

	def _connect(_db_path="database/database.db"):
		return sqlite3.connect(db_path)

	monkeypatch.setattr(databaseConnection, "check_connection", _connect)
	monkeypatch.setattr(db_utils, "check_connection", _connect)
	monkeypatch.setattr(lease_service, "check_connection", _connect, raising=False)


class TestCase90EarlyTerminationFlow:
	def test_early_termination_applies_penalty_and_one_month_vacate_date(self, tmp_path, monkeypatch):
		_use_temp_database(tmp_path, monkeypatch)

		confirmation = {}
		reloads = {"count": 0}
		expected_vacate_by = str(date.today() + timedelta(days=30))

		monkeypatch.setattr(lease_page.messagebox, "askyesno", lambda title, message: confirmation.update({"title": title, "message": message}) or True)
		monkeypatch.setattr(lease_page.messagebox, "showerror", lambda *args, **kwargs: None)

		page = types.SimpleNamespace(
			selected_lease_id="14",
			selected_lease_row=("14", "Uma Patel", "Apartment - 22 Temple Meads, BS1 6QS", "2026-03-15", str(date.today() + timedelta(days=45)), "£1,150.00", "Bristol", "Active"),
			_load_leases=lambda: reloads.update({"count": reloads["count"] + 1}),
		)

		lease_page.LeaseManagerPage._remove_lease(page)

		stored_fee = lease_service.execute_query(
			"SELECT early_termination_fee FROM Lease WHERE lease_id = ?",
			(14,),
			"one",
		)[0]

		assert float(stored_fee) == 57.5
		assert reloads["count"] == 1
		assert confirmation["title"] == "Confirm Removal"
		assert f"Vacate By: {expected_vacate_by}" in confirmation["message"]
		assert "Penalty (5%): £57.50" in confirmation["message"]