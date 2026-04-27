"""Button entities for Samsung Soundbar Local."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .soundbar import AsyncSoundbar


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities) -> None:
    """Set up button entities from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    soundbar: AsyncSoundbar = data["soundbar"]
    host = entry.data[CONF_HOST]

    async_add_entities(
        [
            SoundbarWooferButton(
                coordinator,
                soundbar,
                host,
                "woofer_plus",
                "Woofer +",
                soundbar.sub_plus,
            ),
            SoundbarWooferButton(
                coordinator,
                soundbar,
                host,
                "woofer_minus",
                "Woofer -",
                soundbar.sub_minus,
            ),
        ],
        True,
    )


class SoundbarWooferButton(CoordinatorEntity, ButtonEntity):
    """Representation of a woofer control button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        soundbar: AsyncSoundbar,
        host: str,
        unique_suffix: str,
        label: str,
        action: Callable[[], Awaitable[None]],
    ) -> None:
        super().__init__(coordinator)
        self._soundbar = soundbar
        self._attr_unique_id = f"{DOMAIN}_{host}_{unique_suffix}"
        self._attr_name = label
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            manufacturer="Samsung",
            model="Soundbar",
            name=f"Soundbar {host}",
        )
        self._action = action

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._action()
        await self.coordinator.async_request_refresh()
