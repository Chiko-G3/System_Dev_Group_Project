# Leyla Ahmed (24060594)   
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import tenant_service


def test_delete_tenant_with_linked_leases_cascades_related_records(monkeypatch):
	captured = {}

	def fake_execute_query(query, params=(), fetch_mode='all'):
		if query.startswith("SELECT user_id FROM Tenant"):
			return (42,)
		if query.startswith("SELECT DISTINCT apartment_id FROM Lease"):
			return [(7,), (8,)]
		if "sqlite_master" in query:
			return None
		raise AssertionError(f"Unexpected query: {query}")

	def fake_execute_transaction(operations):
		captured["operations"] = operations
		return True

	monkeypatch.setattr(tenant_service, "execute_query", fake_execute_query)
	monkeypatch.setattr(tenant_service, "execute_transaction", fake_execute_transaction)

	tenant_service.delete_tenant(11)

	queries = [query for query, _params in captured["operations"]]
	params = [params for _query, params in captured["operations"]]

	assert any("DELETE FROM Payment WHERE lease_id IN" in query for query in queries)
	assert any("DELETE FROM Lease WHERE tenant_id = ?" in query for query in queries)
	assert any("DELETE FROM Tenant WHERE tenant_id = ?" in query for query in queries)
	assert any("DELETE FROM User WHERE user_id = ?" in query for query in queries)
	assert any("UPDATE Apartments SET occupancy_status = 'Vacant'" in query for query in queries)
	assert (11,) in params
	assert (42,) in params
	assert (7, 7) in params
	assert (8, 8) in params