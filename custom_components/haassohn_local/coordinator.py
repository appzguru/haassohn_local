"""Polling coordinator."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HaasSohnClient, HaasSohnError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class HaasSohnCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches the stove status every SCAN_INTERVAL."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: HaasSohnClient
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.get_status()
        except HaasSohnError as err:
            raise UpdateFailed(str(err)) from err

    async def async_send(self, payload: dict[str, Any]) -> None:
        """Send a command and publish the status the stove answers with."""
        new_status = await self.client.send(payload)
        self.async_set_updated_data(new_status)
