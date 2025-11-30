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
STATIONS["karlsruhe_schloss"] = Station(
    alias="karlsruhe_schloss",           # Short identifier (used in code)
    city="karlsruhe",                     # Must match weather file name!
    counter_name="Schlossplatz Barometer", # Exact name from CSV
    display_name="Karlsruhe (Schlossplatz)", # Human-readable for plots
    color="#B3DE69",                      # Hex color for multi-station plots
)
```

### Step 3: Ensure Weather Data Exists

The `city` field must match a weather file in `weather_data/hourly/`. If the city doesn't exist yet, see [Section 2](#2-adding-weather-data-for-a-new-city).

### Step 4: Test

```python
from tuecycle import DataManager
dm = DataManager()
df = dm.get("karlsruhe_schloss")
print(df.head())
```

---

## 2. Adding Weather Data for a New City

### Required File Format

Weather files must be placed in `weather_data/hourly/` with this naming convention:

```
{city}_weather_{start_year}-{start_month}-{start_day}_{end_year}-{end_month}-{end_day}.csv
```

Example: `karlsruhe_weather_2024-11-1_2025-10-31.csv`

### Required Columns

The CSV must have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `time` | ISO datetime | `2024-11-01 00:00:00` |
| `temp` | Temperature in °C | `5.2` |
| `prcp` | Precipitation in mm | `0.5` |

Optional columns (not currently used but can be kept):
- `dwpt` - Dew point
- `rhum` - Relative humidity
- `snow` - Snow depth
- `wdir`, `wspd`, `wpgt` - Wind data
- `pres` - Pressure
- `tsun` - Sunshine duration
- `coco` - Weather condition code

### Data Sources

You can obtain hourly weather data from:

1. **Open-Meteo** (free, recommended): https://open-meteo.com/en/docs/historical-weather-api
2. **Meteostat** (free): https://meteostat.net/
3. **DWD Climate Data Center** (official German data): https://opendata.dwd.de/

### Example: Downloading from Open-Meteo

```python
import requests
import pandas as pd

# Karlsruhe coordinates
lat, lon = 49.0069, 8.4037

url = f"https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": lat,
    "longitude": lon,
    "start_date": "2024-11-01",
    "end_date": "2025-10-31",
    "hourly": "temperature_2m,precipitation",
    "timezone": "Europe/Berlin"
}

response = requests.get(url, params=params)
data = response.json()

df = pd.DataFrame({
    "time": data["hourly"]["time"],
    "temp": data["hourly"]["temperature_2m"],
    "prcp": data["hourly"]["precipitation"]
})

df.to_csv("weather_data/hourly/karlsruhe_weather_2024-11-1_2025-10-31.csv", index=False)
```

---

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
