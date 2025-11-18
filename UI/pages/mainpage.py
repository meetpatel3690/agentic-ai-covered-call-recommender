import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add backend integration path
backend_integration_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_integration_path))

from backend_integration import fetch_live_options_data
from backend.strategy_recommendation_agent_langgraph import create_strategy_agent

# Page configuration
st.set_page_config(page_title="Option Recommendations", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 100% !important;
    }
    
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        padding: 12px 60px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .navbar-title {
        text-align: center;
        color: white;
        font-size: 25px;
        font-weight: bold;
    }
    
    .content-wrapper {
        margin-top: 50px;
    }
    
    .summary-card {
        background: linear-gradient(135deg, #2c5282 0%, #1e3a5f 100%);
        color: white;
        padding: 25px 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 15px;
    }
    
    .summary-card .label {
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 12px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .summary-card .value {
        font-size: 32px;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .summary-card.diversification .value {
        font-size: 18px;
        font-weight: 600;
        line-height: 1.6;
    }
    
    .main {
        padding-bottom: 20px !important;
        overflow: hidden;
    }
    
    /* Reduce spacing around elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    .stTabs {
        margin-top: 0rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    
    h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .dataframe {
        font-size: 14px !important;
    }
    
    .dataframe th {
        background-color: #1e3a5f !important;
        color: white !important;
        font-weight: 600 !important;
        text-align: center !important;
        padding: 10px !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 10 !important;
    }
    
    .dataframe td {
        text-align: center !important;
        padding: 8px !important;
    }
    
    [data-testid="stDataFrameToolbar"] button {
        color: #1e3a5f !important;
        font-size: 18px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'options_data' not in st.session_state:
    st.session_state.options_data = None
if 'delta_data' not in st.session_state:
    st.session_state.delta_data = None
if 'portfolio_metrics' not in st.session_state:
    st.session_state.portfolio_metrics = None
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'agent2_analysis' not in st.session_state:
    st.session_state.agent2_analysis = None
if 'highlighted_cells' not in st.session_state:
    st.session_state.highlighted_cells = {}
if 'show_highlights' not in st.session_state:
    st.session_state.show_highlights = False
if 'agent2_instance' not in st.session_state:
    st.session_state.agent2_instance = None

# Fetch live data on first load
if not st.session_state.data_loaded:
    with st.spinner("🔄 Fetching Live Options Data from Stock Market..."):
        try:
            options_df, delta_df, metrics, portfolio = fetch_live_options_data()
            
            if options_df is not None and not options_df.empty:
                st.session_state.options_data = options_df
                st.session_state.delta_data = delta_df  # Store Delta data
                st.session_state.portfolio_metrics = metrics
                st.session_state.portfolio = portfolio
                st.session_state.data_loaded = True
                #st.success(" Live data loaded successfully!")
            else:
                st.error("❌ Failed to fetch options data. Please check your portfolio.")
                
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            import traceback
            st.code(traceback.format_exc())

# Settings in sidebar
with st.sidebar:
    st.header("Display Settings")
    table_font_size = st.slider("Table Font Size", 10, 20, 14)
    card_font_size = st.slider("Card Font Size", 16, 32, 24)
    table_height = st.slider("Table Height (px)", 400, 800, 600)

# Navigation Bar
st.markdown("""
    <div class="navbar">
        <div class="navbar-title">
            📊 Option Recommending Agent
        </div>
    </div>
""", unsafe_allow_html=True)

# # Back button
# if st.button("⬅️ Back to Input", key="back_button"):
#     # Clear loaded data so it refreshes on next visit
#     st.session_state.data_loaded = False
#     st.switch_page("app.py")

# Content Wrapper
st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

# Main layout
col_left, col_right = st.columns([4, 1])

with col_left:
    tab1, tab2 = st.tabs(["📊 Strike Price Details", "📈 Graphical Representation"])
    
    with tab1:
        if st.session_state.options_data is not None:
            options_df = st.session_state.options_data
            
            # Apply custom font size
            st.markdown(f"""
                <style>
                .dataframe {{
                    font-size: {table_font_size}px !important;
                }}
                </style>
            """, unsafe_allow_html=True)
            
            # Display dataframe with or without highlighting based on Agent 2 status
            if st.session_state.show_highlights and st.session_state.highlighted_cells:
                # Create styled dataframe with orange highlighting
                def highlight_max_premium(row):
                    """Apply green background to cells with highest premium"""
                    styles = [''] * len(row)
                    
                    # Check if this row should have any highlighted cells
                    if row.name in st.session_state.highlighted_cells:
                        cols_to_highlight = st.session_state.highlighted_cells[row.name]
                        
                        for col_name in cols_to_highlight:
                            if col_name in row.index:
                                col_idx = row.index.get_loc(col_name)
                                styles[col_idx] = 'background-color: #90EE90; color: black; font-weight: bold'
                    
                    return styles
                
                # Apply styling
                styled_df = options_df.style.apply(highlight_max_premium, axis=1)
                
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=table_height
                )
                
                st.info("🟢 Green cells indicate the Best premium for each stock ( Recommendation Engine Analysis )")
                
                # PHASE 9: Show Income Projections FIRST (moved to top)
                if st.session_state.agent2_analysis and st.session_state.agent2_analysis.get('income_projections'):
                    with st.expander("💰 Income Projections (Monthly)", expanded=True):
                        income_data = st.session_state.agent2_analysis['income_projections']
                        primaries = st.session_state.agent2_analysis.get('primary_recommendations', {})
                        secondaries = st.session_state.agent2_analysis.get('secondary_recommendations', {})
                        allocations = st.session_state.agent2_analysis.get('contract_allocations', {})
                        
                        # Calculate total portfolio income
                        total_income = sum(data['total_income'] for data in income_data.values())
                        
                        # Display portfolio total
                        st.markdown(f"### 🎯 Total Monthly Income: ${total_income:,.2f}")
                        st.markdown("---")
                        
                        # Display per-stock breakdown
                        for stock in sorted(income_data.keys()):
                            income = income_data[stock]
                            primary = primaries.get(stock, {})
                            secondary = secondaries.get(stock)
                            allocation = allocations.get(stock, {})
                            
                            # Create columns for layout
                            col1, col2, col3 = st.columns([2, 2, 2])
                            
                            with col1:
                                st.markdown(f"### {stock}")
                                if allocation:
                                    st.caption(f"📊 {allocation.get('recommended', 1)} contracts recommended")
                                    if allocation.get('buffer', 0) > 0:
                                        st.caption(f"🛡️ {allocation['buffer']} contract buffer")
                                else:
                                    st.caption(f"📊 {income['contracts_used']} contract(s)")
                            
                            with col2:
                                st.markdown("**Strategy:**")
                                if primary:
                                    st.write(f"📈 Primary: ${primary['strike']} exp {primary['expiry']}")
                                if secondary:
                                    st.write(f"📈 Secondary: ${secondary['strike']} exp {secondary['expiry']}")
                                    st.success("💰💰 Multi-trade strategy!")
                                elif primary:
                                    st.info("💰 Single-trade strategy")
                            
                            with col3:
                                st.markdown("**Income:**")
                                if income['primary_income'] > 0:
                                    st.write(f"Primary: ${income['primary_income']:,.2f}")
                                if income['secondary_income'] > 0:
                                    st.write(f"Secondary: ${income['secondary_income']:,.2f}")
                                st.markdown(f"**Total: ${income['total_income']:,.2f}**")
                            
                            st.markdown("---")
                        
                        # Show strategy summary
                        multi_count = sum(1 for inc in income_data.values() if inc['has_secondary'])
                        single_count = len(income_data) - multi_count
                        
                        st.info(f"📊 **Strategy Mix:** {multi_count} multi-trade, {single_count} single-trade")
                        
                        if multi_count > 0:
                            st.success("💡 **Tip:** Multi-trade strategies can earn 1.5x - 2x more income!")
                
                # Show LLM Insights (NEW in LangGraph version!)
                if st.session_state.agent2_analysis and st.session_state.agent2_analysis.get('llm_insights'):
                    with st.expander("🧠 LLM Professional Insights", expanded=True):
                        st.markdown(st.session_state.agent2_analysis['llm_insights'])
            else:
                # Display without highlighting (Agent 2 not run yet)
                st.dataframe(
                    options_df,
                    use_container_width=True,
                    height=table_height
                )
                
                st.info("💡 Click '🎯 Options Strategy Recommendation' above to identify and highlight the best premium opportunities")
            
            # # Download button
            # csv = options_df.to_csv(index=False)
            # st.download_button(
            #     label=" Download Options Data",
            #     data=csv,
            #     file_name="options_recommendations.csv",
            #     mime="text/csv"
            # )
        else:
            st.info(" No options data loaded. Please go back and click 'Get Recommendations'")
    
    with tab2:
        st.markdown("### 📈 Graphical Representation")
        
        # PHASE 9: Show income charts if Agent 2 analysis available
        if st.session_state.agent2_analysis and st.session_state.agent2_analysis.get('income_projections'):
            income_data = st.session_state.agent2_analysis['income_projections']
            
            # Prepare data for charts
            stocks = sorted(income_data.keys())
            primary_incomes = [income_data[s]['primary_income'] for s in stocks]
            secondary_incomes = [income_data[s]['secondary_income'] for s in stocks]
            total_incomes = [income_data[s]['total_income'] for s in stocks]
            contracts = [income_data[s]['contracts_used'] for s in stocks]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 💰 Income by Stock")
                income_chart_data = pd.DataFrame({
                    'Stock': stocks,
                    'Primary Income': primary_incomes,
                    'Secondary Income': secondary_incomes,
                    'Total Income': total_incomes
                })
                st.bar_chart(income_chart_data.set_index('Stock')[['Primary Income', 'Secondary Income']], height=300)
                st.caption("📊 Green = Primary, Red = Secondary")
            
            with col2:
                st.markdown("#### 📊 Contracts by Stock")
                contracts_chart_data = pd.DataFrame({
                    'Stock': stocks,
                    'Contracts': contracts
                })
                st.bar_chart(contracts_chart_data.set_index('Stock')['Contracts'], height=300)
                st.caption(f"Total: {sum(contracts)} contracts")
            
            # Income breakdown
            col3, col4 = st.columns(2)
            
            with col3:
                total_portfolio_income = sum(total_incomes)
                st.metric(
                    label="💵 Total Monthly Income",
                    value=f"${total_portfolio_income:,.0f}",
                    delta=f"{len([i for i in income_data.values() if i['has_secondary']])} multi-trade"
                )
            
            with col4:
                avg_income_per_contract = total_portfolio_income / sum(contracts) if sum(contracts) > 0 else 0
                st.metric(
                    label="📈 Avg Income per Contract",
                    value=f"${avg_income_per_contract:,.0f}",
                    delta=f"{sum(contracts)} total contracts"
                )
        
        # Use stock_contracts for charts (actual contracts based on shares)
        elif st.session_state.portfolio_metrics and st.session_state.portfolio_metrics.get('stock_contracts'):
            stock_contracts = st.session_state.portfolio_metrics['stock_contracts']
            
            chart_data = pd.DataFrame({
                'Stock': list(stock_contracts.keys()),
                'Contracts': list(stock_contracts.values())
            })
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Contracts by Stock")
                st.bar_chart(chart_data.set_index('Stock')['Contracts'], height=300)
            
            with col2:
                st.markdown("#### Portfolio Distribution")
                st.bar_chart(chart_data.set_index('Stock')['Contracts'], height=300)
        else:
            st.info("📊 Charts will appear when data is loaded")

# Right Panel
with col_right:
    st.markdown("### Options Chain Analysis")
    
    # Add Agent 2 Button
    if st.button("🎯 Options Strategy Recommendation", 
                type="primary", 
                use_container_width=True,
                disabled=st.session_state.options_data is None):
        if st.session_state.options_data is not None:
            # PRINT DELTA DATA TO VERIFY IT'S STORED
            print("\n" + "="*70)
            print("📊 DELTA DATA VERIFICATION")
            print("="*70)
            if st.session_state.delta_data is not None:
                print(f"✅ Delta Data Shape: {st.session_state.delta_data.shape}")
                print(f"\n📋 Delta Data Columns: {list(st.session_state.delta_data.columns)}")
                print(f"\n📊 Delta Data (First 10 rows):")
                print(st.session_state.delta_data.head(10).to_string())
                print("\n" + "="*70)
            else:
                print("❌ Delta Data is None!")
                print("="*70)
            
            with st.spinner("🤖 The Strategy Recommending Engine  is analyzing options and finding best premiums..."):
                try:
                    # Create LangGraph Agent 2
                    agent = create_strategy_agent()
                    
                    # Prepare portfolio data in correct format (symbol -> shares)
                    portfolio_dict = {}
                    if st.session_state.portfolio:
                        for stock in st.session_state.portfolio:
                            portfolio_dict[stock['symbol']] = stock['shares']
                    
                    # Get current date
                    current_date = pd.Timestamp.now().strftime('%Y-%m-%d')
                    
                    print("\n" + "="*70)
                    print("📊 PHASE 8: COMPLETE WORKFLOW INTEGRATION")
                    print("="*70)
                    print(f"📋 Options Data: {st.session_state.options_data.shape}")
                    print(f"📋 Delta Data: {st.session_state.delta_data.shape if st.session_state.delta_data is not None else 'None'}")
                    print(f"📋 Portfolio: {portfolio_dict}")
                    print(f"📅 Current Date: {current_date}")
                    print(f"🎯 Analysis Mode: premium_delta")
                    print("="*70 + "\n")
                    
                    # Run Agent 2 Analysis (LangGraph workflow) with COMPLETE data
                    analysis_results = agent.analyze(
                        options_df=st.session_state.options_data,
                        delta_data=st.session_state.delta_data,  # NOW PASSED!
                        portfolio_data=portfolio_dict,            # NOW PASSED!
                        current_date=current_date,                # NOW PASSED!
                        analysis_mode="premium_delta"            # NOW USING PART 2!
                    )
                    
                    # Store results in session state
                    st.session_state.agent2_analysis = analysis_results
                    st.session_state.highlighted_cells = analysis_results.get('highlighted_cells', {})
                    st.session_state.show_highlights = True
                    st.session_state.agent2_instance = agent
                    
                    st.success("✅ The Strategy Recommending Engine Analysis Complete! Best recommendations highlighted in green below.")
                    st.rerun()  # Trigger rerun to update the UI with highlights
                    
                except Exception as e:
                    st.error(f"❌ The Strategy Recommending Engine Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        else:
            st.warning("⚠️ No options data loaded. Please go back and click 'Get Recommendations' first.")
    
    # Bold divider with reduced spacing
    st.markdown("""
        <hr style="border: none; border-top: 3px solid #e5e7eb; margin: 1rem 0 0.5rem 0;">
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <style>
        .summary-card .value {{
            font-size: {card_font_size}px !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Get metrics
    metrics = st.session_state.portfolio_metrics or {}
    total_contracts = metrics.get('total_contracts', 0)  # Based on shares/100
    stock_contracts = metrics.get('stock_contracts', {})  # Contracts per stock
    total_income = metrics.get('total_income', 0.0)
    available = metrics.get('available_capital', 550000.0)
    
    # Only show cards if Agent 2 analysis is available
    if st.session_state.agent2_analysis and st.session_state.agent2_analysis.get('income_projections'):
        # Card 1: Total Recommended Contracts
        contract_allocations = st.session_state.agent2_analysis.get('contract_allocations', {})
        recommended_contracts = sum(alloc['recommended'] for alloc in contract_allocations.values())
        
        st.markdown(f"""
            <div class="summary-card" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
                <div class="label">📋 Total Recommended Contracts</div>
                <div class="value">{recommended_contracts}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Card 2: Projected Income
        income_projections = st.session_state.agent2_analysis['income_projections']
        total_monthly_income = sum(data['total_income'] for data in income_projections.values())
        multi_trades = sum(1 for data in income_projections.values() if data['has_secondary'])
        
        st.markdown(f"""
            <div class="summary-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                <div class="label">💰 Monthly Income</div>
                <div class="value">${total_monthly_income:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Card 3: Strategy Mix
        st.markdown(f"""
            <div class="summary-card" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);">
                <div class="label">📊 Strategy Mix</div>
                <div class="value" style="font-size: 16px;">{multi_trades} Multi-trade<br>{len(income_projections) - multi_trades} Single-trade</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Card 4: Diversification (using recommended contracts from Agent 2)
        if contract_allocations:
            div_text = "<br>".join([f"<strong>{symbol}:</strong> {alloc['recommended']} contract{'s' if alloc['recommended'] != 1 else ''}" 
                                    for symbol, alloc in contract_allocations.items()])
        else:
            div_text = "No contracts"
        
        st.markdown(f"""
            <div class="summary-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                <div class="label">📊 Diversification</div>
                <div class="value" style="font-size: 18px; font-weight: 600; line-height: 1.8;">{div_text}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Card 4: Available Capital
    # st.markdown(f"""
    #     <div class="summary-card">
    #         <div class="label">Available Capital</div>
    #         <div class="value">${available:,.0f}</div>
    #     </div>
    # """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)