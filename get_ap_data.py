# wifi_scanner.py
import pywifi
from pywifi import const
import time
import sys
import pandas as pd # Tambahkan ini jika Anda juga ingin mengembalikan DataFrame langsung dari fungsi

# --- Fallback Dictionaries ---
MANUAL_AKM_TYPE_NAMES = {
    0: "AKM_TYPE_NONE", 1: "AKM_TYPE_WPA", 2: "AKM_TYPE_WPAPSK",
    3: "AKM_TYPE_WPA2", 4: "AKM_TYPE_WPA2PSK", 5: "AKM_TYPE_UNKNOWN",
    6: "AKM_TYPE_WPA3", 7: "AKM_TYPE_WPA3PSK", 8: "AKM_TYPE_WPA3_SAE",
}

MANUAL_CIPHER_TYPE_NAMES = {
    0: "CIPHER_TYPE_NONE", 1: "CIPHER_TYPE_WEP", 2: "CIPHER_TYPE_TKIP",
    3: "CIPHER_TYPE_CCMP", # AES
    4: "CIPHER_TYPE_UNKNOWN", 5: "CIPHER_TYPE_GCMP128",
    6: "CIPHER_TYPE_GCMP256",
}

MANUAL_AUTH_ALG_NAMES = {
    0: "AUTH_ALG_OPEN", 1: "AUTH_ALG_SHARED", 2: "AUTH_ALG_LEAP",
}

def get_wifi_aps_pywifi_windows_robust_v2():
    """
    Mendapatkan daftar Access Point WiFi dengan penanganan fallback yang lebih baik
    untuk konstanta _TYPE_NAMES dan potensi list pada cipher/auth.
    """
    akm_names = getattr(const, 'AKM_TYPE_NAMES', MANUAL_AKM_TYPE_NAMES)
    cipher_names = getattr(const, 'CIPHER_TYPE_NAMES', MANUAL_CIPHER_TYPE_NAMES)
    auth_alg_names = getattr(const, 'AUTH_ALG_NAMES', MANUAL_AUTH_ALG_NAMES)

    if not hasattr(const, 'AKM_TYPE_NAMES'):
        print("Peringatan: pywifi.const.AKM_TYPE_NAMES tidak ditemukan. Menggunakan fallback.")
    if not hasattr(const, 'CIPHER_TYPE_NAMES'):
        print("Peringatan: pywifi.const.CIPHER_TYPE_NAMES tidak ditemukan. Menggunakan fallback.")
    if not hasattr(const, 'AUTH_ALG_NAMES'):
        print("Peringatan: pywifi.const.AUTH_ALG_NAMES tidak ditemukan. Menggunakan fallback.")

    try:
        wifi = pywifi.PyWiFi()
        if len(wifi.interfaces()) == 0:
            print("Tidak ada antarmuka WiFi yang ditemukan.")
            return []
        
        iface = wifi.interfaces()[0]
        print(f"Menggunakan antarmuka: {iface.name()}")

        print("Memulai pemindaian jaringan WiFi...")
        iface.scan()
        
        scan_delay = 8
        print(f"Menunggu {scan_delay} detik hingga pemindaian selesai...")
        time.sleep(scan_delay)

        scan_results = iface.scan_results()
        aps_data = []
        if not scan_results:
            print("Tidak ada jaringan yang terdeteksi.")
            return []

        for i, profile in enumerate(scan_results):
            try:
                ssid_str = profile.ssid
                try:
                    ssid_str = profile.ssid.encode('raw_unicode_escape').decode('utf-8', 'ignore')
                except UnicodeDecodeError:
                    try:
                        ssid_str = profile.ssid.encode('latin-1').decode('utf-8', 'ignore')
                    except Exception:
                        ssid_str = str(profile.ssid)
                except AttributeError:
                    pass

                akm_types_str_list = []
                if isinstance(profile.akm, list):
                    for akm_suite in profile.akm:
                        akm_types_str_list.append(akm_names.get(akm_suite, f"AKM_Raw({akm_suite})"))
                else:
                    akm_types_str_list.append(akm_names.get(profile.akm, f"AKM_Raw({profile.akm})"))
                akm_final_str = ", ".join(akm_types_str_list) if akm_types_str_list else "AKM_Unknown"

                cipher_type_str = "Cipher_Unknown"
                if isinstance(profile.cipher, list):
                    cipher_type_list_str = [cipher_names.get(c, f"Cipher_Raw({c})") for c in profile.cipher]
                    cipher_type_str = ", ".join(cipher_type_list_str) if cipher_type_list_str else "Cipher_Unknown"
                elif profile.cipher is not None:
                    cipher_type_str = cipher_names.get(profile.cipher, f"Cipher_Raw({profile.cipher})")
                
                auth_alg_str = "Auth_Unknown"
                if isinstance(profile.auth, list):
                    auth_alg_list_str = [auth_alg_names.get(a, f"Auth_Raw({a})") for a in profile.auth]
                    auth_alg_str = ", ".join(auth_alg_list_str) if auth_alg_list_str else "Auth_Unknown"
                elif profile.auth is not None:
                    auth_alg_str = auth_alg_names.get(profile.auth, f"Auth_Raw({profile.auth})")

                ap_info = {
                    "ssid": ssid_str,
                    "bssid": profile.bssid,
                    "signal_dBm": profile.signal,
                    "frequency_MHz": profile.freq,
                    "akm_type": akm_final_str,
                    "cipher_type": cipher_type_str,
                    "auth_alg": auth_alg_str
                }
                aps_data.append(ap_info)
            except Exception as e_profile:
                print(f"Error memproses profile #{i} ({getattr(profile, 'ssid', 'Tidak ada SSID')}): {e_profile}")
                print(f"   Detail Profile Bermasalah: SSID: {getattr(profile, 'ssid', 'N/A')}, BSSID: {getattr(profile, 'bssid', 'N/A')}, AKM: {getattr(profile, 'akm', 'N/A')}, Cipher: {getattr(profile, 'cipher', 'N/A')}, Auth: {getattr(profile, 'auth', 'N/A')}")
        # Mengembalikan DataFrame langsung dari fungsi
        return pd.DataFrame(aps_data) if aps_data else pd.DataFrame()
    except AttributeError as e:
        if "'NoneType' object has no attribute 'scan'" in str(e) or \
           "'NoneType' object has no attribute 'name'" in str(e):
            print("Error: Tidak dapat mengakses antarmuka WiFi. Pastikan WiFi adapter aktif dan driver terinstal.")
        else:
            print(f"Terjadi AttributeError lain: {e}")
        return pd.DataFrame()
    except IndexError:
        print("Error: Tidak ada antarmuka WiFi yang terdeteksi oleh pywifi.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Terjadi kesalahan umum di luar loop profile: {e}")
        print(f"Detail error: {type(e).__name__} {e}")
        return pd.DataFrame()

# Hapus bagian `if __name__ == "__main__":` jika Anda hanya ingin mengimpor fungsinya.
# Jika Anda tetap menyertakannya, kode di dalamnya hanya akan berjalan jika file ini dieksekusi langsung.