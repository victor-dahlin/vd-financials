import streamlit as st
import sys
import os

# Add the directory containing this script to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
from data_loader import StockDataLoader
import analysis
import importlib
importlib.reload(analysis)

logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png')
st.set_page_config(page_title="VD Financials", page_icon=logo_path, layout="wide")


ticker_input = st.sidebar.text_input("Enter Stock Ticker (Symbol)", value="AAPL").upper()
exchange_mode = st.sidebar.selectbox("Exchange / Region", options=["Auto-Detect", "US (No Suffix)", "Sweden (.ST)", "Denmark (.CO)"], index=0)

suffix_map = {
    "US (No Suffix)": "",
    "Sweden (.ST)": ".ST",
    "Denmark (.CO)": ".CO"
}

ticker = ticker_input # fallback

if ticker_input:
    resolved_ticker = None
    
    if exchange_mode == "Auto-Detect":
        # Try common suffixes in order
        candidates = [ticker_input, f"{ticker_input}.ST", f"{ticker_input}.CO"]
        
        # We need a way to check validity without expensive full fetch if possible, 
        # but fetch_history is cached so we can just use it.
        # We'll use a placeholder for validity check.
        for cand in candidates:
            # We use a 1d check to be fast
            check_data = StockDataLoader.fetch_history(cand, period="1d", interval="1d")
            if not check_data.empty:
                resolved_ticker = cand
                break
        
        if not resolved_ticker:
             # Default to input if none found (will show error later)
             resolved_ticker = ticker_input
             
    else:
        resolved_ticker = f"{ticker_input}{suffix_map[exchange_mode]}"

    ticker = resolved_ticker

    # Display resolved ticker if different
    if ticker != ticker_input and "Auto" in exchange_mode:
        st.sidebar.info(f"Resolved to: **{ticker}**")

period = st.sidebar.selectbox("Period", options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=5)

# Indicators
st.sidebar.subheader("Technical Indicators")
show_sma = st.sidebar.checkbox("SMA (20)")
show_ema = st.sidebar.checkbox("EMA (20)")
show_rsi = st.sidebar.checkbox("RSI (14)")
show_bb = st.sidebar.checkbox("Bollinger Bands")

# Fundamental Settings
st.sidebar.subheader("Fundamental Data")
fund_freq = st.sidebar.radio("Frequency", options=["Annual", "Quarterly"], index=0)

if ticker:
    # Fetch Data
    with st.spinner('Fetching Data...'):
        try:
            # Determine Interval
            interval = "1d"
            if period in ["1d", "5d"]:
                interval = "1m"
            
            hist_data = StockDataLoader.fetch_history(ticker, period, interval=interval)
            
            # Ensure index is datetime for Plotly rangebreaks
            if not isinstance(hist_data.index, pd.DatetimeIndex):
                hist_data.index = pd.to_datetime(hist_data.index)
            financials = StockDataLoader.fetch_financials(ticker, quarterly=(fund_freq == "Quarterly"))
            company_name = StockDataLoader.fetch_company_name(ticker)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            st.stop()
    
    # Update title with company name and LIVE PRICE
    
    # Fetch live price and calculate delta for sticky header
    current_price = 0.0
    price_change = 0.0
    try:
        t = yf.Ticker(ticker)
        current_price = t.fast_info['last_price']
        prev_close = t.fast_info['previous_close']
        delta = current_price - prev_close
        price_change = (delta / prev_close) * 100
    except Exception:
        pass

    # Theme Management
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

    def toggle_theme():
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

    # CSS for Theme and Layout
    if st.session_state.theme == 'dark':
        bg_color = "#0e1117"
        text_color = "#fafafa"
        header_bg = "rgba(14, 17, 23, 0.95)" # Slightly more opaque for tabs
        border_color = "rgba(255, 255, 255, 0.1)"
        logo_filter = ""
    else:
        bg_color = "#ffffff"
        text_color = "#000000"
        header_bg = "rgba(255, 255, 255, 0.95)"
        border_color = "rgba(0, 0, 0, 0.1)"
        logo_filter = "filter: invert(1) hue-rotate(180deg);"

    # Define CSS with safer formatting - NO INDENTATION to avoid code block rendering
    css_styles = f"""
<style>
    /* Global Theme Overrides */
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_color};
        color: {text_color};
    }}
    [data-testid="stHeader"] {{
        background-color: transparent !important;
        z-index: 1000000 !important;
    }}
    
    /* Remove default top padding so our header sits flush */
    .block-container {{
        padding-top: 0rem !important; 
    }}

    /* FIXED HEADER CSS 
       We target the Streamlit container wrapping our header to make it sticky 
       relative to the main scrolling area. This allows it to:
       1. Stick to the top.
       2. Move when the sidebar opens/closes.
    */
    div[data-testid="stVerticalBlock"] > div:has(div#vd-header) {{
        position: sticky;
        top: 0;
        z-index: 60;
    }}

    div#vd-header {{
        /* No positioning here, let the container handle sticking */
        background-color: {header_bg};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-bottom: 1px solid {border_color};
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: background-color 0.3s ease;
        
        /* Full Width Hack to cover the container's padding */
        margin-left: -5rem;
        margin-right: -5rem;
        padding-left: 5rem;
        padding-right: 5rem;
        width: calc(100% + 10rem);
    }}
    
    /* Make Tabs Sticky underneath the Fixed Header */
    div[data-testid="stTabs"] > div:first-child {{
        position: sticky;
        top: 85px; /* Matches the height of your fixed header */
        z-index: 50;
        background-color: {header_bg};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding-bottom: 10px;
        border-bottom: 1px solid {border_color};
        
        /* Full Width Hack for Tabs */
        margin-left: -5rem;
        margin-right: -5rem;
        padding-left: 5rem;
        padding-right: 5rem;
        width: calc(100% + 10rem);
    }}
    
    /* Evenly Space Tabs */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {{
        flex-grow: 1 !important;
        width: 100% !important;
    }}
</style>
"""
    st.markdown(css_styles, unsafe_allow_html=True)

    # Load and Encode Logo
    logo_html = ""
    try:
        import os
        import base64
        # Relative path to logo in the same directory as app.py
        logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')

        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode()
            # Thinner logo (75px), trimmed watermark
            logo_html = f'<img src="data:image/png;base64,{encoded_image}" style="height: 75px; object-fit: contain; clip-path: inset(0px 30px 0px 0px); {logo_filter}">'
        else:
            logo_html = '<h2 style="color: #4CAF50;">VD Financials</h2>'
    except Exception:
        logo_html = '<h2 style="color: #4CAF50;">VD Financials</h2>'

    # Sticky Header
    price_color = "green" if price_change >= 0 else "red"
    
    header_html = f"""
<div id="vd-header" style="
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    height: 85px; /* Defined height is crucial for the spacer */
    padding: 0 5rem; /* Horizontal padding */
">
    <div style="display: flex; align-items: center; padding-left: 20px;">
        {logo_html}
    </div>
    <div style="display: flex; align-items: center; gap: 15px; text-align: right; padding-right: 50px;">
        <h3 style="margin:0; padding:0; font-size: 1.1rem; color: {text_color}; display: inline-block;">{company_name} ({ticker})</h3>
        <div style="display: flex; flex-direction: column; align-items: flex-end; line-height: 1.1;">
            <span style="font-size: 1.1rem; font-weight: bold; color: {text_color};">${current_price:,.2f}</span>
            <span style="font-size: 1.2rem; color: {price_color}; font-weight: 600;">{price_change:+.2f}%</span>
        </div>
    </div>
</div>
"""
    st.markdown(header_html, unsafe_allow_html=True)

    if hist_data.empty:
        st.warning("No historical data found for this ticker.")
    else:
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Technical Analysis", "Fundamental Analysis", "Full Financial Statements", "Valuation Models"])

        with tab1:
            # Candlestick Chart
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.05, row_heights=[0.7, 0.3],
                                specs=[[{"secondary_y": False}], [{"secondary_y": False}]])

            # Price
            fig.add_trace(go.Candlestick(x=hist_data.index,
                                         open=hist_data['Open'],
                                         high=hist_data['High'],
                                         low=hist_data['Low'],
                                         close=hist_data['Close'],
                                         name='Price'), row=1, col=1)

            # Indicators
            if show_sma:
                sma = analysis.calculate_sma(hist_data)
                fig.add_trace(go.Scatter(x=hist_data.index, y=sma, name='SMA 20', line=dict(color='orange')), row=1, col=1)
            
            if show_ema:
                ema = analysis.calculate_ema(hist_data)
                fig.add_trace(go.Scatter(x=hist_data.index, y=ema, name='EMA 20', line=dict(color='blue')), row=1, col=1)

            if show_bb:
                upper, lower = analysis.calculate_bollinger_bands(hist_data)
                fig.add_trace(go.Scatter(x=hist_data.index, y=upper, name='BB Upper', line=dict(color='gray', dash='dash')), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist_data.index, y=lower, name='BB Lower', line=dict(color='gray', dash='dash'), fill='tonexty'), row=1, col=1)

            # Volume
            fig.add_trace(go.Bar(x=hist_data.index, y=hist_data['Volume'], name='Volume'), row=2, col=1)

            # Chart Layout
            layout_args = dict(
                title=f"{ticker} Stock Price", 
                xaxis_rangeslider_visible=False, 
                height=550
            )
            
            # Formatting X-Axis
            xaxis_args = dict(
                rangebreaks=[
                    dict(bounds=["sat", "mon"]), # Hide weekends
                ] 
            )
            
            # Use interval variable from above
            if interval in ["1m", "5m"]:
                # For intraday, hide overnight gaps (e.g. 16:00 to 09:30)
                # bounds=[16, 9.5] means hide from 16:00 to 09:30
                xaxis_args['rangebreaks'].append(dict(bounds=[16, 9.5], pattern="hour"))
            
            # If Daily interval, format Date only.
            if interval == "1d":
                 xaxis_args['tickformat'] = '%Y-%m-%d'
            
            layout_args['xaxis'] = xaxis_args
            
            fig.update_layout(**layout_args)
            
            # RSI Subplot or separate? Usually separate or below. 
            # If RSI is selected, maybe we need a 3rd row or just show it in a separate chart below.
            # For simplicity, let's render RSI in a separate chart if selected.
            st.plotly_chart(fig, use_container_width=True)

            if show_rsi:
                rsi = analysis.calculate_rsi(hist_data)
                rsi_fig = go.Figure(go.Scatter(x=hist_data.index, y=rsi, name='RSI 14', line=dict(color='purple')))
                rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
                rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
                rsi_fig.update_layout(title="Relative Strength Index (RSI)", height=300, yaxis=dict(range=[0, 100]))
                st.plotly_chart(rsi_fig, use_container_width=True)

            st.subheader("Raw Data")
            # Format raw data for display
            raw_display = hist_data.tail().copy()
            if interval == "1d":
                # For daily data, format index to Date only string
                raw_display.index = raw_display.index.strftime('%Y-%m-%d')
            
            st.dataframe(raw_display)

        with tab2:
            st.header("Fundamental Analysis")
            if not financials.empty:
                # Transpose is done in data_loader, so index is Date, columns are metrics
                financials.index = pd.to_datetime(financials.index)
                
                # Helper to safely get column
                def get_col(cols, keywords):
                    for k in keywords:
                        for c in cols:
                            if k.lower() in c.lower():
                                return c
                    return None

                cols = financials.columns
                rev_col = get_col(cols, ['Total Revenue', 'Revenue'])
                cost_col = get_col(cols, ['Cost Of Revenue', 'Cost of Revenue'])
                gross_profit_col = get_col(cols, ['Gross Profit'])
                op_income_col = get_col(cols, ['Operating Income'])
                net_income_col = get_col(cols, ['Net Income', 'Net Income Common Stockholders'])
                
                # Expense Breakdown
                rnd_col = get_col(cols, ['Research And Development'])
                sga_col = get_col(cols, ['Selling General And Administration'])

                # 1. Revenue, Cost, Profit Trends
                st.markdown("#### Revenue & Profitability Trends")
                
                # Sort financials for Chart (Oldest -> Newest) AND Scale to Millions
                fin_chart = financials.sort_index(ascending=True) / 1e6
                
                fund_fig = go.Figure()
                if rev_col: fund_fig.add_trace(go.Bar(x=fin_chart.index, y=fin_chart[rev_col], name='Revenue', marker_color='#74c476', hovertemplate='%{y:,.0f}<extra></extra>')) # Medium Green
                if cost_col: fund_fig.add_trace(go.Bar(x=fin_chart.index, y=fin_chart[cost_col], name='Cost of Revenue', marker_color='#fb6a4a', hovertemplate='%{y:,.0f}<extra></extra>')) # Medium Red
                if gross_profit_col: fund_fig.add_trace(go.Scatter(x=fin_chart.index, y=fin_chart[gross_profit_col], name='Gross Profit', line=dict(color='purple', width=6), hovertemplate='%{y:,.0f}<extra></extra>'))
                if net_income_col: fund_fig.add_trace(go.Scatter(x=fin_chart.index, y=fin_chart[net_income_col], name='Net Income', line=dict(color='#1f77b4', width=6, dash='dash'), hovertemplate='%{y:,.0f}<extra></extra>'))
                
                fund_fig.update_layout(barmode='group', hovermode="x unified", height=500)
                st.plotly_chart(fund_fig, use_container_width=True)

                col1, col2 = st.columns(2)
                
                with col1:
                    # 2. Operating Expenses Breakdown
                    st.markdown("#### Operating Expenses Breakdown")
                    if rnd_col or sga_col:
                        exp_fig = go.Figure()
                        if rnd_col: exp_fig.add_trace(go.Bar(x=financials.index, y=financials[rnd_col], name='R&D', marker_color='#9467bd'))
                        if sga_col: exp_fig.add_trace(go.Bar(x=financials.index, y=financials[sga_col], name='SG&A', marker_color='#8c564b'))
                        exp_fig.update_layout(barmode='stack', height=400)
                        st.plotly_chart(exp_fig, use_container_width=True)
                    else:
                        st.info("Detailed expense data (R&D, SG&A) not available.")

                with col2:
                    # 3. Margins Analysis
                    st.markdown("#### Profit Margins (%)")
                    if rev_col and gross_profit_col:
                        margin_fig = go.Figure()
                        # Calculate margins
                        gross_margin = (financials[gross_profit_col] / financials[rev_col]) * 100
                        margin_fig.add_trace(go.Scatter(x=financials.index, y=gross_margin, name='Gross Margin %', line=dict(color='#ff7f0e')))
                        
                        if op_income_col:
                            op_margin = (financials[op_income_col] / financials[rev_col]) * 100
                            margin_fig.add_trace(go.Scatter(x=financials.index, y=op_margin, name='Operating Margin %', line=dict(color='#bcbd22')))
                            
                        if net_income_col:
                            net_margin = (financials[net_income_col] / financials[rev_col]) * 100
                            margin_fig.add_trace(go.Scatter(x=financials.index, y=net_margin, name='Net Margin %', line=dict(color='#1f77b4')))
                            
                        margin_fig.update_layout(height=400, yaxis_title="Percentage (%)")
                        st.plotly_chart(margin_fig, use_container_width=True)
                    else:
                        st.info("Insufficient data to calculate margins.")

                # 4. Key Financial Metrics (New)
                st.markdown("#### Key Financial Metrics")
                # Need Balance Sheet and Cash Flow for full metrics
                bs = StockDataLoader.fetch_balance_sheet(ticker, quarterly=(fund_freq == "Quarterly"))
                cfs = StockDataLoader.fetch_cashflow(ticker, quarterly=(fund_freq == "Quarterly"))
                
                if not bs.empty and not cfs.empty:
                    # Current Valuation (Replacing Historical)
                    st.markdown("##### Current Valuation Metrics")
                    try:
                        # Fetch Live Price
                        cur_ticker = yf.Ticker(ticker)
                        curr_price = cur_ticker.fast_info['last_price']
                        
                        fund_metrics = analysis.calculate_fundamental_metrics(financials, bs, cfs)
                        
                        # Get latest metrics (last column after transpose -> Newest is last because we sort sort_index(ascending=True).T)
                        # Wait, ascending=True means Oldest -> Newest. So last column is Newest.
                        latest_metrics = fund_metrics.iloc[:, -1]
                        
                        eps = latest_metrics.get('EPS (Diluted)', None)
                        if eps is None or pd.isna(eps): eps = latest_metrics.get('EPS (Basic)', None)
                        
                        bvps = latest_metrics.get('Book Value Per Share', None)
                        
                        # Revenue Per Share needed for P/S. 
                        # We don't have RPS directly in metrics, let's calc or add to metrics. 
                        # Or just use Revenue / Shares from latest statements?
                        # Simplest: Add RPS to metrics in analysis.py? 
                        # Or just calc here:
                        rev = financials.loc[latest_metrics.name, 'Total Revenue'] if 'Total Revenue' in financials.columns else financials.loc[latest_metrics.name, 'Revenue']
                        shares = financials.loc[latest_metrics.name, 'Diluted Average Shares'] if 'Diluted Average Shares' in financials.columns else financials.loc[latest_metrics.name, 'Basic Average Shares']
                        rps = rev / shares if shares else None

                        pe = curr_price / eps if eps else None
                        pb = curr_price / bvps if bvps else None
                        ps = curr_price / rps if rps else None
                        
                        col_v1, col_v2, col_v3 = st.columns(3)
                        col_v1.metric("P/E Ratio (Current)", f"{pe:.2f}" if pe else "N/A")
                        col_v2.metric("P/B Ratio (Current)", f"{pb:.2f}" if pb else "N/A")
                        col_v3.metric("P/S Ratio (Current)", f"{ps:.2f}" if ps else "N/A")
                        
                    except Exception as e:
                        st.warning(f"Could not calculate current valuation: {e}")

                    st.markdown("##### Key Ratios")
                    
                    # Convert to numeric to handle None -> NaN (fixes TypeError in styling)
                    fund_metrics = fund_metrics.apply(pd.to_numeric, errors='coerce')

                    # Sparse column filtering (Same as main statements)
                    valid_counts = fund_metrics.count()
                    total_rows = len(fund_metrics)
                    keep_cols = valid_counts[valid_counts >= (total_rows * 0.5)].index
                    fund_metrics = fund_metrics[keep_cols]

                    # Format columns (Dates) to YYYY-MM-DD
                    new_cols = []
                    for c in fund_metrics.columns:
                        if hasattr(c, 'strftime'):
                            new_cols.append(c.strftime('%Y-%m-%d'))
                        else:
                            new_cols.append(str(c))
                    fund_metrics.columns = new_cols
                    
                    st.dataframe(fund_metrics.style.format("{:,.2f}"))
                else:
                    st.info("Balance Sheet or Cash Flow data unavailable for comprehensive metrics.")

                # Valuation Snapshot (Current) - REMOVED / INTEGRATED
                pass



            else:
                st.info("No financial data available for this ticker.")
        
        # New Tab: Full Financial Statements
        with tab3:
            st.header(f"Full Financial Statements ({fund_freq})")
            st.markdown("*All values in Millions of USD ($M) unless otherwise noted.*")
            
            # Fetch Data for Statements if not already fetched
            if 'bs' not in locals():
                bs = StockDataLoader.fetch_balance_sheet(ticker, quarterly=(fund_freq == "Quarterly"))
            if 'cfs' not in locals():
                cfs = StockDataLoader.fetch_cashflow(ticker, quarterly=(fund_freq == "Quarterly"))
                
            from financial_definitions import INCOME_STATEMENT_STRUCTURE, BALANCE_SHEET_STRUCTURE, CASH_FLOW_STRUCTURE
            
            def render_structured_statement(df, structure, title):
                st.subheader(title)
                if df.empty:
                    st.info(f"{title} data unavailable.")
                    return

                # Ensure we work with Metrics (Rows) x Dates (Cols)
                # StockDataLoader returns Dates as Index (Rows), but we need Metrics as Index for reindexing.
                
                # Checkbox for Growth
                show_growth = st.checkbox(f"Show Growth % for {title}", key=f"growth_{title}")

                df_standard = df.T
                
                if structure:
                    # Structure is list of tuples (Section, [Metrics]). We need flat list of metrics.
                    flat_metrics = [m for section, metrics in structure for m in metrics]
                    # Attempt to reindex. If metric doesn't exist, it adds NaN row.
                    # We utilize the exact names from definitions.
                    df_standard = df_standard.reindex(flat_metrics)
                    # Drop rows that are ALL NaN
                    df_standard = df_standard.dropna(how='all', axis=0)
                    
                if not df_standard.empty:
                    # Sort Columns: Newest First for display usually, but for Growth calc we need Oldest -> Newest
                    
                    # Sort columns descending (Newest First) -> Standard View
                    # USER REQUEST: Make charts (and presumably tables) Earliest to Left (Ascending)
                    df_standard = df_standard.sort_index(axis=1, ascending=True) 
                    
                    # Filter Sparse Columns (optional logic, kept if user likes it)
                    # Keep columns where we have data for at least 50% of the metrics
                    valid_counts = df_standard.count()
                    total_rows = len(df_standard)
                    keep_cols = valid_counts[valid_counts >= (total_rows * 0.5)].index
                    df_standard = df_standard[keep_cols]

                    if show_growth:
                        # Calculate YoY/QoQ Growth
                        # 1. Sort Ascending (Oldest -> Newest) - ALREADY SORTED, but ensuring
                        df_growth = df_standard.sort_index(axis=1, ascending=True)
                        # 2. Pct Change (Computed across columns/time)
                        df_growth = df_growth.pct_change(axis=1) * 100
                        # 3. Sort - Keep Ascending (Earliest Left)
                        df_standard = df_growth # Already ascending
                        
                        # Format
                        format_str = "{:,.2f}%"
                    else:
                        # Scale to Millions
                        df_standard = df_standard / 1e6
                        format_str = "{:,.0f}"

                    # Format columns as Strings YYYY-MM-DD
                    new_cols = []
                    for c in df_standard.columns:
                        if hasattr(c, 'strftime'):
                            new_cols.append(c.strftime('%Y-%m-%d'))
                        else:
                            new_cols.append(str(c))
                    df_standard.columns = new_cols

                    # Bold Styling for key rows
                    key_rows = ["Gross Profit", "Total Revenue", "Net Income", "Operating Income", "EBIT", "EBITDA", "Net Income Common Stockholders"]
                    
                    def highlight_rows(row):
                        if row.name in key_rows:
                            return ['font-weight: bold'] * len(row)
                        return [''] * len(row)

                    st.dataframe(df_standard.style.apply(highlight_rows, axis=1).format(format_str, na_rep="-"))
                        
                else:
                    # Be informative if reindexing caused empty
                    st.info(f"Data available, but no matching metrics found for {title} structure.")

            render_structured_statement(financials, INCOME_STATEMENT_STRUCTURE, "Income Statement")
            render_structured_statement(bs, BALANCE_SHEET_STRUCTURE, "Balance Sheet")
            render_structured_statement(cfs, CASH_FLOW_STRUCTURE, "Cash Flow Statement")

        with tab4:
            st.header("Discounted Cash Flow (DCF) Analysis")
            
            # Sidebar controls for DCF
            st.sidebar.markdown("---")
            st.sidebar.subheader("DCF Assumptions")
            dcf_growth = st.sidebar.slider("Growth Rate (5y)", min_value=0.0, max_value=50.0, value=10.0, step=0.1, format="%.1f%%")
            dcf_terminal_growth = st.sidebar.slider("Terminal Growth", min_value=0.0, max_value=5.0, value=2.5, step=0.1, format="%.1f%%")
            dcf_wacc = st.sidebar.slider("Discount Rate (WACC)", min_value=5.0, max_value=20.0, value=9.0, step=0.1, format="%.1f%%")
            
            # Theme Toggle (Moved from top)
            st.sidebar.markdown("---")
            st.sidebar.write("### Settings")
            icon = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌑 Dark Mode"
            if st.sidebar.button(icon, key="theme_toggle_sidebar", help="Toggle Light/Dark Mode", on_click=toggle_theme):
                pass
            
            # Fetch inputs if missing
            if 'bs' not in locals(): bs = StockDataLoader.fetch_balance_sheet(ticker, quarterly=(fund_freq == "Quarterly"))
            if 'cfs' not in locals(): cfs = StockDataLoader.fetch_cashflow(ticker, quarterly=(fund_freq == "Quarterly"))
            
            try:
                # Need standardized DF where cols are dates ascending
                # Re-fetch or re-process to be safe
                cfs_corr = cfs.T.sort_index(axis=1, ascending=True).dropna(axis=1, how='all')
                bs_corr = bs.T.sort_index(axis=1, ascending=True).dropna(axis=1, how='all')
                
                # Latest Data
                latest_cfs = cfs_corr.iloc[:, -1]
                latest_bs = bs_corr.iloc[:, -1]
                
                # Extract Inputs
                # FCF = Op Cash Flow + CapEx (negative)
                ocf = latest_cfs.get("Total Cash From Operating Activities", latest_cfs.get("Operating Cash Flow", 0))
                capex = latest_cfs.get("Capital Expenditure", 0)
                fcf = ocf + capex
                
                total_debt = latest_bs.get("Total Debt", 0)
                cash = latest_bs.get("Cash And Cash Equivalents", 0) + latest_bs.get("Cash Cash Equivalents And Short Term Investments", 0)
                # Avoid double counting if using composite key
                if cash > latest_bs.get("Cash And Cash Equivalents", 0) * 1.5:
                     cash = latest_bs.get("Cash Cash Equivalents And Short Term Investments", 0) # Prioritize the aggregate
                
                net_debt = total_debt - cash
                
                # Shares
                # Try to get from basic info if possible
                t_info = yf.Ticker(ticker).info
                shares = t_info.get('sharesOutstanding', 1)
                current_price = t_info.get('currentPrice', 0)
                
                st.subheader("DCF Model Inputs (Latest FY)")
                col1, col2, col3 = st.columns(3)
                col1.metric("Free Cash Flow", f"${fcf/1e9:.2f}B")
                col2.metric("Net Debt", f"${net_debt/1e9:.2f}B")
                col3.metric("Shares Outstanding", f"{shares/1e9:.2f}B")

                # Calculate
                dcf_result = analysis.calculate_dcf(
                    free_cash_flow=fcf,
                    growth_rate=dcf_growth / 100.0,
                    terminal_growth_rate=dcf_terminal_growth / 100.0,
                    discount_rate=dcf_wacc / 100.0,
                    shares_outstanding=shares,
                    net_debt=net_debt
                )
                
                fair_value = dcf_result['fair_value']
                upside = (fair_value - current_price) / current_price * 100
                
                st.divider()
                st.subheader("DCF Valuation Results") # Renamed subheading
                
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.metric("Fair Value", f"${fair_value:.2f}", delta=f"{upside:.2f}% vs Current")
                    st.metric("Current Price", f"${current_price:.2f}")
                    
                    if fair_value > current_price:
                        st.success("Undervalued")
                    else:
                        st.error("Overvalued")

                with res_col2:
                    st.write("**Projections**")
                    proj_df = pd.DataFrame(dcf_result['projections'])
                    
                    # Convert relative Year (1, 2) to Actual Year (2025, 2026)
                    from datetime import datetime
                    current_year = datetime.now().year
                    proj_df['Year'] = proj_df['Year'] + current_year
                    
                    # Force Year to string to avoid commas
                    proj_df['Year'] = proj_df['Year'].apply(lambda x: str(x))

                    st.dataframe(proj_df.style.format({"FCF": "${:,.0f}", "PV": "${:,.0f}"}), hide_index=True)
                    st.caption(f"Terminal Value: ${dcf_result['terminal_value']:,.0f}")
                    
                # Chart
                st.subheader("Projected Free Cash Flow")
                chart_data = proj_df.set_index("Year")['FCF']
                st.bar_chart(chart_data)

            except Exception as e:
                st.error(f"Could not calculate DCF: {e}")
