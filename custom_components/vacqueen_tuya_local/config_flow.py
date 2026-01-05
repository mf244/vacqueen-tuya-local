from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_DEVICE_ID, CONF_LOCAL_KEY, CONF_HOST, CONF_VERSION

class VacQueenTuyaLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="VacQueen Tuya (Local)",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_ID): str,
                    vol.Required(CONF_LOCAL_KEY): str,
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_VERSION, default="3.4"): str,
                }
            ),
        )
