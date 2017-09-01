from collections import namedtuple

Assumption = namedtuple("Assumption", "value description")

HOURLY_WAGE = Assumption(18, "Hourly wage assumed to have this value: {}")
