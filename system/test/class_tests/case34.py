# Ava Abtin (23039373)   
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.Payments_Management import PaymentsManagementPage
from main.Maintenance_page import MaintenancePage


class DummyField:
	def __init__(self, value):
		self.value = value

	def get(self):
		return self.value


class DummyTree:
	def __init__(self):
		self.rows = []

	def get_children(self):
		return list(range(len(self.rows)))

	def delete(self, *_items):
		self.rows = []

	def insert(self, _parent, _index, values=()):
		self.rows.append(values)


class TestCase86PerformanceBulkLoad:
	def test_performance_bulk_load_payment_filter_handles_many_rows_without_crash(self):
		page = PaymentsManagementPage.__new__(PaymentsManagementPage)
		page.user_role = "Finance Manager"
		page.current_range = "All Time"
		page.current_status = "All Status"
		page.current_city = "All Cities"
		page.current_late = "All"

		rows = [
			("Tenant", f"Building {idx}", "Leeds", "2026-04-01", "-", 250.0, 500.0, "partial", "Yes", idx)
			for idx in range(2000)
		]

		filtered = page._apply_filters(rows)

		assert len(filtered) == 2000

	def test_performance_bulk_load_maintenance_rows_render_without_crash(self):
		page = type("DummyPage", (), {})()
		page.user_info = (1, "Pat", "Manager", "Leeds", "Manager", 1)
		page._manager_city_filter_var = DummyField("All Cities")
		page._all_requests = [
			(idx, f"Tenant {idx}", "Issue", "2026-04-01", "Open", "Leeds")
			for idx in range(1500)
		]
		page.tree = DummyTree()

		MaintenancePage._render_request_rows(page)

		assert len(page.tree.rows) == 1500