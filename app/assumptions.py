from collections import namedtuple

Assumption = namedtuple("Assumption", "value description")

HOURLY_WAGE = Assumption(18, "Hourly wage assumed to have this value: {}")
PKG_PRICES = Assumption({"Basic": 100, "Easy": 180, "Medium": 360, "Complex": 680}, "")
PLANNED_HOURS = Assumption({"Basic": 2, "Easy": 4, "Medium": 8, "Complex": 16}, "")
