#!/usr/bin/env python
# coding: utf-8

import datetime

import pandas as pd
import glob

def get_bike_table(start_year, start_month, start_day, end_year, end_month, end_day):
    # Get the necessary files
    df_list = []
    for year in range(start_year, end_year + 1):
        # Determine which months to load for this year
        if (year, year) == (start_year, end_year):
            # Single year span
            months = range(start_month, end_month + 1)
        elif year == start_year:
            # First year: From start_month to December
            months = range(start_month, 13)
        elif year == end_year:
            # Last year: From January to end_month
            months = range(1, end_month + 1)
        else:
            # Middle years: All months
            months = range(1, 13)
        
        # Load only the relevant month files
        for month in months:
            file_pattern = f"data/bike_data/{year}/{month:02d}.csv"
            matching_files = glob.glob(file_pattern)
            
            for f in matching_files:
                df_temp = pd.read_csv(f, low_memory=False)
                df_list.append(df_temp)


    # Put the files together
    df = pd.concat(df_list, ignore_index=True)

    # Convert ISO timestamps to timezone-aware, then to local Berlin time
    df['iso_timestamp'] = pd.to_datetime(df['iso_timestamp'], errors='coerce', utc=True)
    df['iso_timestamp'] = df['iso_timestamp'].dt.tz_convert('Europe/Berlin')
    
    # Convert to naive local time (wall-clock time)
    df['iso_timestamp'] = df['iso_timestamp'].dt.tz_localize(None)
    
    # Remove duplicate hours during fall-back (Keep summer 2AM instead of winter 2AM in)
    df = df.drop_duplicates(subset=['iso_timestamp', 'counter_site'], keep='first')

    # Now only add the necessary data
    df_hourly = df.groupby(['iso_timestamp', 'counter_site']).agg({
    'channels_all': 'first', # for more columns, add them here
    'domain_name': 'first'}).reset_index()

    # Filter to requested date range
    start_ts = pd.Timestamp(start_year, start_month, start_day, 0, 0)
    end_ts   = pd.Timestamp(end_year, end_month, end_day, 23, 0)
    df_hourly = df_hourly[(df_hourly['iso_timestamp'] >= start_ts) & 
                           (df_hourly['iso_timestamp'] <= end_ts)]
    
    return df_hourly.sort_values('iso_timestamp').reset_index(drop=True)

def get_table_with_weather(city,counter_name, start_year, start_month, start_day, end_year, end_month, end_day):
    """
    Merge bike counter data with weather data for a specific city and counter site.
    
    Returns:
        pd.DataFrame: Merged table with columns:
            - datetime: Local wall-clock time (naive datetime, the additional fall back hour is removed)
            - bike: Bike count from channels_all
            - rain: Precipitation in mm from prcp
            - temp: Temperature in °C)
    """

    weather_hourly = pd.read_csv(f'data/weather_data/hourly/{city.lower()}_weather_{start_year}-{start_month}-{start_day}_{end_year}-{end_month}-{end_day}.csv')

    bike_hourly = get_bike_table(start_year, start_month, start_day, end_year, end_month, end_day)
    bike_hourly = bike_hourly[bike_hourly['counter_site'] == counter_name]

    # Convert weather time to datetime and remove duplicate fall-back hours (keep first)
    weather_hourly['datetime'] = pd.to_datetime(weather_hourly['time'])
    weather_hourly = weather_hourly.drop_duplicates(subset='datetime', keep='first')
    
    # Bike iso_timestamp is already datetime, just rename for merge
    bike_hourly = bike_hourly.rename(columns={'iso_timestamp': 'datetime'})

    # Merge both tables on datetime to get all data in one table
    df_common = pd.merge(
        bike_hourly[['datetime', 'channels_all']],
        # If more weather data is needed, add columns here:
        weather_hourly[['datetime', 'prcp', 'temp']],
        on='datetime',
        how='outer'
    ).sort_values('datetime')

    # Rename columns for clarity
    df_common.rename(columns={'channels_all': 'bike', 'prcp': 'rain'}, inplace=True)

    df_common[['bike', 'rain', 'temp']] = df_common[['bike', 'rain', 'temp']].apply(
        pd.to_numeric, errors='coerce'
    )

    return df_common




