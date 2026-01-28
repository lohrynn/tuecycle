"""
Station registry - defines all available bike counting stations.

Each station maps a short alias to the full counter_site name and associated
weather file city + station name.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class Station:
    """A bike counting station with metadata."""
    
    alias: str
    """Short identifier for the station as used in weather file name (e.g., 'tuebingen_tunnel')."""
    
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
    "freiburg_eschholz": Station(
        alias="freiburg_eschholz",
        counter_name="FR3 Eschholzstr. / Egonstr. einzeln",
        display_name="Freiburg (Eschholzstraße)",
        color="#FDB462",
    ),
    "freiburg_gueterbahn": Station(
        alias="freiburg_gueterbahn",
        counter_name="FR2 Güterbahn / Ferd.-Weiß-Str.",
        display_name="Freiburg (Güterbahn)",
        color="#FDB462",
    ),
    "freiburg_wiwili": Station(
        alias="freiburg_wiwili",
        counter_name="Wiwilibrücke",
        display_name="Freiburg (Wiwilibrücke)",
        color="#FDB462",
    ),
    
    # Heidelberg
    "heidelberg_berliner": Station(
        alias="heidelberg_berliner",
        counter_name="Berliner Straße Querschnitt",
        display_name="Heidelberg (Berliner Straße)",
        color="#FB8072",
    ),
    "heidelberg_eppelheimer": Station(
        alias="heidelberg_eppelheimer",
        counter_name="Eppelheimer Str. Querschnitt",
        display_name="Heidelberg (Eppelheimer Straße)",
        color="#FB8072",
    ),
    "heidelberg_kurfuersten": Station(
        alias="heidelberg_kurfuersten",
        counter_name="Kurfürstenanlage Querschnitt",
        display_name="Heidelberg (Kurfürstenanlage)",
        color="#FB8072",
    ),
    "heidelberg_liebermann": Station(
        alias="heidelberg_liebermann",
        counter_name="Liebermannstraße",
        display_name="Heidelberg (Liebermannstraße)",
        color="#FB8072",
    ),
    # "heidelberg_mannheimer": Station(
    #     alias="heidelberg_mannheimer",
    #     counter_name="Mannheimer Straße",
    #     display_name="Heidelberg (Mannheimer Straße)",
    #     color="#FB8072",
    # ),
    "heidelberg_ploeck": Station(
        alias="heidelberg_ploeck",
        counter_name="Plöck",
        display_name="Heidelberg (Plöck)",
        color="#FB8072",
    ),
    "heidelberg_rohrbacher": Station(
        alias="heidelberg_rohrbacher",
        counter_name="Rohrbacher Straße Querschnitt",
        display_name="Heidelberg (Rohrbacher Straße)",
        color="#FB8072",
    ),
    "heidelberg_theodor_heuss": Station(
        alias="heidelberg_theodor_heuss",
        counter_name="Thedor-Heuss-Brücke Querschnitt",
        display_name="Heidelberg (Theodor-Heuss-Brücke)",
        color="#FB8072",
    ),
    
    # Heilbronn
    "heilbronn_neckarufer": Station(
        alias="heilbronn_neckarufer",
        counter_name="Neckarufer",
        display_name="Heilbronn (Neckarufer)",
        color="#C27EB8",
    ),
    "heilbronn_nord": Station(
        alias="heilbronn_nord",
        counter_name="Route Nord",
        display_name="Heilbronn (Route Nord)",
        color="#C27EB8",
    ),
    "heilbronn_sued": Station(
        alias="heilbronn_sued",
        counter_name="Route Süd",
        display_name="Heilbronn (Route Süd)",
        color="#C27EB8",
    ),
    
    # Karlsruhe
    "karlsruhe_erbprinzen": Station(
        alias="karlsruhe_erbprinzen",
        counter_name="Erbprinzenstraße",
        display_name="Karlsruhe (Erbprinzenstraße)",
        color="#96C488",
    ),
    
    # Kirchheim 
    "kirchheim_barometer": Station(
        alias="kirchheim_barometer",
        counter_name="Barometer Kirchheim u. Teck",
        display_name="Kirchheim unter Teck (Barometer)",
        color="#FFB347",
    ),
    
    # Konstanz
    "konstanz_herose": Station(
        alias="konstanz_herose",
        counter_name="Herosepark",
        display_name="Konstanz (Herosé-Park)",
        color="#5DC2D1",
    ),
    
    # Lörrach
    "loerrach_berliner": Station(
        alias="loerrach_berliner",
        counter_name="Berliner Platz",
        display_name="Lörrach (Berliner Platz)",
        color="#FAA43A",
    ),
    "loerrach_friedhof": Station(
        alias="loerrach_friedhof",
        counter_name="Untere Hartmattenstraße / Hauptfriedhof",
        display_name="Lörrach (Hauptfriedhof)",
        color="#FAA43A",
    ),
    
    # Ludwigsburg
    "ludwigsburg_alleen": Station(
        alias="ludwigsburg_alleen",
        counter_name="Alleenstraße",
        display_name="Ludwigsburg (Alleenstraße)",
        color="#DFF15C",
    ),
    "ludwigsburg_favorite": Station(
        alias="ludwigsburg_favorite",
        counter_name="Marbacher Straße - Favoritepark",
        display_name="Ludwigsburg (Favoritepark)",
        color="#DFF15C",
    ),
    # "ludwigsburg_neckarbruecke": Station(
    #     alias="ludwigsburg_neckarbruecke",
    #     counter_name="Marbacher Straße - Neckarbrücke",
    #     display_name="Ludwigsburg (Neckarbrücke)",
    #     color="#DFF15C",
    # ),
    
    # Mannheim
    # "mannheim_feudenheimstr_aus": Station(
    #     alias="mannheim_feudenheimstr_aus",
    #     counter_name="Feudenheimstr. stadtauswärts",
    #     display_name="Mannheim (Feudenheimstr. stadtauswärts)",
    #     color="#80B1D3",
    # ),
    # "mannheim_feudenheimstr_ein": Station(
    #     alias="mannheim_feudenheimstr_ein",
    #     counter_name="Feudenheimerstr. stadteinwärts",
    #     display_name="Mannheim (Feudenheimstr. stadteinwärts)",
    #     color="#80B1D3",
    # ),
    "mannheim_jungbusch": Station(
        alias="mannheim_jungbusch",
        counter_name="Jungbuschbrücke",
        display_name="Mannheim (Jungbuschbrücke)",
        color="#80B1D3",
    ),
    "mannheim_konrad_adenauer": Station(
        alias="mannheim_konrad_adenauer",
        counter_name="Konrad-Adenauer-Brücke",
        display_name="Mannheim (Konrad-Adenauer-Brücke)",
        color="#80B1D3",
    ),
     "mannheim_kurpfalz": Station(
        alias="mannheim_kurpfalz",
        counter_name="Kurpfalzbrücke",
        display_name="Mannheim (Kurpfalzbrücke)",
        color="#80B1D3",
    ),
    "mannheim_lindenhof": Station(
        alias="mannheim_lindenhof",
        counter_name="Lindenhofüberführung",
        display_name="Mannheim (Lindenhofüberführung)",
        color="#80B1D3",
    ),
    "mannheim_luzenberg": Station(
        alias="mannheim_luzenberg",
        counter_name="Luzenbergstr.",
        display_name="Mannheim (Luzenbergstr.)",
        color="#80B1D3",
    ),
    "mannheim_renz": Station(
        alias="mannheim_renz",
        counter_name="Renzstraße",
        display_name="Mannheim (Renzstraße)",
        color="#80B1D3",
    ),
    "mannheim_schlosspark": Station(
        alias="mannheim_schlosspark",
        counter_name="Schlosspark Lindenhof (Richtung Jugendherberge)",
        display_name="Mannheim (Schlosspark)",
        color="#80B1D3",
    ),
    "mannheim_schwetzinger": Station(
        alias="mannheim_schwetzinger",
        counter_name="Neckarauer Übergang -Schwetzinger Str.",
        display_name="Mannheim (Schwetzinger Straße)",
        color="#80B1D3",
    ),
    
    # Ravensburg
    "ravensburg_bahnhof": Station(
        alias="ravensburg_bahnhof",
        counter_name="08 RV Bahnhofstr.",
        display_name="Ravensburg (Bahnhofstraße)",
        color="#BC80BD",
    ),
    "ravensburg_eishalle": Station(
        alias="ravensburg_eishalle",
        counter_name="05 RV Eissporthalle",
        display_name="Ravensburg (Eissporthalle)",
        color="#BC80BD",
    ),
    "ravensburg_meer_ab": Station(
        alias="ravensburg_meer_ab",
        counter_name="06 Meersburger Brücke abwärts",
        display_name="Ravensburg (Meersburger Brücke abwärts)",
        color="#BC80BD",
    ),
    "ravensburg_meer_auf": Station(
        alias="ravensburg_meer_auf",
        counter_name="07 Meersburger Brücke aufwärts",
        display_name="Ravensburg (Meersburger Brücke aufwärts)",
        color="#BC80BD",
    ),
    
    # Stuttgart
    # "stuttgart_boeblinger": Station(
    #     alias="stuttgart_boeblinger",
    #     counter_name="Böblinger Straße",
    #     display_name="Stuttgart (Böblinger Straße)",
    #     color="#BEBADA",
    # ),
    "stuttgart_insel": Station(
        alias="stuttgart_insel",
        counter_name="Inselstraße",
        display_name="Stuttgart (Inselstraße)",
        color="#BEBADA",
    ),
    # "stuttgart_kirchheimer": Station(
    #     alias="stuttgart_kirchheimer",
    #     counter_name="Kirchheimer Straße",
    #     display_name="Stuttgart (Kirchheimer Straße)",
    #     color="#BEBADA",
    # ),
    "stuttgart_koenig_karls": Station(
        alias="stuttgart_koenig_karls",
        counter_name="König-Karls-Brücke Barometer",
        display_name="Stuttgart (König-Karls-Brücke)",
        color="#BEBADA",
    ),
    "stuttgart_kraeherwald": Station(
        alias="stuttgart_kraeherwald",
        counter_name="Am Kräherwald",
        display_name="Stuttgart (Am Kräherwald)",
        color="#BEBADA",
    ),
    # "stuttgart_kremmler": Station(
    #     alias="stuttgart_kremmler",
    #     counter_name="Kremmlerstraße",
    #     display_name="Stuttgart (Kremmlerstraße)",
    #     color="#BEBADA",
    # ),
    "stuttgart_lautenschlager": Station(
        alias="stuttgart_lautenschlager",
        counter_name="Lautenschlager Straße",
        display_name="Stuttgart (Lautenschlager Straße)",
        color="#BEBADA",
    ),
    # "stuttgart_neckartal": Station(
    #     alias="stuttgart_neckartal",
    #     counter_name="Neckartalstraße",
    #     display_name="Stuttgart (Neckartalstraße)",
    #     color="#BEBADA",
    # ),
    "stuttgart_samara": Station(
        alias="stuttgart_samara",
        counter_name="Samaraweg",
        display_name="Stuttgart (Samaraweg)",
        color="#BEBADA",
    ),
    # "stuttgart_solitude": Station(
    #     alias="stuttgart_solitude",
    #     counter_name="Solitudestraße",
    #     display_name="Stuttgart (Solitudestraße)",
    #     color="#BEBADA",
    # ),
    "stuttgart_stuttgarter": Station(
        alias="stuttgart_stuttgarter",
        counter_name="Stuttgarter Straße",
        display_name="Stuttgart (Stuttgarter Straße)",
        color="#BEBADA",
    ),
    "stuttgart_taubenheim": Station(
        alias="stuttgart_taubenheim",
        counter_name="Taubenheimstraße",
        display_name="Stuttgart (Taubenheimstraße)",
        color="#BEBADA",
    ),
    "stuttgart_waiblinger": Station(
        alias="stuttgart_waiblinger",
        counter_name="Waiblinger Straße",
        display_name="Stuttgart (Waiblinger Straße)",
        color="#BEBADA",
    ),
    # "stuttgart_waldburg": Station(
    #     alias="stuttgart_waldburg",
    #     counter_name="Waldburgstraße",
    #     display_name="Stuttgart (Waldburgstraße)",
    #     color="#BEBADA",
    # ),
    "stuttgart_tuebinger": Station(
        alias="stuttgart_tuebinger",
        counter_name="Tübinger Straße",
        display_name="Stuttgart (Tübinger Straße)",
        color="#BEBADA",
    ),
    
    # Tübingen
    # "tuebingen_hirschau": Station(
    #     alias="tuebingen_hirschau",
    #     counter_name="Neckartalradweg Hirschau - parallel L371",
    #     display_name="Tübingen (Hirschau)",
    #     color="#8DD3C7",
    # ),
    "tuebingen_tunnel": Station(
        alias="tuebingen_tunnel",
        counter_name="Fuß- & Radtunnel Südportal - Derendinger Allee",
        display_name="Tübingen (Radtunnel)",
        color="#8DD3C7",
    ),
    "tuebingen_steinlach": Station(
        alias="tuebingen_steinlach",
        counter_name="Unterführung Steinlach/Karlstraße Südseite - Steinlachallee",
        display_name="Tübingen (Steinlach)",
        color="#8DD3C7",
    ),
    
    # Ulm
    "ulm_lupfer": Station(
        alias="ulm_lupfer",
        counter_name="Blautal Lupferbrücke",
        display_name="Ulm (Lupferbrücke)",
        color="#FFFFB3",
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
    
    # Normalize alias to match keys
    station = alias.lower().replace(" ", "_").replace("-", "_").replace("ß", "ss").replace("ü", "ue").replace("ä", "ae").replace("ö", "oe")
    
    if station not in STATIONS:
        available = ", ".join(sorted(STATIONS.keys()))
        raise KeyError(f"Unknown station '{alias}'. Available: {available}")
    return STATIONS[station]

def list_stations() -> list[str]:
    """List all available station aliases."""
    return list(STATIONS.keys())


def get_stations_by_city(city: str) -> list[Station]:
    """Get all stations for a given city.
    
    Args:
        city: City name (case-insensitive).
        
    Returns:
        List of stations in that city.
    """
    city_lower = city.lower()
    
    # Map ä,ö,ü to ae,oe,ue for matching
    city_lower = city_lower.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    
    return [s for s in STATIONS.values() if s.alias.lower().startswith(city_lower)]


def list_stations_with_weather(base_path: str | Path = ".") -> list[str]:
    """List station aliases that have both bike counter data AND weather data.
    
    Args:
        base_path: Base path to the project directory containing data/weather_data/.
                   Defaults to current directory.
    
    Returns:
        List of station aliases that have weather data available.
    """
    base = Path(base_path)
    weather_dir = base / "data" / "weather_data" / "hourly"
    
    if not weather_dir.exists():
        return []
    
    available_stations = []
    
    for alias, station in STATIONS.items():
        # Weather files are named: weather_{station}.csv
        weather_file = weather_dir / f"weather_{station.alias.lower()}.csv"
        
        if weather_file.exists():
            available_stations.append(alias)
    
    return available_stations


def check_station_data_availability(alias: str, base_path: str | Path = ".") -> dict[str, bool]:
    """Check what data is available for a specific station.
    
    Args:
        alias: Station alias to check.
        base_path: Base path to the project directory.
        
    Returns:
        Dictionary with keys 'registered', 'has_weather' indicating availability.
    """
    base = Path(base_path)
    weather_dir = base / "data" / "weather_data" / "hourly"
    
    result = {
        'registered': alias in STATIONS,
        'has_weather': False,
    }
    
    if result['registered']:
        station = STATIONS[alias]
        weather_file = weather_dir / f"weather_{station.alias.lower()}.csv"
        result['has_weather'] = weather_file.exists()
    
    return result
