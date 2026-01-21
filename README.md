# tuecycle

A Python package for analyzing bike counter data with weather correlations.

## Project Structure

```
tuecycle/
├── src/
│   └── tuecycle/          # Main package
│       ├── config/        # Station configuration
│       ├── data/          # Data loading and caching
│       ├── plots/         # Plotting functions
│       └── utils/         # Utility functions
├── data/
│   ├── bike_data/         # Bike counter CSV files (by year/month)
│   └── weather_data/
│       └── hourly/        # Hourly weather data
├── exp/                   # Experiment notebooks
├── cache/                 # Parquet cache files
├── doc/                   # Documentation
└── pyproject.toml         # Package configuration
```

## Installation

Install the package in development mode:

```bash
pip install -e .
```

Or install with optional dependencies for Jupyter notebooks:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from tuecycle import DataManager
from tuecycle.plots import get_plot, list_plots

# Initialize data manager
dm = DataManager()

# Load data for a station
df = dm.get("tuebingen_tunnel")

# Create a plot
fig = get_plot("hourly_pattern")(df, "Tübingen Radtunnel")
fig.show()

# List available stations and plots
from tuecycle import list_stations
print(list_stations())
print(list_plots())
```

## Development

See [GUIDE.md](GUIDE.md) for details on:
- Adding new bike counting stations
- Adding weather data for new cities
- Creating custom plot functions

## Data Sources

- Bike counter data: eco-counter CSV files
- Weather data: Open-Meteo (https://open-meteo.com/)
