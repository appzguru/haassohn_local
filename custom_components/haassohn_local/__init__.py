"""Haas+Sohn pellet stove via the local Wi-Fi module."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HaasSohnClient
from .const import CONF_PIN
from .coordinator import HaasSohnCoordinator

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CLIMATE, Platform.SENSOR, Platform.SWITCH]

type HaasSohnConfigEntry = ConfigEntry[HaasSohnCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: HaasSohnConfigEntry) -> bool:
    client = HaasSohnClient(
        async_get_clientsession(hass), entry.data[CONF_HOST], entry.data[CONF_PIN]
    )
    coordinator = HaasSohnCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: HaasSohnConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: HaasSohnConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
