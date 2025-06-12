import requests
import pandas as pd
from get_ap_data import get_wifi_aps_pywifi_windows_robust_v2
from get_longlat_from_ps import get_location_from_powershell

def get_wifi_data_json(spot="lokal"):
    detected_aps_df = get_wifi_aps_pywifi_windows_robust_v2()
    location_df = get_location_from_powershell("get_location.ps1")
    
    if detected_aps_df.empty or location_df.empty:
        return None
    
    location = location_df.iloc[0].to_dict()
    detected_aps_df['spot'] = spot
    detected_aps_df['latitude'] = location['latitude']
    detected_aps_df['longitude'] = location['longitude']
    
    return detected_aps_df

def upload_snapshot_to_streamlit(df, url):
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    files = {'file': ("snapshot.csv", csv_bytes, "text/csv")}
    
    response = requests.post(url, files=files)
    if response.status_code == 200:
        print("✅ Upload berhasil.")
    else:
        print(f"❌ Upload gagal. Status: {response.status_code}")

if __name__ == "__main__":
    df = get_wifi_data_json()
    if df is not None:
        upload_snapshot_to_streamlit(df, url="https://your-app-name.streamlit.app/")
    else:
        print("Gagal mengambil data.")
