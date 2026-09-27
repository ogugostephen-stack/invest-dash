import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Invest Dash Live", page_icon="🔥", layout="wide")
st.title("🔥 My Invest Dash - Live Any Ticker")

rsi_strike = st.sidebar.slider("RSI Strike", 20, 50, 40)
rsi_toppy = st.sidebar.slider("RSI Toppy", 55, 80, 65)
floor_thresh = st.sidebar.slider("Buy below 200 SMA %", -20, 5, 0)
target = st.sidebar.number_input("Your Target Price", value=0.0)

ticker = st.text_input("🔍 Type Ticker Box", value="AVGO").upper()

def calc_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta>0,0)
    loss = -delta.where(delta<0,0)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    rs = avg_gain/avg_loss
    return 100 - (100/(1+rs))

if ticker:
    df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
    close = df['Close']
    live = float(close.iloc[-1])
    sma200 = float(close.rolling(200).mean().iloc[-1])
    sma50 = float(close.rolling(50).mean().iloc[-1])
    rsi = float(calc_rsi(close).iloc[-1])
    dist_floor = (live - sma200)/sma200
    
    if rsi <= rsi_strike and dist_floor <= floor_thresh/100:
        verdict = "🔥 STRIKE 🔥 - Oversold + Below Floor"
    elif rsi <= rsi_strike:
        verdict = "🤑 BUY ZONE"
    elif rsi >= rsi_toppy:
        verdict = "⚠️ TOPPY - WAIT"
    else:
        verdict = "👀 WATCH"
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Live Price", f"${live:.2f}", verdict)
    col2.metric("200 SMA Floor", f"${sma200:.2f}", f"{dist_floor*100:.2f}%")
    col3.metric("RSI 14d", f"{rsi:.1f}")
    
    st.line_chart(pd.DataFrame({"Price":close[-200:], "200 SMA":close.rolling(200).mean()[-200:], "50 SMA":close.rolling(50).mean()[-200:]}))
