import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Invest Dash V3 Pro", layout="wide")

# --- LOCKED PALETTE: V3 GREEN ---
BG="#0E0E10"; CARD="#15151A"; ACCENT="#4ADE80"; ACCENT2="#14532D"

st.markdown(f"""
<style>
.stApp {{ background:{BG}; color:#E8E8E8; }}
.card {{ background:{CARD}; border:1px solid #232329; border-radius:16px; padding:16px; margin-bottom:10px; }}
.badge {{ padding:6px 12px; border-radius:99px; font-family:monospace; font-size:11px; font-weight:700; }}
.badge-strike {{ background:#0E2A1A; color:{ACCENT}; border:1px solid {ACCENT2}; }}
.badge-buy {{ background:#12261E; color:#86EFAC; border:1px solid #166534; }}
.badge-toppy {{ background:#2A1215; color:#FCA5A5; border:1px solid #7F1D1D; }}
.badge-watch {{ background:#1A1A23; color:#C4B5FD; border:1px solid #3A3A4A; }}
.small {{ font-family:monospace; color:#8B8B93; font-size:11px; }}
</style>
""", unsafe_allow_html=True)

# Market strip
MARKETS = {{"S&P 500":"^GSPC","DOW":"^DJI","NASDAQ":"^IXIC","VIX":"^VIX"}}
html=f"<div style='background:{CARD};border:1px solid #232329;border-radius:12px;padding:10px 14px;display:flex;gap:22px;overflow-x:auto;margin-bottom:12px'>"
for n,s in MARKETS.items():
    try:
        d=yf.download(s, period="2d", progress=False, auto_adjust=True)
        if not d.empty:
            c=float(d['Close'].iloc[-1]); pc=float(d['Close'].iloc[-2]); ch=(c-pc)/pc*100
            html+=f"<span class='small'>{n} <b style='color:white'>{c:,.0f}</b> <span style='color:{'#4ADE80' if ch>=0 else '#FCA5A5'}'>{ch:+.2f}%</span></span>"
    except: pass
html+="</div>"
st.markdown(html, unsafe_allow_html=True)

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
        return {{"live":live,"sma200":sma200,"rsi":rsi,"dist":dist,"struct":struct,"v":v,"vc":vc,"close":cl}}
    except: return None

strike = sum(1 for s in st.session_state.holdings if (x:=get_safe(s)) and ("STRIKE" in x['v'] or "BUY" in x['v']))

# Aesthetic header above tabs
st.markdown(f"""
<div style='background: radial-gradient(120% 120% at 0% 0%, #1A2E22 0%, {CARD} 60%, {BG} 100%); border:1px solid #232329; border-radius:20px; padding:22px 24px; margin-bottom:16px;'>
    <div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:16px;align-items:center'>
        <div style='display:flex;align-items:center;gap:12px'>
            <div style='width:36px;height:36px;background:{ACCENT};border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;color:{BG};font-size:18px'>$</div>
            <div><div style='font-weight:900;font-size:22px;letter-spacing:-0.5px'>INVEST DASH <span style='color:{ACCENT}'>V3 PRO</span></div><div class='small' style='margin-top:2px'>Structural Risk + Dist to Floor + RSI Holy Grail + T1/T2/T3</div></div>
            <div style='background:#0E2A1A;border:1px solid {ACCENT2};color:{ACCENT};font-family:monospace;font-size:10px;padding:5px 10px;border-radius:99px;margin-left:10px'>LIVE • V3 GREEN</div>
        </div>
        <div style='display:flex;gap:10px'>
            <div style='background:{CARD};border:1px solid #232329;border-radius:12px;padding:10px 14px;text-align:center'><div class='small'>HOLDINGS</div><div style='font-size:18px;font-weight:800'>{len(st.session_state.holdings)}</div></div>
            <div style='background:{CARD};border:1px solid #232329;border-radius:12px;padding:10px 14px;text-align:center'><div class='small'>WATCHLIST</div><div style='font-size:18px;font-weight:800'>{len(st.session_state.watchlist)}</div></div>
            <div style='background:#0E2A1A;border:1px solid {ACCENT2};border-radius:12px;padding:10px 14px;text-align:center'><div class='small' style='color:#86EFAC'>STRIKE</div><div style='font-size:18px;font-weight:800;color:{ACCENT}'>{strike}</div></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Ticker Search (Main)","👀 Watchlist","📊 Portfolio"])

with tab1:
    st.markdown(f"<div class='card'><div class='small'>MAIN PAGE • SEARCH ALL STOCKS</div><div style='font-weight:700'>Type any ticker: AAPL, MSFT, SPY, BTC-USD</div></div>", unsafe_allow_html=True)
    q = st.text_input("Ticker", value="NVDA", placeholder="e.g. AAPL").upper().strip()
    if q:
        d=get_safe(q)
        if d:
            st.markdown(f"<div class='card' style='border-color:{ACCENT}'><div style='display:flex;justify-content:space-between'><b style='font-size:28px'>{q} ${d['live']:.2f}</b><span class='badge {d['vc']}' style='font-size:14px'>{d['v']}</span></div><div style='display:flex;gap:10px;margin-top:12px;flex-wrap:wrap'><div class='card' style='flex:1;margin:0'><div class='small'>DIST TO FLOOR</div><div style='font-size:18px;font-weight:700'>{d['dist']*100:+.1f}%</div></div><div class='card' style='flex:1;margin:0'><div class='small'>STRUCT RISK</div><div style='font-size:18px;font-weight:700'>{d['struct']*100:+.1f}%</div></div><div class='card' style='flex:1;margin:0'><div class='small'>RSI 14</div><div style='font-size:18px;font-weight:700'>{d['rsi']:.1f}</div></div></div><div class='small' style='margin-top:10px'>T1 {d['sma200']*1.05:.2f} • T2 {d['sma200']:.2f} • T3 {d['sma200']*0.92:.2f}</div></div>", unsafe_allow_html=True)
            colA,colB=st.columns(2)
            with colA:
                if st.button(f"➕ Add {q} to Portfolio"): 
                    if q not in st.session_state.holdings: st.session_state.holdings.append(q)
            with colB:
                if st.button(f"➕ Add {q} to Watchlist"):
                    if q not in st.session_state.watchlist: st.session_state.watchlist.append(q)
            fig=go.Figure(); fig.add_trace(go.Scatter(x=d['close'].index, y=d['close'], name=q, line=dict(color=ACCENT, width=2))); fig.add_trace(go.Scatter(x=d['close'].index, y=d['close'].rolling(200).mean(), name="200 SMA Floor", line=dict(dash="dash", color="#555"))); fig.add_trace(go.Scatter(x=d['close'].index, y=d['close'].rolling(50).mean(), name="50 SMA", line=dict(color="#888"))); fig.update_layout(template="plotly_dark", paper_bgcolor=CARD, plot_bgcolor=CARD, height=340, margin=dict(l=0,r=0,t=10,b=0)); st.plotly_chart(fig, use_container_width=True)

    # LEGEND AT BOTTOM OF MAIN PAGE
    st.markdown(f"""
    <div style='background:{CARD};border:1px solid #232329;border-radius:16px;padding:18px;margin-top:20px'>
        <div style='display:flex;align-items:center;gap:8px;margin-bottom:14px'><div style='width:24px;height:24px;background:{ACCENT2};border-radius:6px;display:flex;align-items:center;justify-content:center'>📖</div><div style='font-weight:800'>V3 PRO METRICS LEGEND — WHY IT MATTERS</div></div>
        <div style='display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:12px'>
            <div class='card'><b>🔥 STRIKE / 🤑 BUY / ⚠️ TOPPY</b><br><span class='small'><b>STRIKE = RSI<40 + Dist<-5%</b> = oversold + below floor = highest win rate entry (your Excel). <b>BUY = Dist<-10%</b> deep panic. <b>TOPPY = Dist>+25% or RSI>65</b> = extended, trim not chase.</span></div>
            <div class='card'><b>📍 DIST TO FLOOR</b><br><span class='small'><b>(Live - 200SMA)/200SMA.</b> Floor = institutional defense. -15% = fear = you buy. +30% = euphoria = you wait. Your rule: buy <-10%.</span></div>
            <div class='card'><b>🏗️ STRUCTURAL RISK</b><br><span class='small'><b>(50SMA-200SMA)/200SMA.</b> Positive = uptrend healthy. Negative = breakdown risk. You held winners when >+5%, cut when <-5%.</span></div>
            <div class='card'><b>📊 RSI 14</b><br><span class='small'>Momentum 0-100. <35 = panic exhausted = bounce incoming. >65 = overbought = everyone already bought. Your holy grail.</span></div>
            <div class='card'><b>🎯 T1 / T2 / T3</b><br><span class='small'>T1 5% above floor = start, T2 floor = add, T3 8% below = max fear max size. How you turned $2k dips into $15k winners.</span></div>
            <div class='card' style='border-color:{ACCENT}'><b>💡 HOW TO USE DAILY</b><br><span class='small'>1. Search ticker 2. Check Verdict 3. Check Dist 4. Check RSI 5. Execute T1-T3. Mantra: Buy Low. Sell Never. DCA T1-T3.</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("**👀 Watchlist — Editable**")
    nw=st.text_input("Add ticker to watchlist", key="w").upper().strip()
    if st.button("Add to Watchlist") and nw:
        if nw not in st.session_state.watchlist: st.session_state.watchlist.append(nw); st.rerun()
    for s in st.session_state.watchlist[:]:
        d=get_safe(s); c1,c2=st.columns([5,1])
        with c1:
            if d: st.markdown(f"<div class='card'><b>{s} ${d['live']:.2f}</b> <span class='badge {d['vc']}' style='float:right'>{d['v']}</span><div class='small'>RSI {d['rsi']:.0f} | Dist {d['dist']*100:+.0f}%</div></div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='card'><b>{s}</b> <span class='small'>loading...</span></div>", unsafe_allow_html=True)
        with c2:
            if st.button("🗑️", key=f"dw_{s}"): st.session_state.watchlist.remove(s); st.rerun()

with tab3:
    st.markdown("**📊 Portfolio — Last Tab**")
    np=st.text_input("Add ticker to portfolio", key="p").upper().strip()
    if st.button("Add to Portfolio") and np:
        if np not in st.session_state.holdings: st.session_state.holdings.append(np); st.rerun()
    for s in st.session_state.holdings[:]:
        d=get_safe(s); c1,c2=st.columns([5,1])
        with c1:
            if d: st.markdown(f"<div class='card'><b>{s} ${d['live']:.2f}</b> <span class='badge {d['vc']}' style='float:right'>{d['v']}</span><div class='small'>Dist {d['dist']*100:+.1f}% | RSI {d['rsi']:.0f} | Floor ${d['sma200']:.0f}</div></div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='card'><b>{s}</b></div>", unsafe_allow_html=True)
        with c2:
            if st.button("🗑️", key=f"dp_{s}"): st.session_state.holdings.remove(s); st.rerun()
