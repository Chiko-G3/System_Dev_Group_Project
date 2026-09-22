# Leyla Ahmed (24060594)   
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import payment_service


def test_late_payment_logic_marks_due_date_passed_without_full_payment_as_late(monkeypatch):
	captured = {}

	monkeypatch.setattr(payment_service, "sync_lease_payments_up_to_horizon", lambda months_ahead=1: captured.update({"months_ahead": months_ahead}))

	def fake_execute_query(query, params=(), fetch_mode='all'):
		captured["query"] = query
		captured["params"] = params
		captured["fetch_mode"] = fetch_mode

	monkeypatch.setattr(payment_service, "execute_query", fake_execute_query)

	payment_service.update_late_status()

	assert captured["months_ahead"] == 1
	assert "DATE(due_date) < DATE('now')" in captured["query"]
	assert "payment_date IS NULL" in captured["query"]
	assert "amount < (" in captured["query"]
	assert "SELECT Agreed_rent" in captured["query"]
	assert "THEN 'Yes'" in captured["query"]
	assert captured["params"] == ()
	assert captured["fetch_mode"] == 'none'