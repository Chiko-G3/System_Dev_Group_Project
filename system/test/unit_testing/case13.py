# Erin Williams (23072947)  
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import lease_service


def test_fetch_leases_returns_current_and_expired_lease_end_dates(monkeypatch):
	captured = {}
	rows = [
		(1, "John Smith", "Apartment - Baker St, AB12CD", "2026-01-01", "2026-12-31", 1200.0, "London", "Active"),
		(2, "Jane Doe", "Studio - Fleet St, EF34GH", "2025-01-01", "2025-03-31", 900.0, "London", "Expired"),
	]

	def fake_fetch_all(query, params=()):
		captured["query"] = query
		captured["params"] = params
		return rows

	monkeypatch.setattr(lease_service, "fetch_all", fake_fetch_all)

	result = lease_service.fetch_leases(city_id=1)

	assert result == rows
	assert captured["params"] == (1,)
	assert "l.end_date" in captured["query"]
	assert "WHEN DATE(l.end_date) < DATE('now') THEN 'Expired'" in captured["query"]
	assert result[0][4] == "2026-12-31"
	assert result[1][4] == "2025-03-31"
