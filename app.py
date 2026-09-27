import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Invest Dash Live", page_icon="🔥", layout="centered")
st.title("🔥 My Invest Dash - Any Ticker")

st.sidebar.header("⚙️ My Rules")
rsi_strike = st.sidebar.slider("RSI Strike", 20, 50, 40)
rsi_toppy = st.sidebar.slider("RSI Toppy", 55, 85, 65)
floor_buy = st.sidebar.slider("Buy below 200 SMA %", -20, 10, 0)

MY_WATCHLIST = ["AVGO", "ANET", "ETN", "VRT", "MRVL", "CELH", "SOFI", "META", "AMD", "CAKE", "ADBE", "GOOG", "AMZN", "ELF", "CRM"]

ticker = st.text_input("🔍 TICKER BOX - Type ANY ticker", value="AVGO").upper().strip()

def calc_rsi(prices, p=14):
    d = prices.diff()
    g = d.where(d>0,0).rolling(p).mean()
    l = -d.where(d<0,0).rolling(p).mean()
    rs = g/l
    rsi = 100 - (100/(1+rs))
    return rsi

if ticker:
    try:
        df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
        if df.empty:
            st.error(f"No data for {ticker}. Try AAPL, NVDA, MSFT")
        else:
            # FIX: handle new yfinance format
            close = df['Close']
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            close = close.dropna()
            
            if len(close) < 10:
                st.error("Not enough data")
            else:
                live = float(close.iloc[-1])
                sma200_series = close.rolling(200).mean()
                sma50_series = close.rolling(50).mean()
                sma200 = float(sma200_series.iloc[-1]) if not pd.isna(sma200_series.iloc[-1]) else live
                sma50 = float(sma50_series.iloc[-1]) if not pd.isna(sma50_series.iloc[-1]) else live
                
                rsi_series = calc_rsi(close)
                rsi = float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else 50.0
                dist = (live - sma200)/sma200 if sma200 != 0 else 0

                if rsi <= rsi_strike and dist <= floor_buy/100:
                    verdict = "🔥 STRIKE 🔥"
                elif rsi <= rsi_strike:
                    verdict = "🤑 BUY ZONE"
                elif rsi >= rsi_toppy:
                    verdict = "⚠️ TOPPY"
                else:
                    verdict = "👀 WATCH"

                st.subheader(f"{ticker} - {verdict}")
                c1,c2,c3 = st.columns(3)
                c1.metric("Live", f"${live:.2f}")
                c2.metric("200 SMA", f"${sma200:.2f}", f"{dist*100:.1f}%")
                c3.metric("RSI", f"{rsi:.1f}")
                
                chart_df = pd.DataFrame({
                    "Price": close.tail(200),
                    "200 SMA": close.rolling(200).mean().tail(200),
                    "50 SMA": close.rolling(50).mean().tail(200)
                })
                st.line_chart(chart_df)
    except Exception as e:
        st.error(f"Error fetching {ticker}: {e}")
        st.write("Try another ticker like AAPL or MSFT")

st.divider()
st.write("**Your Watchlist - Quick Check**")
st.write(", ".join(MY_WATCHLIST))
