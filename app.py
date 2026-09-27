# --- PATCH for V3 Pro Final ---
HOLDINGS = ["GOOGL","AMZN","AVGO","META","AMD","CELH","ADBE","SOFI"]

def get_safe(ticker):
    try:
        df=yf.download(ticker, period="1y", progress=False, auto_adjust=True)
        if df.empty: return None
        close=df['Close']
        if isinstance(close, pd.DataFrame): close=close.iloc[:,0]
        close=close.dropna()
        if len(close)<50: return None
        live=float(close.iloc[-1])
        sma200=float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else live
        sma50=float(close.rolling(50).mean().iloc[-1])
        # RSI
        d=close.diff()
        g=d.where(d>0,0).rolling(14).mean()
        l=-d.where(d<0,0).rolling(14).mean()
        rsi=float((100-(100/(1+g/l))).iloc[-1])
        dist=(live-sma200)/sma200
        struct=(sma50-sma200)/sma200
        if rsi<40 and dist<-0.05: v,vc="🔥 STRIKE","badge-strike"
        elif dist<-0.10 and rsi<50: v,vc="🤑 BUY ZONE","badge-buy"
        elif dist>0.25 or rsi>65: v,vc="⚠️ TOPPY","badge-toppy"
        else: v,vc="👀 WATCH","badge-watch"
        return {"live":live,"sma200":sma200,"rsi":rsi,"dist":dist,"struct":struct,"v":v,"vc":vc}
    except:
        return None

# --- In your tabs, use this ---
with tab1:
    st.markdown("**Portfolio — Your 8 core holdings**")
    for sym in HOLDINGS:
        d=get_safe(sym)
        if not d:
            st.markdown(f"<div class='card'><b>{sym}</b> <span class='small'>data unavailable</span></div>", unsafe_allow_html=True)
            continue
        sup = SUPPORT_DATA.get(sym, {"t1":"-","t2":"-","t3":"-","logic":""})
        st.markdown(f"<div class='card'><div style='display:flex;justify-content:space-between'><b>{sym} ${d['live']:.2f}</b><span class='badge {d['vc']}'>{d['v']}</span></div><div class='small'>Dist {d['dist']*100:+.1f}% | Struct {d['struct']*100:+.1f}% | RSI {d['rsi']:.0f} | Floor ${d['sma200']:.0f} | T1 {sup['t1']} T2 {sup['t2']} T3 {sup['t3']}</div></div>", unsafe_allow_html=True)

with tab2:
    st.markdown("**Watchlist — Separate tab**")
    for sym in ["SHOP","NVO","HIMS","JMIA","CAKE","ANET","ETN","VRT","NVDA","TSLA","ELF"]:
        d=get_safe(sym)
        if d:
            st.markdown(f"<div class='card'><b>{sym} ${d['live']:.2f}</b> <span class='badge {d['vc']}' style='float:right'>{d['v']}</span><div class='small'>RSI {d['rsi']:.0f} | Dist {d['dist']*100:+.0f}%</div></div>", unsafe_allow_html=True)
