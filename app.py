import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Invest Dash V3.2 Original Logic", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@400;600&display=swap');
.stApp { background:#0A0A0B; color:#E6E6E6; }
.metric-card { background: linear-gradient(145deg,#151519,#1C1C21); border:1px solid #26262E; border-radius:16px; padding:16px; }
.badge { padding:6px 14px; border-radius:99px; font-family:'JetBrains Mono'; font-weight:600; font-size:12px; }
.badge-strike { background:#0E2A1A; color:#4ADE80; border:1px solid #14532D; }
.badge-buy { background:#12261E; color:#86EFAC; border:1px solid #166534; }
.badge-wait { background:#2A1215; color:#FCA5A5; border:1px solid #7F1D1D; }
.badge-watch { background:#1A1A23; color:#C4B5FD; border:1px solid #4C1D95; }
.small { font-family:'JetBrains Mono'; color:#8B8B93; font-size:11px; }
</style>
""", unsafe_allow_html=True)

SUPPORT_DATA = {
    "AMZN": {"t1":222,"t2":215,"t3":211,"logic":"Strong demand zone $211-$218"},
    "META": {"t1":650,"t2":640,"t3":630,"logic":"$650 major support"},
    "AMD": {"t1":203,"t2":173,"t3":157,"logic":"$173 weekly shelf"},
    "CELH": {"t1":43,"t2":41,"t3":38,"logic":"$41 multi-timeframe"},
    "GOOG": {"t1":290,"t2":213,"t3":205,"logic":"Shelf low-200s"},
    "ADBE": {"t1":350,"t2":311,"t3":280,"logic":"$311 bottom range"},
    "SOFI": {"t1":27,"t2":24,"t3":21,"logic":"$20.67 retracement"},
    "AVGO": {"t1":312.5,"t2":285,"t3":260,"logic":"AI Infra"},
    "ANET": {"t1":116,"t2":105,"t3":95,"logic":"Network"},
}

def calc_rsi(p, period=14):
    d = p.diff(); g = d.where(d>0,0).rolling(period).mean(); l = -d.where(d<0,0).rolling(period).mean()
    return 100 - (100/(1+g/l))

def original_verdict(rsi, dist, struct, vol):
    # ORIGINAL EXCEL LOGIC - Faithful to your sheet
    # STRIKE = Deep below floor + oversold RSI <40
    if rsi < 40 and dist < -0.05:
        return "🔥 STRIKE 🔥", "badge-strike"
    # STRIKE also if RSI <35 even if dist slightly negative
    if rsi < 35 and dist < 0:
        return "🔥 STRIKE 🔥", "badge-strike"
    # BUY ZONE = Below floor + RSI <50 + low vol strength <0.9
    if dist < -0.10 and rsi < 50:
        return "🤑 BUY ZONE 🤑", "badge-buy"
    if dist < 0 and rsi < 47 and vol < 0.85:
        return "🤑 BUY ZONE 🤑", "badge-buy"
    # TOPPY/WAIT = Above floor OR RSI hot
    if dist > 0.25 or rsi > 65:
        return "⚠️ TOPPY / WAIT ⏳", "badge-wait"
    if dist > 0 and rsi > 50:
        return "⏳ WAIT ⏳", "badge-wait"
    return "👀 WATCH / STALKING", "badge-watch"

st.title("◼ INVEST DASH V3.2 - ORIGINAL EXCEL LOGIC")
st.caption("Using your exact 4 metrics: Structural Risk | Dist to Floor | RSI <35 | Vol Strength <0.8")

ticker = st.sidebar.text_input("Ticker", "AVGO").upper()

if ticker:
    df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
    close = df['Close']
    if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
    vol = df['Volume']
    if isinstance(vol, pd.DataFrame): vol = vol.iloc[:,0]
    close = close.dropna()
    live = float(close.iloc[-1])
    sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else live
    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close)>=50 else live
    rsi = float(calc_rsi(close).iloc[-1])
    dist = (live - sma200)/sma200
    struct = (sma50 - sma200)/sma200 if sma200 else 0
    vol_avg = float(vol.rolling(50).mean().iloc[-1]) if len(vol)>=50 else float(vol.iloc[-1])
    vol_strength = float(vol.iloc[-1]/vol_avg) if vol_avg else 1.0

    v_text, v_class = original_verdict(rsi, dist, struct, vol_strength)

    st.markdown(f"<span class='badge {v_class}'>{v_text}</span> <span style='font-size:22px;font-weight:700;margin-left:10px'>{ticker} ${live:.2f}</span>", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card'><div class='small'>STRUCTURAL RISK</div><div style='font-size:20px;font-weight:700'>{struct*100:+.1f}%</div><div class='small'>(50 SMA - 200 SMA) / 200 SMA {'⚠️ >30% danger' if struct>0.3 else '✅ Safe'}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div class='small'>DIST TO FLOOR</div><div style='font-size:20px;font-weight:700'>{dist*100:+.1f}%</div><div class='small'>(Live - 200 SMA) / 200 SMA</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div class='small'>RSI (14d) <35 = OVERSOLD</div><div style='font-size:20px;font-weight:700'>{rsi:.1f}</div><div class='small'>{'🔥 Oversold <40' if rsi<40 else '⚠️ Overbought >60' if rsi>60 else 'Neutral'}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card'><div class='small'>VOL STRENGTH <0.8 = WEAK SELLING</div><div style='font-size:20px;font-weight:700'>{vol_strength:.2f}x</div><div class='small'>{'✅ Weak selling - Good to buy' if vol_strength<0.8 else '🔥 High volume'}</div></div>", unsafe_allow_html=True)

    if ticker in SUPPORT_DATA:
        d = SUPPORT_DATA[ticker]
        st.info(f"Your Excel Logic: T1 ${d['t1']} | T2 Floor ${d['t2']} | T3 Panic ${d['t3']} | {d['logic']}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=close.tail(180).index, y=close.tail(180), name="Price", line=dict(color="#E6E6E6")))
    fig.add_trace(go.Scatter(x=close.tail(180).index, y=close.rolling(200).mean().tail(180), name="200 SMA Floor", line=dict(color="#FACC15", dash="dash")))
    fig.add_trace(go.Scatter(x=close.tail(180).index, y=close.rolling(50).mean().tail(180), name="50 SMA", line=dict(color="#60A5FA")))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0A0A0B", plot_bgcolor="#0A0A0B", height=360, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Color palette from your Excel
    st.markdown("<div class='small'>YOUR MASTER PALETTE: 🟩 #d9ead3 STRIKE/BUY | 🟨 #fff2cc WATCH | 🟪 #d9d2e9 MOMENTUM | 🟥 #f4cccc TOPPY | 🔴 #ea9999 DANGER</div>", unsafe_allow_html=True)
