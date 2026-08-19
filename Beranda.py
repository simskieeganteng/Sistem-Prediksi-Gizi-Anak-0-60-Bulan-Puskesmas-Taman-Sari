import streamlit as st

from utils.helpers import load_artifacts, load_riwayat
from utils.theme import inject_css, render_sidebar_brand, growth_curve_svg

st.set_page_config(
    page_title="Sistem Prediksi Status Gizi Anak - Puskesmas Taman Sari",
    page_icon="🌱",
    layout="wide",
)
inject_css()
render_sidebar_brand()
st.sidebar.success("Pilih modul di atas ⬆️")

artifacts = load_artifacts()
riwayat = load_riwayat()

# ---------------------------------------------------------------- HERO ----
st.markdown(
    f"""
    <div class="kg-card" style="padding:0; overflow:hidden; margin-bottom:26px;">
      <div style="padding:34px 36px 0 36px;">
        <div class="kg-eyebrow">Puskesmas Taman Sari &middot; Kota Pangkalpinang</div>
        <h1 style="margin:2px 0 8px 0; font-size:2.5rem; line-height:1.1;">
          Skrining Gizi Anak,<br/>Ditemani Kurva &amp; Data.
        </h1>
        <p style="max-width:560px; color:var(--ink-soft); font-size:16.5px; margin-bottom:0;">
          Sistem klasifikasi status gizi anak usia 0&ndash;60 bulan berbasis
          <em>Random Forest</em> &amp; <em>Decision Tree</em>, dibangun dari data
          antropometri rekam medis Puskesmas Taman Sari.
        </p>
      </div>
      {growth_curve_svg(120)}
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------- METRICS ----
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Status Model", "Siap Digunakan ✅" if artifacts else "Belum Ditemukan ⚠️")
with col2:
    st.metric("Total Prediksi Tersimpan", len(riwayat))
with col3:
    best = "-"
    if artifacts and artifacts.get("metrics"):
        best = artifacts["metrics"].get("best_model", "-").replace("_", " ").title()
    st.metric("Algoritma Terbaik Saat Ini", best)

if not artifacts:
    st.warning(
        "Model belum ditemukan di folder `model/`. Jalankan notebook Google Colab "
        "(`colab/Prediksi_Status_Gizi_Colab.ipynb`) terlebih dahulu, lalu salin file "
        "`random_forest.pkl`, `decision_tree.pkl`, `label_encoder.pkl`, dan `metrics.json` "
        "ke folder `streamlit_app/model/`. Lihat README.md untuk panduan lengkap."
    )

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------- MODULES ----
st.markdown('<div class="kg-eyebrow">Peta Modul</div>', unsafe_allow_html=True)
st.markdown("### Lima Ruang Kerja dalam Satu Alur")

mods = [
    ("📝", "Entri Data Antropometri", "Mencatat hasil pengukuran berat & tinggi badan anak."),
    ("🔮", "Prediksi Status Gizi", "Menjalankan model ML untuk memprediksi status gizi."),
    ("📊", "Visualisasi", "Melihat performa model & distribusi data secara visual."),
    ("🕘", "Riwayat Prediksi", "Menelusuri seluruh riwayat prediksi yang tersimpan."),
    ("📄", "Laporan & Rekapitulasi", "Rekap periodik status gizi anak binaan."),
]
cols = st.columns(5)
for c, (icon, title, desc) in zip(cols, mods):
    with c:
        st.markdown(
            f"""
            <div class="kg-card" style="height:190px; display:flex; flex-direction:column; justify-content:space-between;">
                <div style="font-size:26px;">{icon}</div>
                <div>
                    <div style="font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:15px; margin-bottom:4px;">{title}</div>
                    <div style="color:var(--ink-soft); font-size:12.5px; line-height:1.4;">{desc}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<hr class='kg-divider'/>", unsafe_allow_html=True)

# --------------------------------------------------------- KATEGORI WHO ----
left, right = st.columns([1.1, 1])
with left:
    st.markdown('<div class="kg-eyebrow">Standar Klasifikasi</div>', unsafe_allow_html=True)
    st.markdown("### Empat Kategori Status Gizi (WHO, berbasis Z-score)")
    kategori = [
        ("Gizi Buruk", "Z-score < &minus;3 SD", "#D64550", "#FDEBEA"),
        ("Gizi Kurang", "&minus;3 SD &le; Z-score < &minus;2 SD", "#F2994A", "#FFF1E3"),
        ("Gizi Baik", "&minus;2 SD &le; Z-score &le; +2 SD", "#1F7A5C", "#E9F5EE"),
        ("Gizi Lebih", "Z-score > +2 SD", "#E8B339", "#FDF6E0"),
    ]
    for nama, rentang, fg, bg in kategori:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        background:{bg}; border-radius:12px; padding:10px 16px; margin-bottom:8px;">
                <span style="font-weight:600; color:{fg};">{nama}</span>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:{fg};">{rentang}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

with right:
    st.markdown('<div class="kg-eyebrow">Catatan Penting</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="kg-card" style="background:#FFF8EE; border-color:rgba(232,179,57,0.35);">
        <strong>⚠️ Alat bantu skrining, bukan diagnosis.</strong><br/><br/>
        Sistem ini membantu tenaga kesehatan Puskesmas Taman Sari melakukan skrining
        awal secara cepat dan konsisten. Keputusan klinis akhir tetap berada di tangan
        dokter atau ahli gizi.
        </div>
        """,
        unsafe_allow_html=True,
    )
