"""Constants for the Haas+Sohn local integration."""

from datetime import timedelta

DOMAIN = "haassohn_local"

CONF_PIN = "pin"
CONF_SETBACK_TEMP = "setback_temp"
CONF_OFF_BEHAVIOR = "off_behavior"

OFF_BEHAVIOR_SETBACK = "setback"  # "uit" = doeltemperatuur naar spaarstand, kachel blijft aan
OFF_BEHAVIOR_POWER = "power"  # "uit" = kachel echt uitschakelen (prg = false)

DEFAULT_SETBACK_TEMP = 17.0
DEFAULT_COMFORT_TEMP = 21.0
DEFAULT_OFF_BEHAVIOR = OFF_BEHAVIOR_SETBACK

MIN_TEMP = 10.0
MAX_TEMP = 30.0
TEMP_STEP = 0.5

SCAN_INTERVAL = timedelta(seconds=30)
