"""Binary sensors."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
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
            HaasSohnProblem(coordinator, "problem"),
            HaasSohnWeekProgram(coordinator, "wprg"),
        ]
    )


class HaasSohnProblem(HaasSohnEntity, BinarySensorEntity):
    _attr_translation_key = "problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("error"))


class HaasSohnWeekProgram(HaasSohnEntity, BinarySensorEntity):
    """Read-only: the stove's own week program. Should stay off; HA schedules."""

    _attr_translation_key = "week_program"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("wprg"))
