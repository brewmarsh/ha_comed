"""Support for ComEd Hourly Pricing data."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta

import aiohttp

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_CENT, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CURRENT_HOUR_AVERAGE,
    CONF_FIVE_MINUTE,
    CURRENT_HOUR_AVERAGE_API_URL,
    DOMAIN,
    FIVE_MINUTE_API_URL,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=CONF_FIVE_MINUTE,
        name="ComEd 5 Minute Price",
        native_unit_of_measurement=f"{CURRENCY_CENT}/{UnitOfEnergy.KILO_WATT_HOUR}",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=CONF_CURRENT_HOUR_AVERAGE,
        name="ComEd Current Hour Average Price",
        native_unit_of_measurement=f"{CURRENCY_CENT}/{UnitOfEnergy.KILO_WATT_HOUR}",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ComEd Hourly Pricing sensor."""
    websession = async_get_clientsession(hass)

    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            async with asyncio.timeout(60):
                five_minute_response = await websession.get(FIVE_MINUTE_API_URL)
                five_minute_text = await five_minute_response.text()
                five_minute_data = json.loads(five_minute_text)

                current_hour_average_response = await websession.get(
                    CURRENT_HOUR_AVERAGE_API_URL
                )
                current_hour_average_text = await current_hour_average_response.text()
                current_hour_average_data = json.loads(current_hour_average_text)

                return {
                    CONF_FIVE_MINUTE: float(five_minute_data[0]["price"]),
                    CONF_CURRENT_HOUR_AVERAGE: float(
                        current_hour_average_data[0]["price"]
                    ),
                }
        except (TimeoutError, aiohttp.ClientError, ValueError, KeyError) as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="comed_hourly_pricing",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    entities = [
        ComedHourlyPricingSensor(coordinator, description) for description in SENSOR_TYPES
    ]

    async_add_entities(entities)


class ComedHourlyPricingSensor(SensorEntity):
    """Implementation of a ComEd Hourly Pricing sensor."""

    _attr_attribution = "Data provided by ComEd Hourly Pricing service"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self.coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(self.entity_description.key)
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
