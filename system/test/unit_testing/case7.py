# Erin Williams (23072947)  
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from database import maintaince_service


def test_open_another_city_data_is_restricted(monkeypatch):
	captured = {}

	def fake_execute_query(query, params=(), fetch_mode='all'):
		captured["query"] = query
		captured["params"] = params
		return []

	monkeypatch.setattr(maintaince_service, "execute_query", fake_execute_query)

	user_info = (7, "Alex", "Smith", "Bristol", "Front-desk Staff", 1)
	maintaince_service.get_all_requests(user_info=user_info)

	assert "b.city_id = ?" in captured["query"]
	assert captured["params"] == (1,)