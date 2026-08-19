"""Fungsi-fungsi bantuan yang dipakai bersama oleh seluruh halaman aplikasi."""

import json
import os
from datetime import datetime, date

import joblib
import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")
DATA_DIR = os.path.join(BASE_DIR, "data")
RIWAYAT_PATH = os.path.join(DATA_DIR, "riwayat_prediksi.csv")
ENTRI_PATH = os.path.join(DATA_DIR, "data_entri.csv")

FEATURE_COLS = ["Usia_Bulan", "JK_enc", "Berat", "Tinggi", "ZS_BBU", "ZS_TBU", "ZS_BBTB"]

RIWAYAT_COLS = [
    "waktu_prediksi", "nama_anak", "usia_bulan", "jenis_kelamin", "berat", "tinggi",
    "zs_bbu", "zs_tbu", "zs_bbtb", "algoritma", "status_gizi_prediksi",
    "keyakinan_persen", "petugas",
]

ENTRI_COLS = [
    "id", "waktu_entri", "nama_anak", "tanggal_lahir", "tanggal_ukur", "usia_bulan",
    "jenis_kelamin", "berat", "tinggi", "zs_bbu", "zs_tbu", "zs_bbtb",
]

REKOMENDASI = {
    "Gizi Buruk": (
        "Rujuk segera ke dokter/ahli gizi puskesmas untuk tata laksana gizi buruk. "
        "Pertimbangkan pemberian makanan terapeutik dan pemantauan ketat setiap minggu."
    ),
    "Gizi Kurang": (
        "Berikan edukasi dan konseling gizi kepada orang tua, pantau berat badan "
        "setiap bulan, serta pertimbangkan pemberian makanan tambahan (PMT)."
    ),
    "Gizi Baik": (
        "Status gizi anak dalam rentang normal. Lanjutkan pola asuh dan pemberian "
        "makan yang sudah baik, serta lakukan pemantauan rutin di posyandu."
    ),
    "Gizi Lebih": (
        "Edukasi pola makan seimbang dan aktivitas fisik kepada orang tua, "
        "pantau kenaikan berat badan agar tidak mengarah ke obesitas."
    ),
}


@st.cache_resource
def load_artifacts():
    """Muat model, label encoder, dan metrik hasil training dari folder model/."""
    rf_path = os.path.join(MODEL_DIR, "random_forest.pkl")
    dt_path = os.path.join(MODEL_DIR, "decision_tree.pkl")
    le_path = os.path.join(MODEL_DIR, "label_encoder.pkl")
    metrics_path = os.path.join(MODEL_DIR, "metrics.json")

    if not (os.path.exists(rf_path) and os.path.exists(dt_path) and os.path.exists(le_path)):
        return None

    rf = joblib.load(rf_path)
    dt = joblib.load(dt_path)
    le_label = joblib.load(le_path)
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)

    return {
        "random_forest": rf,
        "decision_tree": dt,
        "label_encoder": le_label,
        "metrics": metrics,
    }


def hitung_usia_bulan(tanggal_lahir: date, tanggal_ukur: date) -> float:
    selisih_hari = (tanggal_ukur - tanggal_lahir).days
    return round(selisih_hari / 30.4375, 1)


def bentuk_fitur(usia_bulan, jk, berat, tinggi, zs_bbu, zs_tbu, zs_bbtb) -> pd.DataFrame:
    jk_enc = 1 if str(jk).upper().startswith("P") else 0
    row = pd.DataFrame([{
        "Usia_Bulan": usia_bulan, "JK_enc": jk_enc, "Berat": berat, "Tinggi": tinggi,
        "ZS_BBU": zs_bbu, "ZS_TBU": zs_tbu, "ZS_BBTB": zs_bbtb,
    }])
    return row[FEATURE_COLS]


def prediksi(model, label_encoder, fitur_df: pd.DataFrame):
    pred_enc = model.predict(fitur_df)[0]
    label = label_encoder.inverse_transform([pred_enc])[0]
    proba = None
    keyakinan = None
    if hasattr(model, "predict_proba"):
        proba_arr = model.predict_proba(fitur_df)[0]
        proba = dict(zip(label_encoder.classes_, np.round(proba_arr * 100, 1)))
        keyakinan = float(np.max(proba_arr) * 100)
    return label, keyakinan, proba


def _pastikan_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_csv(path, cols):
    _pastikan_data_dir()
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)


def append_csv(path, cols, row: dict):
    _pastikan_data_dir()
    df = load_csv(path, cols)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)
    return df


def load_riwayat():
    return load_csv(RIWAYAT_PATH, RIWAYAT_COLS)


def simpan_riwayat(row: dict):
    return append_csv(RIWAYAT_PATH, RIWAYAT_COLS, row)


def load_entri():
    df = load_csv(ENTRI_PATH, ENTRI_COLS)
    if not df.empty and "id" not in df.columns:
        # migrasi otomatis untuk file data_entri.csv lama yang belum punya kolom id
        df.insert(0, "id", range(1, len(df) + 1))
        df.to_csv(ENTRI_PATH, index=False)
    return df


def _next_id(df: pd.DataFrame) -> int:
    if df.empty or "id" not in df.columns:
        return 1
    ids = pd.to_numeric(df["id"], errors="coerce").dropna()
    return int(ids.max()) + 1 if len(ids) else 1


def simpan_entri(row: dict):
    df = load_entri()
    full_row = {"id": _next_id(df), **row}
    df = pd.concat([df, pd.DataFrame([full_row])], ignore_index=True)
    _pastikan_data_dir()
    df.to_csv(ENTRI_PATH, index=False)
    return df


def update_entri(id_val, updated_fields: dict):
    """Perbarui satu baris data entri berdasarkan id-nya."""
    df = load_entri()
    mask = df["id"] == id_val
    if not mask.any():
        return df
    for kolom, nilai in updated_fields.items():
        df.loc[mask, kolom] = nilai
    _pastikan_data_dir()
    df.to_csv(ENTRI_PATH, index=False)
    return df


def hapus_entri(id_val):
    """Hapus satu baris data entri berdasarkan id-nya."""
    df = load_entri()
    df = df[df["id"] != id_val].reset_index(drop=True)
    _pastikan_data_dir()
    df.to_csv(ENTRI_PATH, index=False)
    return df


def rerun():
    """st.rerun() yang aman dipakai di versi Streamlit lama maupun baru."""
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


def timestamp_sekarang():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def tampilkan_gambar(path):
    """st.image() yang aman dipakai di versi Streamlit lama maupun baru.
    Versi Streamlit terbaru memakai parameter use_container_width, versi
    lama memakai use_column_width. Fungsi ini mencoba keduanya secara
    otomatis agar tidak error di komputer manapun."""
    try:
        st.image(path, use_container_width=True)
    except TypeError:
        st.image(path, use_column_width=True)
