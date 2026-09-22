# Erin Williams (23072947)  
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.Property_Management import AddApartmentStepper
from database import property_service


def test_admin_apartment_permissions_scope_add_property_to_assigned_city(monkeypatch):
	captured = {}

	monkeypatch.setattr("modules.Property_Management.get_all_cities", lambda scope_city_id=None: captured.setdefault("city_scopes", []).append(scope_city_id) or [(9, "Leeds")])
	monkeypatch.setattr("modules.Property_Management.get_all_buildings", lambda scope_city_id=None: captured.setdefault("building_scopes", []).append(scope_city_id) or [(15, 9, "12 King St", "AB12 3CD")])
	monkeypatch.setattr("modules.Property_Management.build_city_map", lambda cities: {"Leeds": 9})
	monkeypatch.setattr("modules.Property_Management.build_buildings_by_city", lambda buildings: ({9: [(15, "12 King St (AB12 3CD)")]}, {"12 King St (AB12 3CD)": 15}))
	monkeypatch.setattr(AddApartmentStepper, "step_address", lambda self, city: captured.setdefault("step_address_calls", []).append(city))
	monkeypatch.setattr(AddApartmentStepper, "step_city", lambda self: captured.setdefault("step_city_calls", 0))

	AddApartmentStepper(parent=object(), refresh_callback=lambda: None, user_info=(1, "Admin", "User", "Leeds", "Administrators", 9))

	assert captured["city_scopes"] == [9]
	assert captured["building_scopes"] == [9]
	assert captured["step_address_calls"] == ["Leeds"]
	assert "step_city_calls" not in captured


def test_admin_apartment_permissions_scope_view_queries_to_assigned_city(monkeypatch):
	captured = {}

	def fake_execute_query(query, params=(), fetch_mode="all"):
		captured["query"] = query
		captured["params"] = params
		captured["fetch_mode"] = fetch_mode
		return []

	monkeypatch.setattr(property_service, "execute_query", fake_execute_query)

	property_service.get_all_apartments(scope_city_id=9)

	assert "WHERE a.city_id = ?" in captured["query"]
	assert captured["params"] == (9,)
	assert captured["fetch_mode"] == "all"