# Mohamed Hamouda (23077543)   
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from main.report_page import ReportManagementPage


def test_finance_manager_has_only_financial_report_option():
	page = types.SimpleNamespace(role="Finance Manager")

	allowed = ReportManagementPage._get_allowed_report_types(page)

	assert allowed == ["Financial"]
