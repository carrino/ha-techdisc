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

SCAN_INTERVAL = timedelta(seconds=30)


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
            async with async_timeout.timeout(10):
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
                        
                        # If we get data back, update our timestamp for next request
                        if new_data and "throwTime" in new_data:
                            throw_time = new_data["throwTime"]
                            if "_seconds" in throw_time and "_nanoseconds" in throw_time:
                                # Convert to milliseconds
                                self.last_throw_time_millis = (
                                    throw_time["_seconds"] * 1000 + 
                                    throw_time["_nanoseconds"] // 1000000
                                )
                                _LOGGER.debug(f"Updated last throw time to: {self.last_throw_time_millis}")
                                return new_data
                        
                        # If no new data, return the existing data to avoid clearing sensors
                        if hasattr(self, 'data') and self.data:
                            _LOGGER.debug("No new throw data, keeping existing data")
                            return self.data
                        
                        # First time or no existing data
                        return new_data
                        
        except asyncio.TimeoutError as exception:
            raise UpdateFailed(f"Timeout communicating with API") from exception
        except aiohttp.ClientError as exception:
            raise UpdateFailed(f"Error communicating with API") from exception


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
