# Ava Abtin (23039373)   
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import main.Dashbaord as dashboard


class DummyWidget:
	def __init__(self, *args, **kwargs):
		self.destroy_called = False

	def pack(self, *args, **kwargs):
		return None

	def place(self, *args, **kwargs):
		return None

	def destroy(self):
		self.destroy_called = True

	def configure(self, *args, **kwargs):
		return None

	config = configure

	def pack_propagate(self, *args, **kwargs):
		return None

	def winfo_children(self):
		return []


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


class DummyMainWindow:
	def __init__(self):
		self.deiconify_called = False

	def deiconify(self):
		self.deiconify_called = True


def test_invalid_session_state_is_blocked(monkeypatch):
	root = DummyRoot()
	main_window = DummyMainWindow()
	captured = {}

	monkeypatch.setattr(dashboard.tk, "Tk", lambda: root)
	monkeypatch.setattr(dashboard.tk, "Frame", DummyWidget)
	monkeypatch.setattr(dashboard.messagebox, "showerror", lambda title, message, parent=None: captured.update({"title": title, "message": message}))

	user_info = (1, "Jane", "Doe", "London", "ExpiredSession", 1)
	dashboard.page_template(main_window, user_info)

	assert captured["title"] == "Access Denied"
	assert root.destroy_called is True
	assert main_window.deiconify_called is True