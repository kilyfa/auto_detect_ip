import streamlit as st
import pandas as pd
import numpy as np
from get_longlat_from_ps import get_location_from_powershell
from get_ap_data import get_wifi_aps_pywifi_windows_robust_v2
import base64

def get_wifi_data_streamlit(spot: str, filter_untirta: bool, target_ssid: str = None):
    script_path = "get_location.ps1"
    detected_aps_df = get_wifi_aps_pywifi_windows_robust_v2()
    location_df = get_location_from_powershell(script_path)

    if detected_aps_df.empty or location_df.empty:
        return pd.DataFrame()

    if filter_untirta:
        detected_aps_df = detected_aps_df[detected_aps_df['ssid'].str.strip().str.lower() == 'untirta']
        if detected_aps_df.empty:
            return pd.DataFrame()
    elif target_ssid is not None and target_ssid.strip() != "":
        detected_aps_df = detected_aps_df[detected_aps_df['ssid'].str.strip().str.lower() == target_ssid.strip().lower()]
        if detected_aps_df.empty:
            return pd.DataFrame()

    location_df_final = pd.DataFrame(np.tile(location_df.values, (detected_aps_df.shape[0], 1)), columns=location_df.columns)
    spot_df = pd.DataFrame({"spot": [spot]})
    spot_df_final = pd.DataFrame(np.tile(spot_df.values, (detected_aps_df.shape[0], 1)), columns=spot_df.columns)
    merged_df = pd.concat([detected_aps_df, location_df_final, spot_df_final], axis=1)
    return merged_df.drop_duplicates(subset=['bssid', 'signal_dBm', 'frequency_MHz'])

st.title("🔍 Snapshot Wi-Fi")
spot = st.text_input("Masukkan Nama Spot")
filter_option = st.selectbox("Pilih jaringan yang ingin diambil:", ["Hanya UNTIRTA", "Filter SSID Tertentu", "Semua Jaringan"])
target_ssid = None
if filter_option == "Filter SSID Tertentu":
    target_ssid = st.text_input("Masukkan SSID yang ingin difilter (kosongkan untuk semua):")
filter_untirta = filter_option == "Hanya UNTIRTA"

def get_table_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Klik di sini untuk mengunduh snapshot</a>'
    return href

if st.button("📸 Ambil Snapshot"):
    if spot.strip() == "":
        st.warning("Isi nama spot terlebih dahulu.")
    else:
        with st.spinner("Memindai jaringan dan mengambil lokasi..."):
            df_result = get_wifi_data_streamlit(spot, filter_untirta, target_ssid)
            if df_result.empty:
                st.error("Tidak ada jaringan terdeteksi atau lokasi gagal diambil.")
            else:
                st.success(f"{len(df_result)} jaringan terdeteksi!")
                st.dataframe(df_result)
                filename = f"snapshot_{spot.lower()}_{'untirta' if filter_untirta else 'all'}.csv"
                df_result.to_csv(filename, index=False)
                st.info(f"Hasil disimpan ke '{filename}'")
                html = get_table_download_link(df_result, filename)
                st.markdown(html, unsafe_allow_html=True)