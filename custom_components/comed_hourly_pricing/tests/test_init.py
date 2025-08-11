"""Tests for the ComEd Hourly Pricing integration."""
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

import pytest
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
from unittest.mock import patch

from ..const import DOMAIN


@pytest.mark.asyncio
async def test_setup_unload_and_reload_entry(hass: HomeAssistant) -> None:
    """Test setting up and unloading the entry."""
    entry = ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="ComEd Hourly Pricing",
        data={},
        source="user",
        entry_id="1",
        minor_version=1,
        options={},
        unique_id="1234",
        discovery_keys=[],
    )
    await hass.config_entries.async_add(entry)

    with patch(
        "custom_components.comed_hourly_pricing.sensor.async_get_clientsession"
    ), patch(
        "custom_components.comed_hourly_pricing.sensor.DataUpdateCoordinator.async_config_entry_first_refresh"
    ):
        # Set up the component
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED

    # Unload the entry
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
