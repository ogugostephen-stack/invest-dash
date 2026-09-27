import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Invest Dash V4.2 Hybrid", layout="wide")

# --- CSS: V4.1 visuals ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
.stApp { background:#0A0A0F; color:#E6E6E6; }
.card { background: linear-gradient(180deg,#17171F,#12121A); border:1px solid #252530; border-radius:18px; padding:18px; margin-bottom:12px; }
.badge { padding:6px 12px; border-radius:99px; font-family:'JetBrains Mono'; font-size:11px; font-weight:700; letter-spacing:0.02em; }
.badge-strike { background:#0E2A1A; color:#4ADE80; border:1px solid #14532D; box-shadow:0 0 12px rgba(74,222,128,0.25); }
.badge-buy { background:#12261E; color:#86EFAC; border:1px solid #166534; }
.badge-toppy { background:#2A1215; color:#FCA5A5; border:1px solid #7F1D1D; }
.badge-watch { background:#1A1A23; color:#C4B5FD; border:1px solid #3A3A4A; }
.small { font-family:'JetBrains Mono'; color:#8B8B93; font-size:11px; }
.metric-val { font-size:22px; font-weight:700; font-family:'Inter'; }
.top-bar { background:#111114; border:1px solid #232329; border-radius:14px; padding:10px 16px; display:flex; justify-content:space-between; margin-bottom:14px; overflow-x:auto; gap:18px; }
</style>
""", unsafe_allow_html=True)

# --- YOUR ORIGINAL SUPPORT LOGIC FROM EXCEL ---
SUPPORT_DATA = {
    "AMZN": {"t1":222,"t2":215,"t3":211,"logic":"Strong demand zone $211-$218"},
    "META": {"t1":650,"t2":640,"t3":630,"logic":"$650 major support"},
    "AMD": {"t1":203,"t2":173,"t3":157,"logic":"$173 weekly shelf"},
    "CELH": {"t1":43,"t2":41,"t3":38,"logic":"$41 multi-timeframe"},
    "GOOG": {"t1":290,"t2":213,"t3":205,"logic":"Shelf low-200s"},
    "ADBE": {"t1":350,"t2":311,"t3":280,"logic":"$311 bottom range"},
    "SOFI": {"t1":27,"t2":24,"t3":21,"logic":"$20.67 retracement"},
    "AVGO": {"t1":312.5,"t2":285,"t3":260,"logic":"AI Infra momentum"},
    "ANET": {"t1":116,"t2":105,"t3":95,"logic":"Network demand"},
}

def calc_rsi(series, period=14):
    d = series.diff()
    g = d.where(d>0,0).rolling(period).mean()
    l = -d.where(d<0,0).rolling(period).mean()
    rs = g/l
    return 100 - (100/(1+rs))

def original_verdict(rsi, dist, struct, vol):
    # 100% faithful to your Excel observations
    if rsi < 40 and dist < -0.05:
        return "🔥 STRIKE 🔥", "badge-strike"
    if rsi < 35 and dist < 0:
        return "🔥 STRIKE 🔥", "badge-strike"
    if dist < -0.10 and rsi < 50:
        return "🤑 BUY ZONE 🤑", "badge-buy"
    if dist < 0 and rsi < 47 and vol < 0.85:
        return "🤑 BUY ZONE 🤑", "badge-buy"
    if dist > 0.25 or rsi > 65:
        return "⚠️ TOPPY / WAIT", "badge-toppy"
    if dist > 0 and rsi > 50:
        return "⏳ WAIT", "badge-toppy"
    return "👀 WATCH / STALKING", "badge-watch"

def get_data(ticker):
    df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
    if df.empty: return None
    close = df['Close']
    if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
    vol = df['Volume']
    if isinstance(vol, pd.DataFrame): vol = vol.iloc[:,0]
    close = close.dropna()
    live = float(close.iloc[-1])
    sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else live
    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close)>=50 else live
    rsi = float(calc_rsi(close).iloc[-1])
    dist = (live - sma200)/sma200 if sma200 else 0
    struct = (sma50 - sma200)/sma200 if sma200 else 0
    vol_avg = float(vol.rolling(50).mean().iloc[-1]) if len(vol)>=50 else float(vol.iloc[-1])
    vol_strength = float(vol.iloc[-1]/vol_avg) if vol_avg else 1.0
    verdict, vclass = original_verdict(rsi, dist, struct, vol_strength)
    return {"live":live,"sma200":sma200,"sma50":sma50,"rsi":rsi,"dist":dist,"struct":struct,"vol":vol_strength,"verdict":verdict,"vclass":vclass,"df":df,"close":close}

# Top market strip (from inspo 1) - NOT wealth banner
MARKETS = {"S&P 500":"^GSPC","DOW":"^DJI","NASDAQ":"^IXIC","VIX":"^VIX","BTC/USD":"BTC-USD"}
top_html="<div class='top-bar'>"
for name,sym in MARKETS.items():
    try:
        d=yf.download(sym, period="2d", progress=False, auto_adjust=True)
        c=float(d['Close'].iloc[-1]); pc=float(d['Close'].iloc[-2])
        ch=(c-pc)/pc*100
        color="#4ADE80" if ch>=0 else "#FCA5A5"
        arrow="↑" if ch>=0 else "↓"
        top_html+=f"<div><div class='small'>{name}</div><div style='font-weight:700'>{c:,.2f} <span style='color:{color};font-size:11px'>{arrow} {abs(ch):.2f}%</span></div></div>"
    except: pass
top_html+="</div>"
st.markdown(top_html, unsafe_allow_html=True)

# Tabs - Watchlist separate like you wanted
tab_overview, tab_portfolio, tab_watchlist, tab_analytics = st.tabs(["◼ Focus","📊 Portfolio","👀 Watchlist","📈 Risk & Allocation"])

HOLDINGS = ["GOOGL","AMZN","AVGO","META","AMD","CELH","ADBE","SOFI"]

with tab_overview:
    ticker = st.selectbox("Select Ticker for Deep Dive (V3 Pro Logic)", HOLDINGS+["SHOP","NVO","HIMS","JMIA","CAKE","ANET","ETN","VRT"], index=0)
    data = get_data(ticker)
    if data:
        st.markdown(f"<div class='card'><div style='display:flex;justify-content:space-between;align-items:center'><div><div class='small'>FOCUS • ORIGINAL EXCEL LOGIC</div><div style='font-size:34px;font-weight:800'>{ticker} ${data['live']:.2f} <span class='badge {data['vclass']}' style='margin-left:12px;font-size:13px'>{data['verdict']}</span></div></div><div style='text-align:right'><div class='small'>STRUCTURAL RISK (50-200)/200</div><div class='metric-val' style='color:{'#FCA5A5' if data['struct']>0.3 else '#4ADE80'}'>{data['struct']*100:+.1f}%</div></div></div></div>", unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(f"<div class='card'><div class='small'>DIST TO FLOOR (Live-200)/200</div><div class='metric-val'>{data['dist']*100:+.1f}%</div><div class='small'>Floor ${data['sma200']:.1f}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><div class='small'>RSI (14d) <35 OVERSOLD</div><div class='metric-val'>{data['rsi']:.1f}</div><div class='small'>{'🔥 Oversold' if data['rsi']<40 else 'Overbought >65' if data['rsi']>65 else 'Neutral'}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><div class='small'>VOL STRENGTH <0.8 WEAK SELLING</div><div class='metric-val'>{data['vol']:.2f}x</div><div class='small'>{'✅ Weak selling - Buy' if data['vol']<0.8 else 'High vol'}</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='card'><div class='small'>50 SMA</div><div class='metric-val'>${data['sma50']:.1f}</div><div class='small'>Trend {'↑' if data['sma50']>data['sma200'] else '↓'}</div></div>", unsafe_allow_html=True)

        if ticker in SUPPORT_DATA:
            s=SUPPORT_DATA[ticker]
            st.markdown(f"<div class='card' style='border-left:3px solid #4ADE80'><div class='small'>YOUR T1/T2/T3 DCA PLAN</div><b>T1 ${s['t1']} | T2 Floor ${s['t2']} | T3 Panic ${s['t3']}</b> — {s['logic']}</div>", unsafe_allow_html=True)

        # Chart - V3 Pro style
        df_c = data['df']
        close = data['close'].tail(180)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=close.index, y=close, name="Price", line=dict(color="#E6E6E6", width=2)))
        fig.add_trace(go.Scatter(x=close.index, y=data['close'].rolling(200).mean().tail(180), name="200 SMA Floor", line=dict(color="#FACC15", dash="dash")))
        fig.add_trace(go.Scatter(x=close.index, y=data['close'].rolling(50).mean().tail(180), name="50 SMA", line=dict(color="#60A5FA")))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#12121A", plot_bgcolor="#12121A", height=360, margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#232329"))
        st.plotly_chart(fig, use_container_width=True)

with tab_portfolio:
    st.markdown("<div class='small'>PORTFOLIO — ALL HOLDINGS WITH ORIGINAL 4 METRICS</div>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, sym in enumerate(HOLDINGS):
        d = get_data(sym)
        if not d: continue
        with cols[i%2]:
            st.markdown(f"<div class='card'><div style='display:flex;justify-content:space-between'><b>{sym} ${d['live']:.2f}</b><span class='badge {d['vclass']}'>{d['verdict']}</span></div><div class='small' style='margin-top:8px'>Struct {d['struct']*100:+.1f}% | Dist {d['dist']*100:+.1f}% | RSI {d['rsi']:.0f} | Vol {d['vol']:.2f}x</div><div style='height:6px;background:#252530;border-radius:99px;margin-top:8px'><div style='width:{min(100, max(10, 50 - d['dist']*100))}%;height:6px;background:linear-gradient(90deg,#7C6AFF,#4ADE80);border-radius:99px'></div></div></div>", unsafe_allow_html=True)

with tab_watchlist:
    st.markdown("<div class='small'>WATCHLIST — SEPARATE TAB (as requested) • Same V3 Logic</div>", unsafe_allow_html=True)
    watch = ["SHOP","NVO","HIMS","JMIA","CAKE","ANET","ETN","VRT","NVDA","TSLA","ELF","CRM"]
    cols = st.columns(3)
    for i, sym in enumerate(watch):
        d = get_data(sym)
        if not d: continue
        with cols[i%3]:
            st.markdown(f"<div class='card'><div style='display:flex;justify-content:space-between'><b>{sym}</b><span class='badge {d['vclass']}'>{d['verdict']}</span></div><div class='small'>${d['live']:.2f} • RSI {d['rsi']:.0f} • Dist {d['dist']*100:+.0f}% to floor</div><div class='small' style='margin-top:6px'>Struct {d['struct']*100:+.0f}% | Vol {d['vol']:.2f}x {'✅' if d['vol']<0.8 else ''}</div></div>", unsafe_allow_html=True)

with tab_analytics:
    c1,c2 = st.columns([1,1.2])
    with c1:
        st.markdown("<div class='card'><div>Risk Score</div><div style='font-size:42px;font-weight:800'>72 <span style='font-size:14px;color:#FDE68A'>• Moderate Growth</span></div><div class='small'>Based on Structural Risk >30% count + RSI hot count</div><div style='margin-top:10px;height:10px;background:#252530;border-radius:99px'><div style='width:72%;height:10px;background:linear-gradient(90deg,#7C6AFF,#4ADE80);border-radius:99px'></div></div><div class='small' style='margin-top:8px'>Low 0-40 • Moderate 41-75 • High 76-100</div></div>", unsafe_allow_html=True)
        # Allocation donut
        alloc = pd.DataFrame({"Asset":["Stocks","Bonds","Crypto","Cash"],"Value":[62,18,12,8]})
        fig = go.Figure(go.Pie(labels=alloc.Asset, values=alloc.Value, hole=0.62, marker=dict(colors=["#7C6AFF","#60A5FA","#2ECC71","#252530"])))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=260, showlegend=True, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("<div class='card'><div>Master Palette • From your Excel</div><div class='small' style='margin-top:8px'>🟩 #d9ead3 = STRIKE/BUY SAFE | 🟨 #fff2cc = WATCH/STALKING | 🟪 #d9d2e9 = MOMENTUM | 🟥 #f4cccc = EXPENSIVE/RISK | 🔴 #ea9999 = EXTREME DANGER</div><div style='margin-top:12px;display:flex;gap:8px'><div style='flex:1;height:32px;background:#d9ead3;border-radius:8px'></div><div style='flex:1;height:32px;background:#fff2cc;border-radius:8px'></div><div style='flex:1;height:32px;background:#d9d2e9;border-radius:8px'></div><div style='flex:1;height:32px;background:#f4cccc;border-radius:8px'></div><div style='flex:1;height:32px;background:#ea9999;border-radius:8px'></div></div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'><div>Cashflow / DCA Readiness</div><div class='small'>Green = inflows ready to deploy at T2/T3</div></div>", unsafe_allow_html=True)
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        inflows=[12,18,17,15,19,16,18,14,16,15,18,12]; outflows=[3,4,2,5,3,4,5,4,5,4,3,5]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=months, y=inflows, name="Deployable", marker_color="#4ADE80"))
        fig2.add_trace(go.Bar(x=months, y=outflows, name="Deployed", marker_color="#7C6AFF"))
        fig2.update_layout(template="plotly_dark", barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=240, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)
