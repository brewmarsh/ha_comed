"""Constants for the ComEd Hourly Pricing integration."""

DOMAIN = "comed_hourly_pricing"

CONF_CURRENT_HOUR_AVERAGE = "current_hour_average"
CONF_FIVE_MINUTE = "five_minute"

FIVE_MINUTE_API_URL = "https://hourlypricing.comed.com/api?type=5minutefeed"
CURRENT_HOUR_AVERAGE_API_URL = "https://hourlypricing.comed.com/api?type=currenthouraverage"
