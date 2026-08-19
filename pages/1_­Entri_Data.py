from datetime import date

import pandas as pd
import streamlit as st

from utils.helpers import (
    hitung_usia_bulan, simpan_entri, load_entri, timestamp_sekarang,
    update_entri, hapus_entri, rerun,
)
from utils.theme import inject_css, render_sidebar_brand, page_header

st.set_page_config(page_title="Entri Data Antropometri", page_icon="📝", layout="wide")
inject_css()
render_sidebar_brand()
page_header(
    "📝", "Entri Data Antropometri",
    "Catat hasil pengukuran berat badan dan tinggi/panjang badan anak.",
    eyebrow="Modul 1 dari 5",
)

with st.form("form_entri"):
    c1, c2 = st.columns(2)
    with c1:
        nama = st.text_input("Nama anak")
        jk = st.selectbox("Jenis kelamin", ["Laki-laki (L)", "Perempuan (P)"])
        tgl_lahir = st.date_input("Tanggal lahir", value=date(2023, 1, 1),
                                   min_value=date(2020, 1, 1), max_value=date.today())
        tgl_ukur = st.date_input("Tanggal pengukuran", value=date.today())
    with c2:
        berat = st.number_input("Berat badan (kg)", min_value=1.0, max_value=30.0, value=10.0, step=0.1)
        tinggi = st.number_input("Tinggi/panjang badan (cm)", min_value=30.0, max_value=130.0, value=75.0, step=0.1)
        st.markdown("**Nilai Z-score** (isi sesuai hasil pengukuran e-PPGBM / aplikasi Antro WHO)")
        zs_bbu = st.number_input("Z-score BB/U (Berat Badan per Usia)", min_value=-6.0, max_value=6.0, value=0.0, step=0.01, format="%.2f")
        zs_tbu = st.number_input("Z-score TB/U (Tinggi Badan per Usia)", min_value=-6.0, max_value=6.0, value=0.0, step=0.01, format="%.2f")
        zs_bbtb = st.number_input("Z-score BB/TB (Berat Badan per Tinggi Badan)", min_value=-6.0, max_value=6.0, value=0.0, step=0.01, format="%.2f")

    usia_bulan = hitung_usia_bulan(tgl_lahir, tgl_ukur)
    st.markdown(
        f"""<div style="background:var(--primary); color:#fff !important; border-radius:12px;
                    padding:10px 16px; margin:6px 0 14px 0; display:inline-block;">
              <span style="color:#fff !important;">📅 Usia anak saat pengukuran:
              <strong style="font-family:'IBM Plex Mono',monospace;">{usia_bulan} bulan</strong></span>
            </div>""",
        unsafe_allow_html=True,
    )

    submitted = st.form_submit_button("💾 Simpan Data Entri", use_container_width=True)

    if submitted:
        if not nama:
            st.error("Nama anak wajib diisi.")
        elif usia_bulan < 0 or usia_bulan > 60:
            st.error("Sistem ini hanya mencakup anak usia 0–60 bulan. Periksa kembali tanggal lahir/pengukuran.")
        else:
            row = {
                "waktu_entri": timestamp_sekarang(),
                "nama_anak": nama,
                "tanggal_lahir": tgl_lahir.isoformat(),
                "tanggal_ukur": tgl_ukur.isoformat(),
                "usia_bulan": usia_bulan,
                "jenis_kelamin": "L" if jk.startswith("Laki") else "P",
                "berat": berat,
                "tinggi": tinggi,
                "zs_bbu": zs_bbu,
                "zs_tbu": zs_tbu,
                "zs_bbtb": zs_bbtb,
            }
            simpan_entri(row)
            st.success(f"Data **{nama}** berhasil disimpan. Lanjutkan ke modul **🔮 Prediksi Status Gizi** untuk melihat hasil klasifikasi.")
            st.balloons()

st.markdown("<hr class='kg-divider'/>", unsafe_allow_html=True)
st.markdown('<div class="kg-eyebrow">Rekam Data</div>', unsafe_allow_html=True)
st.markdown("### Data yang Sudah Dientri")

df = load_entri()
if df.empty:
    st.caption("Belum ada data entri.")
else:
    df_sorted = df.sort_values("waktu_entri", ascending=False).reset_index(drop=True)
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="kg-eyebrow">Kelola Data</div>', unsafe_allow_html=True)
    st.markdown("### ✏️ Edit atau 🗑️ Hapus Data")

    pilihan_id = st.selectbox(
        "Pilih data anak",
        df_sorted["id"],
        format_func=lambda i: (
            f"{df_sorted.loc[df_sorted['id'] == i, 'nama_anak'].values[0]} — "
            f"{df_sorted.loc[df_sorted['id'] == i, 'waktu_entri'].values[0]}"
        ),
        key="pilih_kelola_entri",
    )
    rec = df_sorted[df_sorted["id"] == pilihan_id].iloc[0]

    tab_edit, tab_hapus = st.tabs(["✏️ Edit Data", "🗑️ Hapus Data"])

    with tab_edit:
        with st.form("form_edit_entri"):
            ec1, ec2 = st.columns(2)
            with ec1:
                e_nama = st.text_input("Nama anak", value=str(rec["nama_anak"]))
                e_jk = st.selectbox(
                    "Jenis kelamin", ["Laki-laki (L)", "Perempuan (P)"],
                    index=0 if str(rec["jenis_kelamin"]) == "L" else 1,
                )
                e_tgl_lahir = st.date_input("Tanggal lahir", value=pd.to_datetime(rec["tanggal_lahir"]).date())
                e_tgl_ukur = st.date_input("Tanggal pengukuran", value=pd.to_datetime(rec["tanggal_ukur"]).date())
            with ec2:
                e_berat = st.number_input("Berat badan (kg)", min_value=1.0, max_value=30.0,
                                           value=float(rec["berat"]), step=0.1)
                e_tinggi = st.number_input("Tinggi/panjang badan (cm)", min_value=30.0, max_value=130.0,
                                            value=float(rec["tinggi"]), step=0.1)
                e_zs_bbu = st.number_input("Z-score BB/U", min_value=-6.0, max_value=6.0,
                                            value=float(rec["zs_bbu"]), step=0.01, format="%.2f")
                e_zs_tbu = st.number_input("Z-score TB/U", min_value=-6.0, max_value=6.0,
                                            value=float(rec["zs_tbu"]), step=0.01, format="%.2f")
                e_zs_bbtb = st.number_input("Z-score BB/TB", min_value=-6.0, max_value=6.0,
                                             value=float(rec["zs_bbtb"]), step=0.01, format="%.2f")

            e_usia = hitung_usia_bulan(e_tgl_lahir, e_tgl_ukur)
            st.caption(f"📅 Usia setelah diperbarui: **{e_usia} bulan**")

            simpan_perubahan = st.form_submit_button(
                "💾 Simpan Perubahan", use_container_width=True, type="primary"
            )
            if simpan_perubahan:
                if not e_nama:
                    st.error("Nama anak wajib diisi.")
                elif e_usia < 0 or e_usia > 60:
                    st.error("Usia hasil edit berada di luar rentang 0–60 bulan. Periksa kembali tanggal.")
                else:
                    update_entri(pilihan_id, {
                        "nama_anak": e_nama,
                        "tanggal_lahir": e_tgl_lahir.isoformat(),
                        "tanggal_ukur": e_tgl_ukur.isoformat(),
                        "usia_bulan": e_usia,
                        "jenis_kelamin": "L" if e_jk.startswith("Laki") else "P",
                        "berat": e_berat,
                        "tinggi": e_tinggi,
                        "zs_bbu": e_zs_bbu,
                        "zs_tbu": e_zs_tbu,
                        "zs_bbtb": e_zs_bbtb,
                    })
                    st.success(f"Data **{e_nama}** berhasil diperbarui.")
                    rerun()

    with tab_hapus:
        st.warning(
            f"Anda akan menghapus data **{rec['nama_anak']}** "
            f"(dientri pada {rec['waktu_entri']}). Tindakan ini tidak dapat dibatalkan."
        )
        konfirmasi = st.checkbox("Ya, saya yakin ingin menghapus data ini.", key="konfirmasi_hapus_entri")
        if st.button("🗑️ Hapus Data Ini", type="primary", disabled=not konfirmasi, use_container_width=True):
            hapus_entri(pilihan_id)
            st.success("Data berhasil dihapus.")
            rerun()
