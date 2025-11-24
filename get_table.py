import pandas as pd
import glob

def get_table(base_path, start_year, start_month, start_day, end_year, end_month, end_day):
    # Get the necessary files
    df_list = []
    for year in range(start_year, end_year + 1):
        files_to_load = glob.glob(f"{base_path}/{year}/*.csv")
        for f in files_to_load:
            df_temp = pd.read_csv(f, low_memory=False)
            df_list.append(df_temp)

    # Put the files together
    df = pd.concat(df_list, ignore_index=True)

    # Make a correct timestamp column, add an hour because of UTC time
    df['iso_timestamp'] = pd.to_datetime(df['iso_timestamp'], errors='coerce', utc=True)
    df['iso_timestamp'] = df['iso_timestamp'].dt.tz_convert(None) + pd.Timedelta(hours=1)

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
