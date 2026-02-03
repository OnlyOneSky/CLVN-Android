"""DriverFactory — create Appium driver instances from YAML configuration."""

from __future__ import annotations

import logging
from typing import Any

from appium import webdriver as appium_webdriver
from appium.options.common import AppiumOptions

from src.utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class DriverFactory:
    """Factory for creating configured Appium ``WebDriver`` instances.

    Usage::

        driver = DriverFactory.get_driver("android")
    """

    @classmethod
    def get_driver(cls, platform: str) -> appium_webdriver.Remote:
        """Build and return an Appium Remote driver for *platform*.

        Parameters
        ----------
        platform:
            ``"android"`` or ``"ios"``.

        Returns
        -------
        appium.webdriver.Remote
            A connected Appium driver ready for use.
        """
        merged_config = ConfigLoader.load_merged_config(platform)

        server_url: str = merged_config.get("appium", {}).get("server_url", "http://127.0.0.1:4723")
        capabilities: dict[str, Any] = merged_config.get("capabilities", {})
        implicit_wait: int = merged_config.get("timeouts", {}).get("implicit_wait", 10)

        logger.info("Creating %s driver → %s", platform, server_url)
        logger.debug("Capabilities: %s", capabilities)

        options = AppiumOptions()
        options.load_capabilities(capabilities)

        driver = appium_webdriver.Remote(
            command_executor=server_url,
            options=options,
        )

        driver.implicitly_wait(implicit_wait)

        logger.info("Driver session created: %s", driver.session_id)
        return driver
