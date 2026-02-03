"""Config flow for Skylight Calendar integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .skylight_api import SkylightAPI

_LOGGER = logging.getLogger(__name__)

class SkylightCalendarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Skylight Calendar."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        _LOGGER.debug("Config flow step_user called")
        errors = {}
        
        if user_input is not None:
            try:
                api = SkylightAPI()
                await api.authenticate(user_input["email"], user_input["password"])
                return self.async_create_entry(title="Skylight Calendar", data=user_input)
            except Exception as e:
                _LOGGER.error("Authentication failed: %s", e)
                errors["base"] = "auth_error"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("email"): str,
                vol.Required("password"): str,
            }),
            errors=errors
        )
