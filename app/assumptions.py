"""This module houses the various assumptions we made about the data.

Each assumption has a value that's used in computations and a description
which is rendered alongside the plots.
"""
from collections import namedtuple

Assumption = namedtuple("Assumption", "value description")

HOURLY_WAGE = Assumption(18, "Hourly wage assumed to have this value: {}")

# Make sure this stuff stays in sync!
COMPLEXITY_TYPES = Assumption(["Basic", "Easy", "Medium", "Complex"], "")
PKG_PRICES = Assumption({"Basic": 100, "Easy": 180, "Medium": 360, "Complex": 680}, "")
PLANNED_HOURS = Assumption({"Basic": 2, "Easy": 4, "Medium": 8, "Complex": 16}, "")
