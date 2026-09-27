import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Invest Dash V3 Pro", layout="wide")

if "palette" not in st.session_state:
    st.session_state.palette = "V3 Green"

PALETTES = {
    "V3 Green": {"bg":"#0E0E10","card":"#15151A","accent":"#4ADE80","accent2":"#14532D"},
    "Cyber Purple": {"bg":"#0F0E14","card":"#1A1826","accent":"#A78BFA","accent2":"#4C1D95"},
    "Bloomberg Orange": {"bg":"#0E0E0E","card":"#1A1A1A","accent":"#FB923C","accent2":"#7C2D12"},
    "Midnight Blue": {"bg":"#0A0E16","card":"#121A2A","accent":"#60A5FA","accent2":"#1E3A8A"},
    "Monochrome": {"bg":"#0A0A0A","card":"#171717","accent":"#E5E5E5","accent2":"#404040"},
}
P = PALETTES[st.session_state.palette]

st.markdown(f"""
<style>
.stApp {{ background:{P['bg']}; color:#E8E8E8; }}
.card {{ background:{P['card']}; border:1px solid #232329; border-radius:16px; padding:16px; margin-bottom:10px; }}
.badge {{ padding:6px 12px; border-radius:99px; font-family:monospace; font-size:11px; font-weight:700; }}
.badge-strike {{ background:{P['accent2']}; color:{P['accent']}; border:1px solid {P['accent']}; }}
.badge-buy {{ background:#12261E; color:#86EFAC; border:1px solid #166534; }}
.badge-toppy {{ background:#2A1215; color:#FCA5A5; border:1px solid #7F1D1D; }}
.badge-watch {{ background:#1A1A23; color:#C4B5FD; border:1px solid #3A3A4A; }}
.small {{ font-family:monospace; color:#8B8B93; font-size:11px; }}
</style>
""", unsafe_allow_html=True)

# --- PALETTE SELECTOR + MARKETS (THIS IS THE TOP) ---
col_sel, col_m = st.columns([1,3])
with col_sel:
    sel = st.selectbox("🎨 Palette", list(PALETTES.keys()), index=list(PALETTES.keys()).index(st.session_state.palette))
    if sel != st.session_state.palette:
        st.session_state.palette = sel
        st.rerun()
with col_m:
    MARKETS = {"S&P 500":"^GSPC","DOW":"^DJI","NASDAQ":"^IXIC","VIX":"^VIX"}
    h = f"<div style='background:{P['card']};border:1px solid #232329;border-radius:12px;padding:10px 14px;display:flex;gap:20px;overflow-x:auto'>"
    for n,s in MARKETS.items():
        try:
            d=yf.download(s, period="2d", progress=False, auto_adjust=True)
            if not d.empty:
                c=float(d['Close'].iloc[-1]); pc=float(d['Close'].iloc[-2]); ch=(c-pc)/pc*100
                h+=f"<span class='small'>{n} <b style='color:white'>{c:,.0f}</b> <span style='color:{'#4ADE80' if ch>=0 else '#FCA5A5'}'>{ch:+.2f}%</span></span>"
        except: pass
    h+="</div>"
    st.markdown(h, unsafe_allow_html=True)

if "holdings" not in st.session_state:
    st.session_state.holdings = ["GOOGL","AMZN","AVGO","META","AMD","CELH","ADBE","SOFI"]
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["SHOP","NVO","HIMS","JMIA","CAKE","ANET","ETN","VRT","NVDA","TSLA"]

def get_safe(t):
    try:
        df=yf.download(t, period="1y", progress=False, auto_adjust=True)
        if df.empty: return None
        cl=df['Close']
        if isinstance(cl, pd.DataFrame): cl=cl.iloc[:,0]
        cl=cl.dropna()
        if len(cl)<60: return None
        live=float(cl.iloc[-1]); sma200=float(cl.rolling(200).mean().iloc[-1]) if len(cl)>=200 else float(cl.mean()); sma50=float(cl.rolling(50).mean().iloc[-1])
        d=cl.diff(); g=d.where(d>0,0).rolling(14).mean(); l=-d.where(d<0,0).rolling(14).mean(); r=100-(100/(1+g/l)); rsi=float(r.iloc[-1])
        dist=(live-sma200)/sma200; struct=(sma50-sma200)/sma200
        if rsi<40 and dist<-0.05: v,vc="🔥 STRIKE","badge-strike"
        elif dist<-0.10 and rsi<50: v,vc="🤑 BUY ZONE","badge-buy"
        elif dist>0.25 or rsi>65: v,vc="⚠️ TOPPY","badge-toppy"
        elif dist>0: v,vc="⏳ WAIT","badge-toppy"
        else: v,vc="👀 WATCH","badge-watch"
        return {"live":live,"sma200":sma200,"rsi":rsi,"dist":dist,"struct":struct,"v":v,"vc":vc,"close":cl}
    except: return None

strike = sum(1 for s in st.session_state.holdings if (x:=get_safe(s)) and ("STRIKE" in x['v'] or "BUY" in x['v']))

st.markdown(f"""
<div style='background: radial-gradient(120% 120% at 0% 0%, {P['accent2']}66 0%, {P['card']} 60%); border:1px solid #232329; border-radius:20px; padding:20px; margin:14px 0;'>
<b style='font-size:20px'>INVEST DASH <span style='color:{P['accent']}'>V3 PRO</span> • {sel.upper()}</b> <span class='small'>• {len(st.session_state.holdings)} Holdings • {len(st.session_state.watchlist)} Watchlist • {strike} STRIKE</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Ticker Search (Main)","👀 Watchlist","📊 Portfolio"])

with tab1:
    q = st.text_input("Search ticker", value="NVDA").upper().strip()
    if q:
        d=get_safe(q)
        if d:
            st.markdown(f"<div class='card' style='border-color:{P['accent']}'><b style='font-size:26px'>{q} ${d['live']:.2f}</b> <span class='badge {d['vc']}' style='float:right'>{d['v']}</span><div style='display:flex;gap:8px;margin-top:10px'><div class='card' style='flex:1;margin:0'><div class='small'>DIST</div><b>{d['dist']*100:+.1f}%</b></div><div class='card' style='flex:1;margin:0'><div class='small'>STRUCT</div><b>{d['struct']*100:+.1f}%</b></div><div class='card' style='flex:1;margin:0'><div class='small'>RSI</div><b>{d['rsi']:.0f}</b></div></div></div>", unsafe_allow_html=True)
            fig=go.Figure(); fig.add_trace(go.Scatter(x=d['close'].index, y=d['close'], line=dict(color=P['accent']))); fig.add_trace(go.Scatter(x=d['close'].index, y=d['close'].rolling(200).mean(), line=dict(dash="dash"))); fig.update_layout(template="plotly_dark", paper_bgcolor=P['card'], plot_bgcolor=P['card'], height=300, margin=dict(l=0,r=0,t=0,b=0)); st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='card'><b>📖 LEGEND</b><br><span class='small'>STRIKE = RSI<40 + Dist<-5% = best buy • BUY = Dist<-10% deep panic • TOPPY = Dist>+25% or RSI>65 = trim • DIST = (Live-200SMA)/200SMA = distance to floor • STRUCT = (50SMA-200SMA)/200SMA = trend health • RSI 14 = <35 oversold bounce, >65 overbought • T1 5% above floor, T2 floor, T3 8% below floor = DCA plan</span></div>", unsafe_allow_html=True)

with tab2:
    nw=st.text_input("Add to watchlist", key="w2").upper()
    if st.button("Add to Watchlist") and nw:
        if nw not in st.session_state.watchlist: st.session_state.watchlist.append(nw); st.rerun()
    for s in st.session_state.watchlist[:]:
        d=get_safe(s); c1,c2=st.columns([5,1])
        with c1: st.markdown(f"<div class='card'><b>{s} {f'${d['live']:.2f}' if d else ''}</b> <span class='badge {d['vc']}' style='float:right'>{d['v'] if d else ''}</span></div>", unsafe_allow_html=True)
        with c2:
            if st.button("🗑️", key=f"dw{s}"): st.session_state.watchlist.remove(s); st.rerun()

with tab3:
    np=st.text_input("Add to portfolio", key="p2").upper()
    if st.button("Add to Portfolio") and np:
        if np not in st.session_state.holdings: st.session_state.holdings.append(np); st.rerun()
    for s in st.session_state.holdings[:]:
        d=get_safe(s); c1,c2=st.columns([5,1])
        with c1: st.markdown(f"<div class='card'><b>{s} {f'${d['live']:.2f}' if d else ''}</b> <span class='badge {d['vc']}' style='float:right'>{d['v'] if d else ''}</span></div>", unsafe_allow_html=True)
        with c2:
            if st.button("🗑️", key=f"dp{s}"): st.session_state.holdings.remove(s); st.rerun()
