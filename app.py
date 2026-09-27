# --- NEW: SEARCH ANY TICKER TAB ---
tab_search = st.tabs(["📊 Portfolio","👀 Watchlist","🔍 Search All"])[2]

with tab_search:
    st.markdown("<div class='card'><div class='small'>SEARCH ANY TICKER — V3 PRO LOGIC</div><div style='font-size:20px;font-weight:700'>Type any symbol: AAPL, NVDA, TSLA, SPY, BTC-USD, etc.</div></div>", unsafe_allow_html=True)

    query = st.text_input("Ticker", value="NVDA", placeholder="e.g. AAPL").upper().strip()

    if query:
        d = get_safe(query)
        if not d:
            st.error(f"Could not fetch {query}. Check symbol.")
        else:
            # Full V3 Pro metrics for ANY stock
            st.markdown(f"<div class='card' style='border:1px solid #4ADE80'><div style='display:flex;justify-content:space-between'><div><div class='small'>LIVE ANALYSIS</div><div style='font-size:32px;font-weight:800'>{query} ${d['live']:.2f} <span class='badge {d['vc']}' style='font-size:14px;margin-left:10px'>{d['v']}</span></div></div><div style='text-align:right'><div class='small'>VERDICT</div><div style='font-size:18px;font-weight:700'>{d['v']}</div></div></div><div style='display:flex;gap:12px;margin-top:14px'><div class='card' style='flex:1'><div class='small'>DIST TO FLOOR</div><div style='font-size:20px;font-weight:700'>{d['dist']*100:+.1f}%</div><div class='small'>Floor ${d['sma200']:.2f}</div></div><div class='card' style='flex:1'><div class='small'>STRUCTURAL RISK</div><div style='font-size:20px;font-weight:700'>{d['struct']*100:+.1f}%</div></div><div class='card' style='flex:1'><div class='small'>RSI 14</div><div style='font-size:20px;font-weight:700'>{d['rsi']:.1f}</div><div class='small'>{'Oversold <40' if d['rsi']<40 else 'Overbought >65' if d['rsi']>65 else 'Neutral'}</div></div></div></div>", unsafe_allow_html=True)

            # Chart for any ticker
            df = yf.download(query, period="1y", progress=False, auto_adjust=True)
            close = df['Close']
            if isinstance(close, pd.DataFrame): close=close.iloc[:,0]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=close.index, y=close, name="Price"))
            fig.add_trace(go.Scatter(x=close.index, y=close.rolling(200).mean(), name="200 SMA Floor", line=dict(dash="dash")))
            fig.add_trace(go.Scatter(x=close.index, y=close.rolling(50).mean(), name="50 SMA"))
            fig.update_layout(template="plotly_dark", height=360, paper_bgcolor="#15151A", plot_bgcolor="#15151A")
            st.plotly_chart(fig, use_container_width=True)

            # T1/T2/T3 calculator for ANY ticker
            st.markdown(f"<div class='card'><div class='small'>AUTO T1/T2/T3 for {query}</div><div>Based on 200 SMA: <b>T1 {d['sma200']*1.05:.2f} | T2 Floor {d['sma200']:.2f} | T3 Panic {d['sma200']*0.92:.2f}</b></div></div>", unsafe_allow_html=True)
