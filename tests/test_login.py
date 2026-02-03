"""Login test suite — validates authentication flows."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.models.user import User
from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

    from src.utils.wiremock_client import WireMockClient

# ── Test data ─────────────────────────────────────────────────────────────────

VALID_USER = User(username="valid_user", password="valid_pass", expected_name="Remi Chen")
INVALID_USER = User(username="invalid_user", password="wrong_pass")


class TestLogin:
    """Tests for the login screen."""

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_successful_login(self, driver: WebDriver, wiremock: WireMockClient) -> None:
        """A valid user should land on the home screen with a welcome message."""
        # Arrange — prime the API mock
        wiremock.load_mapping_from_file("wiremock/mappings/login_success.json")

        login_page = LoginPage(driver)

        # Act
        login_page.login(VALID_USER.username, VALID_USER.password)

        # Assert
        home_page = HomePage(driver)
        assert home_page.is_home_displayed(), "Home screen did not appear after successful login"

        welcome = home_page.get_welcome_message()
        assert VALID_USER.expected_name in welcome, (
            f"Expected '{VALID_USER.expected_name}' in welcome message, got: '{welcome}'"
        )

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_login_invalid_credentials(self, driver: WebDriver, wiremock: WireMockClient) -> None:
        """An invalid user should see an error message and stay on the login screen."""
        # Arrange
        wiremock.load_mapping_from_file("wiremock/mappings/login_failure.json")

        login_page = LoginPage(driver)

        # Act
        login_page.login(INVALID_USER.username, INVALID_USER.password)

        # Assert
        error_text = login_page.get_error_message()
        assert "Invalid" in error_text or "invalid" in error_text, (
            f"Expected an 'invalid' error message, got: '{error_text}'"
        )
        assert login_page.is_login_button_displayed(), "Login button should still be visible"

    @pytest.mark.regression
    def test_login_empty_fields(self, driver: WebDriver, wiremock: WireMockClient) -> None:
        """Submitting empty credentials should show a validation error."""
        login_page = LoginPage(driver)

        # Act — tap login without entering anything
        login_page.login("", "")

        # Assert — the app should show a validation / error message
        assert login_page.is_login_button_displayed(), "Login button should still be visible"
        error_text = login_page.get_error_message(timeout=5)
        assert error_text, "An error message should be displayed for empty fields"
