import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Invest Dash V2", page_icon="🔥", layout="wide")
st.title("🔥 Invest Dash V2 - Your Full System")

# YOUR DATA FROM EXCEL
SUPPORT_DATA = {
    "AMZN": {"t1": 222, "t2": 215, "t3": 211, "logic": "Strong demand zone at $211-$218."},
    "META": {"t1": 650, "t2": 640, "t3": 630, "logic": "$650 is major horizontal support."},
    "AMD": {"t1": 203, "t2": 173, "t3": 157, "logic": "$173 is the highest-value weekly shelf."},
    "CELH": {"t1": 43, "t2": 41, "t3": 38, "logic": "$41 is multi-timeframe support."},
    "GOOG": {"t1": 290, "t2": 213, "t3": 205, "logic": "Structural shelf in low-200s."},
    "CRM": {"t1": 258, "t2": 252, "t3": 221, "logic": "$221 is 52-week low floor."},
    "ADBE": {"t1": 350, "t2": 311, "t3": 280, "logic": "$311 is bottom of current range."},
    "SOFI": {"t1": 27, "t2": 24, "t3": 21, "logic": "$20.67 major 52-week retracement."},
    "ELF": {"t1": 75, "t2": 69, "t3": 65, "logic": "Falling trend; $69 key support."},
    "SHOP": {"t1": 160, "t2": 153, "t3": 141, "logic": "$153 aligns with 61.8% Fib."},
    "NVO": {"t1": 50, "t2": 48, "t3": 45, "logic": "Falling channel; $45 next floor."},
    "HIMS": {"t1": 33, "t2": 28, "t3": 25, "logic": "High volatility; 200 SMA broken."},
    "JMIA": {"t1": 11, "t2": 10, "t3": 6.8, "logic": "Bubble reset target sub-$7."},
    "CAKE": {"t1": 50, "t2": 48, "t3": 45, "logic": "Already under 200 SMA."},
    "AVGO": {"t1": 312.5, "t2": 285, "t3": 260, "logic": "Brain - AI Infrastructure leader."},
    "ANET": {"t1": 116, "t2": 105, "t3": 95, "logic": "Network - expensive but strong."},
    "ETN": {"t1": 295, "t2": 260, "t3": 240, "logic": "Power - electrification theme."},
    "VRT": {"t1": 139, "t2": 120, "t3": 100, "logic": "Heat - data center cooling."},
}

WATCHLIST = list(SUPPORT_DATA.keys())

def calc_rsi(prices, p=14):
    d = prices.diff()
    g = d.where(d>0,0).rolling(p).mean()
    l = -d.where(d<0,0).rolling(p).mean()
    return 100 - (100/(1+g/l))

def get_verdict(rsi, dist):
    # dist is (live - 200sma)/200sma
    if rsi < 35 and dist < -0.05:
        return "🔥 STRIKE 🔥", "#d9ead3" # GREEN
    elif rsi < 45 and dist < 0:
        return "🤑 BUY ZONE 🤑", "#d9ead3"
    elif rsi > 60 and dist > 0.25:
        return "⚠️ TOPPY - DON'T CHASE", "#ea9999" # ROSE
    elif rsi > 58:
        return "⏳ WAIT / TOPPY", "#f4cccc" # PINK
    elif rsi < 50 and dist > 0:
        return "👀 WATCH / STALKING", "#fff2cc" # YELLOW
    else:
        return "🚀 MOMENTUM", "#d9d2e9" # PURPLE

# SIDEBAR
st.sidebar.header("Your P&L")
st.sidebar.write("**CELH:** 319 shares @ $51.34")
st.sidebar.write("Live ~$28.4 = **-$7,317**")
st.sidebar.divider()
ticker_input = st.sidebar.text_input("🔍 Search ANY ticker", value="AVGO").upper()

# MAIN TABS
tab1, tab2 = st.tabs(["🔍 Live Ticker Scanner", "📋 My Full Watchlist"])

with tab1:
    ticker = ticker_input.strip()
    if ticker:
        try:
            df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
            if df.empty:
                st.error(f"No data for {ticker}")
            else:
                close = df['Close']
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:,0]
                close = close.dropna()
                live = float(close.iloc[-1])
                sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else live
                sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close)>=50 else live
                rsi = float(calc_rsi(close).iloc[-1])
                dist = (live - sma200)/sma200 if sma200 else 0

                verdict, color = get_verdict(rsi, dist)

                # Card with your palette
                st.markdown(f"<div style='background-color:{color};padding:15px;border-radius:10px'><h2 style='margin:0'>{ticker} - {verdict}</h2></div>", unsafe_allow_html=True)
                st.write("")

                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Live Price", f"${live:.2f}")
                c2.metric("200 SMA Floor", f"${sma200:.2f}", f"{dist*100:+.1f}%")
                c3.metric("50 SMA", f"${sma50:.2f}")
                c4.metric("RSI 14d", f"{rsi:.1f}")

                # Support logic if you have it
                if ticker in SUPPORT_DATA:
                    d = SUPPORT_DATA[ticker]
                    st.info(f"**Your Targets:** T1 ${d['t1']} | T2 (Floor) ${d['t2']} | T3 (Panic) ${d['t3']} — {d['logic']}")
                    needed = (d['t2'] - live)/live*100
                    if needed < 0:
                        st.warning(f"Wait for {needed:.1f}% drop to hit your Floor ${d['t2']}")

                st.line_chart(pd.DataFrame({"Price":close.tail(180), "200 SMA":close.rolling(200).mean().tail(180), "50 SMA":close.rolling(50).mean().tail(180)}))
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.write("Click any ticker to scan - Color = Your Master Palette")
    st.caption("🟩 GREEN #d9ead3 = BUY/STRIKE | 🟨 YELLOW #fff2cc = WATCH | 🟪 PURPLE #d9d2e9 = MOMENTUM | 🟥 PINK #f4cccc = EXPENSIVE/TOPPY | 🔴 ROSE #ea9999 = EXTREME DANGER")

    cols = st.columns(4)
    for i, t in enumerate(WATCHLIST):
        try:
            df = yf.download(t, period="6mo", progress=False, auto_adjust=True)
            close = df['Close']
            if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
            close = close.dropna()
            live = float(close.iloc[-1])
            sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else live
            rsi = float(calc_rsi(close).iloc[-1])
            dist = (live - sma200)/sma200 if sma200 else 0
            verdict, color = get_verdict(rsi, dist)
        except:
            verdict, color, live, rsi, dist = "N/A", "#ffffff", 0, 50, 0

        with cols[i % 4]:
            st.markdown(f"<div style='background:{color};padding:10px;border-radius:8px;margin-bottom:8px'><b>{t}</b> ${live:.1f}<br>{verdict}<br>RSI {rsi:.0f} | {dist*100:+.0f}% to floor</div>", unsafe_allow_html=True)

st.divider()
st.caption("V2 Built from your discord_INVESTINGDASH.xlsx - Targets + Support Logic embedded")
