"""
Modul perhitungan Z-score BB/U, TB/U, dan BB/TB secara otomatis berdasarkan
usia, jenis kelamin, berat badan, dan tinggi/panjang badan anak, mengacu
langsung pada tabel WHO Child Growth Standards (bukan tabel pendekatan).

Menggunakan pustaka pygrowup-erknet, yang mengambil tabel LMS resmi dari
cdn.who.int (sumber sama dengan yang dipakai aplikasi e-PPGBM/WHO Anthro),
lalu menghitung Z-score dengan rumus LMS standar WHO:

    Z = ((X/M)^L - 1) / (L * S)      jika L != 0
    Z = ln(X/M) / S                  jika L == 0

Catatan penting:
- Saat pertama kali dipakai, pustaka ini butuh koneksi internet untuk
  mengunduh tabel WHO (sekali saja, lalu disimpan/cache secara lokal).
- Hasil ini adalah PERKIRAAN otomatis berbasis standar WHO, bukan pengganti
  mutlak aplikasi resmi e-PPGBM/WHO Anthro. Tenaga kesehatan tetap dapat
  memeriksa/menimpa nilai hasil hitungan sebelum menyimpan data.
"""

import streamlit as st

try:
    from pygrowup_erknet import Calculator
    _PYGROWUP_OK = True
except ImportError:
    _PYGROWUP_OK = False
import tempfile
from pathlib import Path
import pygrowup_erknet.tables.table as _pg_table

# Streamlit Cloud: site-packages read-only saat runtime,
# jadi cache dialihkan ke /tmp yang selalu writable.
_pg_table.cache_dir = Path(tempfile.gettempdir()) / "pygrowup_erknet_cache"
_pg_table.cache_dir.mkdir(parents=True, exist_ok=True)

@st.cache_resource
def _get_calculator():
    return Calculator(adjust_height_data=False, include_cdc=False)


def tersedia() -> bool:
    """True kalau pustaka pygrowup-erknet ter-install dan siap dipakai."""
    return _PYGROWUP_OK


def hitung_zscore_otomatis(usia_bulan: float, jk: str, berat: float, tinggi: float,
                            cara_ukur: str = "otomatis"):
    """Hitung Z-score BB/U, TB/U, BB/TB berbasis standar WHO.

    Parameters
    ----------
    usia_bulan : usia anak dalam bulan
    jk : "L" atau "P"
    berat : berat badan (kg)
    tinggi : tinggi/panjang badan (cm)
    cara_ukur : "Terlentang" (diukur berbaring/panjang badan, biasa untuk
        usia <24 bulan), "Berdiri" (diukur berdiri/tinggi badan, biasa untuk
        usia >=24 bulan), atau "otomatis" (sistem menentukan sendiri
        berdasarkan usia: <24 bulan -> Terlentang, >=24 bulan -> Berdiri).

    Returns
    -------
    dict berisi zs_bbu, zs_tbu, zs_bbtb (None apabila gagal dihitung) dan
    pesan_error (None apabila berhasil).
    """
    if not _PYGROWUP_OK:
        return {
            "zs_bbu": None, "zs_tbu": None, "zs_bbtb": None,
            "pesan_error": (
                "Pustaka pygrowup-erknet belum terpasang. Jalankan "
                "'pip install pygrowup-erknet' terlebih dahulu."
            ),
        }

    sex = "M" if str(jk).upper().startswith("L") else "F"

    if cara_ukur == "otomatis":
        recumbent = usia_bulan < 24
    else:
        recumbent = (cara_ukur == "Terlentang")

    calc = _get_calculator()
    try:
        zs_bbu = calc.wfa(berat, usia_bulan, sex)
        zs_tbu = calc.lhfa(tinggi, usia_bulan, sex, is_recumbent_height=recumbent)
        if recumbent:
            zs_bbtb = calc.wfl(berat, sex, tinggi, is_recumbent_height=True)
        else:
            zs_bbtb = calc.wfh(berat, sex, tinggi, is_recumbent_height=False)
        return {
            "zs_bbu": round(zs_bbu, 2),
            "zs_tbu": round(zs_tbu, 2),
            "zs_bbtb": round(zs_bbtb, 2),
            "pesan_error": None,
        }
    except Exception as e:
        return {
            "zs_bbu": None, "zs_tbu": None, "zs_bbtb": None,
            "pesan_error": (
                f"Gagal menghitung Z-score otomatis ({e}). Pastikan komputer "
                "terhubung internet (dibutuhkan sekali di awal untuk mengunduh "
                "tabel WHO), atau isi Z-score secara manual."
            ),
        }
