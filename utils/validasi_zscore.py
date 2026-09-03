
akurasi perhitungan Z-score otomatis, dengan membandingkan terhadap nilai
Z-score asli dari e-PPGBM yang sudah ada di file Excel Puskesmas Taman Sari.

Cara pakai:
    pip install pygrowup-erknet openpyxl pandas
    python validasi_zscore.py DATA_GIZI_PUSKESMAS_TAMANSARII.xlsx
"""
import sys
import datetime
import openpyxl
import pandas as pd
from utils.zscore import hitung_zscore_otomatis  # sesuaikan path import jika perlu


def fix_number(val):
    if val is None:
        return None
    if isinstance(val, datetime.time):
        return val.hour + val.minute / 100.0
    if isinstance(val, datetime.timedelta):
        total_menit = round(val.total_seconds() / 60)
        jam, menit = divmod(total_menit, 60)
        return jam + menit / 100.0
    if isinstance(val, str):
        v = val.strip()
        if v in ("-", "", "Outlier"):
            return None
        try:
            return float(v.replace(",", "."))
        except ValueError:
            return None
    if isinstance(val, (int, float)):
        return float(val)
    return None


def main(path_excel, n_sample=15):
    wb = openpyxl.load_workbook(path_excel, data_only=True)
    ws = wb["Lembar1"]
    rows = list(ws.iter_rows(values_only=True))
    header = list(rows[0])
    raw = pd.DataFrame(rows[1:], columns=header)

    selisih_bbu, selisih_tbu, selisih_bbtb = [], [], []
    n_diuji = 0

    for _, r in raw.sample(min(n_sample, len(raw)), random_state=42).iterrows():
        try:
            tgl_lahir = pd.to_datetime(r["Tgl Lahir"])
            tgl_ukur = pd.to_datetime(r["Tanggal Pengukuran"])
            usia = (tgl_ukur - tgl_lahir).days / 30.4375
            jk = r["JK"]
            berat_raw = fix_number(r["Berat"])
            berat = berat_raw / 1000.0 if berat_raw and berat_raw > 100 else berat_raw
            tinggi = fix_number(r["Tinggi"])
            cara_ukur = r["Cara Ukur"]

            asli_bbu = fix_number(r["ZS BB/U"])
            asli_tbu = fix_number(r["ZS TB/U"])
            asli_bbtb = fix_number(r["ZS BB/TB"])

            if None in (berat, tinggi, asli_bbu, asli_tbu, asli_bbtb):
                continue

            hasil = hitung_zscore_otomatis(usia, jk, berat, tinggi, cara_ukur)
            if hasil["pesan_error"]:
                print("GAGAL:", hasil["pesan_error"])
                continue

            n_diuji += 1
            d_bbu = abs(hasil["zs_bbu"] - asli_bbu)
            d_tbu = abs(hasil["zs_tbu"] - asli_tbu)
            d_bbtb = abs(hasil["zs_bbtb"] - asli_bbtb)
            selisih_bbu.append(d_bbu)
            selisih_tbu.append(d_tbu)
            selisih_bbtb.append(d_bbtb)

            print(
                f"Usia={usia:.1f}bln JK={jk} BB={berat}kg TB={tinggi}cm | "
                f"BB/U: hitung={hasil['zs_bbu']:+.2f} asli={asli_bbu:+.2f} (selisih {d_bbu:.2f}) | "
                f"TB/U: hitung={hasil['zs_tbu']:+.2f} asli={asli_tbu:+.2f} (selisih {d_tbu:.2f}) | "
                f"BB/TB: hitung={hasil['zs_bbtb']:+.2f} asli={asli_bbtb:+.2f} (selisih {d_bbtb:.2f})"
            )
        except Exception as e:
            print("Lewati baris (error):", e)

    if n_diuji:
        print(f"\n=== Ringkasan ({n_diuji} data diuji) ===")
        print(f"Rata-rata selisih BB/U : {sum(selisih_bbu)/n_diuji:.3f}")
        print(f"Rata-rata selisih TB/U : {sum(selisih_tbu)/n_diuji:.3f}")
        print(f"Rata-rata selisih BB/TB: {sum(selisih_bbtb)/n_diuji:.3f}")
        print(
            "\nJika rata-rata selisih di bawah ~0.1-0.2, perhitungan otomatis "
            "cukup akurat dipakai. Jika jauh lebih besar, sebaiknya tetap "
            "andalkan input manual dari e-PPGBM."
        )
    else:
        print("Tidak ada data yang berhasil diuji.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "DATA_GIZI_PUSKESMAS_TAMANSARII.xlsx"
    main(path)
