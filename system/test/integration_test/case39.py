# Leyla Ahmed (24060594)   
from pathlib import Path
import sqlite3
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import databaseConnection, db_utils, tenant_service, user_service
import main.Dashbaord as dashboard
import main.log_in as log_in


def _use_temp_database(tmp_path, monkeypatch):
	db_path = tmp_path / "case89.db"
	schema_path = Path(__file__).resolve().parents[2] / "database" / "schema.sql"

	conn = sqlite3.connect(db_path)
	conn.executescript(schema_path.read_text(encoding="utf-8"))
	conn.close()

	def _connect(_db_path="database/database.db"):
		return sqlite3.connect(db_path)

	monkeypatch.setattr(databaseConnection, "check_connection", _connect)
	monkeypatch.setattr(db_utils, "check_connection", _connect)
	monkeypatch.setattr(tenant_service, "check_connection", _connect, raising=False)
	monkeypatch.setattr(user_service, "check_connection", _connect, raising=False)


class DummyEntry:
	def __init__(self, value):
		self.value = value

	def get(self):
		return self.value


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
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.destroyed = False

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

	def deiconify(self):
		return None

	def destroy(self):
		self.destroyed = True


class TestCase89LoginRbacDashboardIntegration:
	def test_integration_login_to_rbac_to_dashboard_loads_only_allowed_pages(self, tmp_path, monkeypatch):
		_use_temp_database(tmp_path, monkeypatch)

		user_service.create_user(
			"Fiona",
			"Ledger",
			"fiona.ledger@paragon.com",
			"StrongPass1",
			2,
			city_id=3,
		)

		captured = {}
		page_errors = []
		dummy_module = types.SimpleNamespace(create_page=lambda parent, user_info=None: DummyWidget())

		monkeypatch.setattr(dashboard.tk, "Tk", DummyRoot)
		monkeypatch.setattr(dashboard.tk, "Frame", DummyWidget)
		monkeypatch.setattr(dashboard.messagebox, "showerror", lambda *args, **kwargs: page_errors.append(args))
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

		monkeypatch.setattr(log_in.messagebox, "showwarning", lambda *args, **kwargs: page_errors.append(args))
		monkeypatch.setattr(log_in.messagebox, "showerror", lambda *args, **kwargs: page_errors.append(args))

		def capture_page_template(main_window, user_info):
			captured["user_info"] = user_info
			return dashboard.page_template(main_window, user_info)

		monkeypatch.setattr(log_in, "page_template", capture_page_template)

		login_page = types.SimpleNamespace(
			email_entry=DummyEntry("fiona.ledger@paragon.com"),
			password_entry=DummyEntry("StrongPass1"),
			login_root=DummyRoot(),
			main_window=DummyRoot(),
		)

		log_in.Log_window.authenticate(login_page)

		assert login_page.login_root.destroyed is True
		assert captured["user_info"][1:5] == ("Fiona", "Ledger", "London", "Finance Manager")
		assert captured["pages"] == ["Reports", "Payments"]
		assert not page_errors