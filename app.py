import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components

# 1. Pengaturan Halaman Utama
st.set_page_config(
    page_title="Screener & Chart Saham IDX",
    layout="wide",
    page_icon="📈"
)

st.title("📈 Screener & Live Chart Saham IDX (Lengkap)")
st.caption("Aplikasi Analisis Saham Komprehensif: Screener TP/SL + Live TradingView Chart dengan Indikator Lengkap")

# 2. Master Daftar Saham Terpopuler & Syariah (100+ Emiten Utama BEI)
@st.cache_data
def load_all_tickers():
    base_tickers = [
        "AALI", "ABDA", "ABMM", "ACES", "ACST", "ADCP", "ADHI", "ADRO", "AGII", "AGRO",
        "AKRA", "ALDO", "AMMN", "AMRT", "ANJT", "ANTM", "APLN", "ARTO", "ASGR", "ASII", 
        "AUTO", "BABP", "BANK", "BBRM", "BBCA", "BBRI", "BMRI", "BBNI", "BBTN", "BBYB", 
        "BCIC", "BDMN", "BEST", "BFIN", "BIPP", "BIRD", "BKSL", "BLTZ", "BMHS", "BMTR", 
        "BNBR", "BNGA", "BNLI", "BREN", "BRIS", "BSDE", "BTPS", "BUKA", "BULL", "BUMI", 
        "CASS", "CITA", "CLPI", "CMNP", "CPIN", "CSAP", "CTRA", "CUAN", "DART", "DILD", 
        "DMAS", "DOID", "DNET", "DVLA", "EAST", "ELSA", "ENRG", "ERAA", "ESSA", "EXCL", 
        "FAST", "FILM", "FORU", "GIAA", "GJTL", "GOOD", "GOTO", "GPSO", "HEAL", "HERO", 
        "HEXA", "HISP", "HMSP", "HRUM", "IATA", "ICBP", "INCF", "INDF", "INKP", "INTP", 
        "IPTV", "IRRA", "ISAT", "ITMG", "JECC", "JSMR", "KBLI", "KBAG", "KDSI", "KIJA", 
        "KKGI", "KLBF", "KMTR", "KPIG", "KRAS", "LPCK", "LPKR", "LPPF", "MAPA", "MAPI", 
        "MBMA", "MDKA", "MEDC", "MIKA", "MNCN", "MPPA", "MSKY", "MTEL", "MYOR", "NCKL", 
        "PALM", "PANR", "PBSD", "PGAS", "PNBN", "PNLF", "PTBA", "PTPP", "PWON", "RALS", 
        "RANC", "ROTI", "SAME", "SCMA", "SIDO", "SILO", "SIMP", "SMSM", "SRTG", "SSMS", 
        "TAPG", "TBIG", "TINS", "TKIM", "TLKM", "TOWR", "TPIA", "UNTR", "UNVR", "WEGE", 
        "WIFI", "WIKA", "WOOD"
    ]
    return sorted(list(set(base_tickers)))

all_tickers_raw = load_all_tickers()

# --- SIDEBAR PENGATURAN ---
st.sidebar.header("🔍 Opsi Pencarian Saham")

# Mode Pencarian Saham
search_type = st.sidebar.radio("Metode Input Saham:", ["Pilih dari Daftar Dropdown", "Ketik Kode Bebas (Seluruh BEI)"])

selected_tickers = []

if search_type == "Pilih dari Daftar Dropdown":
    selected_tickers = st.sidebar.multiselect(
        "Pilih/Cari Kode Saham (Bisa Ketik di Box):",
        options=all_tickers_raw,
        default=["TLKM", "ICBP", "ADRO", "KLBF", "UNVR"]
    )
else:
    custom_input = st.sidebar.text_input(
        "Ketik Kode Saham Bebas (Pisahkan dengan koma):", 
        value="TLKM, ICBP, ADRO, BRIS, BREN"
    )
    if custom_input:
        selected_tickers = [x.strip().upper() for x in custom_input.split(",") if x.strip()]

# Tombol Eksekusi Screener
run_button = st.sidebar.button("🚀 Jalankan Screener", use_container_width=True)

# --- PROSES TABEL SCREENER ---
st.subheader("📋 Tabel Analisis Screener Saham")

if run_button or selected_tickers:
    if not selected_tickers:
        st.warning("Silakan pilih atau ketik minimal satu kode saham.")
    else:
        with st.spinner("Mengambil data harga terkini dari BEI..."):
            results = []
            
            for symbol in selected_tickers:
                # Menyesuaikan format untuk yfinance
                ticker_formatted = f"{symbol}.JK" if not symbol.endswith(".JK") else symbol
                clean_symbol = symbol.replace(".JK", "").upper()
                
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
                            "Kode Saham": clean_symbol,
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
                st.dataframe(res_df, use_container_width=True, hide_index=True)
            else:
                st.error("Data saham tidak ditemukan. Pastikan kode saham benar (Contoh: TLKM, ADRO, BREN, CUAN).")

st.markdown("---")

# --- PROSES TAMPILAN TRADINGVIEW CHART ---
st.sidebar.markdown("---")
st.sidebar.header("📊 Interactive Chart")

# Opsi Pilihan Chart Berdasarkan Saham yang Sedang Dilihat
active_chart_stock = "TLKM"
if selected_tickers:
    active_chart_stock = st.sidebar.selectbox(
        "Pilih Saham untuk Live Chart:",
        options=selected_tickers,
        index=0
    )
else:
    active_chart_stock = st.sidebar.text_input("Ketik Kode Saham untuk Chart:", "TLKM").upper()

st.subheader(f"📊 Live TradingView Chart: {active_chart_stock}")

# Widget HTML Resmi TradingView
tradingview_html = f"""
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container" style="height:100%;width:100%">
  <div id="tradingview_chart" style="height:550px;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {{
    "autosize": true,
    "symbol": "IDX:{active_chart_stock}",
    "interval": "D",
    "timezone": "Asia/Jakarta",
    "theme": "dark",
    "style": "1",
    "locale": "id",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_chart",
    "studies": [
      "RSI@tv-basicstudies",
      "MASimple@tv-basicstudies",
      "MACD@tv-basicstudies"
    ]
  }}
  );
  </script>
</div>
<!-- TradingView Widget END -->
"""

# Menampilkan Widget TradingView di Streamlit
components.html(tradingview_html, height=570)
