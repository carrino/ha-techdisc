"""TechDisc sensor platform."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

DOMAIN = "techdisc"

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TechDisc sensor based on a config entry."""
    coordinator = TechDiscDataUpdateCoordinator(hass, config_entry.data[CONF_API_KEY])
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        TechDiscSpeedSensor(coordinator),
        TechDiscDistanceSensor(coordinator),
        TechDiscHyzerAngleSensor(coordinator),
        TechDiscNoseAngleSensor(coordinator),
        TechDiscRotationSensor(coordinator),
        TechDiscLaunchAngleSensor(coordinator),
        TechDiscWobbleSensor(coordinator),
        TechDiscThrowTypeSensor(coordinator),
    ])


class TechDiscDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the TechDisc API."""

    def __init__(self, hass: HomeAssistant, jwt_token: str) -> None:
        """Initialize."""
        self.jwt_token = jwt_token
        self.last_throw_time_millis = None
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with async_timeout.timeout(60):
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "content-type": "application/json",
                        "authorization": f"Bearer {self.jwt_token}"
                    }
                    
                    # Prepare request payload
                    payload = {}
                    if self.last_throw_time_millis is not None:
                        payload = {"lastThrowTimeMillis": self.last_throw_time_millis}
                    
                    async with session.post(
                        "https://play.api.techdisc.com/loadLatestThrow",
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error communicating with API: {response.status}")
                        
                        new_data = await response.json()

                        # Check if it's a meaningful new throw with valid time
                        if new_data and "throwTime" in new_data and \
                           isinstance(new_data.get("throwTime"), dict) and \
                           "_seconds" in new_data["throwTime"] and \
                           "_nanoseconds" in new_data["throwTime"]:

                            throw_time = new_data["throwTime"]
                            # Convert to milliseconds
                            self.last_throw_time_millis = (
                                throw_time["_seconds"] * 1000 +
                                throw_time["_nanoseconds"] // 1000000
                            )
                            _LOGGER.debug(f"New throw received. Updated last throw time to: {self.last_throw_time_millis}")
                            return new_data
                        else:
                            # This means it's an empty response, the minimal timeout payload from server,
                            # or data not conforming to a valid throw. Treat as no new data.
                            _LOGGER.debug("No new valid throw data received, or received minimal/timeout payload from server.")
                            if hasattr(self, 'data') and self.data:
                                # Return existing data, sensors won't change, coordinator won't push update
                                _LOGGER.debug("Returning existing data.")
                                return self.data
                            else:
                                # No existing data and no new valid throw.
                                # Raise UpdateFailed to prevent processing of minimal payload
                                # and to ensure coordinator handles it as a failed attempt to get *new* data.
                            _LOGGER.debug("No existing data and no new valid throw. Returning None.")
                            return None  # No new data, and no old data to fallback to.
                        
        except asyncio.TimeoutError as exception:
            # Log the error but return existing data if available, or None if not.
            # This prevents sensors from becoming unavailable during transient network issues
            # if there's still valid old data.
            _LOGGER.warning(f"Timeout communicating with API: {exception}")
            if hasattr(self, 'data') and self.data:
                _LOGGER.debug("Timeout, but returning existing data.")
                return self.data
            else:
                _LOGGER.debug("Timeout and no existing data. Returning None.")
                return None
        except aiohttp.ClientError as exception:
            # Similar to TimeoutError, attempt to return existing data if a client error occurs.
            _LOGGER.warning(f"ClientError communicating with API: {exception}")
            if hasattr(self, 'data') and self.data:
                _LOGGER.debug("ClientError, but returning existing data.")
                return self.data
            else:
                _LOGGER.debug("ClientError and no existing data. Returning None.")
                return None


class TechDiscSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for TechDisc sensors."""

    def __init__(self, coordinator: TechDiscDataUpdateCoordinator, sensor_type: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_unique_id = f"techdisc_{sensor_type}"
        self._attr_name = f"TechDisc {sensor_type.replace('_', ' ').title()}"


class TechDiscSpeedSensor(TechDiscSensorBase):
    """Speed sensor for TechDisc."""

    def __init__(self, coordinator: TechDiscDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "speed")
        self._attr_unit_of_measurement = "mph"
        self._attr_icon = "mdi:speedometer"

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("speedMph", 0), 1)
        return None


class TechDiscDistanceSensor(TechDiscSensorBase):
    """Distance sensor for TechDisc."""

    def __init__(self, coordinator: TechDiscDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "distance")
        self._attr_unit_of_measurement = "ft"
        self._attr_icon = "mdi:map-marker-distance"

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("estimatedFeet", 0), 1)
        return None


class TechDiscHyzerAngleSensor(TechDiscSensorBase):
    """Hyzer angle sensor for TechDisc."""

    def __init__(self, coordinator: TechDiscDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "hyzer_angle")
        self._attr_unit_of_measurement = "°"
        self._attr_icon = "mdi:angle-acute"

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("correctedHyzerAngle", 0), 1)
        return None


class TechDiscNoseAngleSensor(TechDiscSensorBase):
    """Nose angle sensor for TechDisc."""

    def __init__(self, coordinator: TechDiscDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "nose_angle")
        self._attr_unit_of_measurement = "°"
        self._attr_icon = "mdi:angle-acute"

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("correctedNoseAngle", 0), 1)
        return None


class TechDiscRotationSensor(TechDiscSensorBase):
    """Spin sensor for TechDisc."""

    def __init__(self, coordinator: TechDiscDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "spin")
        self._attr_unit_of_measurement = "rpm"
        self._attr_icon = "mdi:rotate-360"

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            rps = abs(self.coordinator.data.get("rotPerSec", 0))
            # Convert rps to rpm
            return round(rps * 60, 0)
        return None


class TechDiscLaunchAngleSensor(TechDiscSensorBase):
    """Launch angle sensor for TechDisc."""

    def __init__(self, coordinator: TechDiscDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "launch_angle")
        self._attr_unit_of_measurement = "°"
        self._attr_icon = "mdi:slope-uphill"

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("uphillAngle", 0), 1)
        return None


class TechDiscWobbleSensor(TechDiscSensorBase):
    """Wobble sensor for TechDisc."""

    def __init__(self, coordinator: TechDiscDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "wobble")
        self._attr_unit_of_measurement = "°"
        self._attr_icon = "mdi:rotate-3d-variant"

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return round(self.coordinator.data.get("offAxisDegrees", 0), 1)
        return None


class TechDiscThrowTypeSensor(TechDiscSensorBase):
    """Throw type sensor for TechDisc."""

    def __init__(self, coordinator: TechDiscDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "throw_type")
        self._attr_icon = "mdi:disc"

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            primary = self.coordinator.data.get("primaryType", "")
            secondary = self.coordinator.data.get("secondaryType", "")
            if secondary:
                return f"{primary} - {secondary}"
            return primary
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any] | None:
        """Return additional state attributes."""
        if self.coordinator.data:
            return {
                "throw_time": self.coordinator.data.get("throwTime", {}).get("_seconds"),
                "temperature": self.coordinator.data.get("temp"),
                "bearing": self.coordinator.data.get("bearing"),
                "uphill_angle": self.coordinator.data.get("uphillAngle"),
                "off_axis_degrees": self.coordinator.data.get("offAxisDegrees"),
                "estimated_flight_numbers": self.coordinator.data.get("estimatedFlightNumbers"),
                "handedness": self.coordinator.data.get("handedness"),
                "device_id": self.coordinator.data.get("deviceId"),
            }
        return None
