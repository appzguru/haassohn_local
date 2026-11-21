"""Thermostat entity ("Kachel").

With off_behavior = setback (default):
- OFF  -> remember the comfort temperature, set target to the setback temp.
          The stove stays on, goes out by itself and only re-ignites when the
          room drops below the setback temperature. Saves ignitions.
- HEAT -> restore the remembered comfort temperature (and power on if needed).
- The thermostat reports OFF when the stove is powered off OR its target is
  at/below the setback temperature, so Google's view stays consistent.

The real power switch (prg) is a separate switch entity.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import HaasSohnConfigEntry
from .api import number
from .const import (
    CONF_OFF_BEHAVIOR,
    CONF_SETBACK_TEMP,
    DEFAULT_COMFORT_TEMP,
    DEFAULT_OFF_BEHAVIOR,
    DEFAULT_SETBACK_TEMP,
    MAX_TEMP,
    MIN_TEMP,
    OFF_BEHAVIOR_SETBACK,
    TEMP_STEP,
)
from .entity import HaasSohnEntity

ATTR_COMFORT = "comfort_temperature"

# Stove modes seen as "actively burning". Unknown modes fall back to IDLE;
# the raw mode is always visible in the "Status" sensor.
HEATING_MODES = {"heating", "ignition", "start", "starting", "heat_up", "preheating"}
OFF_MODES = {"off"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HaasSohnConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([HaasSohnClimate(entry)])


class HaasSohnClimate(HaasSohnEntity, ClimateEntity, RestoreEntity):
    _attr_name = None  # entity takes the device name: "Pelletkachel"
    _attr_translation_key = "stove"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_target_temperature_step = TEMP_STEP
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, entry: HaasSohnConfigEntry) -> None:
        super().__init__(entry.runtime_data, "climate")
        self._entry = entry
        self._comfort = DEFAULT_COMFORT_TEMP

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) and (
            saved := last.attributes.get(ATTR_COMFORT)
        ) is not None:
            self._comfort = float(saved)

    # ---- options -------------------------------------------------------
    @property
    def _setback_mode(self) -> bool:
        return (
            self._entry.options.get(CONF_OFF_BEHAVIOR, DEFAULT_OFF_BEHAVIOR)
            == OFF_BEHAVIOR_SETBACK
        )

    @property
    def _setback_temp(self) -> float:
        return float(self._entry.options.get(CONF_SETBACK_TEMP, DEFAULT_SETBACK_TEMP))

    # ---- state ---------------------------------------------------------
    @property
    def _data(self) -> dict[str, Any]:
        return self.coordinator.data

    @property
    def current_temperature(self) -> float | None:
        return self._data.get("is_temp")

    @property
    def target_temperature(self) -> float | None:
        return self._data.get("sp_temp")

    @property
    def hvac_mode(self) -> HVACMode:
        if not self._data.get("prg"):
            return HVACMode.OFF
        if self._setback_mode and float(self._data.get("sp_temp", 99)) <= self._setback_temp:
            return HVACMode.OFF
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction:
        mode = str(self._data.get("mode", "")).lower()
        if not self._data.get("prg") or mode in OFF_MODES:
            return HVACAction.OFF
        if mode in HEATING_MODES:
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            ATTR_COMFORT: self._comfort,
            "setback_temperature": self._setback_temp,
            "stove_mode": self._data.get("mode"),
        }

    # ---- commands ------------------------------------------------------
    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        temp = round(float(temp))  # stove only accepts whole degrees
        if temp > self._setback_temp:
            self._comfort = float(temp)
        await self.coordinator.async_send({"sp_temp": number(temp)})

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self._turn_off()
        elif hvac_mode == HVACMode.HEAT:
            await self._turn_on()

    async def async_turn_on(self) -> None:
        await self._turn_on()

    async def async_turn_off(self) -> None:
        await self._turn_off()

    async def _turn_off(self) -> None:
        if not self._setback_mode:
            await self.coordinator.async_send({"prg": False})
            return
        current = float(self._data.get("sp_temp", 0))
        if current > self._setback_temp:
            self._comfort = current
        await self.coordinator.async_send({"sp_temp": number(round(self._setback_temp))})

    async def _turn_on(self) -> None:
        if not self._data.get("prg"):
            await self.coordinator.async_send({"prg": True})
        if float(self._data.get("sp_temp", 0)) <= self._setback_temp:
            await self.coordinator.async_send({"sp_temp": number(round(self._comfort))})
