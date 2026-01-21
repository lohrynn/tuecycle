"""
tuecycle - Bicycle counting analysis with weather data.

A modular package for loading, caching, and visualizing bicycle counting data
merged with weather information for German cities.
"""

from tuecycle.data.loader import DataManager
from tuecycle.config.stations import Station, STATIONS, get_station, list_stations

__version__ = "0.1.0"

__all__ = [
    "DataManager",
    "Station",
    "STATIONS", 
    "get_station",
    "list_stations"
]
