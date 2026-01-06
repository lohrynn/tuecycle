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
    add_perceived_rainy,
    compute_rolling_baseline,
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
    "Bike counter with rain at ≤5°C - Rush Hour"
)
def plot_bike_vs_rain_rush_hour_city(
    data_dict: dict,      # {station_alias: DataFrame}
    cities,
    title: str = "Bike counter with rain at ≤5°C - Rush Hour"
) -> go.Figure:
    """
    Three separate subplots per city with the bike counter dependent of rain/snow in mm.
    Only rush hour (Morning 7-9, Evening 17-19).
    
    Args:
        data_dict: dict with {station_alias: DataFrame} of all stations
        cities: list of cities
        title: plot titel
        
    Returns:
        Plotly Figure Objekt
    """
    # Farben für Morning vs Evening Rush
    color_map = {
        'Morning Rush (7-9)': 'orange',
        'Evening Rush (17-19)': 'blue'
    }

    fig = make_subplots(
        rows=1,
        cols=len(cities),
        shared_yaxes=True,
        subplot_titles=[city.capitalize() for city in cities]
    )

    for col, city in enumerate(cities, start=1):
        # 🔹 City filter using alias
        city_lower = city.lower()
        city_stations = [alias for alias in data_dict.keys() if alias.lower().startswith(city_lower)]
        if not city_stations:
            continue

        # 🔹 Combine DataFrames of all stations in the city
        city_df_list = [data_dict[alias].copy() for alias in city_stations]
        city_df = pd.concat(city_df_list, ignore_index=True)
        if city_df.empty:
            continue

        # 🔹 Plot points with different colors for morning and evening rush
        for rush_type in ['Morning Rush (7-9)', 'Evening Rush (17-19)']:
            df_rush = city_df[city_df['time_category'] == rush_type]
            if df_rush.empty:
                continue

            fig.add_trace(
                go.Scatter(
                    x=df_rush['rain'],
                    y=df_rush['bike'],
                    mode='markers',
                    name=rush_type if col == 1 else None,  # Legende nur einmal
                    marker=dict(size=5, color=color_map[rush_type], opacity=0.8),
                    hovertemplate="Rain: %{x} mm<br>Bikes: %{y}<br>Rush: %{customdata}",
                    customdata=df_rush['time_category'],
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
    "Boxplot showing the share of bike rides during rain per city (Rush Hour)"
)
def plot_city_rain_share(
    df_city_rain: pd.DataFrame,  # DataFrame mit Spalten ["city", "rain_share"]
    title: str = None
):
    """
    Creates a boxplot of the rain share per city.

    Args:
        df_city_rain: DataFrame with columns ["city", "rain_share"]
        title: optional plot title

    Returns:
        plotly.graph_objects.Figure
    """
    if title is None:
        title = "Rain share of bike counts per city (Rush Hour)"

    fig = px.box(
        df_city_rain,
        x="city",
        y="rain_share",
        points="all",
        color="city",
        labels={"city": "City", "rain_share": "Rain share of bike counts"},
        title=title
    )
    fig.update_layout(showlegend=False, yaxis_tickformat=".0%")
    return fig


# =============================================================================
# Perceived Rainy Day Analysis
# =============================================================================

COLORS_RAIN = {
    'perceived_dry': '#4ECDC4',       # Teal
    'perceived_rainy': '#7B68EE',     # Medium slate blue  
    'weekday_dry': '#2ECC71',         # Emerald green
    'weekday_rainy': '#9B59B6',       # Amethyst purple
    'weekend_dry': '#3498DB',         # Bright blue
    'weekend_rainy': '#E74C3C',       # Alizarin red
}


@register_plot(
    "perceived_rainy_hourly",
    "Hourly bike pattern comparing perceived rainy vs dry days"
)
def plot_perceived_rainy_hourly(
    df: pd.DataFrame,
    title: str = "Hourly Pattern: Perceived Rainy vs Dry Days",
    show_bands: bool = True,
) -> go.Figure:
    """Compare hourly bike patterns between perceived rainy and dry days.
    
    'Perceived rainy' captures days where cyclists would anticipate rain
    when making their commuting decision (rain in morning or previous evening).
    
    Args:
        df: DataFrame with datetime, bike, and rain columns.
        title: Plot title.
        show_bands: If True, show ±1 std deviation bands.
        
    Returns:
        Plotly Figure with comparison of hourly patterns.
    """
    df = add_time_features(df)
    df = add_perceived_rainy(df)
    
    fig = go.Figure()
    
    for category, color in [('Perceived Dry', COLORS_RAIN['perceived_dry']), 
                             ('Perceived Rainy', COLORS_RAIN['perceived_rainy'])]:
        cat_data = df[df['rain_category'] == category]
        hourly_stats = cat_data.groupby('hour')['bike'].agg(['mean', 'std']).reset_index()
        
        # Mean line
        fig.add_trace(go.Scatter(
            x=hourly_stats['hour'],
            y=hourly_stats['mean'],
            mode='lines+markers',
            name=category,
            line=dict(color=color, width=3),
            marker=dict(size=8)
        ))
        
        # Std band
        if show_bands and 'std' in hourly_stats.columns:
            fig.add_trace(go.Scatter(
                x=list(hourly_stats['hour']) + list(hourly_stats['hour'][::-1]),
                y=list(hourly_stats['mean'] + hourly_stats['std']) + 
                  list((hourly_stats['mean'] - hourly_stats['std'])[::-1]),
                fill='toself',
                fillcolor=color.replace(')', ', 0.2)').replace('rgb', 'rgba') if 'rgb' in color else f"rgba{tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}",
                line=dict(color='rgba(255,255,255,0)'),
                name=f'{category} ±1σ',
                showlegend=False,
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


@register_plot(
    "perceived_rainy_weekday_weekend",
    "Hourly pattern by perceived rain, split by weekday/weekend"
)
def plot_perceived_rainy_weekday_weekend(
    df: pd.DataFrame,
    title: str = "Perceived Rainy Days: Weekday vs Weekend Hourly Pattern",
) -> go.Figure:
    """Compare hourly patterns for perceived rainy/dry days, split by weekday/weekend.
    
    Creates a 2x2 comparison:
    - Weekday Dry vs Weekday Rainy
    - Weekend Dry vs Weekend Rainy
    
    This helps understand how perceived rain affects commuting patterns
    differently on workdays vs leisure days.
    
    Args:
        df: DataFrame with datetime, bike, and rain columns.
        title: Plot title.
        
    Returns:
        Plotly Figure with subplots.
    """
    df = add_time_features(df)
    df = add_perceived_rainy(df)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['Weekdays (Mon-Fri)', 'Weekend (Sat-Sun)'],
        shared_yaxes=True,
        horizontal_spacing=0.08,
    )
    
    categories = [
        ('Perceived Dry', 'weekday_dry', False),
        ('Perceived Rainy', 'weekday_rainy', False),
        ('Perceived Dry', 'weekend_dry', True),
        ('Perceived Rainy', 'weekend_rainy', True),
    ]
    
    for rain_cat, color_key, is_weekend in categories:
        cat_data = df[(df['rain_category'] == rain_cat) & (df['is_weekend'] == is_weekend)]
        hourly = cat_data.groupby('hour')['bike'].mean().reset_index()
        
        col = 2 if is_weekend else 1
        show_legend = not is_weekend  # Only show legend once
        
        fig.add_trace(
            go.Scatter(
                x=hourly['hour'],
                y=hourly['bike'],
                mode='lines+markers',
                name=rain_cat,
                line=dict(color=COLORS_RAIN[color_key], width=3),
                marker=dict(size=6),
                showlegend=show_legend,
            ),
            row=1, col=col
        )
    
    fig.update_xaxes(title_text='Hour of Day', tickmode='linear', tick0=0, dtick=2, row=1, col=1)
    fig.update_xaxes(title_text='Hour of Day', tickmode='linear', tick0=0, dtick=2, row=1, col=2)
    fig.update_yaxes(title_text='Average Bike Count', row=1, col=1)
    
    fig.update_layout(
        title=title,
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
        height=450,
    )
    
    return fig


@register_plot(
    "perceived_rainy_reduction",
    "Percentage reduction in bike counts on perceived rainy days by hour"
)
def plot_perceived_rainy_reduction(
    df: pd.DataFrame,
    title: str = "Bike Count Reduction on Perceived Rainy Days",
) -> go.Figure:
    """Show the percentage reduction in bike counts on perceived rainy days.
    
    For each hour, computes: (dry_count - rainy_count) / dry_count * 100
    
    Positive values indicate fewer cyclists on rainy days.
    
    Args:
        df: DataFrame with datetime, bike, and rain columns.
        title: Plot title.
        
    Returns:
        Plotly Figure showing reduction percentage by hour.
    """
    df = add_time_features(df)
    df = add_perceived_rainy(df)
    
    # Compute average by hour and rain category
    hourly_avg = df.groupby(['hour', 'rain_category'])['bike'].mean().unstack()
    
    reduction_pct = (
        (hourly_avg['Perceived Dry'] - hourly_avg['Perceived Rainy']) 
        / hourly_avg['Perceived Dry'] * 100
    )
    
    fig = go.Figure()
    
    # Weekday vs weekend reduction
    weekday_data = df[~df['is_weekend']]
    weekend_data = df[df['is_weekend']]
    
    for data, name, color in [
        (weekday_data, 'Weekdays', COLORS['weekday']),
        (weekend_data, 'Weekend', COLORS['weekend']),
    ]:
        hourly_avg = data.groupby(['hour', 'rain_category'])['bike'].mean().unstack()
        if 'Perceived Dry' in hourly_avg.columns and 'Perceived Rainy' in hourly_avg.columns:
            reduction = (
                (hourly_avg['Perceived Dry'] - hourly_avg['Perceived Rainy']) 
                / hourly_avg['Perceived Dry'] * 100
            )
            
            fig.add_trace(go.Bar(
                x=reduction.index,
                y=reduction.values,
                name=name,
                marker_color=color,
                opacity=0.8,
            ))
    
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    
    fig.update_layout(
        title=title + "<br><sup>Positive = fewer cyclists on rainy days</sup>",
        xaxis_title='Hour of Day',
        yaxis_title='Reduction in Bike Count [%]',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        barmode='group',
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
        height=500,
    )
    
    return fig


@register_plot(
    "deviation_from_baseline",
    "Bike count deviation from rolling baseline by rain category"
)
def plot_deviation_from_baseline(
    df: pd.DataFrame,
    title: str = "Deviation from Local Baseline: Rainy vs Dry Days",
    window_days: int = 14,
) -> go.Figure:
    """Show how perceived rainy days deviate from a local rolling baseline.
    
    This accounts for seasonal variation by comparing each day to a local
    time-window average rather than an annual average. A rainy summer day
    is compared to other nearby summer days, not to winter days.
    
    Args:
        df: DataFrame with datetime, bike, and rain columns.
        title: Plot title.
        window_days: Size of rolling window in days.
        
    Returns:
        Plotly Figure showing deviation distributions.
    """
    df = add_time_features(df)
    df = add_perceived_rainy(df)
    df = compute_rolling_baseline(df, window_days=window_days)
    
    # Filter to daytime hours for cleaner analysis
    df_day = filter_daytime(df, start_hour=7, end_hour=20)
    df_day = df_day.dropna(subset=['deviation_from_baseline'])
    
    fig = go.Figure()
    
    for category, color in [
        ('Perceived Dry', COLORS_RAIN['perceived_dry']),
        ('Perceived Rainy', COLORS_RAIN['perceived_rainy']),
    ]:
        cat_data = df_day[df_day['rain_category'] == category]['deviation_from_baseline']
        
        fig.add_trace(go.Violin(
            y=cat_data,
            name=category,
            box_visible=True,
            meanline_visible=True,
            fillcolor=color,
            line_color=color,
            opacity=0.7,
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                  annotation_text="Baseline (local 2-week avg)")
    
    fig.update_layout(
        title=title + f"<br><sup>Using {window_days}-day rolling window, daytime hours (7-20h)</sup>",
        yaxis_title='Deviation from Baseline [%]',
        showlegend=True,
        height=500,
    )
    
    return fig
