"""
Plot functions for tuecycle.

All plot functions are registered with the PlotRegistry and can be accessed
by name. Each function takes a DataFrame and optional styling parameters.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.fft import fft, fftfreq
from scipy.ndimage import gaussian_filter
from scipy import stats
from plotly.subplots import make_subplots

from tuecycle.plots.registry import register_plot
from tuecycle.utils.transforms import (
    add_time_features,
    filter_daytime,
    compute_deviations,
    classify_time_category,
    add_season,
    prepare_fft_data,
)


# =============================================================================
# Color Constants
# =============================================================================

COLORS = {
    'bike': px.colors.qualitative.Set3[0],      # Teal
    'temp': px.colors.qualitative.Set3[3],      # Yellow-orange
    'rain': px.colors.qualitative.Set3[4],      # Light pink
    'winter': '#4A90D9',
    'transition': '#7CB342',
    'summer': '#F5A623',
    'weekday': '#E74C3C',
    'weekend': '#27AE60',
    'morning_rush': '#E74C3C',
    'evening_rush': '#9B59B6',
    'non_rush': '#3498DB',
}


# =============================================================================
# Time Series Plots
# =============================================================================

@register_plot("time_series", "Time series of bike counts with weather overlay")
def plot_time_series(
    df: pd.DataFrame,
    title: str = "Bike Counts and Weather",
    show_rangeslider: bool = True,
) -> go.Figure:
    """Plot bike counts, temperature, and rain as time series with multiple y-axes."""
    fig = go.Figure()
    
    # Bike trace
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['bike'],
        name='Bike Count',
        line=dict(color=COLORS['bike']),
        yaxis='y1'
    ))
    
    # Temperature trace
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['temp'],
        name='Temperature',
        line=dict(color=COLORS['temp']),
        yaxis='y2'
    ))
    
    # Rain trace
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['rain'],
        name='Rainfall',
        line=dict(color=COLORS['rain']),
        yaxis='y3'
    ))
    
    fig.update_layout(
        title=title,
        legend=dict(y=1, orientation='h'),
        xaxis=dict(
            title='Datetime',
            rangeslider=dict(visible=show_rangeslider),
        ),
        yaxis=dict(
            title=dict(text="Bike Count [#]", font=dict(color=COLORS['bike'])),
            side='left',
            showgrid=False
        ),
        yaxis2=dict(
            title=dict(text="Temperature [°C]", font=dict(color=COLORS['temp'])),
            anchor="x",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        yaxis3=dict(
            title=dict(text="Rainfall [mm]", font=dict(color=COLORS['rain'])),
            anchor="free",
            overlaying="y",
            side="right",
            autoshift=True,
            showgrid=False,
            shift=50,
        ),
        hovermode='x unified',
        height=500,
    )
    
    return fig


# =============================================================================
# Hourly Pattern Plots
# =============================================================================

@register_plot("hourly_pattern", "Average bike count by hour of day with std band")
def plot_hourly_pattern(
    df: pd.DataFrame,
    title: str = "Average Hourly Bike Pattern",
) -> go.Figure:
    """Plot average bike count per hour with ±1 std deviation band."""
    df = add_time_features(df)
    hourly_stats = df.groupby('hour')['bike'].agg(['mean', 'std']).reset_index()
    
    fig = go.Figure()
    
    # Mean line
    fig.add_trace(go.Scatter(
        x=hourly_stats['hour'],
        y=hourly_stats['mean'],
        mode='lines+markers',
        name='Mean Bike Count',
        line=dict(color=COLORS['bike'], width=3),
        marker=dict(size=8)
    ))
    
    # Confidence band (±1 std)
    fig.add_trace(go.Scatter(
        x=list(hourly_stats['hour']) + list(hourly_stats['hour'][::-1]),
        y=list(hourly_stats['mean'] + hourly_stats['std']) + 
          list((hourly_stats['mean'] - hourly_stats['std'])[::-1]),
        fill='toself',
        fillcolor='rgba(141, 211, 199, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        name='±1 Std Dev'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Hour of Day',
        yaxis_title='Bike Count',
        hovermode='x unified',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        height=500,
    )
    
    return fig


@register_plot("weekday_vs_weekend", "Hourly pattern comparison: weekdays vs weekends")
def plot_weekday_vs_weekend(
    df: pd.DataFrame,
    title: str = "Weekday vs Weekend Hourly Pattern",
) -> go.Figure:
    """Compare average hourly patterns between weekdays and weekends."""
    df = add_time_features(df)
    
    weekday_data = df[df['dayofweek'] < 5]
    weekend_data = df[df['dayofweek'] >= 5]
    
    weekday_hourly = weekday_data.groupby('hour')['bike'].mean().reset_index()
    weekend_hourly = weekend_data.groupby('hour')['bike'].mean().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=weekday_hourly['hour'],
        y=weekday_hourly['bike'],
        mode='lines+markers',
        name='Weekdays (Mon-Fri)',
        line=dict(color=COLORS['weekday'], width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=weekend_hourly['hour'],
        y=weekend_hourly['bike'],
        mode='lines+markers',
        name='Weekend (Sat-Sun)',
        line=dict(color=COLORS['weekend'], width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Hour of Day',
        yaxis_title='Average Bike Count',
        hovermode='x unified',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=500,
    )
    
    return fig


# =============================================================================
# Seasonal Comparison Plots
# =============================================================================

@register_plot("seasonal_comparison", "Hourly pattern by season (Winter/Transition/Summer)")
def plot_seasonal_comparison(
    df: pd.DataFrame,
    title: str = "Seasonal Hourly Pattern",
) -> go.Figure:
    """Compare average hourly patterns between seasons."""
    df = add_time_features(df)
    df = add_season(df)
    
    fig = go.Figure()
    
    for season, color in [('Winter', COLORS['winter']), 
                          ('Transition', COLORS['transition']),
                          ('Summer', COLORS['summer'])]:
        season_data = df[df['season'] == season]
        hourly = season_data.groupby('hour')['bike'].mean().reset_index()
        
        fig.add_trace(go.Scatter(
            x=hourly['hour'],
            y=hourly['bike'],
            mode='lines+markers',
            name=season,
            line=dict(color=color, width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Hour of Day',
        yaxis_title='Average Bike Count',
        hovermode='x unified',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=500,
    )
    
    return fig


@register_plot("monthly_average", "Bar chart of average bike counts per month")
def plot_monthly_average(
    df: pd.DataFrame,
    title: str = "Monthly Average Bike Counts",
) -> go.Figure:
    """Bar chart of average bike counts per month."""
    df = add_time_features(df)
    monthly_avg = df.groupby('year_month')['bike'].mean().reset_index()
    
    fig = px.bar(
        monthly_avg,
        x='year_month',
        y='bike',
        title=title
    )
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Average Bike Count per Hour',
        xaxis_tickangle=-45,
        height=500,
    )
    
    return fig


# =============================================================================
# Heatmap Plots
# =============================================================================

@register_plot("hour_weekday_heatmap", "Heatmap of bike counts by hour and day of week")
def plot_hour_weekday_heatmap(
    df: pd.DataFrame,
    title: str = "Bike Traffic Heatmap",
) -> go.Figure:
    """Heatmap showing average bike counts by hour and day of week."""
    df = add_time_features(df)
    
    pivot = df.pivot_table(values='bike', index='hour', columns='dayofweek', aggfunc='mean')
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    pivot.columns = day_names
    
    fig = px.imshow(
        pivot,
        labels=dict(x="Day of Week", y="Hour of Day", color="Avg Bike Count"),
        x=day_names,
        y=list(range(24)),
        color_continuous_scale='YlOrRd',
        aspect='auto',
        title=title
    )
    
    fig.update_layout(
        yaxis=dict(tickmode='linear', tick0=0, dtick=1),
        height=500,
    )
    
    return fig


@register_plot("bike_vs_temp_heatmap", "2D density heatmap of bike counts vs temperature")
def plot_bike_vs_temp_heatmap(
    df: pd.DataFrame,
    title: str = "Bike Count vs Temperature",
    daytime_only: bool = True,
) -> go.Figure:
    """2D density heatmap of bike counts vs temperature with trendline."""
    df = add_time_features(df)
    
    if daytime_only:
        df_clean = filter_daytime(df)
        time_label = " (Daytime 6-22h)"
    else:
        df_clean = df
        time_label = ""
    
    df_clean = df_clean.dropna(subset=['bike', 'temp'])
    
    temp_bins = np.linspace(df_clean['temp'].min(), df_clean['temp'].max(), 50)
    bike_bins = np.linspace(0, df_clean['bike'].quantile(0.99), 50)
    
    hist, xedges, yedges = np.histogram2d(
        df_clean['temp'], df_clean['bike'],
        bins=[temp_bins, bike_bins]
    )
    hist_smooth = gaussian_filter(hist.T, sigma=1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Heatmap(
        z=hist_smooth,
        x=temp_bins,
        y=bike_bins,
        colorscale='YlOrRd',
        colorbar=dict(title='Observations'),
    ))
    
    # Add trendline
    bins = pd.cut(df_clean['temp'], bins=20)
    avg = df_clean.groupby(bins, observed=True)['bike'].mean()
    bin_x = [interval.mid for interval in avg.index]
    
    fig.add_trace(go.Scatter(
        x=bin_x,
        y=avg.values,
        mode='lines+markers',
        name='Mean Bike Count',
        line=dict(color='black', width=3),
        marker=dict(size=8, color='white', line=dict(color='black', width=2)),
    ))
    
    fig.update_layout(
        title=f'{title}{time_label}',
        xaxis_title='Temperature [°C]',
        yaxis_title='Bike Count',
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
        height=500,
    )
    
    return fig


@register_plot("temp_deviation_heatmap", "Temperature deviation vs bike deviation heatmap")
def plot_temp_deviation_heatmap(
    df: pd.DataFrame,
    title: str = "Temp Deviation vs Bike Deviation",
    daytime_only: bool = True,
) -> go.Figure:
    """2D density heatmap of temperature and bike deviations from monthly average."""
    df = add_time_features(df)
    df = compute_deviations(df)
    
    if daytime_only:
        df_clean = filter_daytime(df)
        time_label = " (Daytime 6-22h)"
    else:
        df_clean = df
        time_label = ""
    
    df_clean = df_clean.dropna(subset=['bike_deviation', 'temp_deviation'])
    
    temp_dev_bins = np.linspace(-15, 15, 35)
    bike_dev_bins = np.linspace(-100, 300, 35)
    
    hist, _, _ = np.histogram2d(
        df_clean['temp_deviation'], df_clean['bike_deviation'],
        bins=[temp_dev_bins, bike_dev_bins]
    )
    hist_smooth = gaussian_filter(hist.T, sigma=1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Heatmap(
        z=hist_smooth,
        x=temp_dev_bins,
        y=bike_dev_bins,
        colorscale='Viridis',
        colorbar=dict(title='Observations'),
    ))
    
    # Add regression line
    slope, intercept, r_value, _, _ = stats.linregress(
        df_clean['temp_deviation'], df_clean['bike_deviation']
    )
    reg_x = np.array([-15, 15])
    reg_y = slope * reg_x + intercept
    
    fig.add_trace(go.Scatter(
        x=reg_x,
        y=reg_y,
        mode='lines',
        name=f'Regression (slope={slope:.1f}%/°C)',
        line=dict(color='red', width=2, dash='dash'),
    ))
    
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.5)")
    fig.add_vline(x=0, line_dash="dot", line_color="rgba(255,255,255,0.5)")
    
    fig.update_layout(
        title=f'{title}{time_label}<br><sup>Slope: {slope:.1f}%/°C, R²={r_value**2:.3f}</sup>',
        xaxis_title='Temperature Deviation from Monthly Average [°C]',
        yaxis_title='Bike Count Deviation from Monthly Average [%]',
        xaxis=dict(range=[-15, 15]),
        yaxis=dict(range=[-100, 300]),
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
        height=500,
    )
    
    return fig


# =============================================================================
# Rush Hour Analysis
# =============================================================================

@register_plot("rush_hour_analysis", "Bar chart of bike counts by time category")
def plot_rush_hour_analysis(
    df: pd.DataFrame,
    title: str = "Rush Hour Analysis",
) -> go.Figure:
    """Analyze and visualize rush hour vs non-rush hour bike counts."""
    df = classify_time_category(df)
    
    category_avg = df.groupby('time_category')['bike'].agg(['mean', 'std']).reset_index()
    category_order = ['Morning Rush (7-9)', 'Evening Rush (17-19)', 'Weekday Non-Rush', 'Weekend']
    category_avg['time_category'] = pd.Categorical(
        category_avg['time_category'], 
        categories=category_order, 
        ordered=True
    )
    category_avg = category_avg.sort_values('time_category')
    
    fig = px.bar(
        category_avg,
        x='time_category',
        y='mean',
        error_y='std',
        color='time_category',
        color_discrete_map={
            'Morning Rush (7-9)': COLORS['morning_rush'],
            'Evening Rush (17-19)': COLORS['evening_rush'],
            'Weekday Non-Rush': COLORS['non_rush'],
            'Weekend': COLORS['weekend']
        },
        title=title
    )
    
    fig.update_layout(
        xaxis_title='Time Category',
        yaxis_title='Average Bike Count',
        showlegend=False,
        height=500,
    )
    
    return fig


# =============================================================================
# Fourier Analysis
# =============================================================================

@register_plot("fourier_transform", "Fourier transform showing periodic patterns")
def plot_fourier_transform(
    df: pd.DataFrame,
    column: str = 'bike',
    title: str = "Fourier Transform",
) -> go.Figure:
    """Plot FFT amplitude spectrum with frequency annotations."""
    series = df[column] if isinstance(df, pd.DataFrame) else df
    fourier_data = prepare_fft_data(series)
    
    N = len(fourier_data)
    T = 1.0  # Hourly data
    frequencies = fftfreq(N, T)[:N//2]
    fft_values = fft(fourier_data)
    amplitudes = 2.0/N * np.abs(fft_values[0:N//2])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=frequencies,
        y=amplitudes,
        mode='lines',
        name='FFT Amplitude'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Frequency (1/hour)',
        yaxis_title='Amplitude',
        hovermode='x unified'
    )
    
    # Add frequency reference lines
    freq_refs = [
        (1 / (365 * 24), "Yearly"),
        (1 / (7 * 24), "Weekly"),
        (2 / (7 * 24), "Weekend"),
        (1 / 24, "Daily"),
        (1 / 12, "12h"),
        (1 / 8, "8h"),
        (1 / 6, "6h"),
    ]
    
    for freq, label in freq_refs:
        fig.add_vline(x=freq, line_dash="dash", line_width=1,
                      annotation_text=label, annotation_position="top left")
    
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500)
    
    return fig


# =============================================================================
# Multi-Station Comparison
# =============================================================================

@register_plot("city_comparison_hourly", "Compare hourly patterns across stations")
def plot_city_comparison_hourly(
    data_dict: dict,
    title: str = "Average Hourly Bike Pattern - Station Comparison",
) -> go.Figure:
    """Compare average hourly patterns across multiple stations.
    
    Args:
        data_dict: Dictionary mapping station alias to DataFrame.
        title: Plot title.
    """
    from tuecycle.config.stations import get_station
    
    fig = go.Figure()
    
    for alias, df in data_dict.items():
        station = get_station(alias)
        df_copy = add_time_features(df)
        hourly_avg = df_copy.groupby('hour')['bike'].mean().reset_index()
        
        fig.add_trace(go.Scatter(
            x=hourly_avg['hour'],
            y=hourly_avg['bike'],
            mode='lines+markers',
            name=station.display_name,
            line=dict(color=station.color, width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Hour of Day',
        yaxis_title='Average Bike Count',
        hovermode='x unified',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=500,
    )
    
    return fig


@register_plot("city_comparison_monthly", "Compare monthly patterns across stations (normalized)")
def plot_city_comparison_monthly(
    data_dict: dict,
    title: str = "Monthly Bike Counts - Station Comparison (Normalized)",
) -> go.Figure:
    """Compare monthly patterns across stations, normalized to percentage of max.
    
    Args:
        data_dict: Dictionary mapping station alias to DataFrame.
        title: Plot title.
    """
    from tuecycle.config.stations import get_station
    
    fig = go.Figure()
    
    for alias, df in data_dict.items():
        station = get_station(alias)
        df_copy = add_time_features(df)
        monthly_avg = df_copy.groupby('year_month')['bike'].mean()
        monthly_norm = monthly_avg / monthly_avg.max() * 100
        
        fig.add_trace(go.Scatter(
            x=monthly_norm.index,
            y=monthly_norm.values,
            mode='lines+markers',
            name=station.display_name,
            line=dict(color=station.color, width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Month',
        yaxis_title='% of Maximum Monthly Average',
        hovermode='x unified',
        xaxis_tickangle=-45,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=500,
    )
    
    return fig


@register_plot("winter_summer_ratio", "Winter to summer ratio by hour across stations")
def plot_winter_summer_ratio(
    data_dict: dict,
    title: str = "Winter to Summer Ratio by Hour",
) -> go.Figure:
    """Plot winter/summer ratio for each hour across multiple stations.
    
    Args:
        data_dict: Dictionary mapping station alias to DataFrame.
        title: Plot title.
    """
    from tuecycle.config.stations import get_station
    
    winter_months = [11, 12, 1, 2]
    summer_months = [5, 6, 7, 8]
    
    fig = go.Figure()
    
    for alias, df in data_dict.items():
        station = get_station(alias)
        df_copy = add_time_features(df)
        
        winter_data = df_copy[df_copy['month'].isin(winter_months)]
        summer_data = df_copy[df_copy['month'].isin(summer_months)]
        
        winter_hourly = winter_data.groupby('hour')['bike'].mean()
        summer_hourly = summer_data.groupby('hour')['bike'].mean()
        
        ratio = (winter_hourly / summer_hourly.replace(0, float('nan'))) * 100
        
        fig.add_trace(go.Scatter(
            x=ratio.index,
            y=ratio.values,
            mode='lines+markers',
            name=station.display_name,
            line=dict(color=station.color, width=3),
            marker=dict(size=8)
        ))
    
    fig.add_hline(y=100, line_dash="dash", line_color="gray", 
                  annotation_text="Winter = Summer")
    fig.add_hline(y=50, line_dash="dot", line_color="lightgray",
                  annotation_text="Summer = 2× Winter")
    
    fig.update_layout(
        title=title,
        xaxis_title='Hour of Day',
        yaxis_title='Winter / Summer Ratio [%]',
        hovermode='x unified',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=500,
    )
    
    return fig


# =============================================================================
# Three-cities with rain comparison
# =============================================================================
@register_plot(
    "bike_vs_rain_rush_hour_city",
    "Bike counter with rain - All categories"
)
def plot_bike_vs_rain_rush_hour_city(
    data_dict: dict,      # {station_alias: DataFrame}
    cities,
    title: str = "Bike counter with rain"
) -> go.Figure:
    """
    Subplots per city with bike counts vs rain/snow in mm.
    Plots all time categories: Morning/Evening Rush, Weekday Non-Rush, Weekend.

    Args:
        data_dict: dict with {station_alias: DataFrame} of all stations
        cities: list of cities
        title: plot title

    Returns:
        Plotly Figure
    """
    # Default colors for known categories
    color_map = {
        'Morning Rush (7-9)': 'orange',
        'Evening Rush (17-19)': 'blue',
        'Weekday Non-Rush': 'purple',
        'Weekend': 'green'
    }

    fig = make_subplots(
        rows=1,
        cols=len(cities),
        shared_yaxes=True,
        subplot_titles=[city.capitalize() for city in cities]
    )

    for col, city in enumerate(cities, start=1):
        city_lower = city.lower()
        city_stations = [alias for alias in data_dict.keys() if alias.lower().startswith(city_lower)]
        if not city_stations:
            continue

        city_df_list = [data_dict[alias].copy() for alias in city_stations]
        city_df = pd.concat(city_df_list, ignore_index=True)
        if city_df.empty:
            continue

        # Get all categories present in the filtered data
        categories = city_df['time_category'].unique()

        for cat in categories:
            df_cat = city_df[city_df['time_category'] == cat]
            if df_cat.empty:
                continue

            fig.add_trace(
                go.Scatter(
                    x=df_cat['rain'],
                    y=df_cat['bike'],
                    mode='markers',
                    name=cat if col == 1 else None,  # only show legend in first subplot
                    marker=dict(
                        size=5,
                        color=color_map.get(cat, 'gray'),  # default gray for unknown categories
                        opacity=0.8
                    ),
                    customdata=df_cat['time_category'],
                    showlegend=(col == 1)
                ),
                row=1, col=col
            )

        fig.update_xaxes(title_text="Rain/Snow [mm]", row=1, col=col)

    fig.update_yaxes(title_text="Number of bikes", row=1, col=1)

    fig.update_layout(
        title=title,
        height=500,
        width=1200,
        hovermode="closest",
    )

    return fig


@register_plot(
    "city_rain_share_boxplot",
    "Boxplot showing the share of bike rides during rain per city (All Categories)"
)
def plot_city_rain_share(
    df_city_rain: pd.DataFrame,  # DataFrame with columns ["city", "rain_share", "time_category"]
    categories: list | None = None,  # Which categories to include, None = all
    title: str = None
):
    """
    Creates a boxplot of the rain share per city for each time category.

    Args:
        df_city_rain: DataFrame with columns ["city", "rain_share", "time_category"]
        categories: list of time categories to include (None = all)
        title: optional plot title

    Returns:
        plotly.graph_objects.Figure
    """
    if title is None:
        title = "Rain share of bike counts per city (All Categories)"

    df_plot = df_city_rain.copy()
    
    if categories is not None:
        df_plot = df_plot[df_plot['time_category'].isin(categories)]

    # Default color map for known categories
    color_map = {
        'Morning Rush (7-9)': 'orange',
        'Evening Rush (17-19)': 'blue',
        'Weekday Non-Rush': 'purple',
        'Weekend': 'green'
    }

    fig = px.box(
        df_plot,
        x="city",
        y="rain_share",
        color="time_category",  # Use time category for coloring
        points="all",
        labels={"city": "City", "rain_share": "Rain share of bike counts", "time_category": "Time Category"},
        color_discrete_map=color_map,
        title=title
    )

    fig.update_layout(
        yaxis_tickformat=".0%",
        height=500,
    )

    return fig

