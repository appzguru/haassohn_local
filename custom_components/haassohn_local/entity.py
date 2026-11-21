"""Base entity."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HaasSohnCoordinator


class HaasSohnEntity(CoordinatorEntity[HaasSohnCoordinator]):
    """Common device info and unique-id prefix."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HaasSohnCoordinator, key: str) -> None:
        super().__init__(coordinator)
        meta = coordinator.data["meta"]
        serial = meta["sn"]
        self._attr_unique_id = f"{serial}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer="Haas+Sohn",
            model=meta.get("typ"),
            name="Kachel",
            serial_number=serial,
            sw_version=meta.get("sw_version"),
            hw_version=meta.get("hw_version"),
        )
