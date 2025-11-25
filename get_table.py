#!/usr/bin/env python
# coding: utf-8

# In[53]:


import pandas as pd
import glob

def get_bike_table(start_year, start_month, start_day, end_year, end_month, end_day):
    # Get the necessary files
    df_list = []
    for year in range(start_year, end_year + 1):
        files_to_load = glob.glob(f"{'eco-counter/all_cities'}/{year}/*.csv")
        for f in files_to_load:
            df_temp = pd.read_csv(f, low_memory=False)
            df_list.append(df_temp)

    # Put the files together
    df = pd.concat(df_list, ignore_index=True)

    df['iso_timestamp'] = pd.to_datetime(df['iso_timestamp'], errors='coerce', utc=True)
# Für Deutschland (MEZ/CEST)
    df['iso_timestamp'] = df['iso_timestamp'].dt.tz_convert('Europe/Berlin').dt.tz_localize(None)


    # Now only add the necessary data
    df_hourly = df.groupby(['iso_timestamp', 'counter_site']).agg({
    'channels_all': 'first',  # falls du mehrere Kanäle hast
    'domain_name': 'first'}).reset_index()

    start_ts = pd.Timestamp(start_year, start_month, start_day, 0, 0)
    end_ts   = pd.Timestamp(end_year, end_month, end_day, 23, 0)
    hours = pd.date_range(start=start_ts, end=end_ts, freq='h')

    df_full = pd.DataFrame({'iso_timestamp': hours})
    df_full = df_full.merge(df_hourly, on='iso_timestamp', how='left')
    df_full = df_full.sort_values('iso_timestamp').reset_index(drop=True)
    return df_full


# In[55]:


import pandas as pd
import glob

def get_table_with_weather(city,counter_name, start_year, start_month, start_day, end_year, end_month, end_day):

    weather_hourly = pd.read_csv(f'weather_data/hourly/{city.lower()}_weather_{start_year}-{start_month}-{start_day}_{end_year}-{end_month}-{end_day}.csv')

    bike_hourly = get_bike_table(start_year, start_month, start_day, end_year, end_month, end_day)
    bike_hourly = bike_hourly[bike_hourly['counter_site'] == counter_name]

    # Add a new column datetime in both tables (for same name)
    weather_hourly['datetime'] = pd.to_datetime(weather_hourly['time'])
    bike_hourly['datetime'] = pd.to_datetime(bike_hourly['iso_timestamp'])

    # Merge both tables on datetime to get all data in one table
    df_common = pd.merge(
        bike_hourly[['datetime', 'channels_all']],
        weather_hourly[['datetime', 'prcp', 'temp']],
        on='datetime',
        how='outer'
    ).sort_values('datetime')

    # Rename columns for clarity
    df_common.rename(columns={'channels_all': 'bike', 'prcp': 'rain', 'temp': 'temp'}, inplace=True)

    df_common[['bike', 'rain', 'temp']] = df_common[['bike', 'rain', 'temp']].apply(
        pd.to_numeric, errors='coerce'
    )

    return df_common


# In[ ]:




