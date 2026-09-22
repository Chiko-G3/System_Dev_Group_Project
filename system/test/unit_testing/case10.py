# Mohamed Hamouda (23077543)   
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from database import tenant_service

def test_front_desk_can_submit_complaint(monkeypatch):
    captured = {}

    def fake_execute_query(query, params=(), fetch_mode='all'):
        captured["query"] = query
        captured["params"] = params
        captured["fetch_mode"] = fetch_mode
        return None

    monkeypatch.setattr(tenant_service, "execute_query", fake_execute_query)


    tenant_service.add_complaint(
        tenant_id=12,
        description="Broken hallway light"
    )

    assert "INSERT INTO Complaints" in captured["query"]
    assert captured["params"][0] == 12
    assert captured["params"][1] == "Broken hallway light"
    assert captured["fetch_mode"] == "none"


from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from database import tenant_service

def test_front_desk_can_submit_complaint(monkeypatch):
    captured = {}

    def fake_execute_query(query, params=(), fetch_mode='all'):
        captured["query"] = query
        captured["params"] = params
        captured["fetch_mode"] = fetch_mode
        return None

    monkeypatch.setattr(tenant_service, "execute_query", fake_execute_query)

    tenant_service.add_complaint(
        tenant_id=12,
        description="Broken hallway light"
    )

    assert "INSERT INTO Complaints" in captured["query"]
    assert captured["params"][0] == 12
    assert captured["params"][1] == "Broken hallway light"
    assert captured["fetch_mode"] == "none"

