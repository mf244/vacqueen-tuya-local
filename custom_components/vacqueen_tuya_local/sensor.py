from homeassistant.helpers.entity import Entity
from .const import DOMAIN, BOWLS

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for bowl in BOWLS:
        entities.append(LastManualFeedSensor(coordinator, bowl))
        entities.append(LastScheduledFeedSensor(coordinator, bowl))

    entities.append(LastManualFeedTime(coordinator))
    entities.append(LastScheduledFeedTime(coordinator))

    async_add_entities(entities)


class BaseFeederSensor(Entity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        # 🔴 REQUIRED: subscribe to updates
        coordinator.async_add_listener(self.async_write_ha_state)


class LastManualFeedSensor(BaseFeederSensor):
    def __init__(self, coordinator, bowl):
        super().__init__(coordinator)
        self.bowl = bowl

    @property
    def name(self):
        return f"Feeder Last Manual Feed {self.bowl.capitalize()}"

    @property
    def unique_id(self):
        return f"feeder_last_manual_{self.bowl}"

    @property
    def state(self):
        return self.coordinator.data["last_manual"][self.bowl]


class LastScheduledFeedSensor(BaseFeederSensor):
    def __init__(self, coordinator, bowl):
        super().__init__(coordinator)
        self.bowl = bowl

    @property
    def name(self):
        return f"Feeder Last Scheduled Feed {self.bowl.capitalize()}"

    @property
    def unique_id(self):
        return f"feeder_last_scheduled_{self.bowl}"

    @property
    def state(self):
        return self.coordinator.data["last_scheduled"][self.bowl]


class LastManualFeedTime(BaseFeederSensor):
    @property
    def name(self):
        return "Feeder Last Manual Feed Time"

    @property
    def unique_id(self):
        return "feeder_last_manual_time"

    @property
    def state(self):
        return self.coordinator.data["last_manual"]["time"]


class LastScheduledFeedTime(BaseFeederSensor):
    @property
    def name(self):
        return "Feeder Last Scheduled Feed Time"

    @property
    def unique_id(self):
        return "feeder_last_scheduled_time"

    @property
    def state(self):
        return self.coordinator.data["last_scheduled"]["time"]
