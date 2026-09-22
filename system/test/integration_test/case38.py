# Erin Williams (23072947)  
from pathlib import Path
from datetime import date, timedelta
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import databaseConnection, db_utils, lease_service, payment_service, tenant_service, user_service


def _use_temp_database(tmp_path, monkeypatch):
	db_path = tmp_path / "case88.db"
	schema_path = Path(__file__).resolve().parents[2] / "database" / "schema.sql"

	conn = sqlite3.connect(db_path)
	conn.executescript(schema_path.read_text(encoding="utf-8"))
	conn.close()

	def _connect(_db_path="database/database.db"):
		return sqlite3.connect(db_path)

	monkeypatch.setattr(databaseConnection, "check_connection", _connect)
	monkeypatch.setattr(db_utils, "check_connection", _connect)
	monkeypatch.setattr(tenant_service, "check_connection", _connect, raising=False)
	monkeypatch.setattr(lease_service, "check_connection", _connect, raising=False)

	return db_path


class TestCase88TenantLeasePaymentIntegration:
	def test_integration_tenant_to_lease_to_payment_creates_pending_payment_records(self, tmp_path, monkeypatch):
		_use_temp_database(tmp_path, monkeypatch)

		tenant_service.create_tenant(
			"Case",
			"Tenant",
			"case88.tenant@tenant.paragon.com",
			"07123456789",
			"Ref Person",
			"ref.person@example.com",
			"QQ123456C",
			"12 months",
			"Studio",
			"Analyst",
			city_id=3,
		)

		tenant_id = tenant_service.execute_query(
			"SELECT tenant_id FROM Tenant WHERE email = ?",
			("case88.tenant@tenant.paragon.com",),
			"one",
		)[0]

		lease_result = lease_service.create_lease(
			24,
			tenant_id,
			date.today().isoformat(),
			(date.today() + timedelta(days=62)).isoformat(),
			"1450",
		)

		assert lease_result["lease_id"] > 0
		assert lease_result["payments_created"] >= 1

		payment_rows = payment_service.get_all_payments()
		matching_rows = [row for row in payment_rows if row[0] == "Case Tenant"]

		assert matching_rows
		assert matching_rows[0][1] == "55 Canary Wharf (E14 5AB)"
		assert matching_rows[0][2] == "London"
		assert float(matching_rows[0][5]) == 0.0
		assert float(matching_rows[0][6]) == 1450.0
		assert matching_rows[0][7] == "Unpaid"

	def test_integration_finance_manager_payment_access_is_limited_to_their_city(self, tmp_path, monkeypatch):
		_use_temp_database(tmp_path, monkeypatch)

		finance_user = user_service.retrive_data("eva.finance@bristol.com")

		payment_rows = payment_service.get_all_payments(user_info=finance_user)

		assert payment_rows
		assert {row[2] for row in payment_rows} == {"Bristol"}

		details = payment_service.get_payment_details(25, user_info=finance_user)
		assert details is not None
		assert details["city"] == "Bristol"

		outside_details = payment_service.get_payment_details(47, user_info=finance_user)
		assert outside_details is None