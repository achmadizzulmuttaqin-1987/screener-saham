import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Pengaturan Halaman Utama
st.set_page_config(
    page_title="Screener & Plotly Chart Saham IDX",
    layout="wide",
    page_icon="📈"
)

st.title("📈 Screener Saham & Interactive Chart (SL / TP1-TP3)")
st.caption("Aplikasi Analisis Saham Kompleks: Screener Automatic + Visualisasi Garis Entry, SL, dan TP1–TP3")

# 2. Master Daftar Saham Terpopuler & Syariah
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

run_button = st.sidebar.button("🚀 Jalankan Screener", use_container_width=True)

# Dictionary untuk menyimpan data hasil kalkulasi saham yang diproses
calculated_stocks = {}

# --- PROSES TABEL SCREENER ---
st.subheader("📋 Tabel Analisis Screener Saham")

if run_button or selected_tickers:
    if not selected_tickers:
        st.warning("Silakan pilih atau ketik minimal satu kode saham.")
    else:
        with st.spinner("Mengambil data harga terkini dari BEI..."):
            results = []
            
            for symbol in selected_tickers:
                ticker_formatted = f"{symbol}.JK" if not symbol.endswith(".JK") else symbol
                clean_symbol = symbol.replace(".JK", "").upper()
                
                try:
                    stock = yf.Ticker(ticker_formatted)
                    df = stock.history(period="3mo") # Ambil 3 bulan data untuk grafik ideal
                    
                    if not df.empty and len(df) > 1:
                        last_price = round(df['Close'].iloc[-1])
                        high_price = df['High'].max()
                        low_price = df['Low'].min()
                        
                        price_range = high_price - low_price
                        
                        sl = round(last_price - (price_range * 0.15))
                        tp1 = round(last_price + (price_range * 0.15))
                        tp2 = round(last_price + (price_range * 0.30))
                        tp3 = round(last_price + (price_range * 0.45))
                        
                        calculated_stocks[clean_symbol] = {
                            "df": df,
                            "last_price": last_price,
                            "sl": sl,
                            "tp1": tp1,
                            "tp2": tp2,
                            "tp3": tp3
                        }
                        
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

# --- PROSES TAMPILAN PLOTLY CHART DENGAN GARIS TP & SL ---
st.sidebar.markdown("---")
st.sidebar.header("📊 Interactive Chart SL/TP")

if calculated_stocks:
    active_chart_stock = st.sidebar.selectbox(
        "Pilih Saham untuk Visualisasi Chart & Garis SL/TP:",
        options=list(calculated_stocks.keys()),
        index=0
    )
    
    stock_data = calculated_stocks[active_chart_stock]
    df_chart = stock_data["df"]
    
    st.subheader(f"📊 Chart Candlestick + Level TP/SL: {active_chart_stock}")
    
    # Buat Chart Candlestick
    fig = go.Figure(data=[go.Candlestick(
        x=df_chart.index,
        open=df_chart['Open'],
        high=df_chart['High'],
        low=df_chart['Low'],
        close=df_chart['Close'],
        name="Harga Saham"
    )])
    
    # Tambahkan Garis Horizontal (Entry, SL, TP1, TP2, TP3)
    fig.add_hline(y=stock_data["last_price"], line_dash="dash", line_color="blue", annotation_text=f"Entry: Rp {stock_data['last_price']:,}", annotation_position="top left")
    fig.add_hline(y=stock_data["sl"], line_dash="solid", line_color="red", annotation_text=f"SL: Rp {stock_data['sl']:,}", annotation_position="bottom left")
    fig.add_hline(y=stock_data["tp1"], line_dash="solid", line_color="lightgreen", annotation_text=f"TP1: Rp {stock_data['tp1']:,}", annotation_position="top right")
    fig.add_hline(y=stock_data["tp2"], line_dash="solid", line_color="green", annotation_text=f"TP2: Rp {stock_data['tp2']:,}", annotation_position="top right")
    fig.add_hline(y=stock_data["tp3"], line_dash="solid", line_color="darkgreen", annotation_text=f"TP3: Rp {stock_data['tp3']:,}", annotation_position="top right")
    
    # Pengaturan Tampilan Grafik (Dark Theme & Layout Spacing)
    fig.update_layout(
        template="plotly_dark",
        height=600,
        xaxis_rangeslider_visible=False,
        title=f"Analisis Candlestick {active_chart_stock} (3 Bulan)",
        yaxis_title="Harga (Rp)",
        xaxis_title="Tanggal"
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Jalankan screener terlebih dahulu untuk melihat grafik candlestick beserta garis TP & SL.")
