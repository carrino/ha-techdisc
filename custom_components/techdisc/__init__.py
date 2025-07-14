"""TechDisc integration for Home Assistant."""
from __future__ import annotations

import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.components.http import StaticPathConfig

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TechDisc from a config entry."""
    hass.data.setdefault(entry.domain, {})[entry.entry_id] = entry.data
    # Serve /techdisc-card/... from ./www/
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/techdisc-card", os.path.join(os.path.dirname(__file__), "www"), True)]
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[entry.domain].pop(entry.entry_id)
    return unload_ok
