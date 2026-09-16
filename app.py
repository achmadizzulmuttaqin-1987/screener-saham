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

st.title("📈 Screener & Live Chart Saham IDX")
st.caption("Aplikasi Analisis Saham Kompleks: Screener TP/SL + Interactive TradingView Chart")

# 2. Daftar Ticker Saham Populer BEI
@st.cache_data
def load_all_tickers():
    base_tickers = [
        "TLKM", "ICBP", "ADRO", "KLBF", "UNVR", "ASII", "ANTM", "BRIS", 
        "BBCA", "BBRI", "BMRI", "BBNI", "GOTO", "AMMN", "BREN", "CUAN",
        "PTBA", "ITMG", "PGAS", "HRUM", "EXCL", "ISAT", "BSDE", "CTRA",
        "MYOR", "SIDO", "AMRT", "CPIN", "INDF", "INKP", "TPIA", "UNTR"
    ]
    return sorted(list(set(base_tickers)))

all_tickers_raw = load_all_tickers()

# --- SIDEBAR PENGATURAN ---
st.sidebar.header("🔍 Opsi Screener & Chart")

# Pilihan Saham Interaktif
selected_tickers = st.sidebar.multiselect(
    "Pilih Kode Saham untuk Screener:",
    options=all_tickers_raw,
    default=["TLKM", "ICBP", "ADRO", "KLBF", "UNVR"]
)

# Pilihan Saham Khusus yang Ingin Ditampilkan Chart-nya
st.sidebar.markdown("---")
st.sidebar.header("📊 Tampilan Interactive Chart")
active_chart_stock = st.sidebar.selectbox(
    "Pilih 1 Saham untuk Dilihat Chart-nya:",
    options=all_tickers_raw,
    index=0
)

# --- PROSES TABEL SCREENER ---
if selected_tickers:
    with st.spinner("Mengkalkulasi data screener..."):
        results = []
        for symbol in selected_tickers:
            ticker_formatted = f"{symbol}.JK"
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
                        "Kode Saham": symbol,
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
            st.subheader(f"📋 Tabel Screener ({len(results)} Saham)")
            st.dataframe(res_df, use_container_width=True, hide_index=True)

st.markdown("---")

# --- PROSES TAMPILAN TRADINGVIEW CHART ---
st.subheader(f"📊 Live TradingView Chart: {active_chart_stock}")

# Kode Widget HTML Resmi TradingView
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
