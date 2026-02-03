"""Skylight Calendar platform."""
import logging
from datetime import timedelta
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Skylight Calendar binary sensors."""
    api = hass.data[DOMAIN][config_entry.entry_id]
    
    # Get categories (people)
    categories = await api.get_categories()
    _LOGGER.debug("Found %d categories", len(categories))
    
    entities = []
    for category in categories:
        if category.get("attributes", {}).get("linked_to_profile"):
            _LOGGER.debug("Creating sensor for category: %s", category['attributes']['label'])
            entities.append(SkylightTaskCompletionSensor(api, category))
    
    _LOGGER.debug("Adding %d entities", len(entities))
    async_add_entities(entities)

class SkylightTaskCompletionSensor(BinarySensorEntity):
    """Binary sensor for task completion status by category."""

    def __init__(self, api, category) -> None:
        """Initialize the sensor."""
        self._api = api
        self._category = category
        self._attr_name = f"{category['attributes']['label']} Tasks Complete"
        self._attr_unique_id = f"{DOMAIN}_{category['id']}_tasks_complete"
        self._attr_device_class = "connectivity"
        self._is_on = None

    @property
    def is_on(self) -> bool | None:
        """Return true if tasks are complete."""
        return self._is_on

    async def async_update(self) -> None:
        """Update the sensor."""
        _LOGGER.debug("Updating sensor for category %s", self._category['attributes']['label'])
        try:
            self._is_on = await self._api.check_category_completion(self._category["id"])
            _LOGGER.debug("Category %s completion status: %s", self._category['attributes']['label'], self._is_on)
        except Exception as e:
            _LOGGER.error("Error updating sensor for category %s: %s", self._category['attributes']['label'], e)
            self._is_on = None
