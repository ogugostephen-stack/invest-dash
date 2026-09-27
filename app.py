import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Invest Dash V3 Pro", page_icon="◼", layout="wide")

# --- DARK PRO THEME CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0A0A0B; color: #E6E6E6; }
h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 700; letter-spacing: -0.02em; }
.metric-card {
  background: linear-gradient(145deg, #151519, #1C1C21);
  border: 1px solid #26262E;
  border-radius: 16px; padding: 18px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  transition: transform 0.2s ease, border 0.2s ease;
}
.metric-card:hover { transform: translateY(-2px); border-color: #3A3A44; }
.badge {
  display:inline-block; padding: 6px 14px; border-radius: 99px;
  font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 12px;
  letter-spacing: 0.05em; text-transform: uppercase;
}
.badge-strike { background: #0E2A1A; color: #4ADE80; border: 1px solid #14532D; box-shadow: 0 0 20px rgba(74,222,128,0.2); }
.badge-buy { background: #12261E; color: #86EFAC; border: 1px solid #166534; }
.badge-toppy { background: #2A1215; color: #FCA5A5; border: 1px solid #7F1D1D; box-shadow: 0 0 20px rgba(248,113,113,0.25); }
.badge-wait { background: #261E12; color: #FDE68A; border: 1px solid #92400E; }
.badge-watch { background: #1A1A23; color: #C4B5FD; border: 1px solid #4C1D95; }
.badge-momo { background: #1E1B2E; color: #A5B4FC; border: 1px solid #3730A3; }
.small { font-family: 'JetBrains Mono', monospace; color: #8B8B93; font-size: 12px; }
.live-dot { height:8px; width:8px; background:#22C55E; border-radius:50%; display:inline-block; box-shadow:0 0 10px #22C55E; animation: pulse 2s infinite; }
@keyframes pulse { 0% {opacity:1} 50% {opacity:0.5} 100% {opacity:1} }
</style>
""", unsafe_allow_html=True)

SUPPORT_DATA = {
    "AMZN": {"t1":222,"t2":215,"t3":211,"logic":"Strong demand zone $211-$218"},
    "META": {"t1":650,"t2":640,"t3":630,"logic":"$650 major horizontal support"},
    "AMD": {"t1":203,"t2":173,"t3":157,"logic":"$173 highest-value weekly shelf"},
    "CELH": {"t1":43,"t2":41,"t3":38,"logic":"$41 multi-timeframe support"},
    "GOOG": {"t1":290,"t2":213,"t3":205,"logic":"Structural shelf low-200s"},
    "CRM": {"t1":258,"t2":252,"t3":221,"logic":"$221 52-week low floor"},
    "ADBE": {"t1":350,"t2":311,"t3":280,"logic":"$311 bottom of range"},
    "SOFI": {"t1":27,"t2":24,"t3":21,"logic":"$20.67 major retracement"},
    "ELF": {"t1":75,"t2":69,"t3":65,"logic":"Falling trend $69 key"},
    "SHOP": {"t1":160,"t2":153,"t3":141,"logic":"$153 61.8% Fib"},
    "NVO": {"t1":50,"t2":48,"t3":45,"logic":"Falling channel $45 floor"},
    "HIMS": {"t1":33,"t2":28,"t3":25,"logic":"High vol, 200 SMA broken"},
    "JMIA": {"t1":11,"t2":10,"t3":6.8,"logic":"Bubble reset sub-$7"},
    "CAKE": {"t1":50,"t2":48,"t3":45,"logic":"Already under 200 SMA"},
    "AVGO": {"t1":312.5,"t2":285,"t3":260,"logic":"AI Infra leader"},
    "ANET": {"t1":116,"t2":105,"t3":95,"logic":"Network - rich but strong"},
    "ETN": {"t1":295,"t2":260,"t3":240,"logic":"Power electrification"},
    "VRT": {"t1":139,"t2":120,"t3":100,"logic":"Data center cooling"},
}

def calc_rsi(prices, p=14):
    d = prices.diff()
    g = d.where(d>0,0).rolling(p).mean()
    l = -d.where(d<0,0).rolling(p).mean()
    return 100 - (100/(1+g/l))

def verdict_logic(rsi, dist):
    if rsi < 35 and dist < -0.05:
        return "STRIKE", "badge-strike", "🔥"
    if rsi < 45 and dist < 0:
        return "BUY ZONE", "badge-buy", "🤑"
    if rsi > 60 and dist > 0.25:
        return "TOPPY - DON'T CHASE", "badge-toppy", "⚠️"
    if rsi > 58:
        return "WAIT / TOPPY", "badge-wait", "⏳"
    if rsi < 52:
        return "WATCH / STALKING", "badge-watch", "👀"
    return "MOMENTUM", "badge-momo", "🚀"

# HEADER
st.markdown("<div style='display:flex;align-items:center;gap:12px'><div class='live-dot'></div><span class='small'>LIVE • DARK PRO TERMINAL • V3</span></div><h1 style='margin-top:8px'>INVEST DASH <span style='color:#8B8B93;font-weight:300'>V3 PRO</span></h1>", unsafe_allow_html=True)

# SIDEBAR P&L
with st.sidebar:
    st.markdown("### ◼ Portfolio")
    st.markdown("<span class='small'>CELH • 319 shares @ $51.34</span>", unsafe_allow_html=True)
    shares = st.number_input("Shares", value=319)
    buy = st.number_input("Avg Buy", value=51.34)
    st.divider()
    t_search = st.text_input("Search ticker", value="AVGO").upper()

# MAIN
col_main, col_side = st.columns([3,1])

with col_main:
    ticker = t_search.strip()
    if ticker:
        df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
        close = df['Close']
        if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
        close = close.dropna()
        live = float(close.iloc[-1])
        sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else live
        sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close)>=50 else live
        rsi = float(calc_rsi(close).iloc[-1])
        dist = (live - sma200)/sma200 if sma200 else 0
        v_text, v_class, v_icon = verdict_logic(rsi, dist)

        st.markdown(f"<div style='margin:16px 0'><span class='badge {v_class}'>{v_icon} {v_text}</span> <span style='margin-left:12px;font-family:JetBrains Mono;font-size:22px;font-weight:600'>{ticker} ${live:.2f}</span></div>", unsafe_allow_html=True)

        m1,m2,m3,m4 = st.columns(4)
        with m1: st.markdown(f"<div class='metric-card'><div class='small'>LIVE PRICE</div><div style='font-size:22px;font-weight:700'>${live:.2f}</div><div class='small'>{ticker}</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><div class='small'>200 SMA FLOOR</div><div style='font-size:22px;font-weight:700'>${sma200:.2f}</div><div class='small' style='color:{'#4ADE80' if dist<0 else '#FCA5A5'}'>{dist*100:+.1f}% to floor</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><div class='small'>50 SMA</div><div style='font-size:22px;font-weight:700'>${sma50:.2f}</div></div>", unsafe_allow_html=True)
        with m4: st.markdown(f"<div class='metric-card'><div class='small'>RSI 14D</div><div style='font-size:22px;font-weight:700'>{rsi:.1f}</div><div class='small'>{ 'Oversold' if rsi<40 else 'Overbought' if rsi>65 else 'Neutral'}</div></div>", unsafe_allow_html=True)

        if ticker in SUPPORT_DATA:
            d = SUPPORT_DATA[ticker]
            drop_needed = (d['t2']-live)/live*100
            st.markdown(f"<div class='metric-card' style='margin-top:16px'><div class='small'>YOUR LEVELS • {d['logic']}</div><div style='display:flex;gap:20px;margin-top:8px'><div><span class='small'>T1 TARGET</span><br><b>${d['t1']}</b></div><div><span class='small'>T2 FLOOR</span><br><b>${d['t2']}</b></div><div><span class='small'>T3 PANIC</span><br><b>${d['t3']}</b></div><div><span class='small'>NEEDED</span><br><b style='color:#FCA5A5'>{drop_needed:+.1f}%</b></div></div></div>", unsafe_allow_html=True)

        # Fancy Plotly dark chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=close.tail(180).index, y=close.tail(180), name="Price", line=dict(color="#E6E6E6", width=2)))
        fig.add_trace(go.Scatter(x=close.tail(180).index, y=close.rolling(200).mean().tail(180), name="200 SMA", line=dict(color="#FACC15", width=1, dash="dash")))
        fig.add_trace(go.Scatter(x=close.tail(180).index, y=close.rolling(50).mean().tail(180), name="50 SMA", line=dict(color="#60A5FA", width=1)))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0A0A0B", plot_bgcolor="#0A0A0B", height=380, margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h", y=1.1), font=dict(family="JetBrains Mono"))
        st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.markdown("<div class='small' style='margin-bottom:10px'>WATCHLIST • LIVE SCAN</div>", unsafe_allow_html=True)
    for t in SUPPORT_DATA.keys():
        try:
            dft = yf.download(t, period="3mo", progress=False, auto_adjust=True)
            cl = dft['Close']
            if isinstance(cl, pd.DataFrame): cl = cl.iloc[:,0]
            cl = cl.dropna()
            lv = float(cl.iloc[-1])
            s200 = float(cl.rolling(200).mean().iloc[-1]) if len(cl)>=200 else lv
            r = float(calc_rsi(cl).iloc[-1])
            distt = (lv-s200)/s200 if s200 else 0
            vt, vc, vi = verdict_logic(r, distt)
            color_dot = "#4ADE80" if "STRIKE" in vt or "BUY" in vt else "#FCA5A5" if "TOPPY" in vt else "#8B8B93"
            st.markdown(f"<div class='metric-card' style='padding:12px;margin-bottom:10px'><div style='display:flex;justify-content:space-between'><b>{t}</b><span class='badge {vc}' style='font-size:10px;padding:3px 8px'>{vt}</span></div><div style='display:flex;justify-content:space-between;margin-top:6px'><span style='font-family:JetBrains Mono'>${lv:.1f}</span><span class='small' style='color:{color_dot}'>{distt*100:+.0f}% • RSI {r:.0f}</span></div></div>", unsafe_allow_html=True)
        except:
            pass
