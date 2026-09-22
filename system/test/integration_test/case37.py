# Leyla Ahmed (24060594)   
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import main.Dashbaord as dashboard


class DummyWidget:
	def __init__(self, *args, **kwargs):
		self.children = []

	def pack(self, *args, **kwargs):
		return None

	def place(self, *args, **kwargs):
		return None

	def destroy(self):
		return None

	def configure(self, *args, **kwargs):
		return None

	config = configure

	def pack_propagate(self, *args, **kwargs):
		return None

	def winfo_children(self):
		return []

	def tkraise(self):
		return None


class DummyRoot(DummyWidget):
	def title(self, *args, **kwargs):
		return None

	def minsize(self, *args, **kwargs):
		return None

	def attributes(self, *args, **kwargs):
		if len(args) == 1:
			return False
		return None

	def bind(self, *args, **kwargs):
		return None

	def wait_visibility(self):
		return None

	def after(self, *args, **kwargs):
		return None

	def winfo_screenwidth(self):
		return 1280

	def winfo_screenheight(self):
		return 800

	def geometry(self, *args, **kwargs):
		return None

	def mainloop(self):
		return None


def _capture_allowed_pages(monkeypatch, role_name):
	captured = {}
	dummy_module = types.SimpleNamespace(create_page=lambda parent, user_info=None: DummyWidget())

	monkeypatch.setattr(dashboard.tk, "Tk", DummyRoot)
	monkeypatch.setattr(dashboard.tk, "Frame", DummyWidget)
	monkeypatch.setattr(dashboard.messagebox, "showerror", lambda *args, **kwargs: None)
	monkeypatch.setattr(dashboard, "create_side_navbar", lambda parent, button_text, user_info, button_command=None: captured.setdefault("pages", list(button_text)))
	monkeypatch.setattr(dashboard, "User_Management", dummy_module)
	monkeypatch.setattr(dashboard, "Property_Management", dummy_module)
	monkeypatch.setattr(dashboard, "Tenant_Management", dummy_module)
	monkeypatch.setattr(dashboard, "Payments_Management", dummy_module)
	monkeypatch.setattr(dashboard, "complaints", dummy_module)
	monkeypatch.setattr(dashboard, "Lease_Management", dummy_module)
	monkeypatch.setattr(dashboard, "Report_Management", dummy_module)
	monkeypatch.setattr(dashboard, "Lifecycle_Management", dummy_module)
	monkeypatch.setattr(dashboard.sys, "platform", "win32")
	monkeypatch.setitem(sys.modules, "main.Maintenance_page", dummy_module)

	user_info = (1, "Jane", "Doe", "London", role_name, 1)
	dashboard.page_template(DummyRoot(), user_info)
	return captured["pages"]


def test_rbac_integration_workflow_only_allowed_actions_succeed_for_all_five_roles(monkeypatch):
	assert _capture_allowed_pages(monkeypatch, "Administrators") == ["Users", "Properties", "Lease", "Reports", "Request Lifecycle", "Tenants"]
	assert _capture_allowed_pages(monkeypatch, "Front-desk Staff") == ["Tenants", "Maintenance", "Complaints"]
	assert _capture_allowed_pages(monkeypatch, "Maintenance Staff") == ["Request Lifecycle", "Reports"]
	assert _capture_allowed_pages(monkeypatch, "Manager") == ["Properties", "Lease", "Reports", "Maintenance", "Request Lifecycle"]
	assert _capture_allowed_pages(monkeypatch, "Finance Manager") == ["Reports", "Payments"]