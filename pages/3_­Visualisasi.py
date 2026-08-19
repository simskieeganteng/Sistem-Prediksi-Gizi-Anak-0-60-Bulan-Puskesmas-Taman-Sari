import os

import pandas as pd
import streamlit as st

from utils.helpers import load_artifacts, load_riwayat, MODEL_DIR, tampilkan_gambar
from utils.theme import inject_css, render_sidebar_brand, page_header, status_badge

st.set_page_config(page_title="Visualisasi", page_icon="📊", layout="wide")
inject_css()
render_sidebar_brand()
page_header(
    "📊", "Visualisasi Hasil Prediksi & Performa Model",
    "Telusuri performa model, bobot fitur, dan sebaran hasil prediksi.",
    eyebrow="Modul 3 dari 5",
)

artifacts = load_artifacts()
if not artifacts:
    st.error("Model belum tersedia. Lihat README.md untuk langkah training di Google Colab.")
    st.stop()

metrics = artifacts.get("metrics", {})

tab1, tab2, tab3 = st.tabs(["📈 Performa Model", "🌳 Feature Importance", "🧒 Distribusi Riwayat Prediksi"])

with tab1:
    st.markdown('<div class="kg-eyebrow">Perbandingan Algoritma</div>', unsafe_allow_html=True)
    st.markdown("### Random Forest vs Decision Tree")
    models_metrics = metrics.get("models", {})
    if models_metrics:
        comp = pd.DataFrame({
            nama.replace("_", " ").title(): {
                "Akurasi": m["akurasi"], "Presisi": m["presisi"],
                "Recall": m["recall"], "F1-Score": m["f1_score"],
                "CV-10 Fold": m.get("cv10_mean_accuracy"),
            }
            for nama, m in models_metrics.items()
        }).T
        st.dataframe(comp.style.format("{:.2%}"), use_container_width=True)
        st.bar_chart(comp[["Akurasi", "Presisi", "Recall", "F1-Score"]])
        st.markdown(
            f"""<div class="kg-card" style="background:#FFF8EE; border-color:rgba(232,179,57,0.35); margin-top:10px;">
            📌 Model dengan performa terbaik saat ini (berdasarkan <em>recall</em> makro,
            metrik paling kritis untuk mendeteksi kasus gizi buruk):
            <strong>{metrics.get('best_model', '-').replace('_',' ').title()}</strong>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.info("Belum ada data metrik. Jalankan training di Colab terlebih dahulu.")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="kg-eyebrow">Confusion Matrix</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    for col, nama_file, judul in [
        (c1, "confusion_matrix_random_forest.png", "Random Forest"),
        (c2, "confusion_matrix_decision_tree.png", "Decision Tree"),
    ]:
        path = os.path.join(MODEL_DIR, nama_file)
        with col:
            st.markdown('<div class="kg-card">', unsafe_allow_html=True)
            st.markdown(f"**{judul}**")
            if os.path.exists(path):
                tampilkan_gambar(path)
            else:
                st.caption("Gambar belum tersedia.")
            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="kg-eyebrow">Bobot Variabel</div>', unsafe_allow_html=True)
    st.markdown("### Feature Importance (Random Forest)")
    st.caption("Bobot kepentingan tiap parameter antropometri terhadap hasil prediksi status gizi.")
    fi_path = os.path.join(MODEL_DIR, "feature_importance.csv")
    fi_img = os.path.join(MODEL_DIR, "feature_importance.png")
    if os.path.exists(fi_path):
        fi = pd.read_csv(fi_path, index_col=0)
        fi.columns = ["Bobot Kepentingan"]
        st.bar_chart(fi)
        st.dataframe(fi.style.format("{:.4f}"), use_container_width=True)
    if os.path.exists(fi_img):
        st.markdown('<div class="kg-card">', unsafe_allow_html=True)
        tampilkan_gambar(fi_img)
        st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="kg-eyebrow">Riwayat Tersimpan</div>', unsafe_allow_html=True)
    st.markdown("### Distribusi Hasil Prediksi")
    riwayat = load_riwayat()
    if riwayat.empty:
        st.info("Belum ada riwayat prediksi. Jalankan prediksi di modul 🔮 Prediksi Status Gizi.")
    else:
        status_counts = riwayat["status_gizi_prediksi"].value_counts()
        badge_cols = st.columns(len(status_counts) if len(status_counts) else 1)
        for col, (label, jumlah) in zip(badge_cols, status_counts.items()):
            with col:
                st.markdown(status_badge(label), unsafe_allow_html=True)
                st.markdown(
                    f"<div style='font-family:\"IBM Plex Mono\",monospace; font-size:1.4rem; "
                    f"font-weight:700; margin-top:6px;'>{jumlah}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Distribusi Status Gizi**")
            st.bar_chart(status_counts)
        with colB:
            st.markdown("**Distribusi Jenis Kelamin**")
            st.bar_chart(riwayat["jenis_kelamin"].value_counts())
        st.markdown("**Sebaran Usia (bulan) berdasarkan Status Gizi**")
        st.scatter_chart(riwayat, x="usia_bulan", y="berat", color="status_gizi_prediksi")
