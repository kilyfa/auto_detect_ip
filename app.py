import streamlit as st
import pandas as pd
import base64
from io import StringIO

st.set_page_config(page_title="Wi-Fi Snapshot Viewer", layout="wide")

st.title("📡 Wi-Fi Snapshot UNTIRTA")
st.markdown("Upload otomatis dari aplikasi lokal atau unggah manual file snapshot .csv")

# Simpan snapshot ke session state agar tidak hilang saat reload
if 'snapshots' not in st.session_state:
    st.session_state.snapshots = []

# Fungsi untuk membuat tautan unduhan
def get_table_download_link(df, filename="snapshot.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Unduh snapshot CSV</a>'
    return href

# ------------------------
# 📥 Bagian Upload Otomatis (POST dari script Python lokal)
# ------------------------
# Kompatibel dengan: requests.post(..., files={"file": ("snapshot.csv", csv_bytes, "text/csv")})

uploaded_via_post = False
if "file" in st.query_params:
    uploaded_file = st.query_params["file"]
else:
    uploaded_file = None

if st.requested_session_state is not None:
    # Support file upload via POST from local uploader
    try:
        post_data = st.requested_session_state.uploaded_file_data
        if post_data:
            stringio = StringIO(post_data.getvalue().decode("utf-8"))
            df = pd.read_csv(stringio)
            st.session_state.snapshots.append(df)
            uploaded_via_post = True
    except Exception:
        pass

# ------------------------
# 📤 Upload Manual dari Pengguna
# ------------------------
st.subheader("📤 Upload Manual Snapshot")
manual_upload = st.file_uploader("Unggah file snapshot Wi-Fi (.csv)", type=["csv"])

if manual_upload is not None:
    df = pd.read_csv(manual_upload)
    st.session_state.snapshots.append(df)

# ------------------------
# 📊 Tampilkan Hasil Snapshot
# ------------------------
if st.session_state.snapshots:
    latest_df = st.session_state.snapshots[-1]
    st.success(f"✅ Berhasil menerima data. Jumlah jaringan: {len(latest_df)}")
    st.dataframe(latest_df, use_container_width=True)
    st.markdown(get_table_download_link(latest_df), unsafe_allow_html=True)
else:
    if uploaded_via_post:
        st.warning("Data upload diterima tapi kosong atau gagal dibaca.")
    else:
        st.info("Belum ada data yang diunggah. Unggah file CSV dari aplikasi lokal atau browser.")
