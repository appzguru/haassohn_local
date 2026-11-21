"""Config + options flow."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HaasSohnAuthError, HaasSohnClient, HaasSohnError, number
from .const import (
    CONF_OFF_BEHAVIOR,
    CONF_PIN,
    CONF_SETBACK_TEMP,
    DEFAULT_OFF_BEHAVIOR,
    DEFAULT_SETBACK_TEMP,
    DOMAIN,
    MAX_TEMP,
    MIN_TEMP,
    OFF_BEHAVIOR_POWER,
    OFF_BEHAVIOR_SETBACK,
    TEMP_STEP,
)


class HaasSohnConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ask for host + PIN and verify both."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            client = HaasSohnClient(
                async_get_clientsession(self.hass),
                user_input[CONF_HOST],
                user_input[CONF_PIN],
            )
            try:
                status = await client.get_status()
                # Verify the PIN with a write that changes nothing:
                # re-send the current target temperature.
                await client.send({"sp_temp": number(status["sp_temp"])})
            except HaasSohnAuthError:
                errors["base"] = "invalid_auth"
            except HaasSohnError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(status["meta"]["sn"])
                self._abort_if_unique_id_configured(updates=user_input)
                return self.async_create_entry(
                    title=f"Haas+Sohn {status['meta'].get('typ', '')}".strip(),
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=(user_input or {}).get(CONF_HOST, "")): str,
                vol.Required(CONF_PIN): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return HaasSohnOptionsFlow()


class HaasSohnOptionsFlow(OptionsFlow):
    """What does 'off' mean for the thermostat."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        opts = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_OFF_BEHAVIOR,
                    default=opts.get(CONF_OFF_BEHAVIOR, DEFAULT_OFF_BEHAVIOR),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[OFF_BEHAVIOR_SETBACK, OFF_BEHAVIOR_POWER],
                        translation_key=CONF_OFF_BEHAVIOR,
                    )
                ),
                vol.Required(
                    CONF_SETBACK_TEMP,
                    default=opts.get(CONF_SETBACK_TEMP, DEFAULT_SETBACK_TEMP),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_TEMP,
                        max=MAX_TEMP,
                        step=TEMP_STEP,
                        unit_of_measurement="°C",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
