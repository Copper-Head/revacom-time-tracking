from collections import namedtuple

Assumption = namedtuple("Assumption", "value description")

HOURLY_WAGE = Assumption(18, "Hourly wage assumed to have this value: {}")
PKG_PRICES = Assumption({"Basic": 100, "Easy": 180, "Medium": 360, "Complex": 680}, "")
