import pytest

import allure

from src.taf_core.factories.metrics_factory import (
    create_browser_metrics_collector,
    create_browser_network_metrics_manager,
)
from src.taf_core.factories.validator_factory import create_network_metrics_validator
from src.taf_core.pages.web_page import WebPage
from tests.constants import CaseUrl, Website
from tests.utils.dns_helpers import get_dns_servers
from tests.utils.metrics_helpers import collect_metrics_for_page


@allure.parent_suite("End-To-End")
@allure.suite("End-To-End - Network Properties")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.E2E
@pytest.mark.Smoke
@pytest.mark.Network
class TestWebPageNetworkProperties:
    @allure.testcase(CaseUrl.NETWORK, name="Test Case ID: E2E-NET-TC001")
    @allure.title("Verify Web Page Network Properties")
    @pytest.mark.parametrize(
        "url",
        [
            Website.GOOGLE,
            Website.ONET,
            Website.EXAMPLE,
        ],
    )
    def test_verify_web_page_network_properties(self, page, url):
        # Given
        allure.dynamic.description(f"Verifies network properties of {url} web page")
        get_dns_servers()

        browser_collector = create_browser_metrics_collector(page)
        web_page = WebPage(page, base_url=url)
        metrics_mgr = create_browser_network_metrics_manager(browser_collector)

        # When
        collect_metrics_for_page(browser_collector, web_page)

        # Then
        create_network_metrics_validator(metrics_mgr).validate_page_load()
