# Leyla Ahmed (24060594)   
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from main.report_page import ReportManagementPage


def test_manager_report_access_all_report_types_are_available_to_generate():
	page = types.SimpleNamespace(role="Manager")

	allowed = ReportManagementPage._get_allowed_report_types(page)

	assert allowed == ["Occupancy", "Financial", "Maintenance"]