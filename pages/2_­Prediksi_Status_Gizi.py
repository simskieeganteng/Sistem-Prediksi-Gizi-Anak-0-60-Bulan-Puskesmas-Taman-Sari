import pandas as pd
import streamlit as st

from utils.helpers import (
    load_artifacts, load_entri, bentuk_fitur, prediksi, simpan_riwayat,
    timestamp_sekarang, REKOMENDASI,
)
from utils.theme import inject_css, render_sidebar_brand, page_header, status_badge, STATUS_COLORS

st.set_page_config(page_title="Prediksi Status Gizi", page_icon="🔮", layout="wide")
inject_css()
render_sidebar_brand()
page_header(
    "🔮", "Prediksi Status Gizi Otomatis",
    "Jalankan model machine learning untuk mengklasifikasikan status gizi anak.",
    eyebrow="Modul 2 dari 5",
)

artifacts = load_artifacts()
if not artifacts:
    st.error(
        "Model belum tersedia. Jalankan notebook Colab lalu salin file model ke folder "
        "`streamlit_app/model/` terlebih dahulu (lihat README.md)."
    )
    st.stop()

st.markdown('<div class="kg-eyebrow">Langkah 1</div>', unsafe_allow_html=True)
sumber = st.radio(
    "Sumber data",
    ["Pilih dari data yang sudah dientri", "Isi manual"],
    horizontal=True,
    label_visibility="collapsed",
)

nama_anak = ""
usia_bulan = jk = berat = tinggi = zs_bbu = zs_tbu = zs_bbtb = None

if sumber == "Pilih dari data yang sudah dientri":
    df_entri = load_entri()
    if df_entri.empty:
        st.warning("Belum ada data entri. Silakan buka modul **📝 Entri Data Antropometri** terlebih dahulu, atau pilih 'Isi manual'.")
        st.stop()
    df_entri = df_entri.sort_values("waktu_entri", ascending=False)
    pilihan = st.selectbox(
        "Pilih data anak",
        df_entri.index,
        format_func=lambda i: f"{df_entri.loc[i, 'nama_anak']} — {df_entri.loc[i, 'waktu_entri']}",
    )
    rec = df_entri.loc[pilihan]
    nama_anak = rec["nama_anak"]
    usia_bulan, jk = rec["usia_bulan"], rec["jenis_kelamin"]
    berat, tinggi = rec["berat"], rec["tinggi"]
    zs_bbu, zs_tbu, zs_bbtb = rec["zs_bbu"], rec["zs_tbu"], rec["zs_bbtb"]
    st.dataframe(rec.to_frame().T, use_container_width=True, hide_index=True)
else:
    c1, c2 = st.columns(2)
    with c1:
        nama_anak = st.text_input("Nama anak (opsional)", value="Anonim")
        jk = st.selectbox("Jenis kelamin", ["L", "P"])
        usia_bulan = st.number_input("Usia (bulan)", min_value=0.0, max_value=60.0, value=24.0, step=0.5)
        berat = st.number_input("Berat badan (kg)", min_value=1.0, max_value=30.0, value=11.0, step=0.1)
        tinggi = st.number_input("Tinggi/panjang badan (cm)", min_value=30.0, max_value=130.0, value=85.0, step=0.1)
    with c2:
        zs_bbu = st.number_input("Z-score BB/U", min_value=-6.0, max_value=6.0, value=0.0, step=0.01, format="%.2f")
        zs_tbu = st.number_input("Z-score TB/U", min_value=-6.0, max_value=6.0, value=0.0, step=0.01, format="%.2f")
        zs_bbtb = st.number_input("Z-score BB/TB", min_value=-6.0, max_value=6.0, value=0.0, step=0.01, format="%.2f")

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
st.markdown('<div class="kg-eyebrow">Langkah 2</div>', unsafe_allow_html=True)
algoritma = st.selectbox(
    "Pilih algoritma",
    ["Random Forest", "Decision Tree", "Bandingkan keduanya"],
    label_visibility="collapsed",
)

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
jalankan = st.button("🔍 Jalankan Prediksi", use_container_width=True, type="primary")

if jalankan:
    fitur_df = bentuk_fitur(usia_bulan, jk, berat, tinggi, zs_bbu, zs_tbu, zs_bbtb)
    le = artifacts["label_encoder"]

    def tampilkan_hasil(nama_model, model):
        label, keyakinan, proba = prediksi(model, le, fitur_df)
        warna = STATUS_COLORS.get(label, {"bg": "#EEE", "fg": "#333"})

        st.markdown(
            f"""
            <div class="kg-card" style="background:{warna['bg']}; border-color:transparent; margin-bottom:14px;">
                <div style="font-family:'IBM Plex Mono',monospace; font-size:12px;
                            letter-spacing:0.08em; text-transform:uppercase; color:{warna['fg']}; opacity:0.8;">
                    Hasil &middot; {nama_model}
                </div>
                <div style="margin-top:4px;">{status_badge(label)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if keyakinan is not None:
            st.progress(min(keyakinan / 100, 1.0), text=f"Tingkat keyakinan model: {keyakinan:.1f}%")
        if proba:
            st.bar_chart(pd.Series(proba))
        st.caption(f"**Rekomendasi tindak lanjut:** {REKOMENDASI.get(label, '-')}")
        return label, keyakinan

    st.markdown("<hr class='kg-divider'/>", unsafe_allow_html=True)
    st.markdown('<div class="kg-eyebrow">Hasil Klasifikasi</div>', unsafe_allow_html=True)

    if algoritma == "Bandingkan keduanya":
        col1, col2 = st.columns(2)
        with col1:
            label_rf, conf_rf = tampilkan_hasil("Random Forest", artifacts["random_forest"])
        with col2:
            label_dt, conf_dt = tampilkan_hasil("Decision Tree", artifacts["decision_tree"])
        if label_rf != label_dt:
            st.warning(
                f"⚠️ Kedua algoritma memberikan hasil berbeda (RF: {label_rf} vs DT: {label_dt}). "
                "Disarankan verifikasi manual oleh tenaga kesehatan."
            )
        label_simpan, conf_simpan, algo_simpan = label_rf, conf_rf, "Random Forest & Decision Tree"
    elif algoritma == "Random Forest":
        label_simpan, conf_simpan = tampilkan_hasil("Random Forest", artifacts["random_forest"])
        algo_simpan = "Random Forest"
    else:
        label_simpan, conf_simpan = tampilkan_hasil("Decision Tree", artifacts["decision_tree"])
        algo_simpan = "Decision Tree"

    simpan_riwayat({
        "waktu_prediksi": timestamp_sekarang(),
        "nama_anak": nama_anak,
        "usia_bulan": usia_bulan,
        "jenis_kelamin": jk,
        "berat": berat,
        "tinggi": tinggi,
        "zs_bbu": zs_bbu,
        "zs_tbu": zs_tbu,
        "zs_bbtb": zs_bbtb,
        "algoritma": algo_simpan,
        "status_gizi_prediksi": label_simpan,
        "keyakinan_persen": round(conf_simpan, 1) if conf_simpan else None,
        "petugas": st.session_state.get("petugas", "-"),
    })
    st.success("Hasil prediksi tersimpan ke modul Riwayat Prediksi.")
