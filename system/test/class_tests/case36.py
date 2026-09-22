# Mohamed Hamouda (23077543)   
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from main.apartment_page import ApartmentManagerPage
from main.lease_page import LeaseManagerPage
from main.Lifecycle_page import MaintenanceManagementPage
from main.report_page import ReportManagementPage
import main.report_page as report_page
from modules.Payments_Management import PaymentsManagementPage


class DummyField:
	def __init__(self, value):
		self.value = value

	def get(self):
		return self.value

	def set(self, value):
		self.value = value

	def winfo_exists(self):
		return True

	def config(self, **_kwargs):
		return None

	def __setitem__(self, _key, value):
		self.value = self.value if self.value in value else value[0]


class DummyLabel:
	def __init__(self):
		self.values = []

	def config(self, **kwargs):
		self.values.append(kwargs)


class DummyHost:
	def winfo_children(self):
		return []


class DummyTree:
	def __init__(self):
		self.rows = []

	def get_children(self):
		return list(range(len(self.rows)))

	def delete(self, *_items):
		self.rows = []

	def insert(self, _parent, _index, values=()):
		self.rows.append(values)


class TestCase82SystemFilterLogic:
	def test_filter_logic_across_system_updates_manager_apartment_results_correctly(self):
		rendered_rows = []

		page = types.SimpleNamespace(
			_source_apartments=[
				(1, "Leeds", "12 King St", "AB12 3CD", 2, "Apartment", "Vacant"),
				(2, "Leeds", "22 King St", "AB12 3EF", 3, "Penthouse", "Unavailable"),
				(3, "York", "30 Queen St", "YO10 1AA", 2, "Apartment", "Vacant"),
			],
			_all_apartments=[],
			is_manager=True,
			_manager_city_filter_cb=DummyField("Leeds"),
			_building_filter_cb=DummyField("22 King St (AB12 3EF)"),
			_status_filter_cb=DummyField("Unavailable"),
			_render_apartment_rows=lambda: rendered_rows.append(list(page._all_apartments)),
		)

		ApartmentManagerPage._apply_property_filters(page)

		assert page._all_apartments == [
			(2, "Leeds", "22 King St", "AB12 3EF", 3, "Penthouse", "Unavailable")
		]
		assert rendered_rows[-1] == page._all_apartments

	def test_filter_logic_across_system_updates_manager_lease_results_correctly(self):
		page = types.SimpleNamespace(
			all_leases=[
				(1, "Alex Tenant", "12 King St (AB12 3CD)", "2026-01-01", "2026-12-31", 900, "Leeds", "Active"),
				(2, "Jamie Tenant", "18 King St (AB12 3EF)", "2026-01-01", "2026-12-31", 950, "Leeds", "Active"),
				(3, "Morgan Tenant", "30 Queen St (YO10 1AA)", "2026-01-01", "2026-12-31", 850, "York", "Active"),
			],
			user_role="Manager",
			city_filter_cb=DummyField("Leeds"),
			city_filter_var=DummyField("All Cities"),
			building_filter_cb=DummyField("18 King St (AB12 3EF)"),
			building_filter_var=DummyField("All Buildings"),
		)

		filtered = LeaseManagerPage._get_filtered_leases(page)

		assert filtered == [
			(2, "Jamie Tenant", "18 King St (AB12 3EF)", "2026-01-01", "2026-12-31", 950, "Leeds", "Active")
		]

	def test_filter_logic_across_system_updates_manager_lifecycle_results_correctly(self):
		page = types.SimpleNamespace(
			tree=DummyTree(),
			request_status={},
			_all_requests=[
				(1, "Alex Tenant", "Leak", "2026-04-01", "Open", "Leeds"),
				(2, "Jamie Tenant", "Boiler", "2026-04-02", "Approved", "Leeds"),
				(3, "Morgan Tenant", "Lights", "2026-04-03", "Open", "York"),
			],
			_manager_city_filter_var=DummyField("Leeds"),
		)

		MaintenanceManagementPage._render_request_rows(page)

		assert page.tree.rows == [
			(1, "Alex Tenant", "Leak", "2026-04-01", "Open", "Leeds"),
			(2, "Jamie Tenant", "Boiler", "2026-04-02", "Approved", "Leeds"),
		]
		assert page.request_status == {"1": "Open", "2": "Approved"}

	def test_filter_logic_across_system_updates_finance_payment_results_correctly(self):
		page = PaymentsManagementPage.__new__(PaymentsManagementPage)
		page.user_role = "Finance Manager"
		page.current_range = "Last Month"
		page.current_status = "Pending (Partial)"
		page.current_city = "Leeds"
		page.current_late = "Late Only"

		rows = [
			("Alex Tenant", "12 King St (AB12 3CD)", "Leeds", "2026-04-01", "-", 250.0, 500.0, "partial", "Yes", 91),
			("Alex Tenant", "12 King St (AB12 3CD)", "Leeds", "2026-04-01", "-", 0.0, 500.0, "unpaid", "Yes", 92),
			("Alex Tenant", "12 King St (AB12 3CD)", "York", "2026-04-01", "-", 250.0, 500.0, "partial", "Yes", 93),
			("Alex Tenant", "12 King St (AB12 3CD)", "Leeds", "2026-04-01", "-", 250.0, 500.0, "partial", "No", 94),
		]

		filtered = page._apply_filters(rows)

		assert filtered == [
			("Alex Tenant", "12 King St (AB12 3CD)", "Leeds", "2026-04-01", "-", 250.0, 500.0, "partial", "Yes", 91)
		]

	def test_filter_logic_across_system_updates_report_occupancy_results_correctly(self, monkeypatch):
		render_calls = []

		monkeypatch.setattr(report_page, "fetch_summary_snapshot", lambda city_id: {"apartments": 3, "occupancy_rate": 66.7, "collected": 1000.0, "maintenance": 200.0})
		monkeypatch.setattr(report_page, "fetch_occupancy_rows", lambda city_id: [
			(1, "Leeds", "12 King St", "Apartment", 2, "Vacant"),
			(2, "Leeds", "18 King St", "Apartment", 3, "Unavailable"),
		])
		monkeypatch.setattr(report_page, "fetch_financial_rows", lambda city_id, late_value, paid_value: [])
		monkeypatch.setattr(report_page, "fetch_maintenance_rows", lambda city_id: [])

		page = types.SimpleNamespace(
			role="Manager",
			is_admin=False,
			assigned_city_id=None,
			city_name_to_id={"Leeds": 9},
			selected_city=DummyField("Leeds"),
			selected_report_type=DummyField("Occupancy"),
			building_filter=DummyField("12 King St"),
			building_filter_cb=DummyField("12 King St"),
			city_cb=DummyField("Leeds"),
			late_filter=DummyField("All"),
			paid_filter=DummyField("All"),
			late_filter_cb=None,
			paid_filter_cb=None,
			summary_cards={
				"Apartments": DummyLabel(),
				"Occupancy": DummyLabel(),
				"Collected": DummyLabel(),
				"Maintenance": DummyLabel(),
			},
			finance_graph_host=DummyHost(),
			_update_summary_cards_visibility=lambda report_key: None,
			_set_report_filter_visibility=lambda report_key: None,
			_render_financial_graph=lambda rows: None,
			_render_table=lambda title, columns, headings, widths, rows: render_calls.append(rows),
		)
		page._resolve_city_id = lambda: ReportManagementPage._resolve_city_id(page)
		page._refresh_building_filter_options = lambda: None
		page._get_selected_building = lambda: ReportManagementPage._get_selected_building(page)

		ReportManagementPage.generate_report(page)

		assert render_calls[-1] == [
			(1, "Leeds", "12 King St", "Apartment", 2, "Vacant")
		]

	def test_filter_logic_across_system_updates_report_financial_results_correctly(self, monkeypatch):
		render_calls = []

		monkeypatch.setattr(report_page, "fetch_summary_snapshot", lambda city_id: {"apartments": 4, "occupancy_rate": 50.0, "collected": 1800.0, "maintenance": 300.0})
		monkeypatch.setattr(report_page, "fetch_occupancy_rows", lambda city_id: [])
		monkeypatch.setattr(report_page, "fetch_maintenance_rows", lambda city_id: [])
		monkeypatch.setattr(report_page, "fetch_financial_rows", lambda city_id, late_value, paid_value: [
			(11, "Leeds", "Alex Tenant", "2026-04-01", 500.0, "Yes", "Yes"),
			(12, "Leeds", "Jamie Tenant", "2026-04-01", 500.0, "No", "Yes"),
			(13, "Leeds", "Morgan Tenant", "2026-04-01", 500.0, "Yes", "No"),
		])

		page = types.SimpleNamespace(
			role="Manager",
			is_admin=False,
			assigned_city_id=None,
			city_name_to_id={"Leeds": 9},
			selected_city=DummyField("Leeds"),
			selected_report_type=DummyField("Financial"),
			building_filter=DummyField("All Buildings"),
			building_filter_cb=DummyField("All Buildings"),
			city_cb=DummyField("Leeds"),
			late_filter=DummyField("Late"),
			paid_filter=DummyField("Paid"),
			late_filter_cb=DummyField("Late"),
			paid_filter_cb=DummyField("Paid"),
			summary_cards={
				"Apartments": DummyLabel(),
				"Occupancy": DummyLabel(),
				"Collected": DummyLabel(),
				"Maintenance": DummyLabel(),
			},
			finance_graph_host=DummyHost(),
			_update_summary_cards_visibility=lambda report_key: None,
			_set_report_filter_visibility=lambda report_key: None,
			_render_financial_graph=lambda rows: None,
			_render_table=lambda title, columns, headings, widths, rows: render_calls.append(rows),
		)
		page._resolve_city_id = lambda: ReportManagementPage._resolve_city_id(page)
		page._refresh_building_filter_options = lambda: None
		page._get_selected_building = lambda: ReportManagementPage._get_selected_building(page)
		page._get_financial_filter_values = lambda: ReportManagementPage._get_financial_filter_values(page)

		ReportManagementPage.generate_report(page)

		assert render_calls[-1] == [
			(11, "Leeds", "Alex Tenant", "2026-04-01", 500.0, "Yes", "Yes")
		]