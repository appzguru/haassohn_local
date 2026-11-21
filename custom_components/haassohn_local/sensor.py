"""Sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfMass, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HaasSohnConfigEntry
from .entity import HaasSohnEntity


@dataclass(frozen=True, kw_only=True)
class HaasSohnSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[HaasSohnSensorDescription, ...] = (
    HaasSohnSensorDescription(
        key="is_temp",
        translation_key="room_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda d: d.get("is_temp"),
    ),
    HaasSohnSensorDescription(
        key="sp_temp",
        translation_key="target_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda d: d.get("sp_temp"),
    ),
    HaasSohnSensorDescription(
        key="mode",
        translation_key="mode",
        value_fn=lambda d: d.get("mode"),
    ),
    HaasSohnSensorDescription(
        key="error",
        translation_key="error",
        value_fn=lambda d: ", ".join(str(e) for e in d.get("error") or []) or "geen",
    ),
    HaasSohnSensorDescription(
        key="consumption",
        translation_key="consumption",
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        value_fn=lambda d: d.get("consumption"),
    ),
    HaasSohnSensorDescription(
        key="maintenance_in",
        translation_key="maintenance_in",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        value_fn=lambda d: d.get("maintenance_in"),
    ),
    HaasSohnSensorDescription(
        key="cleaning_in",
        translation_key="cleaning_in",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        value_fn=lambda d: d.get("cleaning_in"),
    ),
    HaasSohnSensorDescription(
        key="ignitions",
        translation_key="ignitions",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("ignitions"),
    ),
    HaasSohnSensorDescription(
        key="on_time",
        translation_key="on_time",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("on_time"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HaasSohnConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(HaasSohnSensor(coordinator, desc) for desc in SENSORS)


class HaasSohnSensor(HaasSohnEntity, SensorEntity):
    entity_description: HaasSohnSensorDescription

    def __init__(self, coordinator, description: HaasSohnSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)
