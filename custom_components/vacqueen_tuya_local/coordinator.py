import tinytuya
import base64
import threading
import time
from datetime import datetime
import logging

from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_LOCAL_KEY,
    CONF_VERSION,
    BOWLS,
)

_LOGGER = logging.getLogger(__name__)


def _bits(data: bytes) -> str:
    return "".join(f"{b:08b}" for b in data)


class TuyaFeederCoordinator:
    def __init__(self, hass, config):
        self.hass = hass

        self.device = tinytuya.Device(
            config[CONF_DEVICE_ID],
            config[CONF_HOST],
            config[CONF_LOCAL_KEY],
        )
        self.device.set_version(float(config[CONF_VERSION]))
        self.device.set_socketPersistent(True)
        self.device.set_retry(False)

        self._running = False
        self._thread = None
        self._dp_state = {}

        # Shared HA state
        self.data = {
            "bowls": dict.fromkeys(BOWLS, False),
            "last_manual": dict.fromkeys(BOWLS, 0) | {"time": None},
            "last_scheduled": dict.fromkeys(BOWLS, 0) | {"time": None},
        }

    # -------------------------
    # Lifecycle
    # -------------------------

    async def async_start(self):
        _LOGGER.info("Starting Tuya feeder listener thread")
        self._running = True
        self._thread = threading.Thread(
            target=self._listen_loop,
            name="tuya_feeder_listener",
            daemon=True,
        )
        self._thread.start()

    async def async_stop(self):
        _LOGGER.info("Stopping Tuya feeder listener thread")
        self._running = False

    # -------------------------
    # Thread loop (BLOCKING)
    # -------------------------

    def _listen_loop(self):
        try:
            _LOGGER.info("Connecting to feeder (push mode)")
            self.device.status()
        except Exception as e:
            _LOGGER.error("Initial status failed: %s", e)

        while self._running:
            try:
                data = self.device.receive()
                if not data or "dps" not in data:
                    time.sleep(0.05)
                    continue

                now = datetime.now().isoformat()

                for dp, value in data["dps"].items():
                    if self._dp_state.get(dp) == value:
                        continue
                    self._dp_state[dp] = value

                    if not isinstance(value, str):
                        continue

                    decoded = base64.b64decode(value)

                    # DP 105 — Bowl presence
                    if str(dp) == "105":
                        bits = _bits(decoded)[-3:]
                        self.data["bowls"] = {
                            "left": bits[2] == "1",
                            "center": bits[1] == "1",
                            "right": bits[0] == "1",
                        }

                    # DP 103 — Last MANUAL feed
                    elif str(dp) == "103" and len(decoded) >= 6:
                        self.data["last_manual"].update(
                            dict(zip(BOWLS, decoded[3:6])) | {"time": now}
                        )

                    # DP 104 — Last SCHEDULED feed
                    elif str(dp) == "104" and len(decoded) >= 6:
                        self.data["last_scheduled"].update(
                            dict(zip(BOWLS, decoded[3:6])) | {"time": now}
                        )

                # Push update into HA thread
                self.hass.loop.call_soon_threadsafe(
                    self._notify_ha
                )

            except Exception as e:
                _LOGGER.error("Listener error: %s", e)
                time.sleep(2)

    def _notify_ha(self):
        """Notify HA entities that data changed."""
        for listener in getattr(self, "_listeners", []):
            listener()

    # -------------------------
    # Entity subscription
    # -------------------------

    def async_add_listener(self, listener):
        if not hasattr(self, "_listeners"):
            self._listeners = []
        self._listeners.append(listener)
