import streamlit as st
from datetime import datetime
from streamlit_searchbox import st_searchbox
from utils.stock_api import StockAPI
import json
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add parent directory to path for backend integration
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

st.set_page_config(
    page_title="Option Recommending Agent",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 0.2rem;
    }
    .stock-symbol { font-weight: bold; color: #2563eb; }
    .stock-name { font-size: 1.4rem; color: #1f2937; font-weight: bold; }
    .stock-price { font-size: 1.4rem; color: #059669; font-weight: bold; }
    .portfolio-stat {
        background: linear-gradient(to bottom right, #dbeafe, #eff6ff);
        border: 1px solid #93c5fd;
        border-radius: 1rem;
        padding: 0.5rem;
        text-align: center;
    }
    .stat-value { font-size: 1.5rem; font-weight: bold; color: #1e40af; }
    .stat-label { font-size: 0.95rem; color: #6b7280; }
    .portfolio-card {
        background: linear-gradient(to bottom right, #f9fafb, #ffffff);
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .portfolio-card:hover { box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Storage - portfolio_data.json in UI folder
STORAGE_FILE = Path(__file__).parent / "portfolio_data.json"

def save_portfolio(portfolio):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)

def load_portfolio():
    if STORAGE_FILE.exists():
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return []

# Initialize
stock_api = StockAPI()

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_portfolio()
if 'selected_stock_for_modal' not in st.session_state:
    st.session_state.selected_stock_for_modal = None
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False
if 'last_selected' not in st.session_state:
    st.session_state.last_selected = None
if 'searchbox_counter' not in st.session_state:
    st.session_state.searchbox_counter = 0
if 'processed_selections' not in st.session_state:
    st.session_state.processed_selections = set()
if 'selected_stock_for_update' not in st.session_state:
    st.session_state.selected_stock_for_update = None
if 'show_update_modal' not in st.session_state:
    st.session_state.show_update_modal = False

# Search function
def search_stocks_live(search_term: str):
    """Called on every keystroke - returns list of display strings"""
    if not search_term or len(search_term) < 1:
        return []
    
    try:
        results = stock_api.search_stocks(search_term)
        return [f"{stock['name']} ({stock['symbol']})" for stock in results]
    except:
        return []

# Helper functions
def add_stock_to_portfolio(stock_data, shares):
    price = stock_api.get_stock_price(stock_data['symbol'])
    portfolio_stock = {
        'id': len(st.session_state.portfolio) + 1,
        'symbol': stock_data['symbol'],
        'name': stock_data['name'],
        'shares': shares,
        'price': price,
        'date_added': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    st.session_state.portfolio.append(portfolio_stock)
    save_portfolio(st.session_state.portfolio)
    
    # Reset all state variables to allow new selection
    st.session_state.show_modal = False
    st.session_state.selected_stock_for_modal = None
    st.session_state.last_selected = None
    st.session_state.searchbox_counter += 1
    
    return True

def remove_stock(stock_id):
    st.session_state.portfolio = [s for s in st.session_state.portfolio if s['id'] != stock_id]
    save_portfolio(st.session_state.portfolio)

def update_stock(stock_id, new_shares):
    for stock in st.session_state.portfolio:
        if stock['id'] == stock_id:
            stock['shares'] = new_shares
            # Update the price as well to get current market value
            price = stock_api.get_stock_price(stock['symbol'])
            if price:
                stock['price'] = price
            break
    save_portfolio(st.session_state.portfolio)

def calculate_portfolio_stats():
    if not st.session_state.portfolio:
        return {'total_stocks': 0, 'total_shares': 0, 'total_value': 0.0}
    return {
        'total_stocks': len(st.session_state.portfolio),
        'total_shares': sum(s['shares'] for s in st.session_state.portfolio),
        'total_value': sum(s['shares'] * (s['price'] or 0) for s in st.session_state.portfolio)
    }

def open_modal(stock):
    st.session_state.selected_stock_for_modal = stock
    st.session_state.show_modal = True

def close_modal():
    st.session_state.show_modal = False
    st.session_state.selected_stock_for_modal = None

def open_update_modal(stock):
    st.session_state.selected_stock_for_update = stock
    st.session_state.show_update_modal = True

def close_update_modal():
    st.session_state.show_update_modal = False
    st.session_state.selected_stock_for_update = None

# Modal
@st.dialog("Add Shares to Portfolio", width="large")
def show_shares_modal():
    stock = st.session_state.selected_stock_for_modal
    if stock:
        st.markdown(f"### {stock['name']}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Symbol:** `{stock['symbol']}`")
        with col2:
            st.markdown(f"**Type:** {stock['type']}")
        
        st.divider()
        
        shares = st.number_input(
            "Number of Shares", 
            min_value=1, 
            max_value=1000000, 
            value=100, 
            step=1,
            help="Minimum 100 shares required"
        )
        
        if shares < 100:
            st.error(f"**You are not eligible** - Minimum 100 shares required. You entered: {shares}")
                
        st.divider()
        
        col_cancel, col_add = st.columns(2)
        
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                close_modal()
                st.rerun()
        
        with col_add:
            add_button_disabled = shares < 100
            
            if st.button(
                "Add to Portfolio", 
                type="primary", 
                use_container_width=True,
                disabled=add_button_disabled
            ):
                if shares >= 100:
                    with st.spinner(f"Fetching price for {stock['symbol']}..."):
                        add_stock_to_portfolio(stock, shares)
                    st.success(f"Added {shares} shares of {stock['symbol']}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("You are not eligible - Minimum 100 shares required")

@st.dialog("Update Shares", width="large")
def show_update_shares_modal():
    stock = st.session_state.selected_stock_for_update
    if stock:
        st.markdown(f"### {stock['name']}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Symbol:** `{stock['symbol']}`")
        with col2:
            st.markdown(f"**Current Shares:** {stock['shares']:,}")
        
        st.divider()
        
        shares = st.number_input(
            "New Number of Shares", 
            min_value=1, 
            max_value=1000000, 
            value=stock['shares'],  # Pre-fill with current value
            step=1,
            help="Minimum 100 shares required"
        )
        
        if shares < 100:
            st.error(f"**You are not eligible** - Minimum 100 shares required. You entered: {shares}")
                
        st.divider()
        
        col_cancel, col_update = st.columns(2)
        
        with col_cancel:
            if st.button("Cancel", use_container_width=True, key="cancel_update"):
                close_update_modal()
                st.rerun()
        
        with col_update:
            update_button_disabled = shares < 100
            
            if st.button(
                "Update Portfolio", 
                type="primary", 
                use_container_width=True,
                disabled=update_button_disabled,
                key="confirm_update"
            ):
                if shares >= 100:
                    with st.spinner(f"Updating {stock['symbol']}..."):
                        update_stock(stock['id'], shares)
                    st.success(f"Updated to {shares} shares of {stock['symbol']}!")
                    close_update_modal()
                    st.rerun()
                else:
                    st.error("You are not eligible - Minimum 100 shares required")

# Main Layout
st.markdown('<div class="main-header">📈 Option Recommending Agent</div>', unsafe_allow_html=True)

if st.session_state.show_modal and st.session_state.selected_stock_for_modal:
    show_shares_modal()

if st.session_state.show_update_modal and st.session_state.selected_stock_for_update:
    show_update_shares_modal()

col1, col2 = st.columns([1, 1])

# Left Column - Search
with col1:
    st.subheader("Search Stocks")
    
    searchbox_key = f"stock_searchbox_{st.session_state.searchbox_counter}"
    
    selected_text = st_searchbox(
        search_stocks_live,
        placeholder="Type to search: 'A', 'Apple', 'MSFT'...",
        clear_on_submit=True,
        key=searchbox_key
    )
    
    # Handle selection
    if selected_text:
        selection_id = f"{selected_text}_{st.session_state.searchbox_counter}"
        
        if selection_id not in st.session_state.processed_selections:
            st.session_state.processed_selections.add(selection_id)
            
            try:
                if '(' in selected_text and ')' in selected_text:
                    symbol = selected_text.split('(')[1].split(')')[0].strip()
                    results = stock_api.search_stocks(symbol)
                    
                    if results and len(results) > 0:
                        stock = results[0]
                        already_added = any(p['symbol'] == stock['symbol'] for p in st.session_state.portfolio)
                        
                        if already_added:
                            st.warning(f"**{stock['name']} ({stock['symbol']})** is already in your portfolio")
                        else:
                            open_modal(stock)
                            st.rerun()
                    else:
                        st.error(f"Could not find data for {symbol}")
            except Exception as e:
                st.error(f"Error processing selection: {e}")
    
    st.caption("Results appear as you type - no Enter key needed!")
    
    if st.session_state.portfolio:
        st.info(f"**Portfolio stocks:** {', '.join([s['symbol'] for s in st.session_state.portfolio])}")
        
        # Get Recommendations Button - positioned right after portfolio stocks info
        st.markdown("""
        <style>
        div.stButton > button {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 15px 20px;
            border-radius: 10px;
            border: none;
            width: 100%;
            margin-top: 10px;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
            transform: scale(1.02);
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("Get Options Data", key="get_recommendations"):
            st.session_state.portfolio_input = st.session_state.portfolio
            st.switch_page("pages/mainpage.py")

# Right Column - Portfolio
with col2:
    st.subheader("My Portfolio")
    
    stats = calculate_portfolio_stats()
    
    # Stats
    stat_cols = st.columns(3)
    with stat_cols[0]:
        st.markdown(f'<div class="portfolio-stat"><div class="stat-value">{stats["total_stocks"]}</div><div class="stat-label">Stocks</div></div>', unsafe_allow_html=True)
    with stat_cols[1]:
        st.markdown(f'<div class="portfolio-stat"><div class="stat-value">{stats["total_shares"]:,}</div><div class="stat-label">Shares</div></div>', unsafe_allow_html=True)
    with stat_cols[2]:
        st.markdown(f'<div class="portfolio-stat"><div class="stat-value">${stats["total_value"]:,.0f}</div><div class="stat-label">Value</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Portfolio list
    if st.session_state.portfolio:
        with st.container(height=550):
            for stock in st.session_state.portfolio:
                st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
                
                stock_col, button_col = st.columns([5, 1])
                
                with stock_col:
                    st.markdown(f'**{stock["name"]}** <span class="stock-symbol">({stock["symbol"]})</span>', unsafe_allow_html=True)
                    st.caption(f"📈 {stock['shares']:,} shares")
                    
                    if stock['price']:
                        total = stock['shares'] * stock['price']
                        st.markdown(f"**${stock['price']:.2f}** per share")
                        st.markdown(f'<span class="stock-price">Total: ${total:,.2f}</span>', unsafe_allow_html=True)
                    else:
                        st.caption("Price not available")
                
                with button_col:
                    if st.button("✏️", key=f"update_{stock['id']}", help="Update shares"):
                        open_update_modal(stock)
                        st.rerun()
                    if st.button("🗑️", key=f"remove_{stock['id']}", help="Remove stock"):
                        remove_stock(stock['id'])
                        st.success("Removed!")
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("**Ahh..!! Your portfolio looks empty**\n\nAdd it now")