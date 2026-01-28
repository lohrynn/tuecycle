"""
Weather composite index and elasticity calculations.

Based on Goldmann & Wessel (2021): "Some people feel the rain, others just get wet:
An analysis of regional differences in the effects of weather on cycling"

The composite weather indicator aggregates multiple weather variables into a single
index (0 = best weather, 1 = worst weather), which can then be used to analyze
how bike traffic responds to weather conditions across different cities.
"""

import numpy as np
import pandas as pd
from scipy import stats


class WeatherCompositeIndex:
    """
    Calculates the Composite Weather Indicator based on Goldmann and Wessel (2021).
    
    The index combines temperature, precipitation, wind speed, humidity, and cloud
    cover into a single metric where 0 represents the best weather and 1 represents
    the worst weather conditions for cycling.
    
    Methodology:
        1. Standardization: All variables converted to z-scores
        2. Temperature inversion: Multiplied by -1 so higher values = worse (colder)
        3. Geometric aggregation: Captures that extreme bad weather in one variable
           cannot be compensated by good weather in another
        4. Winsorization: Caps extreme outliers at 99.8th percentile
        5. Min-max normalization: Scales final index to [0, 1]
    
    Example:
        >>> calculator = WeatherCompositeIndex(df)
        >>> df['weather_index'] = calculator.calculate_metric()
    
    Attributes:
        df (pd.DataFrame): DataFrame containing the hourly weather variables.
        required_cols (list): Required column names for calculation.
    """
    
    # Default column mappings for weather data (original names from weather files)
    DEFAULT_COLUMNS = {
        'temp_c': 'temperature_2m (°C)',
        'precip_mm': 'precipitation (mm)',
        'wind_ms': 'wind_speed_10m (km/h)',  # Will be converted from km/h to m/s
        'humidity_pct': 'relative_humidity_2m (%)',
        'cloud_cover': 'cloud_cover (%)',  # Will be converted from % to eighths
    }
    
    # Alternative column names after DataManager renaming
    LOADER_COLUMNS = {
        'temp_c': 'temp',
        'precip_mm': 'rain',
        'wind_ms': 'wind',
        'humidity_pct': 'humidity',
        'cloud_cover': 'clouds',
    }
    
    def __init__(self, df: pd.DataFrame, column_mapping: dict | None = None):
        """
        Initialize the WeatherCompositeIndex calculator.
        
        Args:
            df: DataFrame containing hourly weather data.
            column_mapping: Optional dict mapping required column names to actual
                           column names in df. If not provided, auto-detects
                           based on available columns.
        
        Raises:
            ValueError: If required columns are missing from the DataFrame.
        """
        self.df = df.copy()
        self._required_keys = ['temp_c', 'precip_mm', 'wind_ms', 'humidity_pct', 'cloud_cover']
        
        # Auto-detect column mapping if not provided
        if column_mapping is None:
            # Try loader columns first (after DataManager renaming)
            if all(v in self.df.columns for v in self.LOADER_COLUMNS.values()):
                self.column_mapping = self.LOADER_COLUMNS.copy()
            # Then try default columns (original weather file names)
            elif all(v in self.df.columns for v in self.DEFAULT_COLUMNS.values()):
                self.column_mapping = self.DEFAULT_COLUMNS.copy()
            else:
                # Try to detect which columns are available
                self.column_mapping = self._detect_columns()
        else:
            self.column_mapping = column_mapping.copy()
        
        # Check that all required keys exist in the mapping
        missing_keys = [k for k in self._required_keys if k not in self.column_mapping]
        if missing_keys:
            available = list(self.df.columns)
            raise ValueError(
                f"Missing required column mappings for: {missing_keys}\n"
                f"Available columns: {available}\n"
                f"Current mapping: {self.column_mapping}"
            )
        
        # Check that all mapped columns exist in DataFrame
        missing_cols = [v for v in self.column_mapping.values() if v not in self.df.columns]
        if missing_cols:
            available = list(self.df.columns)
            raise ValueError(
                f"Missing columns in DataFrame: {missing_cols}\n"
                f"Available columns: {available}"
            )
    
    def _detect_columns(self) -> dict:
        """Auto-detect which column naming convention is being used."""
        mapping = {}
        df_cols = set(self.df.columns)
        
        # Temperature
        if 'temp' in df_cols:
            mapping['temp_c'] = 'temp'
        elif 'temperature_2m (°C)' in df_cols:
            mapping['temp_c'] = 'temperature_2m (°C)'
        
        # Precipitation
        if 'rain' in df_cols:
            mapping['precip_mm'] = 'rain'
        elif 'precipitation (mm)' in df_cols:
            mapping['precip_mm'] = 'precipitation (mm)'
        
        # Wind speed
        if 'wind_speed_10m (km/h)' in df_cols:
            mapping['wind_ms'] = 'wind_speed_10m (km/h)'
        
        # Humidity
        if 'relative_humidity_2m (%)' in df_cols:
            mapping['humidity_pct'] = 'relative_humidity_2m (%)'
        
        # Cloud cover
        if 'cloud_cover (%)' in df_cols:
            mapping['cloud_cover'] = 'cloud_cover (%)'
        
        return mapping
    
    def _prepare_variables(self) -> pd.DataFrame:
        """
        Prepare and normalize weather variables to consistent units.
        
        Returns:
            DataFrame with standardized variable names and units.
        """
        prepared = pd.DataFrame(index=self.df.index)
        
        # Temperature (already in °C)
        prepared['temp_c'] = self.df[self.column_mapping['temp_c']]
        
        # Precipitation (already in mm)
        prepared['precip_mm'] = self.df[self.column_mapping['precip_mm']]
        
        # Wind speed: convert km/h to m/s
        wind_col = self.column_mapping['wind_ms']
        prepared['wind_ms'] = self.df[wind_col] / 3.6
        
        # Humidity (already in %)
        prepared['humidity_pct'] = self.df[self.column_mapping['humidity_pct']]
        
        # Cloud cover: convert from % to eighths (0-8 scale)
        cloud_col = self.column_mapping['cloud_cover']
        prepared['cloud_cover'] = self.df[cloud_col] / 100 * 8
        
        return prepared
    
    def calculate_metric(self) -> pd.Series:
        """
        Performs the standardization, aggregation, and normalization steps.
        
        Returns:
            pd.Series: Weather index values (0 = best, 1 = worst weather).
        """
        # Prepare variables with consistent units
        prepared = self._prepare_variables()
        required_cols = ['temp_c', 'precip_mm', 'wind_ms', 'humidity_pct', 'cloud_cover']
        
        # Drop rows with missing values for calculation
        valid_mask = prepared[required_cols].notna().all(axis=1)
        prepared_valid = prepared.loc[valid_mask, required_cols]
        
        if len(prepared_valid) == 0:
            return pd.Series(np.nan, index=self.df.index)
        
        # 1. Standardization (Z-scores)
        z_scores = (
            (prepared_valid - prepared_valid.mean()) / 
            prepared_valid.std()
        )
        
        # 2. Adjust Temperature Direction 
        # Positive values imply colder and thus worse weather conditions
        z_scores['temp_c'] = z_scores['temp_c'] * -1
        
        # 3. Shift to positive domain for geometric aggregation
        # Standard methodology: shift so minimum value becomes 1
        shifted_z = z_scores.apply(lambda x: x - x.min() + 1)
        
        # 4. Geometric Aggregation with equal weights
        # Product of variables raised to the power of (1/n)
        n_vars = len(required_cols)
        product_series = shifted_z.prod(axis=1)
        composite_raw = np.power(product_series, 1 / n_vars)
        
        # 5. Winsorization at 99.8th percentile
        limit = composite_raw.quantile(0.998)
        composite_winsorized = composite_raw.clip(upper=limit)
        
        # 6. Min-Max Normalization to [0, 1]
        min_val = composite_winsorized.min()
        max_val = composite_winsorized.max()
        
        if max_val == min_val:
            final_index = pd.Series(0.5, index=composite_winsorized.index)
        else:
            final_index = (composite_winsorized - min_val) / (max_val - min_val)
        
        # Create result series with original index, NaN for missing
        result = pd.Series(np.nan, index=self.df.index)
        result.loc[final_index.index] = final_index.values
        
        return result


def calculate_weather_elasticity(
    beta_coefficient: float,
    q1_val: float = 0.209567,
    q3_val: float = 0.262406,
) -> float:
    """
    Calculates the weather elasticity using the scaled formula from Goldmann & Wessel.
    
    The elasticity reflects the percentage change in ridership when the weather 
    index shifts from Q1 (good weather) to Q3 (bad weather).
    
    Formula: (e^(beta * (Q3 - Q1)) - 1) * 100
    
    Args:
        beta_coefficient: The raw regression coefficient for the interaction 
                         between the weather index and the city dummy.
        q1_val: 25th percentile of the weather index (default from paper).
        q3_val: 75th percentile of the weather index (default from paper).
    
    Returns:
        The calculated weather elasticity percentage.
        
    Example:
        >>> elasticity = calculate_weather_elasticity(-1.72)
        >>> print(f"Elasticity: {elasticity:.2f}%")
    """
    weather_diff = q3_val - q1_val
    elasticity = (np.exp(beta_coefficient * weather_diff) - 1) * 100
    return elasticity


def estimate_city_elasticity(
    df: pd.DataFrame,
    bike_col: str = 'bike',
    weather_index_col: str = 'weather_index',
    use_log: bool = True,
    quantile_a: float = 0.25,
    quantile_b: float = 0.75,
) -> dict:
    """
    Estimate weather elasticity for a city using log-linear regression.
    
    Fits a model: log(bike_count) ~ weather_index (+ controls)
    Then calculates the elasticity using the Q1-Q3 shift formula.
    
    Args:
        df: DataFrame with bike counts and weather index.
        bike_col: Name of the bike count column.
        weather_index_col: Name of the weather index column.
        use_log: Whether to log-transform bike counts (for percentage interpretation).
    
    Returns:
        Dictionary containing:
            - beta: Raw regression coefficient
            - elasticity: Percentage change in ridership (Q1→Q3)
            - r_squared: R² of the regression
            - n_obs: Number of observations used
            - qa, qb: Quartile values used for elasticity calculation
            - pvalue: P-value for the beta coefficient
    """
    # Prepare data
    df_clean = df[[bike_col, weather_index_col]].dropna()
    
    # Filter out zero or negative bike counts if using log
    if use_log:
        df_clean = df_clean[df_clean[bike_col] > 0]
        y = np.log(df_clean[bike_col])
    else:
        y = df_clean[bike_col]
    
    x = df_clean[weather_index_col]
    
    if len(df_clean) < 10:
        return {
            'beta': np.nan,
            'elasticity': np.nan,
            'r_squared': np.nan,
            'n_obs': len(df_clean),
            'q1': np.nan,
            'q3': np.nan,
            'pvalue': np.nan,
        }
    
    # Fit regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Calculate quartiles from the data
    q1 = x.quantile(quantile_a)
    q3 = x.quantile(quantile_b)

    # Calculate elasticity using the formula
    weather_diff = q3 - q1
    if use_log:
        # For log model: elasticity = (exp(beta * delta) - 1) * 100
        elasticity = (np.exp(slope * weather_diff) - 1) * 100
    else:
        # For linear model: percentage change relative to mean
        mean_bike = df_clean[bike_col].mean()
        elasticity = (slope * weather_diff / mean_bike) * 100
    
    return {
        'beta': slope,
        'elasticity': elasticity,
        'r_squared': r_value ** 2,
        'n_obs': len(df_clean),
        'q1': q1,
        'q3': q3,
        'pvalue': p_value,
        'std_err': std_err,
    }


def add_weather_index(df: pd.DataFrame, column_mapping: dict | None = None) -> pd.DataFrame:
    """
    Convenience function to add weather index column to a DataFrame.
    
    Args:
        df: DataFrame with weather data columns.
        column_mapping: Optional column name mapping (see WeatherCompositeIndex).
    
    Returns:
        DataFrame with 'weather_index' column added.
    """
    df = df.copy()
    calculator = WeatherCompositeIndex(df, column_mapping)
    df['weather_index'] = calculator.calculate_metric()
    return df


def add_weather_quartile(
    df: pd.DataFrame,
    weather_index_col: str = 'weather_index',
    labels: list[str] | None = None,
) -> pd.DataFrame:
    """
    Add weather quartile classification to DataFrame.
    
    Args:
        df: DataFrame with weather index column.
        weather_index_col: Name of the weather index column.
        labels: Labels for quartiles (default: Q1 Best, Q2, Q3, Q4 Worst).
    
    Returns:
        DataFrame with 'weather_quartile' column added.
    """
    df = df.copy()
    
    if labels is None:
        labels = ['Q1 (Best)', 'Q2', 'Q3', 'Q4 (Worst)']
    
    try:
        # Try standard qcut with 4 bins
        df['weather_quartile'] = pd.qcut(
            df[weather_index_col],
            q=4,
            labels=labels,
            duplicates='drop'
        )
    except ValueError:
        # If labels don't match due to dropped duplicates, use no labels first
        # then map to our desired labels
        quartiles = pd.qcut(
            df[weather_index_col],
            q=4,
            duplicates='drop'
        )
        # Get unique bins and map them to our labels
        unique_bins = quartiles.cat.categories
        n_bins = len(unique_bins)
        
        if n_bins == 4:
            label_map = dict(zip(unique_bins, labels))
        elif n_bins == 3:
            label_map = dict(zip(unique_bins, ['Q1 (Best)', 'Q2-Q3', 'Q4 (Worst)']))
        elif n_bins == 2:
            label_map = dict(zip(unique_bins, ['Q1-Q2 (Good)', 'Q3-Q4 (Bad)']))
        else:
            label_map = {b: f'Bin {i+1}' for i, b in enumerate(unique_bins)}
        
        df['weather_quartile'] = quartiles.map(label_map)
    
    return df
