import streamlit as st
import yfinance as yf
import pandas as pd

# Pengaturan Halaman Utama
st.set_page_config(page_title="Screener Saham IDX Syariah", layout="wide", page_icon="📈")

st.title("📈 Screener Saham IDX Syariah")
st.caption("Aplikasi Screener Saham Real-time Delay dengan Level Stop Loss (SL) & Target Price (TP1 - TP3)")

# Data Saham Syariah Terpopuler berdasarkan Sektor (DES / ISSI)
SHARIAH_STOCKS = {
    "Consumer Goods / FMCG": ["ICBP.JK", "INDF.JK", "UNVR.JK", "KLBF.JK", "MYOR.JK", "SIDO.JK", "AMRT.JK", "GOOD.JK"],
    "Energi & Pertambangan": ["ADRO.JK", "ANTM.JK", "PTBA.JK", "ITMG.JK", "MEDC.JK", "PGAS.JK", "HRUM.JK", "MBMA.JK"],
    "Telekomunikasi & Infrastruktur": ["TLKM.JK", "EXCL.JK", "ISAT.JK", "TOWR.JK", "TBIG.JK", "JSMR.JK"],
    "Keuangan & Perbankan Syariah": ["BRIS.JK", "BTPS.JK"],
    "Properti & Konstruksi": ["BSDE.JK", "CTRA.JK", "PWON.JK", "PTPP.JK", "ADHI.JK", "WEGE.JK"],
    "Otomotif & Industri": ["ASII.JK", "AUTO.JK", "UNTR.JK"]
}

# Gabungan seluruh daftar saham syariah
ALL_SHARIAH_LIST = [ticker for sector_stocks in SHARIAH_STOCKS.values() for ticker in sector_stocks]

# --- SIDEBAR PENGATURAN ---
st.sidebar.header("🔍 Filter & Mode")

# Toggle Syariah Only
syariah_only = st.sidebar.toggle("Hanya Tampilkan Saham Syariah (DES)", value=True)

if syariah_only:
    selected_sector = st.sidebar.selectbox("Pilih Sektor Syariah", ["Semua Sektor"] + list(SHARIAH_STOCKS.keys()))
    if selected_sector == "Semua Sektor":
        stock_options = ALL_SHARIAH_LIST
    else:
        stock_options = SHARIAH_STOCKS[selected_sector]
else:
    # Jika filter syariah dimatikan, tambahkan saham non-syariah seperti Bank Konvensional
    NON_SHARIAH_ADDON = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "GOTO.JK"]
    stock_options = ALL_SHARIAH_LIST + NON_SHARIAH_ADDON

# Pilihan Saham Interaktif
selected_stocks = st.sidebar.multiselect(
    "Pilih Kode Saham:",
    options=stock_options,
    default=stock_options[:5]  # Default 5 saham pertama
)

# Tombol Eksekusi Screener
run_button = st.sidebar.button("🚀 Jalankan Screener", use_container_width=True)

# --- PROSES KALKULASI DEPAN ---
if run_button or selected_stocks:
    if not selected_stocks:
        st.warning("Silakan pilih minimal satu kode saham dari menu sidebar di sebelah kiri.")
    else:
        with st.spinner("Mengambil data harga terkini dari BEI..."):
            results = []
            
            for ticker in selected_stocks:
                try:
                    stock = yf.Ticker(ticker)
                    df = stock.history(period="1mo")
                    
                    if not df.empty:
                        last_price = round(df['Close'].iloc[-1])
                        high_price = df['High'].max()
                        low_price = df['Low'].min()
                        
                        # Hitung Rentang Harga (Volatilitas 1 Bulan Terakhir)
                        price_range = high_price - low_price
                        
                        # Rumus Kalkulasi Risk-to-Reward (SL & TP1 - TP3)
                        sl = round(last_price - (price_range * 0.15))
                        tp1 = round(last_price + (price_range * 0.15))
                        tp2 = round(last_price + (price_range * 0.30))
                        tp3 = round(last_price + (price_range * 0.45))
                        
                        is_shariah = "✅ Syariah" if ticker in ALL_SHARIAH_LIST else "❌ Non-Syariah"
                        
                        results.append({
                            "Kode Saham": ticker.replace(".JK", ""),
                            "Harga Terakhir": f"Rp {last_price:,}",
                            "Stop Loss (SL)": f"Rp {sl:,}",
                            "Target 1 (TP1)": f"Rp {tp1:,}",
                            "Target 2 (TP2)": f"Rp {tp2:,}",
                            "Target 3 (TP3)": f"Rp {tp3:,}",
                            "Status Syariah": is_shariah
                        })
                except Exception as e:
                    continue

            if results:
                res_df = pd.DataFrame(results)
                
                # Tampilkan Ringkasan
                st.subheader(f"Hasil Analisis ({len(results)} Saham)")
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                
                # Catatan Penjelas
                st.info("""
                **Keterangan Kalkulasi:**
                * **SL (Stop Loss):** Batas aman penutupan kerugian (Risk ~15% dari rentang harga bulanan).
                * **TP 1 - TP 3:** Target keuntungan berjenjang berdasarkan rasio Risk-to-Reward.
                * Status Syariah mengacu pada kriteria **Daftar Efek Syariah (DES) OJK**.
                """)
            else:
                st.error("Gagal mengambil data saham. Pastikan koneksi internet stabil.")
