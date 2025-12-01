# -*- coding: utf-8 -*-
"""
Enhanced LLM-Orchestrated Options Analysis Agent (Version 2)
A sophisticated agent where LLM acts as the central orchestrator for:
1. Converting free text to stock symbols
2. Formatting raw Alpha Vantage data into structured 6x6 grids
3. Presenting results in user-friendly format

=============================================================================
ATTRIBUTION:
=============================================================================
- Project Concept & Requirements: Meet Patel (@meetpatel3690)
- Basic Project Structure & Setup: Meet Patel (@meetpatel3690)
- AI Integration & Advanced LLM Orchestration: AI Assistant (GitHub Copilot)
- Complex Data Processing & Matrix Generation: AI Assistant (GitHub Copilot)
- Error Handling & Workflow Management: AI Assistant (GitHub Copilot)
- Documentation & Code Comments: AI Assistant (GitHub Copilot)
=============================================================================
"""

from tkinter import Image
from typing import TypedDict, List, Optional, Union, Annotated
import operator
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser as dateparser
import re
import json
import os
from dotenv import load_dotenv
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pathlib import Path

# Alpha Vantage imports
from alpha_vantage.options import Options
from alpha_vantage.timeseries import TimeSeries

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# =============================================================================
# BASIC UTILITY FUNCTIONS - Written by: Meet Patel (@meetpatel3690)
# =============================================================================

def get_most_recent_trading_day() -> str:
    """
    Get the most recent trading day with likely options data availability (2-3 days back for data lag)
    Author: Meet Patel (@meetpatel3690)
    """
    today = datetime.now()
    
    # Go back 3-4 days to account for data availability lag
    # This ensures we get the most recent day that likely has options data
    days_back = 4
    
    # Start from a few days ago to account for data lag
    target_date = today - timedelta(days=days_back)
    
    # Ensure it's a weekday (Monday=0, Sunday=6)
    while target_date.weekday() > 4:  # If it's Saturday (5) or Sunday (6)
        target_date = target_date - timedelta(days=1)
    
    return target_date.strftime("%Y-%m-%d")


# =============================================================================
# 1. DATA STRUCTURE SCHEMA - Designed by: Meet Patel (@meetpatel3690)
#    Implementation assistance: AI Assistant (GitHub Copilot)
# =============================================================================

class OptionsAnalysisState(TypedDict):
    """
    Enhanced state schema for LLM-orchestrated workflow
    Data structure designed by: Meet Patel (@meetpatel3690)
    """
    # Input
    user_input: str                          # Original user input
    symbols: List[str]                       # Raw symbols/company names
    date: Optional[str]                      # Analysis date
    
    # Processing states
    converted_tickers: List[str]             # LLM-converted ticker symbols
    spot_prices: dict                        # Current prices for each ticker
    raw_options_data: dict                   # Raw Alpha Vantage response (per ticker)
    
    # LLM-orchestrated results
    formatted_options_data: Optional[pd.DataFrame]  # LLM-formatted 6x6 matrix
    delta_data: Optional[pd.DataFrame]       # Delta values for Agent 2 (not displayed in UI)
    
    # Metadata
    messages: Annotated[List[BaseMessage], add_messages]  # Conversation history
    status: str                              # Current processing status
    errors: List[str]                        # Any errors encountered

# =============================================================================
# 2. MAIN AGENT CLASS - Core Structure by: Meet Patel (@meetpatel3690)
#    Advanced Implementation: AI Assistant (GitHub Copilot)
# =============================================================================

class LLMOptionsAgent:
    def __init__(self):
        """
        Initialize the LLM-Orchestrated Options Analysis Agent
        Basic setup by: Meet Patel (@meetpatel3690)
        Advanced initialization: AI Assistant (GitHub Copilot)
        """
        # Load API keys
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.alpha_vantage_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not found in .env file")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        # Initialize clients
        self.options_client = Options(key=self.alpha_vantage_key, output_format="pandas")

        self.time_series_client = TimeSeries(key=self.alpha_vantage_key, output_format="pandas")
        
        self.llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.1,api_key=self.openai_key)
        
        # Build the LLM-orchestrated workflow
        self.workflow = self._build_llm_workflow()
        
        print("🎯 LLM-Orchestrated Options Analysis Agent initialized!")
       
    # =============================================================================
    # 3. HELPER FUNCTIONS - Written by: Meet Patel (@meetpatel3690)
    # =============================================================================
    
    def get_spot_price(self, symbol: str) -> float:
        """
        Get current stock price for a symbol
        Author: Meet Patel (@meetpatel3690)
        """
        try:
            quote_df, _ = self.time_series_client.get_quote_endpoint(symbol)
            price_col = "05. price"
            if price_col not in quote_df.columns:
                daily_df, _ = self.time_series_client.get_daily(symbol, outputsize="compact")
                return float(daily_df["4. close"].iloc[0])
            return float(quote_df[price_col].iloc[0])
        except Exception as e:
            raise ValueError(f"Failed to get price for {symbol}: {e}")

    # =============================================================================
    # 4. ADVANCED LLM-ORCHESTRATED NODES - AI Assistant (GitHub Copilot)
    # =============================================================================
    
    def llm_parse_and_convert_node(self, state: OptionsAnalysisState) -> OptionsAnalysisState:
        """
        LLM parses input and converts company names to ticker symbols
        Advanced LLM integration by: AI Assistant (GitHub Copilot)
        """
        user_input = state["user_input"]
        
        # Add system message
        state["messages"].append(SystemMessage(content="🤖 LLM Orchestrator starting analysis..."))
        state["messages"].append(HumanMessage(content=user_input))
        
        print(f"🧠 LLM parsing and converting: '{user_input}'")
        
        # LLM prompt for parsing and conversion
        prompt = f"""
        You are a financial data analyst. Parse the user input and convert any company names to stock ticker symbols.
        
        USER INPUT: "{user_input}"
        
        TASKS:
        1. Extract all company names and/or ticker symbols from the input
        2. Convert company names to their corresponding stock ticker symbols
        3. Return ONLY a JSON object with the conversion results
        
        OUTPUT FORMAT:
        {{
            "symbols": ["AAPL", "TSLA", "MSFT"],
            "conversions": [
                {{"input": "Apple", "ticker": "AAPL", "converted": true}},
                {{"input": "TSLA", "ticker": "TSLA", "converted": false}},
                {{"input": "Microsoft", "ticker": "MSFT", "converted": true}}
            ]
        }}
        
        RULES:
        - If input is already a ticker symbol, mark converted: false
        - If company name converted to ticker, mark converted: true
        - If unknown company, use "UNKNOWN" as ticker
        - Extract symbols from comma-separated lists or natural language
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result_text = response.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                conversion_result = json.loads(json_match.group())
                
                state["symbols"] = [conv["input"] for conv in conversion_result["conversions"]]
                state["converted_tickers"] = conversion_result["symbols"]
                state["status"] = "llm_converted"
                
                print("📈 LLM Conversion Results:")
                for conv in conversion_result["conversions"]:
                    status = "✅ Converted" if conv["converted"] else "📌 Already ticker"
                    print(f"   '{conv['input']}' → {conv['ticker']} ({status})")
                
            else:
                # Fallback parsing
                if "," in user_input:
                    symbols = [s.strip() for s in user_input.split(",")]
                else:
                    symbols = [user_input.strip()]
                
                state["symbols"] = symbols
                state["converted_tickers"] = symbols  # Assume they're already tickers
                state["status"] = "fallback_parsed"
                state["errors"].append("LLM parsing failed, using fallback")
                
        except Exception as e:
            print(f"❌ LLM parsing error: {e}")
            state["errors"].append(f"LLM parsing failed: {e}")
            # Fallback to simple parsing
            state["symbols"] = [user_input.strip()]
            state["converted_tickers"] = [user_input.strip()]
            state["status"] = "error_fallback"
        
        # Set default date to most recent trading day
        if not state.get("date"):
            state["date"] = get_most_recent_trading_day()
            
        return state
    
    def fetch_financial_data_node(self, state: OptionsAnalysisState) -> OptionsAnalysisState:
        """
        Fetch spot prices and raw options data from Alpha Vantage
        Basic structure by: Meet Patel (@meetpatel3690)
        Advanced implementation: AI Assistant (GitHub Copilot)
        """
        tickers = state["converted_tickers"]
        spot_prices = {}
        raw_options_data = {}
        analysis_date = state["date"]
        
        print(f"📊 Fetching financial data for {len(tickers)} symbols...")
        
        for ticker in tickers:
            if ticker == "UNKNOWN":
                continue
                
            try:
                # Get spot price
                price = self.get_spot_price(ticker)
                spot_prices[ticker] = price
                print(f"   💰 {ticker}: ${price:.2f}")
                
                # Get raw options data
                options_df, _ = self.options_client.get_historical_options(symbol=ticker, date=analysis_date)
                if not options_df.empty:
                    # Convert to JSON for LLM processing
                    raw_options_data[ticker] = {
                        "spot_price": price,
                        "options_data": options_df.to_dict('records'),
                        "columns": list(options_df.columns)
                    }
                    print(f"   📈 {ticker}: Retrieved {len(options_df)} options records")
                    
                    # DEBUG: Check if Delta is in the data
                    if 'delta' in options_df.columns:
                        non_null_deltas = options_df['delta'].notna().sum()
                        total_options = len(options_df)
                        print(f"   🔍 Delta column found: {non_null_deltas}/{total_options} options have Delta values")
                    else:
                        print(f"   ⚠️  Delta column NOT found in API response!")
                        print(f"   📋 Available columns: {list(options_df.columns)}")
                else:
                    print(f"   ⚠️  {ticker}: No options data available")
                    
            except Exception as e:
                print(f"   ❌ {ticker}: Error - {e}")
                state["errors"].append(f"Failed to fetch data for {ticker}: {e}")
        
        state["spot_prices"] = spot_prices
        state["raw_options_data"] = raw_options_data
        state["status"] = "data_fetched"
        
        return state
    
    def llm_format_options_matrix_node(self, state: OptionsAnalysisState) -> OptionsAnalysisState:
        """
        LLM formats raw options data into structured 6x6 matrix
        Complex data processing by: AI Assistant (GitHub Copilot)
        """
        raw_data = state["raw_options_data"]
        spot_prices = state["spot_prices"]
        
        if not raw_data:
            state["formatted_options_data"] = pd.DataFrame()
            state["status"] = "no_data_to_format"
            return state
        
        print("🎨 LLM formatting options data into 6x6 matrix...")
        
        # Pre-filter data to reduce token count before sending to LLM
        filtered_data = {}
        for ticker, data in raw_data.items():
            if data and 'options_data' in data:
                current_price = spot_prices.get(ticker, 0)
                options_records = data['options_data']
                
                # Convert back to DataFrame for filtering
                df = pd.DataFrame(options_records)
                
                # Ensure numeric columns are properly typed
                df['strike'] = pd.to_numeric(df['strike'], errors='coerce')
                df = df.dropna(subset=['strike'])  # Remove rows with invalid strikes
                
                # Filter for calls only with strikes above current price
                calls_df = df[
                    (df['type'] == 'call') & 
                    (df['strike'] > current_price)
                ].copy()
                
                if not calls_df.empty:
                    # Get next 6 Friday expirations starting from current date
                    calls_df['exp_date'] = pd.to_datetime(calls_df['expiration'])
                    calls_df['weekday'] = calls_df['exp_date'].dt.weekday
                    current_date = pd.to_datetime(datetime.now().date())
                    
                    # Filter for Fridays that are on or after current date
                    future_fridays = calls_df[(calls_df['weekday'] == 4) & (calls_df['exp_date'] >= current_date)]['exp_date'].drop_duplicates().sort_values()
                    next_6_fridays = future_fridays.head(6)
                    
                    # Filter for those expirations and lowest 6 strikes above current
                    filtered_calls = calls_df[calls_df['exp_date'].isin(next_6_fridays)]
                    strikes = filtered_calls['strike'].drop_duplicates().sort_values()
                    lowest_6_strikes = strikes.head(6)
                    final_filtered = filtered_calls[filtered_calls['strike'].isin(lowest_6_strikes)]
                    
                    # Keep essential columns + delta for Agent 2 calculations
                    essential_cols = ['strike', 'expiration', 'bid', 'ask', 'mark', 'delta']
                    if not final_filtered.empty:
                        filtered_data[ticker] = final_filtered[essential_cols].to_dict('records')
                        print(f"   📊 {ticker}: Filtered to {len(filtered_data[ticker])} relevant options (with Delta)")
                
        # Create proper 6x6 DataFrame directly (instead of using LLM)
        if not filtered_data:
            state["formatted_options_data"] = pd.DataFrame()
            state["status"] = "no_data_to_format"
            return state
            
        print("🎨 Creating 6×6 options premium matrix...")
        
        # Build the 6x6 matrix programmatically for each ticker
        all_matrices = []
        all_delta_matrices = []  # Separate Delta storage for Agent 2
        
        for ticker, options_records in filtered_data.items():
            current_price = spot_prices.get(ticker, 0)
            df = pd.DataFrame(options_records)
            
            if df.empty:
                continue
                
            # Get exactly 6 strikes above current price
            strikes = df['strike'].drop_duplicates().sort_values()
            strikes_above = strikes[strikes > current_price].head(6)
            
            # Get exactly 6 Friday expirations starting from current date
            df['exp_date'] = pd.to_datetime(df['expiration'])
            df['weekday'] = df['exp_date'].dt.weekday
            current_date = pd.to_datetime(datetime.now().date())
            
            # Filter for Fridays that are on or after current date
            future_fridays = df[(df['weekday'] == 4) & (df['exp_date'] >= current_date)]['exp_date'].drop_duplicates().sort_values()
            next_6_fridays = future_fridays.head(6)
            
            # Create 6x6 matrix for this ticker
            matrix_data = []
            delta_matrix_data = []  # Store delta values for Agent 2
            
            for strike in strikes_above:
                row = {'Stock': ticker, 'Strike_Price': f"{float(strike):.1f}"}
                delta_row = {'Stock': ticker, 'Strike_Price': float(strike)}
                
                for friday in next_6_fridays:
                    # Find the option for this strike and expiration
                    option = df[(df['strike'] == strike) & (df['exp_date'] == friday)]
                    
                    if not option.empty:
                        # Use bid price, fallback to mark, then ask
                        premium = option.iloc[0]['bid']
                        if pd.isna(premium) or premium == 0:
                            premium = option.iloc[0]['mark']
                        if pd.isna(premium) or premium == 0:
                            premium = option.iloc[0]['ask']
                        if pd.isna(premium):
                            premium = 0
                        
                        # Extract Delta value for Agent 2
                        delta = option.iloc[0]['delta'] if 'delta' in option.columns else None
                        if pd.isna(delta):
                            delta = None
                            # IMPORTANT: Log when we have premium but missing Delta
                            if premium > 0:
                                print(f"      ⚠️  {ticker} Strike {strike} @ {friday.strftime('%m/%d/%y')}: Premium ${premium:.2f} but Delta is MISSING!")
                    else:
                        premium = 0
                        delta = None
                        # Option contract doesn't exist for this strike/expiration combination
                        
                    # Format date as MM/DD/YY
                    date_str = friday.strftime('%m/%d/%y')
                    row[date_str] = f"{float(premium):.2f}"
                    delta_row[date_str] = delta  # Store raw Delta value
                
                # Add current price only to first row
                if len(matrix_data) == 0:
                    row['Current_Price'] = f"${current_price:.2f}"
                else:
                    row['Current_Price'] = ""
                    
                matrix_data.append(row)
                delta_matrix_data.append(delta_row)
            
            all_matrices.extend(matrix_data)
            all_delta_matrices.extend(delta_matrix_data)
            print(f"   ✅ {ticker}: Created 6×6 matrix ({len(matrix_data)} rows) with Delta data stored")
        
        # Convert to DataFrame
        if all_matrices:
            # Premium DataFrame (displayed in UI)
            df = pd.DataFrame(all_matrices)
            state["formatted_options_data"] = df
            
            # Delta DataFrame (stored for Agent 2, NOT displayed)
            delta_df = pd.DataFrame(all_delta_matrices)
            state["delta_data"] = delta_df
            
            state["status"] = "matrix_created"
            print(f"✅ Successfully created {df.shape[0]}×{df.shape[1]} options matrix")
            print(f"📊 Delta data: {delta_df.shape[0]}×{delta_df.shape[1]} matrix stored for Agent 2")
            print(f"📊 Columns: {list(df.columns)}")
        else:
            state["formatted_options_data"] = pd.DataFrame()
            state["delta_data"] = pd.DataFrame()
            state["status"] = "no_matrix_created"
        
        return state
    
    def llm_generate_analysis_node(self, state: OptionsAnalysisState) -> OptionsAnalysisState:
        """
        LLM generates insights and analysis of the options data
        AI analysis generation by: AI Assistant (GitHub Copilot)
        """
        options_data = state["formatted_options_data"]
        spot_prices = state["spot_prices"]
        
        if options_data is None or options_data.empty:
            state["llm_analysis"] = "No options data available for analysis."
            state["status"] = "analysis_complete"
            return state
        
        print("🧠 LLM generating options analysis and insights...")
        
        # Create prompt for analysis
        prompt = f"""
        You are a professional options trader and analyst. Analyze the options premium matrix and provide insights.
        
        OPTIONS MATRIX:
        {options_data.to_string(index=False)}
        
        CURRENT PRICES:
        {json.dumps(spot_prices, indent=2)}
        
        Provide a concise analysis covering:
        1. Premium levels assessment (high/low/fair)
        2. Most attractive strikes for covered calls
        3. Time decay patterns across expirations
        4. Any notable patterns or opportunities
        5. Risk considerations
        
        Keep the analysis practical and actionable for covered call strategies.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            state["llm_analysis"] = response.content.strip()
            
            # Add success message
            state["messages"].append(AIMessage(
                content=f"✅ Analysis complete! Generated {options_data.shape[0]} option entries with LLM insights."
            ))
            
        except Exception as e:
            print(f"❌ LLM analysis error: {e}")
            state["llm_analysis"] = "Analysis generation failed due to LLM error."
            state["errors"].append(f"LLM analysis failed: {e}")
        
        state["status"] = "analysis_complete"
        return state

    # =============================================================================
    # 5. WORKFLOW MANAGEMENT - Written by: Meet Patel
    # =============================================================================
    
    def _build_llm_workflow(self) -> StateGraph:
        """
        Build the LLM-orchestrated workflow
        Advanced workflow orchestration by: Meet Patel
        """
        workflow = StateGraph(OptionsAnalysisState)
        
        # Add LLM-orchestrated nodes
        workflow.add_node("llm_parse_convert", self.llm_parse_and_convert_node)
        workflow.add_node("fetch_data", self.fetch_financial_data_node)
        workflow.add_node("llm_format_matrix", self.llm_format_options_matrix_node)
        workflow.add_node("llm_analyze", self.llm_generate_analysis_node)
        
        # Define the LLM-orchestrated flow
        workflow.add_edge(START, "llm_parse_convert")
        workflow.add_edge("llm_parse_convert", "fetch_data")
        workflow.add_edge("fetch_data", "llm_format_matrix")
        workflow.add_edge("llm_format_matrix", "llm_analyze")
        workflow.add_edge("llm_analyze", END)
        
        return workflow.compile()
    

    # =============================================================================
    # 6. USER INTERFACE FUNCTIONS - Meet Patel (@meetpatel3690) + AI Assistant
    # =============================================================================
    
    def analyze(self, user_input: str, date: Optional[str] = None) -> dict:
        """
        Main interface for LLM-Orchestrated Options Analysis
        
        Basic interface design by: Meet Patel (@meetpatel3690)
        Advanced implementation: AI Assistant (GitHub Copilot)
        
        Args:
            user_input: Natural language input (e.g., "Apple, Tesla, Microsoft")
            date: Optional analysis date (defaults to 2025-10-02)
            
        Returns:
            dict with LLM-processed analysis results
        """
        # Initialize state
        initial_state = OptionsAnalysisState(
            user_input=user_input,
            symbols=[],
            date=date or get_most_recent_trading_day(),
            converted_tickers=[],
            spot_prices={},
            raw_options_data={},
            formatted_options_data=None,
            delta_data=None,  # Delta DataFrame for Agent 2
            llm_analysis=None,
            messages=[],
            status="initializing",
            errors=[]
        )
        
        print(f"🚀 Starting LLM-Orchestrated Options Analysis...")
        print(f"🧠 LLM will handle: Parse → Convert → Format → Analyze")
        print(f"📝 Input: {user_input}")
        print(f"📅 Date: {initial_state['date']}")
        print("-" * 70)
        
        try:
            # Run the LLM-orchestrated workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Prepare response
            response = {
                "success": final_state["status"] in ["matrix_created", "analysis_complete"],
                "status": final_state["status"],
                "original_input": user_input,
                "input_symbols": final_state["symbols"],
                "converted_tickers": final_state["converted_tickers"],
                "spot_prices": final_state["spot_prices"],
                "formatted_matrix": final_state["formatted_options_data"],
                "delta_matrix": final_state.get("delta_data"),  # Delta data for Agent 2
                "errors": final_state["errors"],
                "messages": [msg.content for msg in final_state["messages"]]
            }
            
            print("-" * 70)
            if response["success"]:
                print(f"✅ LLM orchestration completed successfully!")
                if final_state["formatted_options_data"] is not None:
                    print(f"📊 Generated matrix: {final_state['formatted_options_data'].shape}")
                    print(f"🧠 LLM analysis: Generated")
            else:
                print(f"❌ LLM orchestration failed: {final_state['status']}")
                if final_state["errors"]:
                    for error in final_state["errors"]:
                        print(f"   💥 {error}")
            
            return response
            
        except Exception as e:
            error_response = {
                "success": False,
                "status": "workflow_error",
                "error": str(e),
                "original_input": user_input,
                "input_symbols": [],
                "converted_tickers": [],
                "spot_prices": {},
                "formatted_matrix": None,
                "llm_analysis": None,
                "errors": [str(e)],
                "messages": []
            }
            print(f"❌ Workflow error: {e}")
            return error_response
    
    def get_options_dataframe(self, user_input: str, date: Optional[str] = None) -> pd.DataFrame:
        """
        Get options data as a clean pandas DataFrame without CSV generation
        
        Simple interface by: Meet Patel (@meetpatel3690)
        
        Args:
            user_input: Free text input with company names or tickers
            date: Optional analysis date (defaults to 2025-10-02)
            
        Returns:
            pandas.DataFrame: 6x6 options matrix with premium data
        """
        result = self.analyze(user_input, date)
        
        if result["success"] and result["formatted_matrix"] is not None:
            df = result["formatted_matrix"].copy()
            # Reset index to get sequential numbering starting from 0
            df.reset_index(drop=True, inplace=True)
            return df
        else:
            # Return empty DataFrame if analysis failed
            print("Analysis failed, returning empty DataFrame")
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"Error: {error}")
            return pd.DataFrame()
    
    def display_results(self, result: dict):
        """
        Display LLM-orchestrated analysis results
        Output formatting by: AI Assistant (GitHub Copilot)
        """
        if not result["success"]:
            print(f"\n❌ LLM Analysis failed: {result.get('status', 'Unknown error')}")
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"💥 {error}")
            return
        
        print(f"\n🎯 LLM-ORCHESTRATED OPTIONS ANALYSIS")
        print("=" * 80)
        
        # Show LLM conversions
        print("🤖 LLM Symbol Processing:")
        print(f"   Input: {result['original_input']}")
        print(f"   Detected: {result['input_symbols']}")
        print(f"   Converted: {result['converted_tickers']}")
        print()
        
        # Show current prices
        print("💰 Current Market Prices:")
        for ticker, price in result["spot_prices"].items():
            print(f"   {ticker}: ${price:.2f}")
        print()
        
        # Show LLM-formatted matrix
        if result["formatted_matrix"] is not None and not result["formatted_matrix"].empty:
            print("📊 6×6 Options Premium Matrix:")
            print(result["formatted_matrix"].to_string(index=False))
            print(f"\n✅ Matrix shape: {result['formatted_matrix'].shape}")
        else:
            print("⚠️  No options matrix generated")
        
        # Show LLM analysis
        if result["llm_analysis"]:
            print("\n🧠 LLM Options Analysis & Insights:")
            print("-" * 50)
            print(result["llm_analysis"])
        
        print("\n" + "=" * 80)
        print("🎯 LLM ORCHESTRATION SUMMARY:")
        print("   ✅ Parsed natural language input")
        print("   ✅ Converted company names to tickers")
        print("   ✅ Fetched real-time financial data")
        print("   ✅ Formatted data into structured matrix")
        print("   ✅ Generated professional analysis")
        print("=" * 80)


# =============================================================================
# 7. TESTING & EXAMPLES - Written by: Meet Patel (@meetpatel3690)
# =============================================================================

def main():
    """
    Main function - automatically runs DataFrame generation
    Basic testing structure by: Meet Patel (@meetpatel3690)
    """
    try:
        print("🚀 Starting LLM-Orchestrated Options Analysis Agent...")
        print("=" * 70)
        
        # Initialize the agent
        agent = LLMOptionsAgent()
        
        # Test input
        user_input = "Apple, Tesla Motors, Microsoft"
        print(f"\n📝 Analyzing: {user_input}")
        print("-" * 70)
        
        # Method 1: Get DataFrame directly
        print("📊 Method 1: Getting DataFrame directly...")
        df = agent.get_options_dataframe(user_input)
        
        if not df.empty:
            print(f"\n✅ Successfully generated 6x6 options matrix!")
            print(f"📈 DataFrame shape: {df.shape}")
            print(f"📋 Columns: {df.columns.tolist()}")
            print("\n📊 Options Premium Matrix (6 Strikes × 6 Fridays):")
            print(df.to_string(index=True))
        else:
            print("❌ No DataFrame generated")
            
        print("\n" + "=" * 70)
        print("🎯 Analysis Complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

