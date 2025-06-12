import subprocess
import re # Untuk mengurai output
import pandas as pd # Import pandas
import os

def get_location_from_powershell(script_name):
    """
    Menjalankan skrip PowerShell untuk mendapatkan latitude dan longitude,
    lalu mengembalikan hasilnya sebagai pandas DataFrame.
    """
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    try:
        # Panggil PowerShell dan jalankan skrip
        # -ExecutionPolicy Bypass diperlukan agar skrip bisa dijalankan tanpa masalah kebijakan
        command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]
        
        # Jalankan perintah dan tangkap outputnya
        result = subprocess.run(
            command,
            capture_output=True,
            text=True, # Tangkap output sebagai teks (string)
            check=True # Akan raise CalledProcessError jika PowerShell mengembalikan kode error (bukan 0)
        )
        
        # Output dari PowerShell ada di result.stdout
        output_lines = result.stdout.strip().split('\n')
        
        # Cari baris yang berisi latitude dan longitude
        location_data = None
        for line in output_lines:
            if "Latitude:" in line and "Longitude:" in line:
                location_data = line
                break

        if location_data:
            # Gunakan regex untuk mengekstrak nilai latitude dan longitude
            match = re.search(r"Latitude:\s*(-?\d+\.\d+),\s*Longitude:\s*(-?\d+\.\d+)", location_data)
            if match:
                latitude = float(match.group(1))
                longitude = float(match.group(2))
                
                # Buat dictionary dari data
                data_dict = {"latitude": [latitude], "longitude": [longitude]}
                
                # Konversi dictionary menjadi DataFrame
                df = pd.DataFrame(data_dict)
                return df
            else:
                print(f"Error: Gagal mengurai output lokasi: {location_data}")
                return pd.DataFrame() # Mengembalikan DataFrame kosong jika parsing gagal
        else:
            print("Error: Output lokasi tidak ditemukan dari skrip PowerShell.")
            return pd.DataFrame() # Mengembalikan DataFrame kosong jika lokasi tidak ditemukan

    except subprocess.CalledProcessError as e:
        # Menangani error jika skrip PowerShell mengembalikan kode exit non-nol
        print(f"Error saat menjalankan skrip PowerShell:")
        print(f"  Kode Error: {e.returncode}")
        print(f"  Standard Output: {e.stdout.strip()}")
        print(f"  Standard Error: {e.stderr.strip()}")
        return pd.DataFrame() # Mengembalikan DataFrame kosong jika ada error proses
    except FileNotFoundError:
        print(f"Error: File skrip PowerShell tidak ditemukan di '{script_path}'.")
        return pd.DataFrame() # Mengembalikan DataFrame kosong jika file tidak ditemukan
    except Exception as e:
        print(f"Terjadi kesalahan tak terduga: {e}")
        return pd.DataFrame() # Mengembalikan DataFrame kosong untuk error lainnya