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
    """Short identifier for the station (e.g., 'tuebingen_tunnel')."""
    
    station: str
    """City and station name as used in weather file names (e.g., 'tuebingen_radtunnel')."""
    
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
    # Freiburg
    "freiburg_dreisam": Station(
        alias="freiburg_dreisam",
        station="freiburg_dreisam",
        counter_name="FR1 Dreisam / Otto-Wels-Str.",
        display_name="Freiburg (Dreisam)",
        color="#FDB462",
    ),
    "freiburg_eschholz": Station(
        alias="freiburg_eschholz",
        station="freiburg_eschholzstrasse",
        counter_name="FR3 Eschholzstr. / Egonstr. einzeln",
        display_name="Freiburg (Eschholzstraße)",
        color="#FDB462",
    ),
    "freiburg_gueterbahn": Station(
        alias="freiburg_gueterbahn",
        station="freiburg_gueterbahn",
        counter_name="FR2 Güterbahn / Ferd.-Weiß-Str.",
        display_name="Freiburg (Güterbahn)",
        color="#FDB462",
    ),
    "freiburg_wiwili": Station(
        alias="freiburg_wiwili",
        station="freiburg_wiwilibruecke",
        counter_name="Wiwilibrücke",
        display_name="Freiburg (Wiwilibrücke)",
        color="#FDB462",
    ),
    
    # Heidelberg
    "heidelberg_ernst_walz": Station(
        alias="heidelberg_ernst_walz",
        station="heidelberg_ernstwalzbruecke",
        counter_name="Ernst-Walz-Brücke Querschnitte",
        display_name="Heidelberg (Ernst-Walz-Brücke)",
        color="#FB8072",
    ),
    "heidelberg_gaisberg": Station(
        alias="heidelberg_gaisberg",
        station="heidelberg_gaisbergstrasse",
        counter_name="Gaisbergstraße",
        display_name="Heidelberg (Gaisbergstraße)",
        color="#FB8072",
    ),
    "heidelberg_kurfuersten": Station(
        alias="heidelberg_kurfuersten",
        station="heidelberg_kurfuerstenanlage",
        counter_name="Kurfürstenanlage Querschnitt",
        display_name="Heidelberg (Kurfürstenanlage)",
        color="#FB8072",
    ),
    "heidelberg_liebermann": Station(
        alias="heidelberg_liebermann",
        station="heidelberg_liebermannstrasse",
        counter_name="Liebermannstraße",
        display_name="Heidelberg (Liebermannstraße)",
        color="#FB8072",
    ),
    "heidelberg_mannheimer": Station(
        alias="heidelberg_mannheimer",
        station="heidelberg_mannheimerstrasse",
        counter_name="Mannheimer Straße",
        display_name="Heidelberg (Mannheimer Straße)",
        color="#FB8072",
    ),
    "heidelberg_ploeck": Station(
        alias="heidelberg_ploeck",
        station="heidelberg_ploeck",
        counter_name="Plöck",
        display_name="Heidelberg (Plöck)",
        color="#FB8072",
    ),
    "heidelberg_rohrbacher": Station(
        alias="heidelberg_rohrbacher",
        station="heidelberg_rohrbacherstrasse",
        counter_name="Rohrbacher Straße Querschnitt",
        display_name="Heidelberg (Rohrbacher Straße)",
        color="#FB8072",
    ),
    "heidelberg_thedor_heuss": Station(
        alias="heidelberg_thedor_heuss",
        station="heidelberg_theodorheussbruecke",
        counter_name="Thedor-Heuss-Brücke Querschnitt",
        display_name="Heidelberg (Thedor-Heuss-Brücke)",
        color="#8DD3C7",
    ),
    "heidelberg_ziegelhaeuser": Station(
        alias="heidelberg_ziegelhaeuser",
        station="heidelberg_ziegelhaeuser",
        counter_name="Ziegelhäuser Landstraße",
        display_name="Heidelberg (Ziegelhäuser Landstraße)",
        color="#FB8072",
    ),
    "heidelberg_berliner": Station(
        alias="heidelberg_ziegelhaeuser",
        station="heidelberg_berlinerstrasse",
        counter_name="Berliner Straße Querschnitt",
        display_name="Heidelberg (Berliner Straße)",
        color="#FB8072",
    ),
    "heidelberg_eppelheimer": Station(
        alias="heidelberg_eppelheimer",
        station="heidelberg_eppelheimerstrasse",
        counter_name="Eppelheimer Str. Querschnitt",
        display_name="Heidelberg (Eppelheimer Straße)",
        color="#FB8072",
    ),
    
    # Heilbronn
    "heilbronn_neckarufer": Station(
        alias="heilbronn_neckarufer",
        station="heilbronn_neckarufer",
        counter_name="Neckarufer",
        display_name="Heilbronn (Neckarufer)",
        color="#C27EB8",
    ),
    "heilbronn_nord": Station(
        alias="heilbronn_nord",
        station="heilbronn_nord",
        counter_name="Route Nord",
        display_name="Heilbronn (Route Nord)",
        color="#C27EB8",
    ),
    "heilbronn_sued": Station(
        alias="heilbronn_sued",
        station="heilbronn_sued",
        counter_name="Route Süd",
        display_name="Heilbronn (Route Süd)",
        color="#C27EB8",
    ),
    
    # Karlsruhe
    "karlsruhe_erbprinzen": Station(
        alias="karlsruhe_erbprinzen",
        station="karlsruhe_erbprinzenstrasse",
        counter_name="Erbprinzenstraße",
        display_name="Karlsruhe (Erbprinzenstraße)",
        color="#96C488",
    ),
    
    # Kirchheim 
    "kirchheim_barometer": Station(
        alias="kirchheim_barometer",
        station="kirchheim_barometer",
        counter_name="Barometer Kirchheim u. Teck",
        display_name="Kirchheim unter Teck (Barometer)",
        color="#FFB347",
    ),
    
    # Konstanz
    "konstanz_herose": Station(
        alias="konstanz_herose",
        station="konstanz_herosepark",
        counter_name="Herosepark",
        display_name="Konstanz (Herosé-Park)",
        color="#5DC2D1",
    ),
    
    # Lörrach
    "loerrach_berliner": Station(
        alias="loerrach_berliner",
        station="loerrach_berlinerplatz",
        counter_name="Berliner Platz",
        display_name="Lörrach (Berliner Platz)",
        color="#FAA43A",
    ),
    "loerrach_friedhof": Station(
        alias="loerrach_friedhof",
        station="loerrach_hauptfriedhof",
        counter_name="Untere Hartmattenstraße / Hauptfriedhof",
        display_name="Lörrach (Hauptfriedhof)",
        color="#FAA43A",
    ),
    
    # Ludwigsburg
    "ludwigsburg_alleen": Station(
        alias="ludwigsburg_alleen",
        station="ludwigsburg_alleenstrasse",
        counter_name="Alleenstraße",
        display_name="Ludwigsburg (Alleenstraße)",
        color="#DFF15C",
    ),
    "ludwigsburg_favorite": Station(
        alias="ludwigsburg_favorite",
        station="ludwigsburg_favoritepark",
        counter_name="Marbacher Straße - Favoritepark",
        display_name="Ludwigsburg (Favoritepark)",
        color="#DFF15C",
    ),
    "ludwigsburg_neckarbruecke": Station(
        alias="ludwigsburg_neckarbruecke",
        station="ludwigsburg_neckarbruecke",
        counter_name="Marbacher Straße - Neckarbrücke",
        display_name="Ludwigsburg (Neckarbrücke)",
        color="#DFF15C",
    ),
    
    # Mannheim
    "mannheim_jungbusch": Station(
        alias="mannheim_jungbusch",
        station="mannheim_jungbuschbruecke",
        counter_name="Jungbuschbrücke",
        display_name="Mannheim (Jungbuschbrücke)",
        color="#80B1D3",
    ),
    "mannheim_konrad_adenauer": Station(
        alias="mannheim_konrad_adenauer",
        station="mannheim_konradadenauerbruecke",
        counter_name="Konrad-Adenauer-Brücke",
        display_name="Mannheim (Konrad-Adenauer-Brücke)",
        color="#80B1D3",
    ),
     "mannheim_kurpfalz": Station(
        alias="mannheim_kurpfalz",
        station="mannheim_kurpfalzbruecke",
        counter_name="Kurpfalzbrücke",
        display_name="Mannheim (Kurpfalzbrücke)",
        color="#80B1D3",
    ),
    "mannheim_lindenhof": Station(
        alias="mannheim_lindenhof",
        station="mannheim_lindenhofueberfuehrung",
        counter_name="Lindenhofüberführung",
        display_name="Mannheim (Lindenhofüberführung)",
        color="#80B1D3",
    ),
    "mannheim_renz": Station(
        alias="mannheim_renz",
        station="mannheim_renzstrasse",
        counter_name="Renzstraße",
        display_name="Mannheim (Renzstraße)",
        color="#80B1D3",
    ),
    "mannheim_schloss": Station(
        alias="mannheim_schloss",
        station="mannheim_schlosspark",
        counter_name="Schlosspark Lindenhof (Richtung Jugendherberge)",
        display_name="Mannheim (Schlosspark)",
        color="#80B1D3",
    ),
    "mannheim_schwetzinger": Station(
        alias="mannheim_schwetzinger",
        station="mannheim_schwetzingerstrasse",
        counter_name="Neckarauer Übergang -Schwetzinger Str.",
        display_name="Mannheim (Schwetzinger Straße)",
        color="#80B1D3",
    ),
    "mannheim_feudenheimstr_aufwaerts": Station(
        alias="mannheim_feudenheimstr_aufwaerts",
        station="mannheim_feudenheimstr_aufwaerts",
        counter_name="Feudenheimstr. stadtauswärts",
        display_name="Mannheim (Feudenheimstr. stadtauswärts)",
        color="#80B1D3",
    ),
    "mannheim_feudenheimstr_einwaerts": Station(
        alias="mannheim_feudenheimstr_einwaerts",
        station="mannheim_feudenheimstr_einwaerts",
        counter_name="Feudenheimerstr. stadteinwärts",
        display_name="Mannheim (Feudenheimstr. stadteinwärts)",
        color="#80B1D3",
    ),
    "mannheim_luzenbergstr": Station(
        alias="mannheim_luzenbergstr",
        station="mannheim_luzenbergstr",
        counter_name="Luzenbergstr.",
        display_name="Mannheim (Luzenbergstr.)",
        color="#80B1D3",
    ),
    
    # Offenburg
    "offenburg_haupt": Station(
        alias="offenburg_haupt",
        station="offenburg_hauptstrasse",
        counter_name="Hauptstraße neu",
        display_name="Offenburg (Hauptstraße)",
        color="#FB8072",
    ),
    
    # Ravensburg
    "ravensburg_bahnhof": Station(
        alias="ravensburg_bahnhof",
        station="ravensburg_bahnhofstrasse",
        counter_name="08 RV Bahnhofstr.",
        display_name="Ravensburg (Bahnhofstraße)",
        color="#BC80BD",
    ),
    "ravensburg_eishalle": Station(
        alias="ravensburg_eishalle",
        station="ravensburg_eissporthalle",
        counter_name="05 RV Eissporthalle",
        display_name="Ravensburg (Eissporthalle)",
        color="#BC80BD",
    ),
    "ravensburg_meer_ab": Station(
        alias="ravensburg_meer_ab",
        station="ravensburg_meersburgerab",
        counter_name="06 Meersburger Brücke abwärts",
        display_name="Ravensburg (Meersburger Brücke abwärts)",
        color="#BC80BD",
    ),
    "ravensburg_meer_auf": Station(
        alias="ravensburg_meer_auf",
        station="ravensburg_meersburgerauf",
        counter_name="07 Meersburger Brücke aufwärts",
        display_name="Ravensburg (Meersburger Brücke aufwärts)",
        color="#BC80BD",
    ),
    
    # Stuttgart
    "stuttgart_boeblinger": Station(
        alias="stuttgart_boeblinger",
        station="stuttgart_boeblingerstrasse",
        counter_name="Böblinger Straße",
        display_name="Stuttgart (Böblinger Straße)",
        color="#BEBADA",
    ),
    "stuttgart_koenig_karls": Station(
        alias="stuttgart_koenig_karls",
        station="stuttgart_koenigkarlsbruecke",
        counter_name="König-Karls-Brücke Barometer",
        display_name="Stuttgart (König-Karls-Brücke)",
        color="#BEBADA",
    ),
    "stuttgart_taubenheim": Station(
        alias="stuttgart_taubenheim",
        station="stuttgart_taubenheimstrasse",
        counter_name="Taubenheimstraße",
        display_name="Stuttgart (Taubenheimstraße)",
        color="#BEBADA",
    ),
    "stuttgart_waiblinger": Station(
        alias="stuttgart_waiblinger",
        station="stuttgart_waiblingerstrasse",
        counter_name="Waiblinger Straße",
        display_name="Stuttgart (Waiblinger Straße)",
        color="#BEBADA",
    ),
    "stuttgart_samaraweg": Station(
        alias="stuttgart_samaraweg",
        station="stuttgart_samaraweg",
        counter_name="Samaraweg",
        display_name="Stuttgart (Samaraweg)",
        color="#BEBADA",
    ),
    "stuttgart_waldburgstrasse": Station(
        alias="stuttgart_waldburgstrasse",
        station="stuttgart_waldburgstrasse",
        counter_name="Waldburgstraße",
        display_name="Stuttgart (Waldburgstraße)",
        color="#BEBADA",
    ),
    "stuttgart_kremmlerstrasse": Station(
        alias="stuttgart_kremmlerstrasse",
        station="stuttgart_kremmlerstrasse",
        counter_name="Kremmlerstraße",
        display_name="Stuttgart (Kremmlerstraße)",
        color="#BEBADA",
    ),
    "stuttgart_kirchheimer": Station(
        alias="stuttgart_kirchheimer",
        station="stuttgart_kirchheimer",
        counter_name="Kirchheimer Straße",
        display_name="Stuttgart (Kirchheimer Straße)",
        color="#BEBADA",
    ),
    "stuttgart_stuttgarter": Station(
        alias="stuttgart_stuttgarter",
        station="stuttgart_stuttgarter",
        counter_name="Stuttgarter Straße",
        display_name="Stuttgart (Stuttgarter Straße)",
        color="#BEBADA",
    ),
    "stuttgart_solitudestrasse": Station(
        alias="stuttgart_solitudestrasse",
        station="stuttgart_solitudestrasse",
        counter_name="Solitudestraße",
        display_name="Stuttgart (Solitudestraße)",
        color="#BEBADA",
    ),
    "stuttgart_kraehenwald": Station(
        alias="stuttgart_kraehenwald",
        station="stuttgart_kraehenwald",
        counter_name="Am Kräherwald",
        display_name="Stuttgart (Am Kräherwald)",
        color="#BEBADA",
    ),
    "stuttgart_inselstrasse": Station(
        alias="stuttgart_inselstrasse",
        station="stuttgart_inselstrasse",
        counter_name="Inselstraße",
        display_name="Stuttgart (Inselstraße)",
        color="#BEBADA",
    ),
    "stuttgart_neckartalstrasse": Station(
        alias="stuttgart_neckartalstrasse",
        station="stuttgart_neckartalstrasse",
        counter_name="Neckartalstraße",
        display_name="Stuttgart (Neckartalstraße)",
        color="#BEBADA",
    ),
    "stuttgart_lautenschlager": Station(
        alias="stuttgart_lautenschlager",
        station="stuttgart_lautenschlager",
        counter_name="Lautenschlager Straße",
        display_name="Stuttgart (Lautenschlager Straße)",
        color="#BEBADA",
    ),
    "stuttgart_tuebinger": Station(
        alias="stuttgart_tuebinger",
        station="stuttgart_tuebinger",
        counter_name="Tübinger Straße",
        display_name="Stuttgart (Tübinger Straße)",
        color="#BEBADA",
    ),
    
    # Tübingen
    "tuebingen_hirschau": Station(
        alias="tuebingen_hirschau",
        station="tuebingen_hirschau",
        counter_name="Neckartalradweg Hirschau - parallel L371",
        display_name="Tübingen (Hirschau)",
        color="#8DD3C7",
    ),
    "tuebingen_tunnel": Station(
        alias="tuebingen_tunnel",
        station="tuebingen_radtunnel",
        counter_name="Fuß- & Radtunnel Südportal - Derendinger Allee",
        display_name="Tübingen (Radtunnel)",
        color="#8DD3C7",
    ),
    "tuebingen_steinlach": Station(
        alias="tuebingen_steinlach",
        station="tuebingen_steinlachallee",
        counter_name="Unterführung Steinlach/Karlstraße Südseite - Steinlachallee",
        display_name="Tübingen (Steinlach)",
        color="#8DD3C7",
    ),
    
    # Ulm
    "ulm_lupferbruecke": Station(
        alias="ulm_lupferbruecke",
        station="ulm_lupferbruecke",
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
    
    return [s for s in STATIONS.values() if s.station.lower().startswith(city_lower)]


def list_stations_with_weather(base_path: str | Path = ".") -> list[str]:
    """List station aliases that have both bike counter data AND weather data.
    
    Args:
        base_path: Base path to the project directory containing weather_data/.
                   Defaults to current directory.
    
    Returns:
        List of station aliases that have weather data available.
    """
    base = Path(base_path)
    weather_dir = base / "weather_data" / "hourly"
    
    if not weather_dir.exists():
        return []
    
    available_stations = []
    
    for alias, station in STATIONS.items():
        # Weather files are named: weather_{station}.csv
        weather_file = weather_dir / f"weather_{station.station.lower()}.csv"
        
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
    weather_dir = base / "weather_data" / "hourly"
    
    result = {
        'registered': alias in STATIONS,
        'has_weather': False,
    }
    
    if result['registered']:
        station = STATIONS[alias]
        weather_file = weather_dir / f"weather_{station.station.lower()}.csv"
        result['has_weather'] = weather_file.exists()
    
    return result
