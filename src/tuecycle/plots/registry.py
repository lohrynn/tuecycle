"""
Plot registry for tuecycle.

Provides a decorator-based registration system for plot functions, making it
easy to add new plots and access them programmatically.
"""

from typing import Callable, Dict
import pandas as pd

# Global registry of plot functions
_PLOT_REGISTRY: Dict[str, Callable] = {}


def register_plot(name: str, description: str = ""):
    """Decorator to register a plot function.
    
    Args:
        name: Unique identifier for the plot (e.g., 'hourly_pattern').
        description: Human-readable description of the plot.
        
    Example:
        @register_plot("hourly_pattern", "Average bike count by hour of day")
        def plot_hourly_pattern(df, title=""):
            ...
    """
    def decorator(func: Callable) -> Callable:
        func._plot_name = name
        func._plot_description = description
        _PLOT_REGISTRY[name] = func
        return func
    return decorator


def get_plot(name: str) -> Callable:
    """Get a registered plot function by name.
    
    Args:
        name: The plot identifier.
        
    Returns:
        The plot function.
        
    Raises:
        KeyError: If no plot with that name is registered.
    """
    if name not in _PLOT_REGISTRY:
        available = ", ".join(sorted(_PLOT_REGISTRY.keys()))
        raise KeyError(f"Unknown plot '{name}'. Available: {available}")
    return _PLOT_REGISTRY[name]


def list_plots() -> list[dict]:
    """List all registered plots with their descriptions.
    
    Returns:
        List of dicts with 'name' and 'description' keys.
    """
    return [
        {"name": name, "description": getattr(func, '_plot_description', '')}
        for name, func in sorted(_PLOT_REGISTRY.items())
    ]


class PlotRegistry:
    """Convenience class for accessing and running registered plots.
    
    Example:
        registry = PlotRegistry()
        registry.show("hourly_pattern", df, title="My Title")
        
        # List all available plots
        registry.list()
    """
    
    def __init__(self):
        pass
    
    def show(self, name: str, df: pd.DataFrame, **kwargs):
        """Run a plot by name.
        
        Args:
            name: Plot identifier.
            df: DataFrame to plot.
            **kwargs: Additional arguments passed to the plot function.
        """
        plot_func = get_plot(name)
        return plot_func(df, **kwargs)
    
    def list(self) -> list[dict]:
        """List all available plots."""
        return list_plots()
    
    def __getitem__(self, name: str) -> Callable:
        """Get a plot function by name using bracket notation."""
        return get_plot(name)
    
    def __contains__(self, name: str) -> bool:
        """Check if a plot name is registered."""
        return name in _PLOT_REGISTRY
