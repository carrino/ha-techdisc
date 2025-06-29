"""Config flow for TechDisc integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

DOMAIN = "techdisc"

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    jwt_token = data[CONF_API_KEY]
    
    async with aiohttp.ClientSession() as session:
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {jwt_token}"
        }
        try:
            async with session.post(
                "https://play.api.techdisc.com/loadLatestThrow",
                headers=headers,
                json={}
            ) as response:
                if response.status != 200:
                    raise InvalidAuth
                
                data = await response.json()
                if "id" not in data:
                    raise InvalidAuth
                    
        except aiohttp.ClientError as err:
            raise CannotConnect from err

    return {"title": "TechDisc"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TechDisc."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return await self.async_create_entry(
                    title=info["title"], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_create_entry(self, *, title, data):
        """Create the config entry and notify user exactly once on install."""
        hass = self.hass

        hass.async_create_task(
            hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "TechDisc Setup",
                    "message": (
                        "TechDisc has been installed.\n\n"
                        "**Next Step:**\n"
                        "Please add this Lovelace resource:\n\n"
                        "`/techdisc-card/techdisc-card.js`\n\n"
                        "[Click here to open Lovelace Resources](https://my.home-assistant.io/redirect/lovelace_resources/)\n\n"
                        "**Type:** JavaScript Module\n\n"
                        "Then refresh your browser."
                    ),
                    "notification_id": "techdisc_setup"
                }
            )
        )

        # This calls the normal base class behavior
        return await super().async_create_entry(title=title, data=data)

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
