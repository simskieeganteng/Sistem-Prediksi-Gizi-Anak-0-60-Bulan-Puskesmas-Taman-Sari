from datetime import date, timedelta

import pandas as pd
import streamlit as st

from utils.helpers import load_riwayat
from utils.theme import inject_css, render_sidebar_brand, page_header, STATUS_COLORS

st.set_page_config(page_title="Laporan & Rekapitulasi", page_icon="📄", layout="wide")
inject_css()
render_sidebar_brand()
page_header(
    "📄", "Laporan & Rekapitulasi Data Periodik",
    "Rekap jumlah kasus status gizi dalam rentang tanggal tertentu.",
    eyebrow="Modul 5 dari 5",
)

df = load_riwayat()
if df.empty:
    st.info("Belum ada data prediksi untuk direkapitulasi.")
    st.stop()

df["tanggal"] = pd.to_datetime(df["waktu_prediksi"]).dt.date

st.markdown('<div class="kg-eyebrow">Rentang Waktu</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    tgl_awal = st.date_input("Dari tanggal", value=df["tanggal"].min())
with c2:
    tgl_akhir = st.date_input("Sampai tanggal", value=df["tanggal"].max())

periode = df[(df["tanggal"] >= tgl_awal) & (df["tanggal"] <= tgl_akhir)]

st.markdown(f"### Rekapitulasi Periode {tgl_awal} — {tgl_akhir}")

if periode.empty:
    st.warning("Tidak ada data pada rentang tanggal tersebut.")
    st.stop()

total = len(periode)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Anak Diperiksa", total)
for kolom, label in zip([k2, k3, k4, k5], ["Gizi Buruk", "Gizi Kurang", "Gizi Baik", "Gizi Lebih"]):
    jumlah = (periode["status_gizi_prediksi"] == label).sum()
    persen = f"{jumlah/total*100:.1f}%" if total else "0%"
    warna = STATUS_COLORS.get(label, {"bg": "#EEE", "fg": "#333"})
    with kolom:
        st.markdown(
            f"""<div class="kg-card" style="background:{warna['bg']}; border-color:transparent;">
                <div style="font-size:0.78rem; font-weight:600; color:{warna['fg']};">{label}</div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:1.5rem; font-weight:700;
                            color:{warna['fg']}; margin-top:2px;">{jumlah}</div>
                <div style="font-size:0.75rem; color:{warna['fg']}; opacity:0.8;">{persen}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<hr class='kg-divider'/>", unsafe_allow_html=True)

st.markdown('<div class="kg-eyebrow">Rekap Kategori</div>', unsafe_allow_html=True)
st.markdown("#### Rekap per Kategori Status Gizi")
rekap_status = periode["status_gizi_prediksi"].value_counts().rename_axis("Status Gizi").reset_index(name="Jumlah Anak")
st.dataframe(rekap_status, use_container_width=True, hide_index=True)
st.bar_chart(rekap_status.set_index("Status Gizi"))

st.markdown('<div class="kg-eyebrow">Tren Harian</div>', unsafe_allow_html=True)
st.markdown("#### Rekap Harian")
rekap_harian = periode.groupby("tanggal").size().rename("Jumlah Pemeriksaan")
st.line_chart(rekap_harian)

st.markdown('<div class="kg-eyebrow">Data Mentah</div>', unsafe_allow_html=True)
st.markdown("#### Data Detail Periode Ini")
st.dataframe(
    periode.drop(columns=["tanggal"]).sort_values("waktu_prediksi", ascending=False),
    use_container_width=True,
    hide_index=True,
)

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button(
        "⬇️ Unduh rekap ringkas (CSV)",
        data=rekap_status.to_csv(index=False).encode("utf-8"),
        file_name=f"rekap_gizi_{tgl_awal}_sd_{tgl_akhir}.csv",
        mime="text/csv",
        use_container_width=True,
    )
with col_dl2:
    st.download_button(
        "⬇️ Unduh data lengkap periode (CSV)",
        data=periode.drop(columns=["tanggal"]).to_csv(index=False).encode("utf-8"),
        file_name=f"data_lengkap_gizi_{tgl_awal}_sd_{tgl_akhir}.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption(
    "💡 Laporan ini dapat digunakan sebagai bahan rekapitulasi bulanan/triwulan "
    "kegiatan pemantauan gizi anak di Puskesmas Taman Sari, termasuk untuk pelaporan ke Dinas Kesehatan."
)
