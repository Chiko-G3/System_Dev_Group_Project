# Leyla Ahmed (24060594)   
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import main.report_page as report_page
from database import report_service


def test_finance_manager_city_restriction_resolves_assigned_city_only():
	page = types.SimpleNamespace(
		role="Finance Manager",
		is_admin=False,
		assigned_city_id=4,
		city_cb=None,
		selected_city=types.SimpleNamespace(get=lambda: "All Cities"),
		city_name_to_id={"Bristol": 1, "Cardiff": 2, "London": 3, "Manchester": 4},
	)

	city_id = report_page.ReportManagementPage._resolve_city_id(page)

	assert city_id == 4


def test_finance_manager_financial_rows_are_filtered_to_assigned_city(monkeypatch):
	captured = {}

	def fake_execute_query(query, params=(), fetch_mode='all'):
		captured["query"] = query
		captured["params"] = params
		captured["fetch_mode"] = fetch_mode
		return []

	monkeypatch.setattr(report_service, "execute_query", fake_execute_query)

	report_service.fetch_financial_rows(city_id=4)

	assert "a.city_id = ?" in captured["query"]
	assert captured["params"] == (4,)
	assert captured["fetch_mode"] == 'all'