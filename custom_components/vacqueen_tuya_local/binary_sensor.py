from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN, BOWLS

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        FeederBowlSensor(coordinator, bowl)
        for bowl in BOWLS
    ]

    async_add_entities(entities)


class FeederBowlSensor(BinarySensorEntity):
    def __init__(self, coordinator, bowl):
        self.coordinator = coordinator
        self.bowl = bowl

        # 🔴 REQUIRED: subscribe to push updates
        coordinator.async_add_listener(self.async_write_ha_state)

    @property
    def name(self):
        return f"Feeder {self.bowl.capitalize()} Bowl"

    @property
    def unique_id(self):
        return f"feeder_bowl_{self.bowl}"

    @property
    def is_on(self):
        return self.coordinator.data["bowls"][self.bowl]
