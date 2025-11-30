"""
Station registry - defines all available bike counting stations.

Each station maps a short alias to the full counter_site name and associated
weather file city name.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Station:
    """A bike counting station with metadata."""
    
    alias: str
    """Short identifier for the station (e.g., 'tuebingen_tunnel')."""
    
    city: str
    """City name as used in weather file names (e.g., 'tuebingen')."""
    
    counter_name: str
    """Full counter_site name from the eco-counter data."""
    
    display_name: str
    """Human-readable name for plot titles."""
    
    color: str = "#8DD3C7"
    """Default color for this station in plots."""


# =============================================================================
# Station Registry
# =============================================================================

STATIONS: Dict[str, Station] = {
    # Tübingen
    "tuebingen_tunnel": Station(
        alias="tuebingen_tunnel",
        city="tuebingen",
        counter_name="Fuß- & Radtunnel Südportal - Derendinger Allee",
        display_name="Tübingen (Radtunnel)",
        color="#8DD3C7",
    ),
    "tuebingen_steinlach": Station(
        alias="tuebingen_steinlach",
        city="tuebingen",
        counter_name="Unterführung Steinlach/Karlstraße Südseite",
        display_name="Tübingen (Steinlach)",
        color="#8DD3C7",
    ),
    "tuebingen_hirschau": Station(
        alias="tuebingen_hirschau",
        city="tuebingen",
        counter_name="Neckartalradweg Hirschau",
        display_name="Tübingen (Hirschau)",
        color="#8DD3C7",
    ),
    
    # Heidelberg
    "heidelberg_mannheimer": Station(
        alias="heidelberg_mannheimer",
        city="heidelberg",
        counter_name="Mannheimer Straße",
        display_name="Heidelberg (Mannheimer Str.)",
        color="#FB8072",
    ),
    "heidelberg_ploeck": Station(
        alias="heidelberg_ploeck",
        city="heidelberg",
        counter_name="Plöck",
        display_name="Heidelberg (Plöck)",
        color="#FB8072",
    ),
    "heidelberg_ernst_walz": Station(
        alias="heidelberg_ernst_walz",
        city="heidelberg",
        counter_name="Ernst-Walz-Brücke",
        display_name="Heidelberg (Ernst-Walz-Brücke)",
        color="#FB8072",
    ),
    "heidelberg_theodor_heuss": Station(
        alias="heidelberg_theodor_heuss",
        city="heidelberg",
        counter_name="Theodor-Heuss-Brücke",
        display_name="Heidelberg (Theodor-Heuss-Brücke)",
        color="#FB8072",
    ),
    
    # Mannheim
    "mannheim_fernmeldeturm": Station(
        alias="mannheim_fernmeldeturm",
        city="mannheim",
        counter_name="Fernmeldeturm.",
        display_name="Mannheim (Fernmeldeturm)",
        color="#80B1D3",
    ),
    "mannheim_jungbusch": Station(
        alias="mannheim_jungbusch",
        city="mannheim",
        counter_name="Jungbuschbrücke",
        display_name="Mannheim (Jungbuschbrücke)",
        color="#80B1D3",
    ),
    "mannheim_kurpfalz": Station(
        alias="mannheim_kurpfalz",
        city="mannheim",
        counter_name="Kurpfalzbrücke",
        display_name="Mannheim (Kurpfalzbrücke)",
        color="#80B1D3",
    ),
    
    # Stuttgart
    "stuttgart_koenig_karls": Station(
        alias="stuttgart_koenig_karls",
        city="stuttgart",
        counter_name="König-Karls-Brücke Barometer",
        display_name="Stuttgart (König-Karls-Brücke)",
        color="#BEBADA",
    ),
    
    # Freiburg
    "freiburg_wiwili": Station(
        alias="freiburg_wiwili",
        city="freiburg",
        counter_name="Wiwilibrücke",
        display_name="Freiburg (Wiwilibrücke)",
        color="#FDB462",
    ),
    "freiburg_dreisam": Station(
        alias="freiburg_dreisam",
        city="freiburg",
        counter_name="FR1 Dreisam",
        display_name="Freiburg (Dreisam)",
        color="#FDB462",
    ),
}


def get_station(alias: str) -> Station:
    """Get a station by its alias.
    
    Args:
        alias: The short station identifier.
        
    Returns:
        Station: The matching station.
        
    Raises:
        KeyError: If no station with that alias exists.
    """
    if alias not in STATIONS:
        available = ", ".join(sorted(STATIONS.keys()))
        raise KeyError(f"Unknown station '{alias}'. Available: {available}")
    return STATIONS[alias]


def list_stations() -> list[str]:
    """List all available station aliases."""
    return sorted(STATIONS.keys())


def get_stations_by_city(city: str) -> list[Station]:
    """Get all stations for a given city.
    
    Args:
        city: City name (case-insensitive).
        
    Returns:
        List of stations in that city.
    """
    city_lower = city.lower()
    return [s for s in STATIONS.values() if s.city.lower() == city_lower]
