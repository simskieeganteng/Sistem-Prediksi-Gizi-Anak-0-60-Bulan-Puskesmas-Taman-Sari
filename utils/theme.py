"""
Modul tema visual terpusat — 'Kartu Tumbuh Kembang'.
Diinspirasi kartu KMS/Buku KIA yang akrab bagi tenaga posyandu, dipadu
motif kurva pertumbuhan (Z-score WHO) sebagai elemen signature.

Panggil inject_css() dan render_sidebar_brand() di awal SETIAP halaman
(app.py maupun tiap file di pages/) agar tema konsisten di semua halaman,
karena Streamlit multipage menjalankan ulang script per halaman.
"""

import streamlit as st

# ----------------------------------------------------------------------
# Token warna status gizi — dipakai di seluruh aplikasi agar konsisten
# ----------------------------------------------------------------------
STATUS_COLORS = {
    "Gizi Buruk":  {"bg": "#FDEBEA", "fg": "#B23A45", "dot": "#D64550"},
    "Gizi Kurang": {"bg": "#FFF1E3", "fg": "#B5651D", "dot": "#F2994A"},
    "Gizi Baik":   {"bg": "#E9F5EE", "fg": "#1F7A5C", "dot": "#1F7A5C"},
    "Gizi Lebih":  {"bg": "#FDF6E0", "fg": "#8A6D1B", "dot": "#E8B339"},
}


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

        :root {
            --paper: #F5F7F1;
            --paper-grid: rgba(31,122,92,0.07);
            --ink: #17261F;
            --ink-soft: #5C6B62;
            --primary: #1F7A5C;
            --primary-dark: #14523E;
            --coral: #FF6B54;
            --sand: #E8B339;
            --card: #FFFFFF;
            --border: rgba(23,38,31,0.10);
            --radius: 18px;
        }

        html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

        [data-testid="stAppViewContainer"] {
            background-color: var(--paper);
            background-image:
                linear-gradient(var(--paper-grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--paper-grid) 1px, transparent 1px);
            background-size: 28px 28px;
        }
        [data-testid="stHeader"] { background: transparent; }

        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: var(--ink) !important;
            letter-spacing: -0.01em;
        }
        p, li, span, label, div { color: var(--ink); }
        .stCaption, [data-testid="stCaptionContainer"] { color: var(--ink-soft) !important; }

        code, .stCodeBlock, [data-testid="stMetricValue"] {
            font-family: 'IBM Plex Mono', monospace !important;
        }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background-color: var(--primary-dark);
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] * { color: #EAF3EE !important; }
        [data-testid="stSidebarNav"] a {
            border-radius: 10px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }
        [data-testid="stSidebarNav"] a:hover { background-color: rgba(255,255,255,0.08); }
        [data-testid="stSidebarNav"] li div[aria-current="page"] a {
            background-color: rgba(255,255,255,0.14);
        }

        /* ---------- Kartu / eyebrow / divider ---------- */
        .kg-eyebrow {
            display: inline-flex; align-items: center; gap: 8px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12.5px; letter-spacing: 0.10em; text-transform: uppercase;
            color: var(--primary); font-weight: 600; margin-bottom: 6px;
        }
        .kg-eyebrow::before {
            content: ""; width: 7px; height: 7px; border-radius: 50%;
            background: var(--coral); display: inline-block;
        }
        .kg-card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 22px 24px;
            box-shadow: 0 1px 2px rgba(23,38,31,0.04);
        }
        .kg-divider {
            border: none; height: 1px;
            background-image: repeating-linear-gradient(90deg, var(--border) 0 6px, transparent 6px 12px);
            margin: 28px 0;
        }

        /* ---------- Badge status gizi ---------- */
        .kg-badge {
            display: inline-flex; align-items: center; gap: 7px;
            padding: 5px 14px; border-radius: 999px;
            font-family: 'Inter', sans-serif; font-weight: 600; font-size: 14px;
        }
        .kg-badge .dot { width: 8px; height: 8px; border-radius: 50%; display:inline-block; }

        /* ---------- Metric bawaan Streamlit ---------- */
        [data-testid="stMetric"] {
            background: var(--card); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 16px 18px;
        }
        [data-testid="stMetricLabel"] { color: var(--ink-soft) !important; font-weight: 500; }

        /* ---------- Tombol ---------- */
        .stButton > button, .stFormSubmitButton > button {
            background: var(--primary); color: #FFFFFF; border: none;
            border-radius: 12px; font-weight: 600; padding: 0.6em 1.2em;
            transition: transform 0.12s ease, background 0.12s ease;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            background: var(--primary-dark); transform: translateY(-1px);
        }

        /* ---------- Tabs ---------- */
        [data-testid="stTabs"] button { font-family: 'Space Grotesk', sans-serif; font-weight: 600; }
        [data-testid="stTabs"] [aria-selected="true"] { color: var(--primary) !important; }

        /* ---------- DataFrame ---------- */
        [data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid var(--border); }

        /* ---------- Form (bungkus kartu otomatis, tanpa div manual) ---------- */
        [data-testid="stForm"] {
            background: var(--card); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 24px 26px 8px 26px;
        }

        /* ---------- Tabel widget bawaan (mis. selectbox, expander) ikut rounded ---------- */
        [data-testid="stExpander"] { border-radius: var(--radius); border: 1px solid var(--border); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def growth_curve_svg(height=150, stroke="#FF6B54"):
    """Elemen signature: kurva pertumbuhan (persentil WHO) yang menggambar
    dirinya sendiri saat halaman dimuat."""
    return f"""
    <svg viewBox="0 0 600 {height}" width="100%" height="{height}" preserveAspectRatio="none"
         xmlns="http://www.w3.org/2000/svg">
        <path d="M0,{height*0.85} C120,{height*0.75} 160,{height*0.35} 300,{height*0.30}
                 C440,{height*0.25} 480,{height*0.6} 600,{height*0.12}"
              fill="none" stroke="{stroke}" stroke-width="4" stroke-linecap="round"
              stroke-dasharray="900" stroke-dashoffset="900">
            <animate attributeName="stroke-dashoffset" from="900" to="0" dur="1.6s"
                     fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" />
        </path>
        <path d="M0,{height*0.95} C140,{height*0.9} 180,{height*0.6} 300,{height*0.55}
                 C420,{height*0.5} 470,{height*0.8} 600,{height*0.4}"
              fill="none" stroke="#1F7A5C" stroke-width="2.5" stroke-opacity="0.35"
              stroke-linecap="round" stroke-dasharray="900" stroke-dashoffset="900">
            <animate attributeName="stroke-dashoffset" from="900" to="0" dur="2s" begin="0.15s"
                     fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" />
        </path>
    </svg>
    """


def page_header(icon: str, title: str, subtitle: str, eyebrow: str):
    st.markdown(
        f"""
        <div class="kg-eyebrow">{eyebrow}</div>
        <h1 style="margin-top:0;">{icon} {title}</h1>
        <p style="color:var(--ink-soft); font-size:16px; margin-top:-8px;">{subtitle}</p>
        <hr class="kg-divider"/>
        """,
        unsafe_allow_html=True,
    )


def status_badge(label: str) -> str:
    c = STATUS_COLORS.get(label, {"bg": "#EEE", "fg": "#333", "dot": "#999"})
    return (
        f'<span class="kg-badge" style="background:{c["bg"]}; color:{c["fg"]};">'
        f'<span class="dot" style="background:{c["dot"]};"></span>{label}</span>'
    )


def render_sidebar_brand(icon: str = "🌱", nama: str = "Puskesmas Taman Sari",
                          versi: str = "Machine Learning",
                          logo_path: str | None = "assets/logo.png"):
    """Render logo & nama aplikasi di sidebar.

    - icon: satu emoji/karakter yang ditampilkan di kotak logo (dipakai kalau
      logo_path tidak ditemukan). Ganti sesuai selera, misal "👶", "📊", "🏥".
    - logo_path: path ke file gambar (PNG/JPG/SVG) untuk dipakai sebagai logo
      asli (mis. logo Puskesmas), menggantikan emoji. Defaultnya membaca
      streamlit_app/assets/logo.png bila file tersebut ada.
    """
    import base64
    import os

    logo_html = f'<span>{icon}</span>'
    kotak_bg = "linear-gradient(135deg,#FF6B54,#E8B339)"
    kotak_padding = "0"

    if logo_path and os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(logo_path)[1].lstrip(".").lower()
        mime = "svg+xml" if ext == "svg" else ext
        logo_html = (
            f'<img src="data:image/{mime};base64,{b64}" '
            f'style="width:100%; height:100%; object-fit:contain; border-radius:8px;" />'
        )
        # logo punya latar putih sendiri -> kotak dibuat putih polos + sedikit
        # padding supaya logo tidak menempel ke tepi kotak
        kotak_bg = "#FFFFFF"
        kotak_padding = "3px"

    st.sidebar.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; padding:4px 2px 18px 2px;">
            <div style="width:38px; height:38px; border-radius:11px;
                        background:{kotak_bg}; padding:{kotak_padding};
                        display:flex; align-items:center; justify-content:center;
                        font-size:19px; overflow:hidden; box-sizing:border-box;">{logo_html}</div>
            <div style="line-height:1.15;">
                <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:15.5px;">
                    {nama}
                </div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:11px; opacity:0.7;">
                    {versi}
                </div>
            </div>
        </div>
        <hr class="kg-divider" style="margin:0 0 10px 0; opacity:0.25;"/>
        """,
        unsafe_allow_html=True,
    )
