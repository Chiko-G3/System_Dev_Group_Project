# Momchil Georgiev (24033989) 
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import user_service, payment_service


class TestCase84DatabaseConsistency:
	def test_database_consistency_cross_city_user_scope_prevents_leakage(self, monkeypatch):
		captured = {}

		def fake_execute_query(query, params=(), fetch_mode="all"):
			captured["query"] = query
			captured["params"] = params
			captured["fetch_mode"] = fetch_mode
			return []

		monkeypatch.setattr(user_service, "execute_query", fake_execute_query)

		user_service.get_all_users(scope_city_id=7)

		assert "AND u.city_id = ?" in captured["query"]
		assert captured["params"] == (7,)
		assert captured["fetch_mode"] == "all"

	def test_database_consistency_tenant_payment_view_groups_by_lease_and_prevents_cross_city_leakage(self, monkeypatch):
		captured = {}

		monkeypatch.setattr(payment_service, "update_late_status", lambda: None)

		def fake_execute_query(query, params=(), fetch_mode="all"):
			captured["query"] = query
			captured["params"] = params
			captured["fetch_mode"] = fetch_mode
			return []

		monkeypatch.setattr(payment_service, "execute_query", fake_execute_query)

		payment_service.get_tenant_payments(15)

		assert "AND b.city_id = u.city_id" in captured["query"]
		assert "GROUP BY l.lease_id, apartment, l.Agreed_rent" in captured["query"]
		assert captured["params"] == (15,)
		assert captured["fetch_mode"] == "all"