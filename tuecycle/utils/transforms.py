"""
Data transformation and preprocessing utilities.

These functions add derived columns to DataFrames for analysis and plotting.
All functions follow a non-mutating pattern: they return a copy with new columns.
"""

import pandas as pd
import numpy as np


def add_time_features(df: pd.DataFrame, datetime_col: str = 'datetime') -> pd.DataFrame:
    """Add common time-based features to a DataFrame.
    
    Adds columns: hour, dayofweek, month, year_month, is_weekend
    
    Args:
        df: DataFrame with a datetime column.
        datetime_col: Name of the datetime column.
        
    Returns:
        DataFrame with additional time feature columns.
    """
    df = df.copy()
    dt = df[datetime_col]
    
    df['hour'] = dt.dt.hour
    df['dayofweek'] = dt.dt.dayofweek  # 0=Monday, 6=Sunday
    df['month'] = dt.dt.month
    df['year_month'] = dt.dt.to_period('M').astype(str)
    df['is_weekend'] = df['dayofweek'] >= 5
    
    return df


def filter_daytime(
    df: pd.DataFrame, 
    start_hour: int = 6, 
    end_hour: int = 22,
    hour_col: str = 'hour'
) -> pd.DataFrame:
    """Filter DataFrame to daytime hours only.
    
    Args:
        df: DataFrame with an hour column.
        start_hour: First hour to include (inclusive).
        end_hour: Last hour to include (inclusive).
        hour_col: Name of the hour column.
        
    Returns:
        Filtered DataFrame.
    """
    if hour_col not in df.columns:
        df = add_time_features(df)
    return df[(df[hour_col] >= start_hour) & (df[hour_col] <= end_hour)]


def compute_deviations(
    df: pd.DataFrame,
    bike_col: str = 'bike',
    temp_col: str = 'temp',
    month_col: str = 'month'
) -> pd.DataFrame:
    """Compute temperature and bike count deviations from monthly averages.
    
    Adds columns:
        - temp_deviation: hourly temp - monthly average temp
        - bike_deviation: (hourly bike - monthly avg) / monthly avg * 100 (percentage)
    
    Args:
        df: DataFrame with bike, temp, and month columns.
        bike_col: Name of the bike count column.
        temp_col: Name of the temperature column.
        month_col: Name of the month column.
        
    Returns:
        DataFrame with deviation columns added.
    """
    df = df.copy()
    
    if month_col not in df.columns:
        df = add_time_features(df)
    
    # Calculate monthly averages
    monthly_avg_temp = df.groupby(month_col)[temp_col].transform('mean')
    monthly_avg_bike = df.groupby(month_col)[bike_col].transform('mean')
    
    # Temperature deviation (absolute)
    df['temp_deviation'] = df[temp_col] - monthly_avg_temp
    
    # Bike deviation (percentage)
    df['bike_deviation'] = ((df[bike_col] - monthly_avg_bike) / monthly_avg_bike) * 100
    
    return df


def classify_time_category(df: pd.DataFrame) -> pd.DataFrame:
    """Classify each row into a time category for rush hour analysis.
    
    Categories:
        - 'Morning Rush (7-9)': Weekday hours 7-8
        - 'Evening Rush (17-19)': Weekday hours 17-18
        - 'Weekday Non-Rush': Other weekday hours
        - 'Weekend': Saturday and Sunday
    
    Args:
        df: DataFrame with hour and dayofweek columns.
        
    Returns:
        DataFrame with 'time_category' column added.
    """
    df = df.copy()
    
    if 'hour' not in df.columns or 'dayofweek' not in df.columns:
        df = add_time_features(df)
    
    def classify(row):
        if row['dayofweek'] >= 5:
            return 'Weekend'
        if row['hour'] in [7, 8]:
            return 'Morning Rush (7-9)'
        if row['hour'] in [17, 18]:
            return 'Evening Rush (17-19)'
        return 'Weekday Non-Rush'
    
    df['time_category'] = df.apply(classify, axis=1)
    
    return df


def add_season(df: pd.DataFrame, month_col: str = 'month') -> pd.DataFrame:
    """Add season classification based on month.
    
    Seasons:
        - Winter: Nov, Dec, Jan, Feb
        - Transition: Mar, Apr, Sep, Oct
        - Summer: May, Jun, Jul, Aug
    
    Args:
        df: DataFrame with a month column.
        month_col: Name of the month column.
        
    Returns:
        DataFrame with 'season' column added.
    """
    df = df.copy()
    
    if month_col not in df.columns:
        df = add_time_features(df)
    
    winter_months = [11, 12, 1, 2]
    summer_months = [5, 6, 7, 8]
    # transition_months = [3, 4, 9, 10]
    
    def get_season(month):
        if month in winter_months:
            return 'Winter'
        if month in summer_months:
            return 'Summer'
        return 'Transition'
    
    df['season'] = df[month_col].apply(get_season)
    
    return df


def prepare_fft_data(series: pd.Series, fill_value: float = 0) -> np.ndarray:
    """Prepare a time series for FFT analysis.
    
    - Fills NaN values
    - Converts to numpy array
    - Removes mean (detrending)
    
    Args:
        series: Pandas Series with the data.
        fill_value: Value to use for NaN replacement.
        
    Returns:
        Numpy array ready for FFT.
    """
    data = series.fillna(fill_value).to_numpy()
    return data - np.mean(data)


def compute_hourly_stats(
    df: pd.DataFrame,
    value_col: str = 'bike',
    group_cols: list[str] | None = None
) -> pd.DataFrame:
    """Compute hourly statistics (mean, std) for a value column.
    
    Args:
        df: DataFrame with hour and value columns.
        value_col: Column to compute statistics for.
        group_cols: Additional columns to group by (default: just 'hour').
        
    Returns:
        DataFrame with hour, mean, and std columns.
    """
    if 'hour' not in df.columns:
        df = add_time_features(df)
    
    if group_cols is None:
        group_cols = ['hour']
    else:
        group_cols = ['hour'] + [c for c in group_cols if c != 'hour']
    
    return df.groupby(group_cols)[value_col].agg(['mean', 'std']).reset_index()


def add_perceived_rainy(
    df: pd.DataFrame,
    rain_col: str = 'rain',
    datetime_col: str = 'datetime',
    rain_threshold: float = 0.1,
    morning_hours: tuple[int, int] = (5, 9),
    evening_hours: tuple[int, int] = (18, 23),
) -> pd.DataFrame:
    """Classify each day as 'perceived rainy' based on when rain occurred.
    
    A day is considered 'perceived rainy' if cyclists would anticipate rain
    when making their commuting decision. This captures the idea that cyclists
    can't cancel mid-ride, so the decision is made before departure based on:
    
    1. Rain the previous evening (18:00-23:00)
    2. Rain in the early morning (5:00-9:00)
    
    This is more relevant than "did it rain at this exact hour?".
    
    Args:
        df: DataFrame with datetime and rain columns.
        rain_col: Name of the rain column (mm).
        datetime_col: Name of the datetime column.
        rain_threshold: Minimum rain (mm) to count as rainy.
        morning_hours: Tuple of (start, end) hours for morning rain check.
        evening_hours: Tuple of (start, end) hours for previous evening rain check.
        
    Returns:
        DataFrame with added columns:
            - date: The date (for grouping)
            - morning_rain: Total rain in morning hours
            - prev_evening_rain: Total rain in previous evening
            - perceived_rainy: Boolean, True if morning or prev evening had rain
            - rain_category: 'Perceived Dry' or 'Perceived Rainy'
    """
    df = df.copy()
    
    # Ensure datetime and hour columns exist
    if datetime_col in df.columns:
        dt = df[datetime_col]
    else:
        raise ValueError(f"Column '{datetime_col}' not found in DataFrame")
    
    if 'hour' not in df.columns:
        df = add_time_features(df, datetime_col)
    
    df['date'] = dt.dt.date
    
    # Calculate morning rain for each day (rain during morning_hours)
    morning_mask = (df['hour'] >= morning_hours[0]) & (df['hour'] <= morning_hours[1])
    morning_rain = df[morning_mask].groupby('date')[rain_col].sum()
    morning_rain.name = 'morning_rain'
    
    # Calculate previous evening rain (shift by 1 day)
    evening_mask = (df['hour'] >= evening_hours[0]) & (df['hour'] <= evening_hours[1])
    evening_rain = df[evening_mask].groupby('date')[rain_col].sum()
    
    # Shift evening rain to next day (it affects the next day's perception)
    evening_rain_shifted = evening_rain.shift(1, fill_value=0)
    evening_rain_shifted.name = 'prev_evening_rain'
    
    # Create a daily summary DataFrame
    daily_rain = pd.DataFrame({
        'morning_rain': morning_rain,
        'prev_evening_rain': evening_rain_shifted
    }).fillna(0)
    
    # Merge back to hourly data
    df = df.merge(daily_rain, left_on='date', right_index=True, how='left')
    df['morning_rain'] = df['morning_rain'].fillna(0)
    df['prev_evening_rain'] = df['prev_evening_rain'].fillna(0)
    
    # Classify as perceived rainy
    df['perceived_rainy'] = (
        (df['morning_rain'] > rain_threshold) | 
        (df['prev_evening_rain'] > rain_threshold)
    )
    
    df['rain_category'] = df['perceived_rainy'].map({
        True: 'Perceived Rainy',
        False: 'Perceived Dry'
    })
    
    return df


def compute_rolling_baseline(
    df: pd.DataFrame,
    value_col: str = 'bike',
    datetime_col: str = 'datetime',
    window_days: int = 14,
    by_hour: bool = True,
    by_weekday_type: bool = True,
) -> pd.DataFrame:
    """Compute a rolling baseline for bike counts to account for seasonal variation.
    
    This computes a local time-window average, allowing to see deviations
    that account for the natural seasonal fluctuation in cycling.
    
    For example, a rainy day in summer might still have more cyclists than
    an average winter day, but fewer than the surrounding summer days.
    
    Args:
        df: DataFrame with datetime and value columns.
        value_col: Column to compute baseline for.
        datetime_col: Name of the datetime column.
        window_days: Size of the rolling window in days (default 14 = 2 weeks).
        by_hour: If True, compute separate baselines for each hour of day.
        by_weekday_type: If True, compute separate baselines for weekdays vs weekends.
        
    Returns:
        DataFrame with added columns:
            - rolling_baseline: The local average for this hour/weekday-type
            - deviation_from_baseline: (value - baseline) / baseline * 100
    """
    df = df.copy()
    
    if 'hour' not in df.columns or 'is_weekend' not in df.columns:
        df = add_time_features(df, datetime_col)
    
    df['date'] = df[datetime_col].dt.date
    
    # Build grouping key
    group_cols = ['date']
    if by_hour:
        group_cols.append('hour')
    if by_weekday_type:
        group_cols.append('is_weekend')
    
    # For each unique combination of (hour, is_weekend), compute rolling mean
    df = df.sort_values(datetime_col)
    
    # Create a daily average first (to smooth out hourly noise)
    if by_hour and by_weekday_type:
        # Group by date, hour, is_weekend and take mean
        daily_hourly = df.groupby(['date', 'hour', 'is_weekend'])[value_col].mean().reset_index()
        daily_hourly = daily_hourly.sort_values(['is_weekend', 'hour', 'date'])
        
        # Rolling mean within each (hour, is_weekend) group
        daily_hourly['rolling_baseline'] = daily_hourly.groupby(['hour', 'is_weekend'])[value_col].transform(
            lambda x: x.rolling(window=window_days, min_periods=3, center=True).mean()
        )
        
        # Merge back
        df = df.merge(
            daily_hourly[['date', 'hour', 'is_weekend', 'rolling_baseline']],
            on=['date', 'hour', 'is_weekend'],
            how='left'
        )
    else:
        # Simpler case: just rolling mean over all data
        df['rolling_baseline'] = df[value_col].rolling(
            window=window_days * 24, min_periods=24, center=True
        ).mean()
    
    # Compute deviation as percentage
    df['deviation_from_baseline'] = (
        (df[value_col] - df['rolling_baseline']) / df['rolling_baseline'] * 100
    ).replace([np.inf, -np.inf], np.nan)
    
    return df


def aggregate_stations_zscore(
    dfs: dict[str, pd.DataFrame],
    stations: list[str] | None = None,
    bike_col: str = 'bike',
    winsorize_percentiles: tuple[float, float] | None = (0.01, 0.99),
) -> pd.DataFrame:
    """Aggregate multiple stations into a single city-level representation using z-score normalization.
    
    Each station's bike counts are z-score normalized (mean=0, std=1), then averaged
    across stations for each timestamp. This removes scale differences between stations
    while preserving temporal patterns.
    
    The resulting 'bike' column represents a normalized city-wide cycling index that
    can be used with all existing plot functions and weather elasticity metrics.
    
    Args:
        dfs: Dictionary mapping station aliases to DataFrames (from DataManager.get_multiple()).
        stations: List of station aliases to include. If None, uses all stations in dfs.
        bike_col: Name of the bike count column in input DataFrames.
        winsorize_percentiles: Tuple of (lower, upper) percentiles for winsorization.
                               Values outside these percentiles are capped before z-scoring.
                               Default (0.01, 0.99) caps at 1st and 99th percentiles.
                               Set to None to disable winsorization.
        
    Returns:
        DataFrame with columns:
            - datetime: Timestamp
            - bike: Z-score normalized average across selected stations
            - bike_raw_sum: Sum of raw counts (for reference)
            - n_stations: Number of stations with data at each timestamp
            - Plus all weather columns from the first station (rain, temp, etc.)
            
    Example:
        >>> dm = DataManager()
        >>> dfs = dm.get_multiple(["heidelberg_kurfuersten", "heidelberg_mannheimer", "heidelberg_gaisberg"])
        >>> # Default: with winsorization
        >>> city_df = aggregate_stations_zscore(dfs)
        >>> 
        >>> # More aggressive outlier capping
        >>> city_df = aggregate_stations_zscore(dfs, winsorize_percentiles=(0.005, 0.995))
        >>> 
        >>> # No outlier treatment
        >>> city_df = aggregate_stations_zscore(dfs, winsorize_percentiles=None)
    """
    if stations is None:
        stations = list(dfs.keys())
    
    # Filter to requested stations
    selected_dfs = {k: v for k, v in dfs.items() if k in stations}
    
    if not selected_dfs:
        raise ValueError(f"No matching stations found. Available: {list(dfs.keys())}")
    
    # Compute z-scores for each station
    zscore_dfs = []
    for alias, df in selected_dfs.items():
        df = df.copy()
        
        # Apply winsorization if requested
        bike_data = df[bike_col].copy()
        if winsorize_percentiles is not None:
            lower_pct, upper_pct = winsorize_percentiles
            lower_bound = bike_data.quantile(lower_pct)
            upper_bound = bike_data.quantile(upper_pct)
            bike_data = bike_data.clip(lower=lower_bound, upper=upper_bound)
        
        # Compute z-score for bike counts
        mean_bike = bike_data.mean()
        std_bike = bike_data.std()
        
        if std_bike > 0:
            df['bike_zscore'] = (bike_data - mean_bike) / std_bike
        else:
            df['bike_zscore'] = 0.0
        
        df['station'] = alias
        zscore_dfs.append(df)
    
    # Combine all stations
    combined = pd.concat(zscore_dfs, ignore_index=True)
    
    # Aggregate by timestamp: mean of z-scores and sum of raw counts
    agg_result = combined.groupby('datetime').agg({
        'bike_zscore': 'mean',
        bike_col: ['sum', 'count'],
    }).reset_index()
    
    # Flatten column names
    agg_result.columns = ['datetime', 'bike', 'bike_raw_sum', 'n_stations']
    
    # Add weather data from the first station (assuming same location/weather)
    first_station = list(selected_dfs.values())[0]
    weather_cols = [c for c in first_station.columns if c not in ['datetime', bike_col, 'bike_zscore', 'station']]
    
    if weather_cols:
        weather_df = first_station[['datetime'] + weather_cols].drop_duplicates(subset='datetime')
        agg_result = agg_result.merge(weather_df, on='datetime', how='left')
    
    return agg_result.sort_values('datetime').reset_index(drop=True)
