"""Config flow for TechDisc."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
    }
)

async def validate_api_key(hass: HomeAssistant, api_key: str) -> bool:
    """Validate the API key. Placeholder for actual validation."""
    # Here you would typically make a test call to the API.
    # For this example, we'll assume any non-empty key is valid.
    _LOGGER.info("Placeholder API key validation called for TechDisc.")
    # Replace with actual validation logic if possible
    if not api_key:
        return False
    # Example: try to connect to TechDisc API or a specific endpoint
    # For now, just returning True if api_key is not empty
    return True

class TechDiscConfigFlow(ConfigFlow, domain="techdisc"):
    """Handle a config flow for TechDisc."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user initiation."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY]

            # For unique ID, typically you'd derive this from device information
            # or account details obtained via the API key.
            # Using a static string like "techdisc_unique_id" means only one instance
            # can be configured. If your API key is globally unique for a user/device,
            # you could potentially use a hash of it or a device ID returned by validation.
            # For simplicity here, using a static one.
            await self.async_set_unique_id("techdisc_default_unique_id") # Consider making this more dynamic if needed
            self._abort_if_unique_id_configured()

            if await validate_api_key(self.hass, api_key):
                return self.async_create_entry(
                    title="TechDisc",  # This title will be shown in the integrations list
                    data={CONF_API_KEY: api_key}
                )
            else:
                errors["base"] = "invalid_auth" # This will show "Invalid authentication"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
