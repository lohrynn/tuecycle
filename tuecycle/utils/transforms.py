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
