"""Plotting module for tuecycle with registry pattern."""

from tuecycle.plots.registry import PlotRegistry, register_plot, get_plot, list_plots
from tuecycle.plots import functions  # Import to register all plots

__all__ = ["PlotRegistry", "register_plot", "get_plot", "list_plots"]
