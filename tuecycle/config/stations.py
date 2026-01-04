"""
Station registry - defines all available bike counting stations.

Each station maps a short alias to the full counter_site name and associated
weather file city + station name.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Station:
    """A bike counting station with metadata."""

    city: str
    """Name of the city (e.g. 'tuebingen')"""
    
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
        city="freiburg",
        alias="freiburg_dreisam",
        station="freiburg_dreisam",
        counter_name="FR1 Dreisam / Otto-Wels-Str.",
        display_name="Freiburg (Dreisam)",
        color="#FDB462",
    ),
    "freiburg_eschholz": Station(
        city="freiburg",
        alias="freiburg_eschholz",
        station="freiburg_eschholzstrasse",
        counter_name="FR3 Eschholzstr. / Egonstr. einzeln",
        display_name="Freiburg (Eschholzstraße)",
        color="#FDB462",
    ),
    "freiburg_gueterbahn": Station(
        city="freiburg",
        alias="freiburg_gueterbahn",
        station="freiburg_gueterbahn",
        counter_name="FR2 Güterbahn / Ferd.-Weiß-Str.",
        display_name="Freiburg (Güterbahn)",
        color="#FDB462",
    ),
    "freiburg_wiwili": Station(
        city="freiburg",
        alias="freiburg_wiwili",
        station="freiburg_wiwilibruecke",
        counter_name="Wiwilibrücke",
        display_name="Freiburg (Wiwilibrücke)",
        color="#FDB462",
    ),
    
    # Heidelberg
    "heidelberg_ernst_walz": Station(
        city="heidelberg",
        alias="heidelberg_ernst_walz",
        station="heidelberg_ernstwalzbruecke",
        counter_name="Ernst-Walz-Brücke Querschnitte",
        display_name="Heidelberg (Ernst-Walz-Brücke)",
        color="#FB8072",
    ),
    "heidelberg_gaisberg": Station(
        city="heidelberg",
        alias="heidelberg_gaisberg",
        station="heidelberg_gaisbergstrasse",
        counter_name="Gaisbergstraße",
        display_name="Heidelberg (Gaisbergstraße)",
        color="#FB8072",
    ),
    "heidelberg_kurfuersten": Station(
        city="heidelberg",
        alias="heidelberg_kurfuersten",
        station="heidelberg_kurfuerstenanlage",
        counter_name="Kurfürstenanlage Querschnitt",
        display_name="Heidelberg (Kurfürstenanlage)",
        color="#FB8072",
    ),
    "heidelberg_liebermann": Station(
        city="heidelberg",
        alias="heidelberg_liebermann",
        station="heidelberg_liebermannstrasse",
        counter_name="Liebermannstraße",
        display_name="Heidelberg (Liebermannstraße)",
        color="#FB8072",
    ),
    "heidelberg_mannheimer": Station(
        city="heidelberg",
        alias="heidelberg_mannheimer",
        station="heidelberg_mannheimerstrasse",
        counter_name="Mannheimer Straße",
        display_name="Heidelberg (Mannheimer Straße)",
        color="#FB8072",
    ),
    "heidelberg_ploeck": Station(
        city="heidelberg",
        alias="heidelberg_ploeck",
        station="heidelberg_ploeck",
        counter_name="Plöck",
        display_name="Heidelberg (Plöck)",
        color="#FB8072",
    ),
    "heidelberg_rohrbacher": Station(
        city="heidelberg",
        alias="heidelberg_rohrbacher",
        station="heidelberg_rohrbacherstrasse",
        counter_name="Rohrbacher Straße Querschnitt",
        display_name="Heidelberg (Rohrbacher Straße)",
        color="#FB8072",
    ),
    "heidelberg_schlierbacher": Station(
        city="heidelberg",
        alias="heidelberg_schlierbacher",
        station="heidelberg_schlierbacher",
        counter_name="Schlierbacher Landstraße",
        display_name="Heidelberg (Schlierbacher Landstraße)",
        color="#FB8072",
    ),
    "heidelberg_theodor_heuss": Station(
        city="heidelberg",
        alias="heidelberg_theodor_heuss",
        station="heidelberg_theodorheussbruecke",
        counter_name="Theodor-Heuss-Brücke",
        display_name="Heidelberg (Theodor-Heuss-Brücke)",
        color="#FB8072",
    ),
    "heidelberg_ziegelhaeuser": Station(
        city="heidelberg",
        alias="heidelberg_ziegelhaeuser",
        station="heidelberg_ziegelhaeuser",
        counter_name="Ziegelhäuser Landstraße",
        display_name="Heidelberg (Ziegelhäuser Landstraße)",
        color="#FB8072",
    ),
    
    # Heilbronn
    "heilbronn_neckarufer": Station(
        city="heilbronn",
        alias="heilbronn_neckarufer",
        station="heilbronn_neckarufer",
        counter_name="Neckarufer",
        display_name="Heilbronn (Neckarufer)",
        color="#C27EB8",
    ),
    "heilbronn_nord": Station(
        city="heilbronn",
        alias="heilbronn_nord",
        station="heilbronn_nord",
        counter_name="Route Nord",
        display_name="Heilbronn (Route Nord)",
        color="#C27EB8",
    ),
    "heilbronn_sued": Station(
        city="heilbronn",
        alias="heilbronn_sued",
        station="heilbronn_sued",
        counter_name="Route Süd",
        display_name="Heilbronn (Route Süd)",
        color="#C27EB8",
    ),
    
    # Karlsruhe
    "karlsruhe_erbprinzen": Station(
        city="karlsruhe",
        alias="karlsruhe_erbprinzen",
        station="karlsruhe_erbprinzenstrasse",
        counter_name="Erbprinzenstraße",
        display_name="Karlsruhe (Erbprinzenstraße)",
        color="#96C488",
    ),
    
    # Kirchheim 
    "kirchheim_barometer": Station(
        city="kirchheim",
        alias="kirchheim_barometer",
        station="kirchheim_barometer",
        counter_name="Barometer Kirchheim u. Teck",
        display_name="Kirchheim unter Teck (Barometer)",
        color="#FFB347",
    ),
    
    # Konstanz
    "konstanz_herose": Station(
        city="konstanz",
        alias="konstanz_herose",
        station="konstanz_herosepark",
        counter_name="Herosepark",
        display_name="Konstanz (Herosé-Park)",
        color="#5DC2D1",
    ),
    
    # Lörrach
    "loerrach_berliner": Station(
        city="loerrach",
        alias="loerrach_berliner",
        station="loerrach_berlinerplatz",
        counter_name="Berliner Platz",
        display_name="Lörrach (Berliner Platz)",
        color="#FAA43A",
    ),
    "loerrach_friedhof": Station(
        city="loerrach",
        alias="loerrach_friedhof",
        station="loerrach_hauptfriedhof",
        counter_name="Untere Hartmattenstraße / Hauptfriedhof",
        display_name="Lörrach (Hauptfriedhof)",
        color="#FAA43A",
    ),
    
    # Ludwigsburg
    "ludwigsburg_alleen": Station(
        city="ludwigsburg",
        alias="ludwigsburg_alleen",
        station="ludwigsburg_alleenstrasse",
        counter_name="Alleenstraße",
        display_name="Ludwigsburg (Alleenstraße)",
        color="#DFF15C",
    ),
    "ludwigsburg_favorite": Station(
        city="ludwigsburg",
        alias="ludwigsburg_favorite",
        station="ludwigsburg_favoritepark",
        counter_name="Marbacher Straße - Favoritepark",
        display_name="Ludwigsburg (Favoritepark)",
        color="#DFF15C",
    ),
    "ludwigsburg_neckarbruecke": Station(
        city="ludwigsburg",
        alias="ludwigsburg_neckarbruecke",
        station="ludwigsburg_neckarbruecke",
        counter_name="Marbacher Straße - Neckarbrücke",
        display_name="Ludwigsburg (Neckarbrücke)",
        color="#DFF15C",
    ),
    
    # Mannheim
    "mannheim_jungbusch": Station(
        city="mannheim",
        alias="mannheim_jungbusch",
        station="mannheim_jungbuschbruecke",
        counter_name="Jungbuschbrücke",
        display_name="Mannheim (Jungbuschbrücke)",
        color="#80B1D3",
    ),
    "mannheim_konrad_adenauer": Station(
        city="mannheim",
        alias="mannheim_konrad_adenauer",
        station="mannheim_konradadenauerbruecke",
        counter_name="Konrad-Adenauer-Brücke",
        display_name="Mannheim (Konrad-Adenauer-Brücke)",
        color="#80B1D3",
    ),
     "mannheim_kurpfalz": Station(
        city="mannheim",
        alias="mannheim_kurpfalz",
        station="mannheim_kurpfalzbruecke",
        counter_name="Kurpfalzbrücke",
        display_name="Mannheim (Kurpfalzbrücke)",
        color="#80B1D3",
    ),
    "mannheim_lindenhof": Station(
        city="mannheim",
        alias="mannheim_lindenhof",
        station="mannheim_lindenhofueberfuehrung",
        counter_name="Lindenhofüberführung",
        display_name="Mannheim (Lindenhofüberführung)",
        color="#80B1D3",
    ),
    "mannheim_renz": Station(
        city="mannheim",
        alias="mannheim_renz",
        station="mannheim_renzstrasse",
        counter_name="Renzstraße",
        display_name="Mannheim (Renzstraße)",
        color="#80B1D3",
    ),
    "mannheim_schloss": Station(
        city="mannheim",
        alias="mannheim_schloss",
        station="mannheim_schlosspark",
        counter_name="Schlosspark Lindenhof (Richtung Jugendherberge)",
        display_name="Mannheim (Schlosspark)",
        color="#80B1D3",
    ),
    "mannheim_schwetzinger": Station(
        city="mannheim",
        alias="mannheim_schwetzinger",
        station="mannheim_schwetzingerstrasse",
        counter_name="Neckarauer Übergang -Schwetzinger Str..",
        display_name="Mannheim (Schwetzinger Straße)",
        color="#80B1D3",
    ),
    
    # Offenburg
    "offenburg_haupt": Station(
        city="offenburg",
        alias="offenburg_haupt",
        station="offenburg_hauptstrasse",
        counter_name="Hauptstraße neu",
        display_name="Offenburg (Hauptstraße)",
        color="#FB8072",
    ),
    
    # Ravensburg
    "ravensburg_bahnhof": Station(
        city="ravensburg",
        alias="ravensburg_bahnhof",
        station="ravensburg_bahnhofstrasse",
        counter_name="08 RV Bahnhofstr.",
        display_name="Ravensburg (Bahnhofstraße)",
        color="#BC80BD",
    ),
    "ravensburg_eishalle": Station(
        city="ravensburg",
        alias="ravensburg_eishalle",
        station="ravensburg_eissporthalle",
        counter_name="05 RV Eissporthalle",
        display_name="Ravensburg (Eissporthalle)",
        color="#BC80BD",
    ),
    "ravensburg_meer_ab": Station(
        city="ravensburg",
        alias="ravensburg_meer_ab",
        station="ravensburg_meersburgerab",
        counter_name="06 Meersburger Brücke abwärts",
        display_name="Ravensburg (Meersburger Brücke abwärts)",
        color="#BC80BD",
    ),
    "ravensburg_meer_auf": Station(
        city="ravensburg",
        alias="ravensburg_meer_auf",
        station="ravensburg_meersburgerauf",
        counter_name="07 Meersburger Brücke aufwärts",
        display_name="Ravensburg (Meersburger Brücke aufwärts)",
        color="#BC80BD",
    ),
    
    # Stuttgart
    "stuttgart_boeblinger": Station(
        city="stuttgart",
        alias="stuttgart_boeblinger",
        station="stuttgart_boeblingerstrasse",
        counter_name="Böblinger Straße",
        display_name="Stuttgart (Böblinger Straße)",
        color="#BEBADA",
    ),
    "stuttgart_koenig_karls": Station(
        city="stuttgart",
        alias="stuttgart_koenig_karls",
        station="stuttgart_koenigkarlsbruecke",
        counter_name="König-Karls-Brücke Barometer",
        display_name="Stuttgart (König-Karls-Brücke)",
        color="#BEBADA",
    ),
    "stuttgart_taubenheim": Station(
        city="stuttgart",
        alias="stuttgart_taubenheim",
        station="stuttgart_taubenheimstrasse",
        counter_name="Taubenheimstraße",
        display_name="Stuttgart (Taubenheimstraße)",
        color="#BEBADA",
    ),
    "stuttgart_waiblinger": Station(
        city="stuttgart",
        alias="stuttgart_waiblinger",
        station="stuttgart_waiblingerstrasse",
        counter_name="Waiblinger Straße",
        display_name="Stuttgart (Waiblinger Straße)",
        color="#BEBADA",
    ),
    
    # Tübingen
    "tuebingen_hirschau": Station(
        city="tuebingen",
        alias="tuebingen_hirschau",
        station="tuebingen_hirschau",
        counter_name="Neckartalradweg Hirschau",
        display_name="Tübingen (Hirschau)",
        color="#8DD3C7",
    ),
    "tuebingen_tunnel": Station(
        city="tuebingen",
        alias="tuebingen_tunnel",
        station="tuebingen_radtunnel",
        counter_name="Fuß- & Radtunnel Südportal - Derendinger Allee",
        display_name="Tübingen (Radtunnel)",
        color="#8DD3C7",
    ),
    "tuebingen_steinlach": Station(
        city="tuebingen",
        alias="tuebingen_steinlach",
        station="tuebingen_steinlachallee",
        counter_name="Unterführung Steinlach/Karlstraße Südseite",
        display_name="Tübingen (Steinlach)",
        color="#8DD3C7",
    ),
    
    # Ulm
    "ulm_lupferbruecke": Station(
        city="ulm",
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
