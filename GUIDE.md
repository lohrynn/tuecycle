# tuecycle Development Guide

This guide explains how to extend the tuecycle package with new stations, weather data, and plot functions.

---

## Table of Contents

1. [Adding a New Bike Counting Station](#1-adding-a-new-bike-counting-station)
2. [Adding Weather Data for a New City](#2-adding-weather-data-for-a-new-city)
3. [Creating a New Plot Function](#3-creating-a-new-plot-function)
4. [Best Practices](#4-best-practices)

---

## 1. Adding a New Bike Counting Station

### Step 1: Find the Counter Name

First, identify the exact `counter_site` name from the eco-counter CSV files. Open any CSV in `eco-counter/all_cities/YYYY/MM.csv` and look at the `counter_site` column.

```python
import pandas as pd
df = pd.read_csv("eco-counter/all_cities/2024/11.csv")
print(df['counter_site'].unique())
```

### Step 2: Add to Station Registry

Edit `tuecycle/config/stations.py` and add a new entry to the `STATIONS` dictionary:

```python
STATIONS["freiburg_wiwili"] = Station(
    alias="freiburg_wiwili",                # Short identifier matching the weather file (used in code)
    counter_name="Wiwilibrücke",            # Exact name from CSV
    display_name="Freiburg (Wiwilibrücke)", # Human-readable for plots
    color="#FDB462",                        # Hex color for multi-station plots
)
```

### Step 3: Ensure Weather Data Exists

The `alias` field must match a weather file in `weather_data/hourly/`. If the city doesn't exist yet, see [Section 2](#2-adding-weather-data-for-a-new-city).

### Step 4: Test

```python
from tuecycle import DataManager
dm = DataManager()
df = dm.get("freiburg_wiwili")
print(df.head())
```

---

## 2. Adding Weather Data for a New City

### Data Sources

You can obtain hourly weather data from [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api) (free).

### Required File Format

Weather files must be placed in `weather_data/hourly/` with this naming convention:

```shell
weather_{city}_{station_alias}.csv
```

Example: `weather_freiburg_wiwili.csv`

### Required Columns

The CSV must have these columns:

| Column | Description | Example |
| ------ | ----------- | ------- |
| `time` | ISO datetime | `2019-12-01T00:00` |
| `temperature_2m (°C)` | Temperature in °C | `5.2 = 5.2°C` |
| `precipitation (mm)` | Precipitation in mm | `0.5 = 0.5mm` |
| `cloud_cover (%)` | Total cloud cover as an area fraction | `5 = 5%` |
| `wind_speed_10m (km/h)` | Wind speed at 10 meters above ground | `5 = 5km/h` |
| `is_day ()` | Day or night | `0 = night, 1 = day` |



When using get(), the columns are renamed as follows:
- `precipitation (mm)`: rain`, 
- `temperature_2m (°C)`: `temp`,
- `cloud_cover (%)`: `clouds`,
- `wind_speed_10m (km/h)`: `wind`,
- `is_day ()`: `day`

Optional columns (not currently used but can be kept):
apparent_temperature (°C),rain (mm),snow_depth (m),snowfall (cm),weather_code (wmo code),cloud_cover (%),cloud_cover_high (%),cloud_cover_mid (%),cloud_cover_low (%),wind_speed_10m (km/h),wind_direction_100m (°),wind_direction_10m (°),wind_speed_100m (km/h),wind_gusts_10m (km/h),is_day (),sunshine_duration (s),pressure_msl (hPa),surface_pressure (hPa)

- `relative_humidity_2m (%)`
- `dew_point_2m (°C)`
- `apparent_temperature (°C)`
- `rain (mm)`
- `snow_depth (m)`, `snowfall (cm)`
- `weather_code (wmo code)`
- `cloud_cover (%)`, `cloud_cover_high (%)`, `cloud_cover_mid (%)`, `cloud_cover_low (%)`,
- `wind_speed_10m (km/h)`, `wind_direction_100m (°)`, `wind_direction_10m (°)`, `wind_speed_100m (km/h)`, `wind_gusts_10m (km/h)`
- `is_day ()`
- `sunshine_duration (s)`
- `pressure_msl (hPa)`, `surface_pressure (hPa)`

## 3. Creating a New Plot Function

### Step 1: Add Function to `tuecycle/plots/functions.py`

Use the `@register_plot` decorator to automatically register your plot:

```python
from tuecycle.plots.registry import register_plot

@register_plot("my_new_plot", "Description of what this plot shows")
def plot_my_new_plot(
    df: pd.DataFrame,
    title: str = "My New Plot",
) -> go.Figure:
    """Docstring explaining the plot.
    
    Args:
        df: DataFrame with datetime, bike, rain, temp columns.
        title: Plot title.
        
    Returns:
        Plotly Figure object.
    """
    # Use helper functions for common operations
    df = add_time_features(df)  # Adds hour, dayofweek, month, etc.
    
    # Create your plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['bike'],
        mode='lines',
        name='Bike Count'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title='Bikes',
        height=500,
    )
    
    return fig
```

### Step 2: Available Helper Functions

Import these from `tuecycle.utils.transforms`:

```python
from tuecycle.utils.transforms import (
    add_time_features,      # Adds hour, dayofweek, month, year_month, is_weekend
    filter_daytime,         # Filters to hours 6-22
    compute_deviations,     # Adds temp_deviation and bike_deviation columns
    classify_time_category, # Adds time_category (rush hour classification)
    add_season,             # Adds season column (Winter/Transition/Summer)
    prepare_fft_data,       # Prepares data for FFT analysis
)
```

### Step 3: Multi-Station Plots

For plots comparing multiple stations, accept a `dict` instead of a single DataFrame:

```python
@register_plot("my_comparison_plot", "Compare multiple stations")
def plot_my_comparison(
    data_dict: dict,  # {station_alias: DataFrame}
    title: str = "Station Comparison",
) -> go.Figure:
    from tuecycle.config.stations import get_station
    
    fig = go.Figure()
    
    for alias, df in data_dict.items():
        station = get_station(alias)  # Get display name and color
        
        fig.add_trace(go.Scatter(
            x=...,
            y=...,
            name=station.display_name,
            line=dict(color=station.color),
        ))
    
    return fig
```

### Step 4: Test Your Plot

```python
from tuecycle import DataManager
from tuecycle.plots import get_plot, list_plots

# Verify it's registered
print(list_plots())  # Should include your new plot

# Test it
dm = DataManager()
df = dm.get("tuebingen_tunnel")
fig = get_plot("my_new_plot")(df, title="Test")
fig.show()
```

---

## 4. Best Practices

### Station Naming

- Use lowercase with underscores: `city_location`
- Be consistent with existing patterns
- Use descriptive location names

### Colors

Use consistent colors per city. Current palette:

| City | Color |
|------|-------|
| Tübingen | `#8DD3C7` (teal) |
| Heidelberg | `#FB8072` (salmon) |
| Mannheim | `#80B1D3` (light blue) |
| Stuttgart | `#BEBADA` (lavender) |
| Freiburg | `#FDB462` (orange) |

### Plot Functions

1. Always return a `go.Figure` object
2. Set `height=500` for consistent sizing
3. Use `hovermode='x unified'` for time series
4. Include clear axis labels with units
5. Add a descriptive docstring

### Weather Data

1. Ensure hourly resolution (8760-8784 rows per year)
2. Use Europe/Berlin timezone
3. Handle DST transitions (duplicate hours in fall)

---

## Quick Reference

### Load Data

```python
from tuecycle import DataManager
dm = DataManager()
df = dm.get("station_alias")
```

### Create Plot

```python
from tuecycle.plots import get_plot
fig = get_plot("plot_name")(df, title="My Title")
fig.show()
```

### List Available

```python
from tuecycle import list_stations
from tuecycle.plots import list_plots

print(list_stations())  # All station aliases
print(list_plots())     # All plot names
```
