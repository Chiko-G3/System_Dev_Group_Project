# Momchil Georgiev (24033989) 
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import modules.Payments_Management as payments_module
from modules.Payments_Management import PaymentsManagementPage


def test_payment_status_update_normalizes_paid_unpaid_and_partial_states():
	page = PaymentsManagementPage.__new__(PaymentsManagementPage)

	assert page._normalize_status("paid") == "Fully Paid"
	assert page._normalize_status("not paid") == "Unpaid"
	assert page._normalize_status("partial") == "Pending (Partial)"
	assert page._normalize_status("pending (partial)") == "Pending (Partial)"


def test_payment_status_update_reads_status_from_finance_manager_rows():
	finance_page = PaymentsManagementPage.__new__(PaymentsManagementPage)
	finance_page.user_role = "Finance Manager"

	finance_row = (
		"Alex Tenant",
		"12 King St (AB12 3CD)",
		"Leeds",
		"2026-04-01",
		"-",
		250.0,
		500.0,
		"partial",
		"No",
		91,
	)

	assert finance_page._row_status(finance_row) == "Pending (Partial)"


def test_finance_manager_refresh_uses_logged_in_user_scope(monkeypatch):
	page = PaymentsManagementPage.__new__(PaymentsManagementPage)
	page.user_info = (40, "Eva", "Stone", "Bristol", "Finance Manager", 1)
	page.user_id = 40
	page.user_role = "Finance Manager"
	page.current_view = "payments"

	captured = {}

	def fake_get_all_payments(user_info=None, city_id=None):
		captured["user_info"] = user_info
		captured["city_id"] = city_id
		return []

	monkeypatch.setattr(payments_module, "get_all_payments", fake_get_all_payments)
	monkeypatch.setattr(PaymentsManagementPage, "_render_current_view", lambda self: None)

	page.refresh_payments()

	assert captured["user_info"] == page.user_info
	assert captured["city_id"] is None
