import streamlit as st
import pandas as pd
import base64

# ------------------------
# Konfigurasi tampilan halaman
# ------------------------
st.set_page_config(
    page_title="Wi-Fi Snapshot UNTIRTA",
    layout="wide"
)

st.title("📡 Wi-Fi Snapshot UNTIRTA")
st.markdown("""
Unggah file snapshot jaringan Wi-Fi hasil dari aplikasi lokal Anda (.csv).  
Aplikasi ini akan menampilkan isi file dan menyediakan tautan untuk mengunduh ulang.
""")

# ------------------------
# Fungsi: Buat tautan unduhan CSV dari DataFrame
# ------------------------
def get_table_download_link(df, filename="snapshot.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'''
        <a href="data:file/csv;base64,{b64}" download="{filename}" style="font-size:16px;">
            📥 Unduh kembali file snapshot
        </a>
    '''
    return href

# ------------------------
# Upload file
# ------------------------
uploaded_file = st.file_uploader("📤 Unggah file snapshot jaringan Wi-Fi (.csv)", type=["csv"])

# ------------------------
# Proses dan tampilkan data
# ------------------------
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ File berhasil diunggah. Jumlah jaringan: {len(df)}")
        st.dataframe(df, use_container_width=True)
        
        # Tampilkan tautan unduhan
        st.markdown("---")
        st.markdown("### 🔽 Unduh Data")
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Gagal membaca file. Pastikan file dalam format .csv yang benar.\n\n**Error:** {e}")
else:
    st.info("Silakan unggah file hasil snapshot dari aplikasi lokal untuk melihat datanya di sini.")
