import streamlit as st
import yfinance as yf
import pandas as pd

# Pengaturan Halaman Utama
st.set_page_config(page_title="Screener Saham Syariah Lengkap", layout="wide", page_icon="📈")

st.title("📈 Screener Saham IDX (Syariah / All Emiten)")
st.caption("Pencarian dan kalkulasi Target Price (TP1-TP3) & Stop Loss (SL) untuk seluruh emiten BEI.")

# 1. Daftar Utama Ticker Saham Populer & Lengkap
# Catatan: yfinance membutuhkan akhiran '.JK' untuk bursa Indonesia
@st.cache_data
def load_all_tickers():
    # Daftar ticker komprehensif dari sektor-sektor utama BEI
    base_tickers = [
        "AALI", "ABDA", "ABMM", "ACES", "ACST", "ADCP", "ADHI", "ADRO", "AGII", "AGRO",
        "AKRA", "ALDO", "AMRT", "ANJT", "ANTM", "APLN", "ARTO", "ASGR", "ASII", "AUTO",
        "BABP", "BANK", "BBRM", "BBTN", "BBYB", "BCIC", "BDMN", "BEST", "BFIN", "BIPP",
        "BIRD", "BISIP", "BKSL", "BLTZ", "BMHS", "BMTR", "BNBR", "BNGA", "BNLI", "BSDE",
        "BTPS", "BUKA", "BULL", "BUMI", "CASS", "CITA", "CLPI", "CMNP", "CPIN", "CSAP",
        "CTRA", "DART", "DILD", "DMAS", "DOOID", "DNET", "DVLA", "EAST", "ELSA", "ENRG",
        "ERAA", "ESSA", "EXCL", "FAST", "FILM", "FORU", "GIAA", "GJTL", "GOOD", "GOTO",
        "GPSO", "HEAL", "HERO", "HEXA", "HISP", "HMSO", "HRUM", "IATA", "ICBP", "INCF",
        "INDF", "INKP", "INTP", "IPTV", "IRRA", "ISAT", "ITMG", "JECC", "JSMR", "KBLI",
        "KBAG", "KDSI", "KIJA", "KKGI", "KLBF", "KMTR", "KPIG", "KRAS", "LPCK", "LPKR",
        "LPPF", "MAPA", "MAPI", "MBMA", "MDCA", "MEDC", "MIKA", "MNCN", "MPPA", "MSKY",
        "MTEL", "MYOR", "NCKL", "PALM", "PANR", "PBSD", "PGAS", "PNBN", "PNLF", "PTBA",
        "PTPP", "PWON", "RALS", "RANC", "ROTI", "SAME", "SCMA", "SIDO", "SILO", "SIMP",
        "SMAA", "SMBR", "SMSM", "SRTG", "SSMS", "TAPG", "TBIG", "TINS", "TKIM", "TLKM",
        "TOWR", "TPIA", "UANG", "UNTR", "UNVR", "WEGE", "WIFI", "WIKA", "WOOD", "YPAS"
    ]
    return sorted(list(set(base_tickers)))

all_tickers_raw = load_all_tickers()

# --- SIDEBAR PENGATURAN ---
st.sidebar.header("🔍 Opsi Pencarian Saham")

# Mode Pencarian
search_type = st.sidebar.radio("Metode Pilih Saham:", ["Pilih dari Daftar", "Ketik Kode Saham Sendiri"])

selected_tickers = []

if search_type == "Pilih dari Daftar":
    selected_tickers = st.sidebar.multiselect(
        "Pilih/Cari Kode Saham (Ketik untuk mencari):",
        options=all_tickers_raw,
        default=["TLKM", "ICBP", "ADRO", "KLBF", "UNVR"]
    )
else:
    custom_input = st.sidebar.text_input("Masukkan Kode Saham (Pisahkan dengan koma):", "TLKM, ICBP, ADRO")
    if custom_input:
        selected_tickers = [x.strip().upper() for x in custom_input.split(",") if x.strip()]

# Tombol Eksekusi Screener
run_button = st.sidebar.button("🚀 Jalankan Screener", use_container_width=True)

# --- PROSES KALKULASI DEPAN ---
if run_button or selected_tickers:
    if not selected_tickers:
        st.warning("Silakan pilih atau ketik minimal satu kode saham.")
    else:
        with st.spinner("Mengambil data harga terkini dari BEI..."):
            results = []
            
            for symbol in selected_tickers:
                ticker_formatted = f"{symbol}.JK" if not symbol.endswith(".JK") else symbol
                try:
                    stock = yf.Ticker(ticker_formatted)
                    df = stock.history(period="1mo")
                    
                    if not df.empty and len(df) > 1:
                        last_price = round(df['Close'].iloc[-1])
                        high_price = df['High'].max()
                        low_price = df['Low'].min()
                        
                        price_range = high_price - low_price
                        
                        sl = round(last_price - (price_range * 0.15))
                        tp1 = round(last_price + (price_range * 0.15))
                        tp2 = round(last_price + (price_range * 0.30))
                        tp3 = round(last_price + (price_range * 0.45))
                        
                        results.append({
                            "Kode Saham": symbol.replace(".JK", ""),
                            "Harga Terakhir": f"Rp {last_price:,}",
                            "Stop Loss (SL)": f"Rp {sl:,}",
                            "Target 1 (TP1)": f"Rp {tp1:,}",
                            "Target 2 (TP2)": f"Rp {tp2:,}",
                            "Target 3 (TP3)": f"Rp {tp3:,}"
                        })
                except Exception:
                    continue

            if results:
                res_df = pd.DataFrame(results)
                st.subheader(f"Hasil Analisis ({len(results)} Saham)")
                st.dataframe(res_df, use_container_width=True, hide_index=True)
            else:
                st.error("Data tidak ditemukan. Pastikan kode saham benar (contoh: TLKM, ADRO, ICBP).")
