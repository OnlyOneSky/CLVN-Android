"""Custom explicit-wait utility functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.utils.config_loader import ConfigLoader

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

_settings = ConfigLoader.load_settings()
DEFAULT_TIMEOUT: int = _settings.get("timeouts", {}).get("explicit_wait", 15)


def wait_for_element_visible(
    driver: WebDriver,
    locator: tuple[str, str],
    timeout: int = DEFAULT_TIMEOUT,
) -> WebElement:
    """Wait until an element is both present and visible.

    Raises ``TimeoutException`` if the element does not appear within *timeout*.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.visibility_of_element_located(locator))


def wait_for_element_clickable(
    driver: WebDriver,
    locator: tuple[str, str],
    timeout: int = DEFAULT_TIMEOUT,
) -> WebElement:
    """Wait until an element is visible **and** enabled (clickable).

    Raises ``TimeoutException`` if the condition is not met within *timeout*.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable(locator))


def wait_for_text_present(
    driver: WebDriver,
    locator: tuple[str, str],
    text: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> bool:
    """Wait until the element identified by *locator* contains *text*.

    Returns ``True`` when the text is found; raises ``TimeoutException`` otherwise.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.text_to_be_present_in_element(locator, text))


def wait_for_element_gone(
    driver: WebDriver,
    locator: tuple[str, str],
    timeout: int = DEFAULT_TIMEOUT,
) -> bool:
    """Wait until the element is no longer visible (or absent from the DOM).

    Returns ``True`` when the element disappears; raises ``TimeoutException``
    if it is still visible after *timeout*.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.invisibility_of_element_located(locator))
