import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Invest Dash V3 Pro", layout="wide")

# --- CSS ---
st.markdown("""
<style>
.stApp { background:#0E0E10; color:#E8E8E8; }
.card { background:#15151A; border:1px solid #232329; border-radius:16px; padding:16px; margin-bottom:10px; }
.badge { padding:6px 12px; border-radius:99px; font-family:monospace; font-size:11px; font-weight:700; }
.badge-strike { background:#0E2A1A; color:#4ADE80; border:1px solid #14532D; }
.badge-buy { background:#12261E; color:#86EFAC; border:1px solid #166534; }
.badge-toppy { background:#2A1215; color:#FCA5A5; border:1px solid #7F1D1D; }
.badge-watch { background:#1A1A23; color:#C4B5FD; border:1px solid #3A3A4A; }
.small { font-family:monospace; color:#8B8B93; font-size:11px; }
</style>
""", unsafe_allow_html=True)

# --- Top strip ---
MARKETS = {"S&P 500":"^GSPC","DOW":"^DJI","NASDAQ":"^IXIC","VIX":"^VIX"}
html="<div style='background:#111114;border:1px solid #232329;border-radius:12px;padding:8px 14px;display:flex;gap:20px;margin-bottom:14px;overflow-x:auto'>"
for n,s in MARKETS.items():
    try:
        d=yf.download(s, period="2d", progress=False, auto_adjust=True)
        if not d.empty:
            c=float(d['Close'].iloc[-1]); pc=float(d['Close'].iloc[-2]); ch=(c-pc)/pc*100
            html+=f"<span class='small'>{n} <b style='color:#E8E8E8'>{c:,.1f}</b> <span style='color:{'#4ADE80' if ch>=0 else '#FCA5A5'}'>{'↑' if ch>=0 else '↓'}{abs(ch):.2f}%</span></span>"
    except: pass
html+="</div>"
st.markdown(html, unsafe_allow_html=True)

# --- State for editable lists ---
if "holdings" not in st.session_state:
    st.session_state.holdings = ["GOOGL","AMZN","AVGO","META","AMD","CELH","ADBE","SOFI"]
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["SHOP","NVO","HIMS","JMIA","CAKE","ANET","ETN","VRT","NVDA","TSLA"]

SUPPORT_DATA = {
    "AMZN": {"t1":222,"t2":215,"t3":211,"logic":"Strong demand $211-$218"},
    "META": {"t1":650,"t2":640,"t3":630,"logic":"$650 support"},
    "AMD": {"t1":203,"t2":173,"t3":157,"logic":"$173 weekly shelf"},
    "CELH": {"t1":43,"t2":41,"t3":38,"logic":"$41 multi-TF"},
    "GOOGL": {"t1":290,"t2":213,"t3":205,"logic":"Shelf low-200s"},
    "ADBE": {"t1":350,"t2":311,"t3":280,"logic":"$311 bottom"},
    "SOFI": {"t1":27,"t2":24,"t3":21,"logic":"$20.67 retracement"},
}

def get_safe(ticker):
    try:
        df=yf.download(ticker, period="1y", progress=False, auto_adjust=True)
        if df.empty: return None
        close=df['Close']
        if isinstance(close, pd.DataFrame): close=close.iloc[:,0]
        close=close.dropna()
        if len(close)<60: return None
        live=float(close.iloc[-1])
        sma200=float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else float(close.mean())
        sma50=float(close.rolling(50).mean().iloc[-1])
        delta=close.diff()
        gain=delta.where(delta>0,0).rolling(14).mean()
        loss=-delta.where(delta<0,0).rolling(14).mean()
        rsi=100-(100/(1+gain/loss))
        rsi_val=float(rsi.iloc[-1])
        dist=(live-sma200)/sma200 if sma200!=0 else 0
        struct=(sma50-sma200)/sma200 if sma200!=0 else 0
        if rsi_val<40 and dist<-0.05: v,vc="🔥 STRIKE","badge-strike"
        elif dist<-0.10 and rsi_val<50: v,vc="🤑 BUY ZONE","badge-buy"
        elif dist>0.25 or rsi_val>65: v,vc="⚠️ TOPPY","badge-toppy"
        elif dist>0: v,vc="⏳ WAIT","badge-toppy"
        else: v,vc="👀 WATCH","badge-watch"
        return {"live":live,"sma200":sma200,"sma50":sma50,"rsi":rsi_val,"dist":dist,"struct":struct,"v":v,"vc":vc,"close":close}
    except:
        return None

# --- TABS ORDER: Ticker first, Portfolio last ---
tab_ticker, tab_watchlist, tab_portfolio = st.tabs(["🔍 Ticker Search (Main)","👀 Watchlist","📊 Portfolio"])

# 1. TICKER SEARCH - MAIN PAGE
with tab_ticker:
    st.markdown("<div class='card'><div class='small'>MAIN PAGE • SEARCH ALL STOCKS • V3 PRO LOGIC</div><div style='font-weight:700;font-size:18px'>Type any ticker: AAPL, MSFT, SPY, BTC-USD, etc.</div></div>", unsafe_allow_html=True)
    c1,c2=st.columns([3,1])
    with c1:
        query = st.text_input("Ticker", value="NVDA", placeholder="e.g. AAPL").upper().strip()
    with c2:
        st.markdown("<div class='small' style='margin-top:28px'>Add to list after search</div>")

    if query:
        d=get_safe(query)
        if not d:
            st.error(f"Could not fetch {query}")
        else:
            st.markdown(f"<div class='card' style='border-color:#4ADE80'><div style='display:flex;justify-content:space-between'><b style='font-size:28px'>{query} ${d['live']:.2f}</b><span class='badge {d['vc']}' style='font-size:14px'>{d['v']}</span></div><div style='display:flex;gap:10px;margin-top:12px'><div class='card' style='flex:1;margin:0'><div class='small'>DIST TO FLOOR</div><div style='font-size:18px;font-weight:700'>{d['dist']*100:+.1f}%</div><div class='small'>Floor ${d['sma200']:.2f}</div></div><div class='card' style='flex:1;margin:0'><div class='small'>STRUCT RISK</div><div style='font-size:18px;font-weight:700'>{d['struct']*100:+.1f}%</div></div><div class='card' style='flex:1;margin:0'><div class='small'>RSI 14</div><div style='font-size:18px;font-weight:700'>{d['rsi']:.1f}</div></div></div><div class='small' style='margin-top:10px'>Auto T1 {d['sma200']*1.05:.2f} | T2 Floor {d['sma200']:.2f} | T3 Panic {d['sma200']*0.92:.2f}</div></div>", unsafe_allow_html=True)
            
            b1,b2=st.columns(2)
            with b1:
                if st.button(f"➕ Add {query} to Portfolio", key=f"add_p_{query}"):
                    if query not in st.session_state.holdings:
                        st.session_state.holdings.append(query)
                        st.success(f"{query} added to Portfolio")
            with b2:
                if st.button(f"➕ Add {query} to Watchlist", key=f"add_w_{query}"):
                    if query not in st.session_state.watchlist:
                        st.session_state.watchlist.append(query)
                        st.success(f"{query} added to Watchlist")

            close=d['close']
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=close.index, y=close, name=query))
            fig.add_trace(go.Scatter(x=close.index, y=close.rolling(200).mean(), name="200 SMA Floor", line=dict(dash="dash")))
            fig.add_trace(go.Scatter(x=close.index, y=close.rolling(50).mean(), name="50 SMA"))
            fig.update_layout(template="plotly_dark", paper_bgcolor="#15151A", plot_bgcolor="#15151A", height=350, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

# 2. WATCHLIST - EDITABLE
with tab_watchlist:
    st.markdown("**Watchlist — Editable**")
    new_w = st.text_input("Add ticker to watchlist", placeholder="e.g. ELF").upper().strip()
    if st.button("Add to Watchlist") and new_w:
        if new_w not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_w)
            st.rerun()
    
    for sym in st.session_state.watchlist[:]:
        d=get_safe(sym)
        col1,col2,col3=st.columns([4,1,1])
        with col1:
            if d:
                st.markdown(f"<div class='card'><b>{sym} ${d['live']:.2f}</b> <span class='badge {d['vc']}' style='float:right'>{d['v']}</span><div class='small'>RSI {d['rsi']:.0f} | Dist {d['dist']*100:+.0f}%</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='card'><b>{sym}</b> <span class='small'>failed to fetch</span></div>", unsafe_allow_html=True)
        with col2:
            if st.button("✏️", key=f"edit_w_{sym}"):
                st.session_state.holdings.append(sym)
                st.success(f"Moved {sym} to Portfolio")
        with col3:
            if st.button("🗑️", key=f"del_w_{sym}"):
                st.session_state.watchlist.remove(sym)
                st.rerun()

# 3. PORTFOLIO - LAST TAB, EDITABLE
with tab_portfolio:
    st.markdown("**Portfolio — Last Tab, Editable / Deletable**")
    new_p = st.text_input("Add ticker to portfolio", placeholder="e.g. GOOGL").upper().strip()
    if st.button("Add to Portfolio") and new_p:
        if new_p not in st.session_state.holdings:
            st.session_state.holdings.append(new_p)
            st.rerun()

    for sym in st.session_state.holdings[:]:
        d=get_safe(sym)
        c1,c2=st.columns([5,1])
        with c1:
            if d:
                sup=SUPPORT_DATA.get(sym, {})
                st.markdown(f"<div class='card'><div style='display:flex;justify-content:space-between'><b>{sym} ${d['live']:.2f}</b><span class='badge {d['vc']}'>{d['v']}</span></div><div class='small'>Dist {d['dist']*100:+.1f}% | Struct {d['struct']*100:+.1f}% | RSI {d['rsi']:.0f} | Floor ${d['sma200']:.0f} | T1 {sup.get('t1','-')} T2 {sup.get('t2','-')} T3 {sup.get('t3','-')}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='card'><b>{sym}</b> <span class='small'>fetch failed</span></div>", unsafe_allow_html=True)
        with c2:
            if st.button("🗑️ Delete", key=f"del_p_{sym}"):
                st.session_state.holdings.remove(sym)
                st.rerun()
