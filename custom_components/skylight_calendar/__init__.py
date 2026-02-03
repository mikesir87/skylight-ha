"""Skylight Calendar integration for Home Assistant."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry

from .const import DOMAIN
from .skylight_api import SkylightAPI

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Skylight Calendar from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Initialize API client
    api = SkylightAPI()
    await api.authenticate(entry.data["email"], entry.data["password"])
    
    hass.data[DOMAIN][entry.entry_id] = api
    
    # Register service to force update
    async def force_update(call):
        """Force update all Skylight sensors."""
        # Trigger homeassistant.update_entity service for all our entities
        ent_reg = entity_registry.async_get(hass)
        entity_ids = [
            entity_id for entity_id, entity in ent_reg.entities.items()
            if entity.platform == DOMAIN and hass.states.get(entity_id) is not None
        ]
        
        if entity_ids:
            await hass.services.async_call(
                "homeassistant", "update_entity", {"entity_id": entity_ids}
            )
    
    hass.services.async_register(DOMAIN, "force_update", force_update)
    
    await hass.config_entries.async_forward_entry_setups(entry, ["binary_sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["binary_sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        hass.services.async_remove(DOMAIN, "force_update")
    return unload_ok
