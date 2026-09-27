import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Invest Dash V4.1", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400&display=swap');
.stApp { background:#0A0A0F; }
.card { background: linear-gradient(180deg,#17171F,#12121A); border:1px solid #252530; border-radius:18px; padding:18px; }
.badge { padding:6px 12px; border-radius:99px; font-family:'JetBrains Mono'; font-size:11px; font-weight:600; }
.badge-strike { background:#0E2A1A; color:#4ADE80; border:1px solid #14532D; }
.badge-toppy { background:#2A1215; color:#FCA5A5; border:1px solid #7F1D1D; }
.badge-buy { background:#12261E; color:#86EFAC; border:1px solid #166534; }
.small { font-family:'JetBrains Mono'; color:#8B8B93; font-size:11px; }
h2,h3 { font-family:'Inter'; letter-spacing:-0.02em; }
</style>
""", unsafe_allow_html=True)

# ---- TOP WEALTH BANNER ----
st.markdown("<div class='card' style='display:flex;justify-content:space-between;align-items:center;background:radial-gradient(120% 120% at 100% 0%, #2A1F6A 0%, #17171F 60%);'><div><div class='small'>TOTAL WEALTH</div><div style='font-size:38px;font-weight:800'>$2,847,921 <span style='font-size:14px;background:#0E2A1A;color:#4ADE80;border:1px solid #14532D;padding:4px 10px;border-radius:99px'>+12.4% ↗</span></div><div class='small'>Updated today • +$314,892 this month • Data live from yfinance</div></div><div style='display:flex;gap:28px'><div><div class='small'>MONTHLY RETURN</div><div style='color:#4ADE80;font-weight:700'>+8.2% ✨</div></div><div><div class='small'>YTD GROWTH</div><div style='color:#4ADE80;font-weight:700'>+24.7% ✨</div></div><div><div class='small'>CASH AVAILABLE</div><div style='font-weight:700'>$142,530</div></div></div></div>", unsafe_allow_html=True)

tabs = st.tabs(["◼ Overview","📊 Portfolio","👀 Watchlist","📈 Analytics"])

# Shared data
HOLDINGS = {"GOOGL":125,"TSLA":100,"AMZN":32,"CELH":319,"AVGO":10,"META":20}
TICKERS = list(HOLDINGS.keys())

def get_verdict(ticker):
    try:
        df=yf.download(ticker, period="1y", progress=False, auto_adjust=True)
        close=df['Close']
        if isinstance(close,pd.DataFrame): close=close.iloc[:,0]
        close=close.dropna()
        live=float(close.iloc[-1])
        sma200=float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else live
        dist=(live-sma200)/sma200
        rsi=close.diff()
        g=rsi.where(rsi>0,0).rolling(14).mean(); l=-rsi.where(rsi<0,0).rolling(14).mean()
        r=float((100-(100/(1+g/l))).iloc[-1])
        if r<40 and dist<-0.05: return "🔥 STRIKE", "badge-strike", live, r, dist
        if dist<-0.10 and r<50: return "🤑 BUY ZONE", "badge-buy", live, r, dist
        if dist>0.25 or r>65: return "⚠️ TOPPY", "badge-toppy", live, r, dist
        return "👀 WATCH", "badge-buy", live, r, dist
    except: return "WATCH","badge-buy",0,50,0

with tabs[0]:
    c1,c2,c3 = st.columns([1,1.2,1])
    with c1:
        st.markdown("<div class='card'><div>Portfolio Allocation</div><div class='small'>31% Stocks • Real-time</div></div>", unsafe_allow_html=True)
        alloc = pd.DataFrame({"Asset":["Stocks","Bonds","Crypto","Real Estate"],"Value":[31,24,20,15]})
        fig = go.Figure(go.Pie(labels=alloc.Asset, values=alloc.Value, hole=0.6, marker=dict(colors=["#7C6AFF","#60A5FA","#2ECC71","#A78BFA"])))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=260, showlegend=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<div class='card' style='margin-top:12px'><div>Risk Score</div><div style='font-size:36px;font-weight:800'>72 <span style='font-size:14px;color:#FDE68A'>• Moderate Growth</span></div><div class='small'>Low 0-40 • Moderate 41-75 • High 76-100</div><div style='margin-top:8px;height:8px;background:#252530;border-radius:99px'><div style='width:72%;height:8px;background:linear-gradient(90deg,#7C6AFF,#2ECC71);border-radius:99px'></div></div></div>", unsafe_allow_html=True)
    with c2:
        # Market Overview from inspo 2
        st.markdown("<div class='card'><div>Market Overview</div><div style='display:flex;gap:24px;margin-top:12px'><div><div class='small'>S&P 500</div><b>5,843.21</b><div style='color:#4ADE80'>+1.24% ↑</div></div><div><div class='small'>NASDAQ</div><b>18,391.45</b><div style='color:#4ADE80'>+1.89% ↑</div></div><div><div class='small'>BTC/USD</div><b>$62,104</b><div style='color:#FCA5A5'>-0.82% ↓</div></div></div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card' style='margin-top:12px'><div>Cashflow Analytics</div><div class='small'>Net: +$18.4k avg monthly</div></div>", unsafe_allow_html=True)
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        inflows=[12,18,17,15,19,16,18,14,16,15,18,12]; outflows=[3,4,2,5,3,4,5,4,5,4,3,5]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=months, y=inflows, name="Inflows", marker_color="#4ADE80"))
        fig2.add_trace(go.Bar(x=months, y=outflows, name="Outflows", marker_color="#F472B6"))
        fig2.update_layout(template="plotly_dark", barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("<div class='card'><div>Investment Opportunities</div><div style='margin-top:12px'><div style='display:flex;justify-content:space-between'><span>🤖 AI Tech Fund • 15.2% APY</span><span class='badge badge-buy'>+ Invest</span></div><div style='display:flex;justify-content:space-between;margin-top:10px'><span>🌱 Sustainable Energy ETF • 9.8% APY</span><span class='badge badge-buy'>+ Invest</span></div><div style='display:flex;justify-content:space-between;margin-top:10px'><span>🏠 Real Estate REIT • 6.4% APY</span><span class='badge badge-buy'>+ Invest</span></div></div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='card'><div>Recent Transactions</div>", unsafe_allow_html=True)
        for sym in TICKERS[:5]:
            v,vc,lv,rsi,d = get_verdict(sym)
            st.markdown(f"<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #252530'><span>{sym}</span><span class='badge {vc}'>{v}</span><span>${lv:.0f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.markdown("### Portfolio — Your 6 holdings with your T1/T2/T3 logic")
    for sym in TICKERS:
        v,vc,lv,rsi,d = get_verdict(sym)
        st.markdown(f"<div class='card' style='margin-bottom:8px;display:flex;justify-content:space-between'><b>{sym} ${lv:.2f}</b><span class='badge {vc}'>{v} • RSI {rsi:.0f} • Dist {d*100:+.0f}%</span></div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown("### Watchlist — Separate Tab (like you wanted)")
    watch = ["AMD","SOFI","ADBE","SHOP","NVO","HIMS","JMIA","CAKE","ANET","ETN","VRT"]
    cols = st.columns(3)
    for i, w in enumerate(watch):
        v,vc,lv,rsi,d = get_verdict(w)
        with cols[i%3]:
            st.markdown(f"<div class='card' style='margin-bottom:10px'><div style='display:flex;justify-content:space-between'><b>{w}</b><span class='badge {vc}'>{v}</span></div><div class='small'>Live ${lv:.2f} • RSI {rsi:.0f} • {d*100:+.0f}% to floor</div></div>", unsafe_allow_html=True)

with tabs[3]:
    st.markdown("### Analytics — Risk + Goals")
    st.markdown("<div class='card'><div>Financial Goals</div><div style='margin-top:10px'><div>Emergency Fund 78% — $23,400 / $30,000</div><div style='height:8px;background:#252530;border-radius:99px;margin:6px 0'><div style='width:78%;height:8px;background:#7C6AFF;border-radius:99px'></div></div><div>Retirement 2035 56% — $118,200 / $210,000</div><div style='height:8px;background:#252530;border-radius:99px;margin:6px 0'><div style='width:56%;height:8px;background:#60A5FA;border-radius:99px'></div></div></div></div>", unsafe_allow_html=True)
