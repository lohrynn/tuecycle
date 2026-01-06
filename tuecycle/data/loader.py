"""
Data loading and caching for bike counter and weather data.

The DataManager class provides:
- Automatic Parquet caching for fast repeated access
- Lazy loading of data on first access
- Merging bike counts with weather data
- Support for multiple stations and date ranges
"""

import glob
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

from tuecycle.config.stations import Station, get_station, STATIONS


class DataManager:
    """Manages loading, caching, and access to bike/weather data.
    
    Data is cached as Parquet files for fast repeated access. The first load
    reads from CSVs and creates the cache; subsequent loads read from Parquet.
    
    Example:
        >>> dm = DataManager()
        >>> df = dm.get("tuebingen_tunnel")
        >>> df.head()
        
        # Load multiple stations at once
        >>> data = dm.get_multiple(["tuebingen_tunnel", "heidelberg_mannheimer"])
    """
    
    def __init__(
        self,
        base_path: str | Path = ".",
        cache_dir: str | Path = "cache",
        start_date: Tuple[int, int, int] = (2024, 11, 1),
        end_date: Tuple[int, int, int] = (2025, 10, 31),
    ):
        """Initialize the DataManager.
        
        Args:
            base_path: Base path to the project directory containing eco-counter/
                       and weather_data/ folders.
            cache_dir: Directory for Parquet cache files (relative to base_path).
            start_date: Tuple of (year, month, day) for data start.
            end_date: Tuple of (year, month, day) for data end.
        """
        self.base_path = Path(base_path)
        self.cache_dir = self.base_path / cache_dir
        self.start_date = start_date
        self.end_date = end_date
        
        # In-memory cache of loaded DataFrames
        self._data_cache: Dict[str, pd.DataFrame] = {}
        
        # Create cache directory if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _cache_path(self, station_alias: str) -> Path:
        """Get the Parquet cache file path for a station."""
        start_str = f"{self.start_date[0]}-{self.start_date[1]:02d}-{self.start_date[2]:02d}"
        end_str = f"{self.end_date[0]}-{self.end_date[1]:02d}-{self.end_date[2]:02d}"
        return self.cache_dir / f"{station_alias}_{start_str}_{end_str}.parquet"
    
    def _load_bike_data(self) -> pd.DataFrame:
        """Load all bike counter data from CSVs for the date range."""
        df_list = []
        
        start_year, start_month, start_day = self.start_date
        end_year, end_month, end_day = self.end_date
        
        for year in range(start_year, end_year + 1):
            # Determine which months to load for this year
            if (year, year) == (start_year, end_year):
                months = range(start_month, end_month + 1)
            elif year == start_year:
                months = range(start_month, 13)
            elif year == end_year:
                months = range(1, end_month + 1)
            else:
                months = range(1, 13)
            
            for month in months:
                file_pattern = self.base_path / f"eco-counter/all_cities/{year}/{month:02d}.csv"
                matching_files = glob.glob(str(file_pattern))
                
                for f in matching_files:
                    df_temp = pd.read_csv(f, low_memory=False)
                    df_list.append(df_temp)
        
        if not df_list:
            raise FileNotFoundError(
                f"No bike data files found for {start_year}-{start_month} to {end_year}-{end_month}"
            )
        
        df = pd.concat(df_list, ignore_index=True)
        
        # Convert ISO timestamps to timezone-aware, then to local Berlin time
        df['iso_timestamp'] = pd.to_datetime(df['iso_timestamp'], errors='coerce', utc=True)
        df['iso_timestamp'] = df['iso_timestamp'].dt.tz_convert('Europe/Berlin')
        
        # Convert to naive local time (wall-clock time)
        df['iso_timestamp'] = df['iso_timestamp'].dt.tz_localize(None)
        
        # Remove duplicate hours during fall-back (Keep summer 2AM instead of winter 2AM)
        df = df.drop_duplicates(subset=['iso_timestamp', 'counter_site'], keep='first')
        
        # Aggregate by timestamp and counter site
        df_hourly = df.groupby(['iso_timestamp', 'counter_site']).agg({
            'channels_all': 'first',
            'domain_name': 'first'
        }).reset_index()
        
        # Filter to requested date range
        start_ts = pd.Timestamp(start_year, start_month, start_day, 0, 0)
        end_ts = pd.Timestamp(end_year, end_month, end_day, 23, 0)
        df_hourly = df_hourly[
            (df_hourly['iso_timestamp'] >= start_ts) & 
            (df_hourly['iso_timestamp'] <= end_ts)
        ]
        
        return df_hourly.sort_values('iso_timestamp').reset_index(drop=True)
    
    def _load_weather_data(self, station: str) -> pd.DataFrame:
        """Load weather data for a station."""
        
        weather_file = (
            self.base_path / 
            f"weather_data/hourly/weather_{station.lower()}.csv"
        )
        
        if not weather_file.exists():
            raise FileNotFoundError(f"Weather file not found: {weather_file}")
        
        df = pd.read_csv(weather_file)
        df['datetime'] = pd.to_datetime(df['time'])
        df = df.drop_duplicates(subset='datetime', keep='first')
        
        # Filter to requested date range (same as bike data filtering)
        start_year, start_month, start_day = self.start_date
        end_year, end_month, end_day = self.end_date
        start_ts = pd.Timestamp(start_year, start_month, start_day, 0, 0)
        end_ts = pd.Timestamp(end_year, end_month, end_day, 23, 0)
        df = df[
            (df['datetime'] >= start_ts) & 
            (df['datetime'] <= end_ts)
        ]
        
        return df
    
    def _merge_bike_weather(self, station: Station, bike_df: pd.DataFrame) -> pd.DataFrame:
        """Merge bike data for a station with weather data."""
        # Filter bike data to this counter
        counter_df = bike_df[bike_df['counter_site'] == station.counter_name].copy()
        counter_df = counter_df.rename(columns={'iso_timestamp': 'datetime'})
        
        # Load weather for this city
        weather_df = self._load_weather_data(station.station)
        
        # Merge on datetime
        merged = pd.merge(
            counter_df[['datetime', 'channels_all']],
            weather_df[['datetime', 'precipitation (mm)', 'temperature_2m (°C)']],
            on='datetime',
            how='outer'
        ).sort_values('datetime')
        
        # Filter merged data to the requested date range
        # This ensures we don't include extra weather data outside the date range
        # start_year, start_month, start_day = self.start_date
        # end_year, end_month, end_day = self.end_date
        # start_ts = pd.Timestamp(start_year, start_month, start_day, 0, 0)
        # end_ts = pd.Timestamp(end_year, end_month, end_day, 23, 0)
        # merged = merged[
        #     (merged['datetime'] >= start_ts) & 
        #     (merged['datetime'] <= end_ts)
        # ]
        
        # Rename columns
        merged = merged.rename(columns={'channels_all': 'bike', 'precipitation (mm)': 'rain', 'temperature_2m (°C)': 'temp'})
        
        # Ensure numeric types
        merged[['bike', 'rain', 'temp']] = merged[['bike', 'rain', 'temp']].apply(
            pd.to_numeric, errors='coerce'
        )
        
        return merged.reset_index(drop=True)
    
    def get(self, station_alias: str, force_reload: bool = False) -> pd.DataFrame:
        """Get data for a station, using cache if available.
        
        Args:
            station_alias: Station identifier (e.g., 'tuebingen_tunnel').
            force_reload: If True, reload from CSVs even if cache exists.
            
        Returns:
            DataFrame with columns: datetime, bike, rain, temp
        """
        # Check in-memory cache first
        if station_alias in self._data_cache and not force_reload:
            return self._data_cache[station_alias].copy()
        
        station = get_station(station_alias)
        cache_path = self._cache_path(station_alias)
        
        # Try to load from Parquet cache
        if cache_path.exists() and not force_reload:
            df = pd.read_parquet(cache_path)
            self._data_cache[station_alias] = df
            return df.copy()
        
        # Load fresh from CSVs
        print(f"Loading data for {station.display_name}...")
        bike_df = self._load_bike_data()
        df = self._merge_bike_weather(station, bike_df)
        
        # Save to Parquet cache
        df.to_parquet(cache_path, index=False)
        print(f"Cached to {cache_path}")
        
        # Store in memory cache
        self._data_cache[station_alias] = df
        
        return df.copy()
    
    def get_multiple(
        self, 
        station_aliases: list[str], 
        force_reload: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """Get data for multiple stations.
        
        Args:
            station_aliases: List of station identifiers.
            force_reload: If True, reload from CSVs even if cache exists.
            
        Returns:
            Dictionary mapping station alias to DataFrame.
        """
        return {alias: self.get(alias, force_reload) for alias in station_aliases}
    
    def clear_cache(self, station_alias: str | None = None):
        """Clear cached data.
        
        Args:
            station_alias: If provided, clear only this station's cache.
                          If None, clear all caches.
        """
        if station_alias:
            # Clear specific station
            if station_alias in self._data_cache:
                del self._data_cache[station_alias]
            cache_path = self._cache_path(station_alias)
            if cache_path.exists():
                cache_path.unlink()
        else:
            # Clear all
            self._data_cache.clear()
            for cache_file in self.cache_dir.glob("*.parquet"):
                cache_file.unlink()
    
    def preload_all(self, force_reload: bool = False):
        """Preload and cache data for all registered stations.
        
        Useful for batch processing or to warm the cache.
        """
        for alias in STATIONS:
            try:
                self.get(alias, force_reload)
            except FileNotFoundError as e:
                print(f"Skipping {alias}: {e}")
    
    @property
    def cached_stations(self) -> list[str]:
        """List stations that have Parquet cache files."""
        cached = []
        for alias in STATIONS:
            if self._cache_path(alias).exists():
                cached.append(alias)
        return cached
