import streamlit as st

from utils.helpers import load_riwayat, RIWAYAT_PATH
from utils.theme import inject_css, render_sidebar_brand, page_header, status_badge

st.set_page_config(page_title="Riwayat Prediksi", page_icon="🕘", layout="wide")
inject_css()
render_sidebar_brand()
page_header(
    "🕘", "Riwayat & Histori Prediksi",
    "Telusuri, cari, dan kelola seluruh riwayat prediksi yang tersimpan.",
    eyebrow="Modul 4 dari 5",
)

df = load_riwayat()

if df.empty:
    st.info("Belum ada riwayat prediksi tersimpan.")
    st.stop()

# --- Ringkasan cepat via badge status ---
status_counts = df["status_gizi_prediksi"].value_counts()
ring_cols = st.columns(len(status_counts) if len(status_counts) else 1)
for col, (label, jumlah) in zip(ring_cols, status_counts.items()):
    with col:
        st.markdown(
            f"""<div class="kg-card" style="text-align:center;">
                {status_badge(label)}
                <div style="font-family:'IBM Plex Mono',monospace; font-size:1.6rem;
                            font-weight:700; margin-top:10px;">{jumlah}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<hr class='kg-divider'/>", unsafe_allow_html=True)
st.markdown('<div class="kg-eyebrow">Pencarian &amp; Filter</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    cari_nama = st.text_input("🔎 Cari nama anak")
with c2:
    filter_status = st.multiselect(
        "Filter status gizi",
        options=sorted(df["status_gizi_prediksi"].dropna().unique()),
    )
with c3:
    filter_algo = st.multiselect(
        "Filter algoritma",
        options=sorted(df["algoritma"].dropna().unique()),
    )

hasil = df.copy()
if cari_nama:
    hasil = hasil[hasil["nama_anak"].str.contains(cari_nama, case=False, na=False)]
if filter_status:
    hasil = hasil[hasil["status_gizi_prediksi"].isin(filter_status)]
if filter_algo:
    hasil = hasil[hasil["algoritma"].isin(filter_algo)]

st.markdown(f"Menampilkan **{len(hasil)}** dari **{len(df)}** total riwayat prediksi.")
st.dataframe(
    hasil.sort_values("waktu_prediksi", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "⬇️ Unduh riwayat (CSV)",
    data=hasil.to_csv(index=False).encode("utf-8"),
    file_name="riwayat_prediksi_gizi_anak.csv",
    mime="text/csv",
)

with st.expander("⚠️ Hapus seluruh riwayat"):
    st.warning("Tindakan ini tidak dapat dibatalkan.")
    if st.button("Hapus semua riwayat prediksi", type="primary"):
        import pandas as pd
        from utils.helpers import RIWAYAT_COLS
        pd.DataFrame(columns=RIWAYAT_COLS).to_csv(RIWAYAT_PATH, index=False)
        st.success("Riwayat berhasil dihapus. Muat ulang halaman untuk melihat perubahan.")
