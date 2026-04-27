"""Config flow for Samsung Soundbar Local."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers import aiohttp_client

from .const import CONF_VERIFY_SSL, DOMAIN
from .soundbar import AsyncSoundbar, SoundbarApiError

_LOGGER = logging.getLogger(__name__)


class SoundbarLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Soundbar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the step when user initiates a flow via the UI."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            verify_ssl = user_input.get(CONF_VERIFY_SSL, False)

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            session = aiohttp_client.async_get_clientsession(
                self.hass, verify_ssl=verify_ssl
            )
            soundbar = AsyncSoundbar(
                host=host, session=session, verify_ssl=verify_ssl
            )
            try:
                await soundbar.create_token()
            except SoundbarApiError as err:
                _LOGGER.warning("Cannot connect to soundbar at %s: %s", host, err)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=host, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_VERIFY_SSL, default=False): bool,
                }
            ),
            errors=errors,
        )
