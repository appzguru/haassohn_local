"""Switches: main power (prg) and eco mode."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HaasSohnConfigEntry
from .entity import HaasSohnEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HaasSohnConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [
            HaasSohnSwitch(coordinator, "prg", "power"),
            HaasSohnSwitch(coordinator, "eco_mode", "eco_mode"),
        ]
    )


class HaasSohnSwitch(HaasSohnEntity, SwitchEntity):
    def __init__(self, coordinator, field: str, translation_key: str) -> None:
        super().__init__(coordinator, field)
        self._field = field
        self._attr_translation_key = translation_key

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(self._field))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_send({self._field: True})

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_send({self._field: False})
