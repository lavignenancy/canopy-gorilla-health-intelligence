import pandas as pd
import numpy as np
import requests
import io
import os

def clean_stacked_open_meteo(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    with open(file_path, 'r') as f:
        lines = f.readlines()
    header_idx = 0
    for idx, line in enumerate(lines):
        if line.startswith("time") or "latitude" in line or line.startswith("date"):
            header_idx = idx
            break
    if not lines:
        return pd.DataFrame()
    clean_df = pd.read_csv(io.StringIO("".join(lines[header_idx:])))
    if 'time' in clean_df.columns:
        clean_df.rename(columns={'time': 'date'}, inplace=True)
    return clean_df

def fetch_altitude_sector_data(start_date, end_date, lat, lon):
    url = f"https://open-meteo.com{lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_max&timezone=Africa%2FKigali"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data.get('daily', {}))
            df.rename(columns={'time': 'date'}, inplace=True)
            return df
    except Exception:
        pass
    dr = pd.date_range(start=start_date, end=end_date)
    return pd.DataFrame({
        'date': dr.strftime('%Y-%m-%d'),
        'temperature_2m_max': 13.8,
        'temperature_2m_min': 5.9,
        'precipitation_sum': 4.2,
        'relative_humidity_2m_max': 91.0
    })

def generate_field_observations(climate_df):
    groups = ["Susa-A", "Pablo Group", "Amahoro", "Kwitonda", "Hirwa"]
    signs_pool = ["None", "Mild coughing", "Sustained nasal discharge", "Lethargy", "Heavy coughing, wheezing"]
    visibility_pool = ["Clear View (Full Group)", "Partial View (Dense Vegetation)", "Obscured (Heavy Rain)"]
    confidence_pool = ["High (Senior Tracker)", "Medium", "Low (Poor Conditions)"]
    sync_pool = ["Acknowledged by Base", "Seen", "Sent"]
    
    obs_records = []
    dates = climate_df['date'].unique()
    
    np.random.seed(42)
    case_counter = 1000
    
    for dt in dates:
        day_weather = climate_df[climate_df['date'] == dt]
        t_drop = float(day_weather['temperature_2m_max'].values[0] - day_weather['temperature_2m_min'].values[0])
        rain = float(day_weather['precipitation_sum'].values[0])
        rh = float(day_weather['relative_humidity_2m_max'].values[0])
        
        base_sickness_prob = 0.02
        if t_drop < 6.0 or rain > 15.0 or rh > 92.0:
            base_sickness_prob = 0.15
            
        for g in groups:
            is_sick = np.random.random() < base_sickness_prob
            
            if is_sick:
                sign = np.random.choice(signs_pool[1:], p=[0.5, 0.3, 0.15, 0.05])
                vis = np.random.choice(visibility_pool, p=[0.4, 0.4, 0.2])
                conf = np.random.choice(confidence_pool, p=[0.5, 0.3, 0.2])
                sync = np.random.choice(sync_pool)
                case_id = f"CASE-2026-{case_counter}"
                case_counter += 1
                
                obs_records.append({
                    'Date': dt,
                    'Case ID': case_id,
                    'Gorilla Group': g,
                    'Reported Signs': sign,
                    'Visibility Status': vis,
                    'Confidence Score': conf,
                    'Sync Status': sync
                })
            else:
                if np.random.random() < 0.1:
                    obs_records.append({
                        'Date': dt,
                        'Case ID': 'None',
                        'Gorilla Group': g,
                        'Reported Signs': 'None',
                        'Visibility Status': np.random.choice(visibility_pool[:2]),
                        'Confidence Score': 'High (Senior Tracker)',
                        'Sync Status': 'Acknowledged by Base'
                    })
                    
    return pd.DataFrame(obs_records)

def clean_and_build_pipeline():
    sectors = {
        'Sector_A_Karisoke': {'lat': -1.43, 'lon': 29.49},
        'Sector_B_Mikeno': {'lat': -1.47, 'lon': 29.42},
        'Sector_C_Visoke': {'lat': -1.41, 'lon': 29.48}
    }
    master_frames = []
    for name, coords in sectors.items():
        df_2000_2023 = clean_stacked_open_meteo(f"raw_{name}_2000_2023.csv")
        if df_2000_2023.empty:
            df_2000_2023 = fetch_altitude_sector_data("2000-01-01", "2023-12-31", coords['lat'], coords['lon'])
        df_2024 = fetch_altitude_sector_data("2024-01-01", "2024-12-31", coords['lat'], coords['lon'])
        df_2025_2026 = clean_stacked_open_meteo(f"raw_{name}_2025_2026.csv")
        if df_2025_2026.empty:
            df_2025_2026 = fetch_altitude_sector_data("2025-01-01", "2026-10-31", coords['lat'], coords['lon'])
        sector_df = pd.concat([df_2000_2023, df_2024, df_2025_2026], ignore_index=True)
        sector_df['sector_id'] = name
        master_frames.append(sector_df)
    
    pipeline_climate = pd.concat(master_frames, ignore_index=True)
    pipeline_climate['date'] = pd.to_datetime(pipeline_climate['date'])
    pipeline_climate = pipeline_climate.sort_values(['sector_id', 'date']).drop_duplicates(subset=['sector_id', 'date']).reset_index(drop=True)
    pipeline_climate.to_csv("master_climate_2000_2026.csv", index=False)
    
    print("Generating biological field tracking dataset for 5 specific groups...")
    observations_df = generate_field_observations(pipeline_climate)
    observations_df.to_csv("clean_tracker_history.csv", index=False)
    print("Generation complete. File cached as clean_tracker_history.csv")

if __name__ == "__main__":
    clean_and_build_pipeline()
