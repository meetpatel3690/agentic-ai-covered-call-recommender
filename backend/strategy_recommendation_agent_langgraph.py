# -*- coding: utf-8 -*-
"""
Strategy Recommendation Agent (Agent 2) - LangGraph Implementation
A sophisticated agent that analyzes options data and recommends optimal strategies.

PART 1 (Current Implementation):
- Analyzes the 6x6 options grid from Agent 1
- Highlights cells with highest premium for each stock
- Provides visual feedback on which options have the best premiums
- Uses LangGraph workflow for scalable orchestration

PART 2 (Future Enhancement - Scalable Design):
- The architecture is designed to be easily extended
- Can incorporate Delta values for directional risk analysis
- Supports custom scoring formulas that can be finalized with mentors
- Modular LangGraph nodes allow adding Delta analysis without breaking existing functionality

=============================================================================
ATTRIBUTION:
=============================================================================
- Project Concept & Requirements: Meet Patel (@meetpatel3690)
- Agent 2 Architecture & LangGraph Implementation: AI Assistant (GitHub Copilot)
- Scalable Design for Future Enhancements: AI Assistant (GitHub Copilot)
=============================================================================
"""

import pandas as pd
import numpy as np
from typing import TypedDict, List, Optional, Dict, Annotated
import operator
from datetime import datetime, timedelta
from pathlib import Path
import os
import json
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


# =============================================================================
# 1. DATA STRUCTURE SCHEMA
# =============================================================================

class StrategyAnalysisState(TypedDict):
    """
    State schema for LangGraph-orchestrated strategy recommendation workflow
    
    This state tracks the entire analysis pipeline from input to recommendations
    """
    # Input
    options_dataframe: Optional[pd.DataFrame]  # Input 6x6 grid from Agent 1
    delta_data: Optional[pd.DataFrame]         # PART 2: Delta values DataFrame from Agent 1
    portfolio_data: Optional[Dict]             # PART 2: Portfolio holdings {stock: shares}
    current_date: Optional[str]                # PART 2: Current date for expiration filtering (YYYY-MM-DD)
    analysis_mode: str                          # "premium_only" (Part 1) or "premium_delta" (Part 2)
    
    # Processing states
    validated_data: bool                        # Data validation result
    premium_analysis: Dict                      # Premium analysis results per stock
    highest_premium_cells: Dict                 # Cells with max premium per stock
    stock_analysis: Dict                        # Detailed analysis per stock
    merged_data: Optional[pd.DataFrame]         # PART 2: Merged premium + delta data
    primary_recommendations: Dict               # PART 2: Primary recommendations per stock
    secondary_recommendations: Dict             # PART 2: Secondary recommendations per stock (if Week 1-2)
    contract_allocations: Dict                  # PART 2: Contract allocation per stock
    income_projections: Dict                    # PART 2: Projected income per stock
    
    # LLM-orchestrated results
    recommendations: List[Dict]                 # Strategy recommendations
    llm_insights: Optional[str]                 # LLM-generated analysis
    highlighted_cells: Dict                     # Cells to highlight in UI
    
    # Configuration (Part 2 ready)
    scoring_config: Dict                        # Scoring formula configuration
    
    # Metadata
    messages: Annotated[List[BaseMessage], add_messages]  # Conversation history
    status: str                                 # Current processing status
    errors: List[str]                          # Any errors encountered
    analysis_timestamp: str                     # When analysis was performed


# =============================================================================
# 2. MAIN AGENT CLASS - LANGGRAPH IMPLEMENTATION
# =============================================================================

class StrategyRecommendationAgentLangGraph:
    """
    Agent 2: Analyzes options data and recommends optimal strategies using LangGraph
    
    This agent is designed with scalability in mind:
    - PART 1: Premium-based analysis (current implementation)
    - PART 2: Will support Delta values with configurable formulas
    
    LangGraph workflow ensures:
    - Clear separation of concerns (each node = one task)
    - Easy debugging and monitoring
    - Scalable for future enhancements
    - Consistent with Agent 1 architecture
    """
    
    def __init__(self):
        """Initialize the Strategy Recommendation Agent with LangGraph workflow"""
        
        # Load OpenAI API key for LLM insights
        self.openai_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_key:
            print("⚠️ Warning: OPENAI_API_KEY not found. LLM insights will be limited.")
            self.llm = None
        else:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1, api_key=self.openai_key)
        
        # Default scoring configuration (Part 1)
        self.default_scoring_config = {
            'use_premium': True,      # PART 1: Premium analysis
            'use_delta': False,       # PART 2: Delta analysis (to be enabled)
            'custom_formula': None,   # PART 2: Custom formula from mentors
            'weights': {              # PART 2: Configurable weights
                'premium': 1.0,
                'delta': 0.0          # Will be configured after mentor meeting
            }
        }
        
        # Build the LangGraph workflow
        self.workflow = self._build_strategy_workflow()
        
        print("🎯 Strategy Recommendation Agent (LangGraph) initialized!")
        print("📊 Ready to analyze options data and generate recommendations")
    
    # =============================================================================
    # 2A. HELPER FUNCTIONS - PART 2 ENHANCEMENTS
    # =============================================================================
    
    def merge_premium_delta_data(self, premium_df: pd.DataFrame, delta_df: Optional[pd.DataFrame]) -> pd.DataFrame:
        """
        Merge premium and delta DataFrames for scoring
        
        Args:
            premium_df: DataFrame with premium values
                       Format: Stock | Strike_Price | Date1 | Date2 | Date3 | ...
            delta_df: DataFrame with Delta values (same format) or None
        
        Returns:
            DataFrame with combined data in long format:
            Columns: Stock | Strike | Expiry | Premium | Delta
            
            If delta_df is None, Delta column will contain None values
        """
        if premium_df is None or premium_df.empty:
            return pd.DataFrame(columns=['Stock', 'Strike', 'Expiry', 'Premium', 'Delta'])
        
        # Get date columns (expiry dates)
        date_columns = [col for col in premium_df.columns if '/' in col]
        
        if not date_columns:
            return pd.DataFrame(columns=['Stock', 'Strike', 'Expiry', 'Premium', 'Delta'])
        
        # Melt premium DataFrame to long format
        premium_long = premium_df.melt(
            id_vars=['Stock', 'Strike_Price'],
            value_vars=date_columns,
            var_name='Expiry',
            value_name='Premium'
        )
        premium_long.rename(columns={'Strike_Price': 'Strike'}, inplace=True)
        
        # Convert Strike to float to ensure consistent data types
        premium_long['Strike'] = pd.to_numeric(premium_long['Strike'], errors='coerce')
        
        # If delta_df is provided, melt it and merge
        if delta_df is not None and not delta_df.empty:
            delta_long = delta_df.melt(
                id_vars=['Stock', 'Strike_Price'],
                value_vars=date_columns,
                var_name='Expiry',
                value_name='Delta'
            )
            delta_long.rename(columns={'Strike_Price': 'Strike'}, inplace=True)
            
            # Convert Strike to float to ensure consistent data types
            delta_long['Strike'] = pd.to_numeric(delta_long['Strike'], errors='coerce')
            
            # Merge on Stock, Strike, Expiry
            merged = premium_long.merge(
                delta_long[['Stock', 'Strike', 'Expiry', 'Delta']],
                on=['Stock', 'Strike', 'Expiry'],
                how='left'
            )
        else:
            # No delta data - add None column
            merged = premium_long.copy()
            merged['Delta'] = None
        
        # Handle None values in Delta column - treat as 0
        # This is part of the Hybrid Approach
        merged['Delta'] = merged['Delta'].apply(lambda x: 0 if x is None or pd.isna(x) else x)
        
        # Convert Premium and Delta to numeric to avoid type errors
        merged['Premium'] = pd.to_numeric(merged['Premium'], errors='coerce')
        merged['Delta'] = pd.to_numeric(merged['Delta'], errors='coerce')
        
        # Fill any NaN values after conversion
        merged['Premium'] = merged['Premium'].fillna(0)
        merged['Delta'] = merged['Delta'].fillna(0)
        
        return merged
    
    def calculate_option_score(self, premium: float, delta: float) -> tuple[float, str]:
        """
        Calculate option score using Delta-based formula (PART 2)
        
        Formula: Score = Premium × (1 - Delta)
        
        This formula represents "risk-adjusted premium":
        - Higher Delta = Higher risk = Lower score (discount applied)
        - Lower Delta = Lower risk = Higher score (premium preserved)
        - Delta = 0 (None treated as 0) = Full premium (no discount)
        
        Args:
            premium: Option premium value (e.g., 2.5 means $2.50)
            delta: Option delta value (0.0 to 1.0) or 0 if None
                  Note: None values are converted to 0 by merge function
        
        Returns:
            Tuple of (score, confidence_level):
            - score: Calculated risk-adjusted score
            - confidence: "HIGH" if delta was present, "MEDIUM" if delta was 0 (originally None)
        
        Examples:
            Premium=2.5, Delta=0.3 → Score=1.75, Confidence=HIGH
            Premium=3.0, Delta=0 (was None) → Score=3.0, Confidence=MEDIUM
        """
        # Input validation - convert to numeric first
        try:
            premium = float(premium) if premium is not None else None
            delta = float(delta) if delta is not None else None
        except (ValueError, TypeError):
            return 0.0, "LOW"
        
        if premium is None or pd.isna(premium) or premium < 0:
            return 0.0, "LOW"
        
        if delta is None or pd.isna(delta):
            delta = 0  # Fallback (should already be handled by merge function)
        
        # Ensure delta is in valid range
        if delta < 0:
            delta = 0
        elif delta > 1:
            delta = 1
        
        # Calculate score: Premium × (1 - Delta)
        score = premium * (1 - delta)
        
        # Determine confidence level
        # HIGH: Delta was present (any value > 0)
        # MEDIUM: Delta = 0 (treated as missing data, using Hybrid Approach)
        if delta > 0:
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"  # Delta was 0 (originally None)
        
        return round(score, 2), confidence
    
    def get_week_of_month(self, expiry_date: str) -> int:
        """
        Determine which week of the month a given expiry date falls into (PART 2)
        
        Week determination based on day of month:
        - Week 1: Days 1-7
        - Week 2: Days 8-14
        - Week 3: Days 15-21
        - Week 4: Days 22-28
        - Week 5: Days 29+
        
        This is critical for multi-trade strategy:
        - Week 1 or 2 → Look for secondary trade (early in month)
        - Week 3, 4, or 5 → NO secondary (too late in month)
        
        Args:
            expiry_date: Date string in format "MM/DD" (e.g., "12/06", "12/20")
        
        Returns:
            Integer week number (1-5)
        
        Examples:
            "12/06" → Week 1 (day 6 is in days 1-7)
            "12/13" → Week 2 (day 13 is in days 8-14)
            "12/20" → Week 3 (day 20 is in days 15-21)
            "12/27" → Week 4 (day 27 is in days 22-28)
            "12/31" → Week 5 (day 31 is in days 29+)
        """
        try:
            # Parse the expiry date string
            if '/' in expiry_date:
                parts = expiry_date.split('/')
                day = int(parts[1])  # Get day from "MM/DD"
            else:
                # Handle other formats if needed
                return 0
            
            # Determine week based on day of month
            if day <= 7:
                return 1
            elif day <= 14:
                return 2
            elif day <= 21:
                return 3
            elif day <= 28:
                return 4
            else:
                return 5
                
        except (ValueError, IndexError) as e:
            # If parsing fails, return 0 (invalid)
            print(f"   ⚠️ Error parsing expiry date '{expiry_date}': {e}")
            return 0
    
    def select_primary_recommendation(self, scored_options: pd.DataFrame, stock: str) -> Optional[Dict]:
        """
        Select the primary (best) recommendation from scored options (PART 2 - Phase 4)
        
        The primary recommendation is the highest-scored option for the given stock.
        This will be the first (and possibly only) trade recommendation.
        
        Args:
            scored_options: DataFrame with scored and sorted options
                          Columns: Stock, Strike, Expiry, Premium, Delta, Score, Confidence, Week
            stock: Stock symbol to filter for (e.g., "AAPL")
        
        Returns:
            Dictionary with primary recommendation details:
            {
                'type': 'Primary',
                'stock': str,
                'strike': float,
                'expiry': str,
                'premium': float,
                'delta': float,
                'score': float,
                'confidence': str,
                'week': int
            }
            
            Returns None if no options available for the stock.
        
        Example:
            Primary: {
                'type': 'Primary',
                'stock': 'AAPL',
                'strike': 150.0,
                'expiry': '12/06',
                'premium': 2.5,
                'delta': 0.3,
                'score': 1.75,
                'confidence': 'HIGH',
                'week': 1
            }
        """
        # Filter options for this stock
        stock_options = scored_options[scored_options['Stock'] == stock].copy()
        
        if stock_options.empty:
            return None
        
        # Already sorted by score (descending), so first row is the best
        best_option = stock_options.iloc[0]
        
        # Create primary recommendation dictionary
        primary = {
            'type': 'Primary',
            'stock': stock,
            'strike': float(best_option['Strike']),
            'expiry': str(best_option['Expiry']),
            'premium': float(best_option['Premium']),
            'delta': float(best_option['Delta']) if best_option['Delta'] != 0 else 0,
            'score': float(best_option['Score']),
            'confidence': str(best_option['Confidence']),
            'week': int(best_option['Week'])
        }
        
        return primary
    
    def select_secondary_recommendation(
        self,
        scored_options: pd.DataFrame,
        primary: Dict,
        stock: str
    ) -> Optional[Dict]:
        """
        PART 2 - PHASE 5: Select secondary trade based on primary week and 7-day gap
        
        Multi-trade strategy logic:
        - If primary is Week 1 or 2: Look for secondary trade (early month)
        - If primary is Week 3, 4, or 5: NO secondary (too late)
        - Secondary must expire >= primary expiry + 7 days
        
        Args:
            scored_options: DataFrame with all scored options
                          Columns: Stock, Strike, Expiry, Premium, Delta, Score, Confidence, Week
            primary: Primary recommendation dictionary from select_primary_recommendation()
            stock: Stock symbol to filter for
        
        Returns:
            Dictionary with secondary recommendation details (same structure as primary)
            OR None if:
            - Primary is Week 3+ (too late in month)
            - No valid secondary found (no options with 7+ day gap)
        
        Example - Week 1 Primary (Secondary Found):
            Primary: {'week': 1, 'expiry': '12/06', ...}
            Secondary: {'week': 2, 'expiry': '12/13', ...}  (7 days later)
        
        Example - Week 3 Primary (NO Secondary):
            Primary: {'week': 3, 'expiry': '12/20', ...}
            Secondary: None  (too late in month)
        """
        # Week-based decision: Only look for secondary if primary is Week 1 or 2
        primary_week = primary['week']
        
        if primary_week >= 3:
            # Week 3, 4, or 5 - too late in month for secondary trade
            return None
        
        # Primary is Week 1 or 2 - look for secondary with 7-day gap
        primary_expiry_str = primary['expiry']  # e.g., "12/06"
        
        # Parse primary expiry date
        try:
            # Handle both MM/DD and MM/DD/YY formats
            parts = primary_expiry_str.split('/')
            if len(parts) == 2:
                # Format: MM/DD - use current year
                month, day = map(int, parts)
                current_year = datetime.now().year
            elif len(parts) == 3:
                # Format: MM/DD/YY or MM/DD/YYYY
                month, day, year = map(int, parts)
                if year < 100:
                    year = 2000 + year  # Convert YY to YYYY
            else:
                print(f"      ⚠️ Invalid date format: {primary_expiry_str}")
                return None
            
            primary_expiry_date = datetime(year if len(parts) == 3 else current_year, month, day)
        except Exception as e:
            print(f"      ⚠️ Could not parse primary expiry '{primary_expiry_str}': {e}")
            return None
        
        # Calculate minimum secondary expiry (primary + 7 days)
        min_secondary_date = primary_expiry_date + timedelta(days=7)
        
        # Filter options for this stock, excluding the primary option
        stock_options = scored_options[scored_options['Stock'] == stock].copy()
        
        # Remove the primary option (same strike and expiry)
        stock_options = stock_options[
            ~((stock_options['Strike'] == primary['strike']) & 
              (stock_options['Expiry'] == primary['expiry']))
        ]
        
        if stock_options.empty:
            return None
        
        # Filter for options that expire >= min_secondary_date
        valid_secondaries = []
        
        for _, row in stock_options.iterrows():
            expiry_str = str(row['Expiry'])
            try:
                month, day = map(int, expiry_str.split('/'))
                expiry_date = datetime(current_year, month, day)
                
                # Check if this option meets the 7-day gap requirement
                if expiry_date >= min_secondary_date:
                    valid_secondaries.append(row)
            except:
                continue  # Skip options with unparseable dates
        
        if not valid_secondaries:
            return None
        
        # Convert to DataFrame and sort by score (descending)
        valid_df = pd.DataFrame(valid_secondaries)
        valid_df = valid_df.sort_values('Score', ascending=False)
        
        # Select the best (highest-scored) secondary
        best_secondary = valid_df.iloc[0]
        
        # Create secondary recommendation dictionary
        secondary = {
            'type': 'Secondary',
            'stock': stock,
            'strike': float(best_secondary['Strike']),
            'expiry': str(best_secondary['Expiry']),
            'premium': float(best_secondary['Premium']),
            'delta': float(best_secondary['Delta']) if best_secondary['Delta'] != 0 else 0,
            'score': float(best_secondary['Score']),
            'confidence': str(best_secondary['Confidence']),
            'week': int(best_secondary['Week'])
        }
        
        return secondary
    
    def calculate_contracts(
        self,
        shares: int,
        stock: str
    ) -> Dict[str, int]:
        """
        PART 2 - PHASE 6: Calculate contract allocation based on position size
        
        Strategy:
        - Large positions (≥3 contracts / ≥300 shares): Keep 1 contract buffer
        - Small positions (<3 contracts / <300 shares): Use all contracts
        
        Purpose:
        - Maintain flexibility for future opportunities
        - Risk management (not fully exposed to options)
        - Stock retention (lower chance of losing entire position)
        
        Args:
            shares: Number of shares owned for this stock
            stock: Stock symbol (for logging)
        
        Returns:
            Dictionary with allocation details:
            {
                'total_contracts': int,      # Total contracts available (shares / 100)
                'recommended': int,           # Contracts to use for options
                'buffer': int,                # Contracts kept as buffer
                'buffer_shares': int          # Shares kept as buffer (buffer * 100)
            }
        
        Examples:
            100 shares (1 contract):
                total_contracts=1, recommended=1, buffer=0, buffer_shares=0
            
            200 shares (2 contracts):
                total_contracts=2, recommended=2, buffer=0, buffer_shares=0
            
            300 shares (3 contracts):
                total_contracts=3, recommended=2, buffer=1, buffer_shares=100
            
            600 shares (6 contracts):
                total_contracts=6, recommended=5, buffer=1, buffer_shares=100
        """
        # Calculate total contracts available
        total_contracts = shares // 100
        
        # Strategy: Keep 1 contract buffer for large positions (≥3 contracts)
        if total_contracts >= 3:
            recommended = total_contracts - 1
            buffer = 1
        else:
            # Small positions: use all contracts
            recommended = total_contracts
            buffer = 0
        
        buffer_shares = buffer * 100
        
        allocation = {
            'total_contracts': total_contracts,
            'recommended': recommended,
            'buffer': buffer,
            'buffer_shares': buffer_shares
        }
        
        return allocation
    
    def calculate_income(
        self,
        primary: Dict,
        secondary: Optional[Dict],
        contracts: int,
        stock: str
    ) -> Dict[str, float]:
        """
        PART 2 - PHASE 7: Calculate projected income from options trades
        
        Formula: Income = Premium × Contracts × 100
        
        Multi-trade income:
        - If only primary: Income = primary premium × contracts × 100
        - If primary + secondary: Income = (primary + secondary) × contracts × 100
        
        Args:
            primary: Primary recommendation dictionary
            secondary: Secondary recommendation dictionary (or None)
            contracts: Number of contracts to use (from allocation)
            stock: Stock symbol (for logging)
        
        Returns:
            Dictionary with income details:
            {
                'primary_income': float,      # Income from primary trade
                'secondary_income': float,    # Income from secondary trade (0 if none)
                'total_income': float,        # Total monthly income for this stock
                'contracts_used': int,        # Number of contracts
                'has_secondary': bool         # Whether secondary trade exists
            }
        
        Examples:
            Primary only (Week 3):
                Premium: $26.20, Contracts: 5
                Income = $26.20 × 5 × 100 = $13,100
            
            Primary + Secondary (Week 1):
                Primary: $28.40 × 5 × 100 = $14,200
                Secondary: $26.20 × 5 × 100 = $13,100
                Total: $27,300
        """
        # Calculate primary income
        primary_premium = primary['premium']
        primary_income = primary_premium * contracts * 100
        
        # Calculate secondary income (if exists)
        if secondary is not None:
            secondary_premium = secondary['premium']
            secondary_income = secondary_premium * contracts * 100
            has_secondary = True
        else:
            secondary_income = 0.0
            has_secondary = False
        
        # Calculate total income
        total_income = primary_income + secondary_income
        
        income_details = {
            'primary_income': primary_income,
            'secondary_income': secondary_income,
            'total_income': total_income,
            'contracts_used': contracts,
            'has_secondary': has_secondary
        }
        
        return income_details
    
    # =============================================================================
    # 3. LANGGRAPH NODES - WORKFLOW COMPONENTS
    # =============================================================================
    
    def validate_input_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:
        """
        Node 1: Validate input options dataframe
        
        Checks:
        - DataFrame is not None and not empty
        - Required columns exist (Stock, Strike_Price, date columns)
        - Data types are correct
        """
        print("\n🔍 Node 1: Validating input data...")
        
        state["messages"].append(SystemMessage(content="🤖 Strategy Agent starting analysis..."))
        
        options_df = state.get("options_dataframe")
        
        # Validation checks
        if options_df is None:
            state["validated_data"] = False
            state["status"] = "error_no_data"
            state["errors"].append("No options data provided")
            print("   ❌ Validation failed: No data provided")
            return state
        
        if options_df.empty:
            state["validated_data"] = False
            state["status"] = "error_empty_data"
            state["errors"].append("Options dataframe is empty")
            print("   ❌ Validation failed: Empty dataframe")
            return state
        
        # Check required columns
        required_cols = ['Stock', 'Strike_Price']
        missing_cols = [col for col in required_cols if col not in options_df.columns]
        
        if missing_cols:
            state["validated_data"] = False
            state["status"] = "error_missing_columns"
            state["errors"].append(f"Missing required columns: {missing_cols}")
            print(f"   ❌ Validation failed: Missing columns {missing_cols}")
            return state
        
        # Get date columns (contain premium values)
        date_columns = [col for col in options_df.columns if '/' in col]
        
        if not date_columns:
            state["validated_data"] = False
            state["status"] = "error_no_date_columns"
            state["errors"].append("No date columns found in options data")
            print("   ❌ Validation failed: No date columns found")
            return state
        
        # Validation passed
        state["validated_data"] = True
        state["status"] = "data_validated"
        
        print(f"   ✅ Validation passed!")
        print(f"   📊 Data shape: {options_df.shape}")
        print(f"   📈 Stocks: {options_df['Stock'].unique().tolist()}")
        print(f"   📅 Date columns: {len(date_columns)}")
        
        return state
    
    def analyze_premiums_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:
        """
        Node 2: Analyze premiums across the 6x6 grid
        
        For each stock:
        - Scan all 36 cells (6 strikes × 6 expirations)
        - Identify highest premium cell
        - Calculate statistics (avg premium, total options)
        """
        print("\n📊 Node 2: Analyzing premiums...")
        
        if not state["validated_data"]:
            print("   ⚠️ Skipping analysis - data validation failed")
            return state
        
        options_df = state["options_dataframe"]
        
        # Get date columns (these contain premium values)
        date_columns = [col for col in options_df.columns if '/' in col]
        
        # Initialize results
        highest_premium_cells = {}
        stock_analysis = {}
        
        # Get unique stocks
        stocks = options_df['Stock'].unique()
        
        print(f"   🔍 Analyzing {len(stocks)} stocks across {len(date_columns)} expiration dates...")
        
        # Analyze each stock
        for stock in stocks:
            stock_data = options_df[options_df['Stock'] == stock].copy()
            
            # Find the cell with highest premium for this stock
            max_premium = -1
            max_cell = None
            all_premiums = []
            
            # Iterate through all cells for this stock
            for idx, row in stock_data.iterrows():
                strike_price = row['Strike_Price']
                
                for date_col in date_columns:
                    try:
                        premium = float(row[date_col])
                        all_premiums.append(premium)
                        
                        if premium > max_premium:
                            max_premium = premium
                            max_cell = {
                                'row_index': idx,
                                'stock': stock,
                                'strike_price': strike_price,
                                'expiration_date': date_col,
                                'premium': premium
                            }
                    except (ValueError, TypeError):
                        # Skip non-numeric values
                        continue
            
            # Store results for this stock
            if max_cell:
                highest_premium_cells[stock] = max_cell
                stock_analysis[stock] = {
                    'highest_premium': max_premium,
                    'avg_premium': np.mean(all_premiums) if all_premiums else 0,
                    'total_options': len(stock_data) * len(date_columns),
                    'best_strike': max_cell['strike_price'],
                    'best_expiration': max_cell['expiration_date']
                }
                
                print(f"   ✓ {stock}: Best premium ${max_premium:.2f} at strike ${max_cell['strike_price']} expiring {max_cell['expiration_date']}")
        
        # Update state
        state["highest_premium_cells"] = highest_premium_cells
        state["stock_analysis"] = stock_analysis
        state["premium_analysis"] = {
            'total_stocks': len(stocks),
            'total_opportunities': len(highest_premium_cells),
            'date_columns': date_columns
        }
        state["status"] = "premiums_analyzed"
        
        print(f"   ✅ Premium analysis complete! Found {len(highest_premium_cells)} opportunities")
        
        return state
    
    def calculate_scores_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:
        """
        Node 2B: Calculate Delta-based scores (PART 2)
        
        This node:
        1. Merges premium and delta data
        2. Filters expired options
        3. Calculates scores using: Score = Premium × (1 - Delta)
        4. Sorts options by score (highest first)
        5. Stores scored options for recommendation selection
        
        Only runs when analysis_mode = "premium_delta"
        """
        print("\n🧮 Node 2B: Calculating Delta-based scores...")
        
        analysis_mode = state.get("analysis_mode", "premium_only")
        
        # Check if we should run Delta-based scoring
        if analysis_mode == "premium_only":
            print("   ⏭️ Skipping - Mode is 'premium_only'")
            return state
        
        if not state["validated_data"]:
            print("   ⚠️ Skipping - data validation failed")
            return state
        
        options_df = state["options_dataframe"]
        delta_df = state.get("delta_data")
        
        # Step 1: Merge premium and delta data
        print("   📊 Step 1: Merging premium and delta data...")
        merged_df = self.merge_premium_delta_data(options_df, delta_df)
        
        if merged_df.empty:
            print("   ❌ No data after merging")
            state["errors"].append("Merged DataFrame is empty")
            return state
        
        state["merged_data"] = merged_df
        print(f"      ✓ Merged {len(merged_df)} option entries")
        
        # Step 2: Filter expired options
        print("   🗓️ Step 2: Filtering expired options...")
        current_date = datetime.now()
        
        # Convert expiry dates to datetime for comparison
        def parse_expiry(expiry_str):
            try:
                # Handle different date formats
                if '/' in str(expiry_str):
                    parts = str(expiry_str).split('/')
                    if len(parts) == 2:
                        # Format: "MM/DD" - add current year
                        month, day = parts
                        year = current_date.year
                        expiry = datetime(year, int(month), int(day))
                        # If date has passed, try next year
                        if expiry < current_date:
                            expiry = datetime(year + 1, int(month), int(day))
                        return expiry
                    elif len(parts) == 3:
                        # Format: "MM/DD/YYYY" or "MM/DD/YY"
                        month, day, year = parts
                        if len(year) == 2:
                            year = 2000 + int(year)
                        else:
                            year = int(year)
                        return datetime(year, int(month), int(day))
                return None
            except Exception as e:
                print(f"      ⚠️ Could not parse date: {expiry_str} - {e}")
                return None
        
        merged_df['Expiry_Date'] = merged_df['Expiry'].apply(parse_expiry)
        
        # Filter out None dates first
        merged_df = merged_df[merged_df['Expiry_Date'].notna()].copy()
        
        # Filter expired options
        valid_options = merged_df[merged_df['Expiry_Date'] > current_date].copy()
        
        print(f"      ✓ {len(valid_options)} valid options (filtered {len(merged_df) - len(valid_options)} expired)")
        
        if valid_options.empty:
            print("   ❌ No valid options after filtering expired dates")
            print(f"      Current date: {current_date.strftime('%Y-%m-%d')}")
            if not merged_df.empty:
                print(f"      Sample expiry dates: {merged_df['Expiry'].head(3).tolist()}")
            state["errors"].append("All options are expired or have invalid dates")
            return state
        
        # Step 3: Calculate scores for all valid options
        print("   🎯 Step 3: Calculating scores...")
        scores = []
        confidences = []
        
        for idx, row in valid_options.iterrows():
            score, confidence = self.calculate_option_score(row['Premium'], row['Delta'])
            scores.append(score)
            confidences.append(confidence)
        
        valid_options['Score'] = scores
        valid_options['Confidence'] = confidences
        
        # Step 3B: Identify week for each option (PART 2 - Phase 3)
        print("   📅 Step 3B: Identifying week of month for each option...")
        weeks = []
        
        for idx, row in valid_options.iterrows():
            week = self.get_week_of_month(row['Expiry'])
            weeks.append(week)
        
        valid_options['Week'] = weeks
        
        print(f"      ✓ Week distribution: {valid_options['Week'].value_counts().sort_index().to_dict()}")
        
        # Step 4: Sort by score (descending)
        scored_options = valid_options.sort_values('Score', ascending=False).reset_index(drop=True)
        
        print(f"      ✓ Calculated scores for {len(scored_options)} options")
        print(f"      ✓ Score range: ${scored_options['Score'].min():.2f} to ${scored_options['Score'].max():.2f}")
        
        # Show top 3 options
        if len(scored_options) >= 3:
            print("      📈 Top 3 options:")
            for i in range(3):
                opt = scored_options.iloc[i]
                print(f"         {i+1}. {opt['Stock']} ${opt['Strike']} exp {opt['Expiry']} (Week {opt['Week']}) - Score: ${opt['Score']:.2f} ({opt['Confidence']})")
        
        # Store in state
        state["merged_data"] = scored_options
        state["status"] = "scores_calculated"
        
        print("   ✅ Scoring complete!")
        
        return state
    
    def select_primary_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:
        """
        Node 2C: Select primary recommendations (PART 2 - Phase 4)
        
        For each stock in the scored options:
        1. Select the top-scored option as the primary recommendation
        2. Extract all metadata (strike, expiry, premium, delta, score, confidence, week)
        3. Store in state for secondary trade logic (Phase 5)
        
        Only runs when analysis_mode = "premium_delta"
        """
        print("\n🎯 Node 2C: Selecting primary recommendations...")
        
        analysis_mode = state.get("analysis_mode", "premium_only")
        
        # Check if we should run primary selection
        if analysis_mode == "premium_only":
            print("   ⏭️ Skipping - Mode is 'premium_only'")
            return state
        
        # Check if we have scored data
        scored_options = state.get("merged_data")
        if scored_options is None or scored_options.empty:
            print("   ⚠️ No scored options available")
            state["errors"].append("No scored options for primary selection")
            return state
        
        # Check if Score column exists (means scoring was successful)
        if 'Score' not in scored_options.columns:
            print("   ⚠️ No scores calculated - options may be expired or invalid")
            state["errors"].append("No valid scored options available")
            return state
        
        # Get unique stocks
        stocks = scored_options['Stock'].unique()
        
        print(f"   🔍 Selecting primary for {len(stocks)} stock(s)...")
        
        primary_recommendations = {}
        
        for stock in stocks:
            primary = self.select_primary_recommendation(scored_options, stock)
            
            if primary:
                primary_recommendations[stock] = primary
                
                # Display primary selection
                print(f"   ✓ {stock}: Primary selected")
                print(f"      Strike: ${primary['strike']}, Expiry: {primary['expiry']} (Week {primary['week']})")
                print(f"      Score: ${primary['score']:.2f}, Premium: ${primary['premium']:.2f}, Confidence: {primary['confidence']}")
        
        # Store primary recommendations in state
        state["primary_recommendations"] = primary_recommendations
        state["status"] = "primary_selected"
        
        print(f"   ✅ Selected {len(primary_recommendations)} primary recommendation(s)")
        
        return state
    
    def select_secondary_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:
        """
        PART 2 - PHASE 5: Select secondary trades for Week 1-2 primaries
        
        Multi-trade strategy:
        - Week 1-2 primaries → Look for secondary (7+ day gap)
        - Week 3-5 primaries → NO secondary (too late)
        
        Workflow:
        1. Check each primary's week
        2. If Week 1-2: Call select_secondary_recommendation()
        3. If Week 3+: Skip (no secondary)
        4. Store secondaries in state
        
        Only runs when analysis_mode = "premium_delta"
        """
        print("\n🎯 Node 2D: Selecting secondary recommendations...")
        
        analysis_mode = state.get("analysis_mode", "premium_only")
        
        # Check if we should run secondary selection
        if analysis_mode == "premium_only":
            print("   ⏭️ Skipping - Mode is 'premium_only'")
            return state
        
        # Check if we have primary recommendations
        primary_recommendations = state.get("primary_recommendations", {})
        if not primary_recommendations:
            print("   ⚠️ No primary recommendations available")
            return state
        
        # Check if we have scored data
        scored_options = state.get("merged_data")
        if scored_options is None or scored_options.empty:
            print("   ⚠️ No scored options available")
            return state
        
        print(f"   🔍 Checking {len(primary_recommendations)} primary recommendation(s) for secondary opportunities...")
        
        secondary_recommendations = {}
        week_1_2_count = 0
        week_3_plus_count = 0
        secondaries_found = 0
        
        for stock, primary in primary_recommendations.items():
            primary_week = primary['week']
            
            if primary_week >= 3:
                # Week 3, 4, or 5 - too late for secondary
                print(f"   ⏭️ {stock}: Primary is Week {primary_week} - NO secondary (too late in month)")
                week_3_plus_count += 1
            else:
                # Week 1 or 2 - look for secondary
                print(f"   🔍 {stock}: Primary is Week {primary_week} - Looking for secondary...")
                week_1_2_count += 1
                
                secondary = self.select_secondary_recommendation(scored_options, primary, stock)
                
                if secondary:
                    secondary_recommendations[stock] = secondary
                    secondaries_found += 1
                    
                    # Display secondary selection
                    print(f"      ✓ Secondary found!")
                    print(f"         Strike: ${secondary['strike']}, Expiry: {secondary['expiry']} (Week {secondary['week']})")
                    print(f"         Score: ${secondary['score']:.2f}, Premium: ${secondary['premium']:.2f}")
                    print(f"         Gap: {secondary['expiry']} is 7+ days after {primary['expiry']}")
                else:
                    print(f"      ⚠️ No valid secondary found (no options with 7+ day gap)")
        
        # Store secondary recommendations in state
        state["secondary_recommendations"] = secondary_recommendations
        state["status"] = "secondary_selected"
        
        # Summary
        print(f"\n   📊 Summary:")
        print(f"      • Week 1-2 primaries: {week_1_2_count} (eligible for secondary)")
        print(f"      • Week 3-5 primaries: {week_3_plus_count} (too late for secondary)")
        print(f"      • Secondaries found: {secondaries_found}")
        print(f"   ✅ Secondary selection complete")
        
        return state
    
    def allocate_contracts_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:
        """
        PART 2 - PHASE 6: Allocate contracts based on portfolio holdings
        
        Strategy:
        - Large positions (≥3 contracts): Keep 1 contract buffer
        - Small positions (<3 contracts): Use all contracts
        
        Workflow:
        1. Check if portfolio_data exists
        2. For each stock with primary recommendation:
           - Get shares from portfolio
           - Calculate contract allocation
           - Store in state
        
        Only runs when analysis_mode = "premium_delta" and portfolio_data provided
        """
        print("\n💼 Node 2E: Allocating contracts...")
        
        analysis_mode = state.get("analysis_mode", "premium_only")
        
        # Check if we should run contract allocation
        if analysis_mode == "premium_only":
            print("   ⏭️ Skipping - Mode is 'premium_only'")
            return state
        
        # Check if we have portfolio data
        portfolio_data = state.get("portfolio_data")
        if not portfolio_data:
            print("   ⚠️ No portfolio data provided - skipping contract allocation")
            print("   ℹ️  Will recommend 1 contract per stock by default")
            return state
        
        # Check if we have primary recommendations
        primary_recommendations = state.get("primary_recommendations", {})
        if not primary_recommendations:
            print("   ⚠️ No primary recommendations available")
            return state
        
        print(f"   🔍 Allocating contracts for {len(primary_recommendations)} stock(s)...")
        
        contract_allocations = {}
        
        for stock in primary_recommendations.keys():
            # Get shares from portfolio
            shares = portfolio_data.get(stock, 0)
            
            if shares == 0:
                print(f"   ⚠️ {stock}: Not in portfolio - skipping allocation")
                continue
            
            if shares < 100:
                print(f"   ⚠️ {stock}: Only {shares} shares (need 100 for 1 contract) - skipping")
                continue
            
            # Calculate allocation
            allocation = self.calculate_contracts(shares, stock)
            contract_allocations[stock] = allocation
            
            # Display allocation
            print(f"   ✓ {stock}: {shares} shares")
            print(f"      Total contracts: {allocation['total_contracts']}")
            print(f"      Recommended: {allocation['recommended']} contract(s)")
            if allocation['buffer'] > 0:
                print(f"      Buffer: {allocation['buffer']} contract ({allocation['buffer_shares']} shares)")
        
        # Store allocations in state
        state["contract_allocations"] = contract_allocations
        state["status"] = "contracts_allocated"
        
        print(f"   ✅ Contract allocation complete for {len(contract_allocations)} stock(s)")
        
        return state
    
    def calculate_income_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:
        """
        PART 2 - PHASE 7: Calculate projected income from all recommendations
        
        Formula: Income = Premium × Contracts × 100
        
        Workflow:
        1. Check if we have primaries, contract allocations
        2. For each stock:
           - Get primary recommendation
           - Get secondary recommendation (if exists)
           - Get contract allocation
           - Calculate income using formula
           - Store per-stock income
        3. Calculate total portfolio income
        
        Only runs when analysis_mode = "premium_delta"
        """
        print("\n💰 Node 2F: Calculating projected income...")
        
        analysis_mode = state.get("analysis_mode", "premium_only")
        
        # Check if we should run income calculation
        if analysis_mode == "premium_only":
            print("   ⏭️ Skipping - Mode is 'premium_only'")
            return state
        
        # Check if we have necessary data
        primary_recommendations = state.get("primary_recommendations", {})
        if not primary_recommendations:
            print("   ⚠️ No primary recommendations available")
            return state
        
        secondary_recommendations = state.get("secondary_recommendations", {})
        contract_allocations = state.get("contract_allocations", {})
        
        # If no allocations, assume 1 contract per stock
        default_contracts = not bool(contract_allocations)
        
        if default_contracts:
            print("   ℹ️  No contract allocations - using 1 contract per stock")
        
        print(f"   🔍 Calculating income for {len(primary_recommendations)} stock(s)...")
        
        income_projections = {}
        total_portfolio_income = 0.0
        
        for stock, primary in primary_recommendations.items():
            # Get secondary (if exists)
            secondary = secondary_recommendations.get(stock)
            
            # Get contracts (default to 1 if no allocation)
            if stock in contract_allocations:
                contracts = contract_allocations[stock]['recommended']
            else:
                contracts = 1
            
            # Calculate income
            income = self.calculate_income(primary, secondary, contracts, stock)
            income_projections[stock] = income
            total_portfolio_income += income['total_income']
            
            # Display income
            print(f"   ✓ {stock}: {contracts} contract(s)")
            print(f"      Primary: ${income['primary_income']:,.2f} ({primary['expiry']})")
            
            if income['has_secondary']:
                print(f"      Secondary: ${income['secondary_income']:,.2f} ({secondary['expiry']})")
                print(f"      Total: ${income['total_income']:,.2f} 💰💰")
            else:
                print(f"      Total: ${income['total_income']:,.2f} 💰")
        
        # Store income projections in state
        state["income_projections"] = income_projections
        state["status"] = "income_calculated"
        
        # Display total portfolio income
        print(f"\n   📊 Portfolio Summary:")
        print(f"      Total Projected Monthly Income: ${total_portfolio_income:,.2f} 💰")
        print(f"      Stocks with income: {len(income_projections)}")
        
        # Count multi-trade stocks
        multi_trade_count = sum(1 for inc in income_projections.values() if inc['has_secondary'])
        single_trade_count = len(income_projections) - multi_trade_count
        
        print(f"      Multi-trade strategies: {multi_trade_count} (primary + secondary)")
        print(f"      Single-trade strategies: {single_trade_count} (primary only)")
        print(f"   ✅ Income calculation complete")
        
        return state
    
    def generate_recommendations_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:

        """
        Node 3: Generate strategy recommendations based on analysis
        
        PART 1: Simple premium-based recommendations
        PART 2: Premium_delta mode - recommendations already generated in Nodes 2C-2F
        """
        print("\n💡 Node 3: Generating recommendations...")
        
        analysis_mode = state.get("analysis_mode", "premium_only")
        
        # In premium_delta mode, recommendations are already generated in Nodes 2C-2F
        if analysis_mode == "premium_delta" and state["status"] == "income_calculated":
            print("   ✅ Using recommendations from premium_delta workflow (Nodes 2C-2F)")
            state["status"] = "recommendations_generated"
            return state
        
        # For premium_only mode, generate recommendations here
        if state["status"] != "premiums_analyzed":
            print("   ⚠️ Skipping recommendations - premium analysis not complete")
            return state
        
        highest_premium_cells = state["highest_premium_cells"]
        stock_analysis = state["stock_analysis"]
        scoring_config = state.get("scoring_config", self.default_scoring_config)
        
        recommendations = []
        
        # Generate recommendations for each stock
        for stock, cell_info in highest_premium_cells.items():
            analysis = stock_analysis[stock]
            
            # Calculate confidence based on premium vs average
            premium_ratio = cell_info['premium'] / analysis['avg_premium'] if analysis['avg_premium'] > 0 else 1
            
            if premium_ratio >= 1.5:
                confidence = "HIGH"
            elif premium_ratio >= 1.2:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
            
            recommendation = {
                'stock': stock,
                'strategy': 'Sell Covered Call',  # Simple strategy for PART 1
                'strike_price': cell_info['strike_price'],
                'expiration': cell_info['expiration_date'],
                'premium': cell_info['premium'],
                'rationale': f"Highest premium of ${cell_info['premium']:.2f} available ({premium_ratio:.1f}x average)",
                'confidence': confidence,
                # Placeholders for PART 2 enhancements
                'delta': None,  # Will be populated in PART 2
                'expected_return': None,  # Will be calculated in PART 2
                'risk_score': None  # Will be calculated in PART 2
            }
            
            recommendations.append(recommendation)
            print(f"   ✓ {stock}: {recommendation['strategy']} - ${recommendation['premium']:.2f} ({confidence} confidence)")
        
        # Sort by premium (highest first)
        recommendations.sort(key=lambda x: x['premium'], reverse=True)
        
        # Update state
        state["recommendations"] = recommendations
        state["status"] = "recommendations_generated"
        
        print(f"   ✅ Generated {len(recommendations)} recommendations")
        
        return state
    
    def prepare_highlighting_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:
        """
        Node 4: Prepare cell highlighting information for UI
        
        Creates a mapping of which cells should be highlighted
        Format: {row_index: [column_names]}
        
        PART 2: In premium_delta mode, use primary/secondary recommendations from Nodes 2C-2D
        """
        print("\n🎨 Node 4: Preparing cell highlighting...")
        
        if state["status"] != "recommendations_generated":
            print("   ⚠️ Skipping highlighting - recommendations not generated")
            return state
        
        analysis_mode = state.get("analysis_mode", "premium_only")
        
        # In premium_delta mode, create highlighting from primary/secondary recommendations
        if analysis_mode == "premium_delta":
            primary_recommendations = state.get("primary_recommendations", {})
            secondary_recommendations = state.get("secondary_recommendations", {})
            options_df = state.get("options_dataframe")
            
            if options_df is None:
                print("   ⚠️ No options dataframe available for highlighting")
                state["highlighted_cells"] = {}
                state["status"] = "highlighting_prepared"
                return state
            
            # Create highlighting in the format the UI expects: {row_index: [column_names]}
            highlighted_cells = {}
            
            for stock, primary in primary_recommendations.items():
                # Find the row in options_df that matches this stock and strike
                # Convert strike to string for comparison since DataFrame has string values
                strike_str = str(primary['strike'])
                matching_rows = options_df[
                    (options_df['Stock'] == stock) & 
                    (options_df['Strike_Price'] == strike_str)
                ]
                
                if not matching_rows.empty:
                    row_idx = matching_rows.index[0]
                    expiry_col = primary['expiry']  # e.g., "12/05/25"
                    
                    if row_idx not in highlighted_cells:
                        highlighted_cells[row_idx] = []
                    highlighted_cells[row_idx].append(expiry_col)
                
                # Add secondary if it exists
                if stock in secondary_recommendations:
                    secondary = secondary_recommendations[stock]
                    strike_str = str(secondary['strike'])
                    matching_rows = options_df[
                        (options_df['Stock'] == stock) & 
                        (options_df['Strike_Price'] == strike_str)
                    ]
                    
                    if not matching_rows.empty:
                        row_idx = matching_rows.index[0]
                        expiry_col = secondary['expiry']
                        
                        if row_idx not in highlighted_cells:
                            highlighted_cells[row_idx] = []
                        highlighted_cells[row_idx].append(expiry_col)
            
            state["highlighted_cells"] = highlighted_cells
            state["status"] = "highlighting_prepared"
            print(f"   ✅ Prepared highlighting for {len(highlighted_cells)} cells")
            return state
        
        # For premium_only mode, use highest_premium_cells
        highest_premium_cells = state["highest_premium_cells"]
        
        # Store highlighting information
        highlight_info = {}
        
        for stock, cell_info in highest_premium_cells.items():
            row_idx = cell_info['row_index']
            expiration_col = cell_info['expiration_date']
            
            # Store which cell to highlight
            if row_idx not in highlight_info:
                highlight_info[row_idx] = []
            highlight_info[row_idx].append(expiration_col)
        
        # Update state
        state["highlighted_cells"] = highlight_info
        state["status"] = "highlighting_prepared"
        
        print(f"   ✅ Prepared highlighting for {len(highlight_info)} cells")
        
        return state
    
    def llm_generate_insights_node(self, state: StrategyAnalysisState) -> StrategyAnalysisState:
        """
        Node 5: LLM generates professional insights and analysis
        
        Uses GPT to create human-readable analysis of the recommendations
        
        PART 2: In premium_delta mode, use income projections and primary/secondary recommendations
        """
        print("\n🧠 Node 5: Generating LLM insights...")
        
        if not self.llm:
            state["llm_insights"] = "LLM insights unavailable (no OpenAI API key configured)"
            state["status"] = "analysis_complete"
            print("   ⚠️ LLM not available - skipping insights generation")
            return state
        
        analysis_mode = state.get("analysis_mode", "premium_only")
        
        # In premium_delta mode, use income projections
        if analysis_mode == "premium_delta":
            income_projections = state.get("income_projections", {})
            primary_recommendations = state.get("primary_recommendations", {})
            secondary_recommendations = state.get("secondary_recommendations", {})
            
            if not income_projections:
                state["llm_insights"] = "No income projections available for analysis"
                state["status"] = "analysis_complete"
                print("   ⚠️ No income projections to analyze")
                return state
            
            # Create summary for LLM
            total_income = sum(inc['total_income'] for inc in income_projections.values())
            multi_trade_count = sum(1 for inc in income_projections.values() if inc['has_secondary'])
            
            rec_summary = f"Total Monthly Income: ${total_income:,.2f}\n"
            rec_summary += f"Stocks: {len(income_projections)}\n"
            rec_summary += f"Multi-trade strategies: {multi_trade_count}\n\n"
            
            for stock, income in income_projections.items():
                primary = primary_recommendations[stock]
                rec_summary += f"{stock}: ${income['total_income']:,.2f}\n"
                rec_summary += f"  Primary: ${primary['strike']} exp {primary['expiry']} (${income['primary_income']:,.2f})\n"
                
                if income['has_secondary']:
                    secondary = secondary_recommendations[stock]
                    rec_summary += f"  Secondary: ${secondary['strike']} exp {secondary['expiry']} (${income['secondary_income']:,.2f})\n"
            
            prompt = f"""
Based on the following covered call recommendations, provide professional investment insights:

{rec_summary}

Provide:
1. Overall assessment of the strategy
2. Risk/reward analysis
3. Key considerations for the investor
4. Market outlook implications

Keep it concise (3-4 sentences) and professional.
"""
            
            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                insights = response.content
                state["llm_insights"] = insights
                state["status"] = "analysis_complete"
                print("   ✅ LLM insights generated")
            except Exception as e:
                state["llm_insights"] = f"Error generating insights: {str(e)}"
                state["status"] = "analysis_complete"
                print(f"   ⚠️ Error generating insights: {e}")
            
            return state
        
        # For premium_only mode, use recommendations
        recommendations = state.get("recommendations", [])
        stock_analysis = state.get("stock_analysis", {})
        
        if not recommendations:
            state["llm_insights"] = "No recommendations available for analysis"
            state["status"] = "analysis_complete"
            print("   ⚠️ No recommendations to analyze")
            return state
        
        # Create analysis prompt
        rec_summary = "\n".join([
            f"{i+1}. {rec['stock']}: {rec['strategy']} at ${rec['strike_price']} "
            f"expiring {rec['expiration']} for ${rec['premium']:.2f} premium ({rec['confidence']} confidence)"
            for i, rec in enumerate(recommendations)
        ])
        
        prompt = f"""
        You are a professional options trading analyst. Analyze these strategy recommendations and provide insights.
        
        RECOMMENDATIONS:
        {rec_summary}
        
        STOCK ANALYSIS DATA:
        {json.dumps(stock_analysis, indent=2, default=str)}
        
        Provide a concise professional analysis covering:
        1. Overall assessment of the opportunities
        2. Which recommendations are most attractive and why
        3. Risk considerations for each strategy
        4. Timing and execution suggestions
        5. Portfolio diversification thoughts
        
        Keep the analysis practical and actionable for covered call strategies.
        Limit response to 250-300 words.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            state["llm_insights"] = response.content.strip()
            
            print("   ✅ LLM insights generated successfully")
            
            # Add success message
            state["messages"].append(AIMessage(
                content=f"✅ Analysis complete! Generated {len(recommendations)} recommendations with professional insights."
            ))
            
        except Exception as e:
            print(f"   ❌ LLM error: {e}")
            state["llm_insights"] = "Failed to generate LLM insights due to API error."
            state["errors"].append(f"LLM insights generation failed: {e}")
        
        # Update state
        state["status"] = "analysis_complete"
        state["analysis_timestamp"] = datetime.now().isoformat()
        
        return state
    
    # =============================================================================
    # 4. WORKFLOW BUILDING
    # =============================================================================
    
    def _build_strategy_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for strategy recommendation
        
        Workflow:
        1. Validate Input → Check data quality
        2. Analyze Premiums → Find highest premiums (Part 1)
        2B. Calculate Scores → Delta-based scoring (Part 2 - conditional)
        2C. Select Primary → Choose best option per stock (Part 2 - Phase 4)
        2D. Select Secondary → Find secondary trades for Week 1-2 primaries (Part 2 - Phase 5)
        2E. Allocate Contracts → Calculate contracts based on portfolio (Part 2 - Phase 6)
        2F. Calculate Income → Project monthly income (Part 2 - Phase 7)
        3. Generate Recommendations → Create strategy recommendations
        4. Prepare Highlighting → Mark cells for UI
        5. LLM Insights → Generate professional analysis
        """
        workflow = StateGraph(StrategyAnalysisState)
        
        # Add nodes
        workflow.add_node("validate_input", self.validate_input_node)
        workflow.add_node("analyze_premiums", self.analyze_premiums_node)
        workflow.add_node("calculate_scores", self.calculate_scores_node)  # PART 2
        workflow.add_node("select_primary", self.select_primary_node)      # PART 2 - Phase 4
        workflow.add_node("select_secondary", self.select_secondary_node)  # PART 2 - Phase 5
        workflow.add_node("allocate_contracts", self.allocate_contracts_node)  # PART 2 - Phase 6
        workflow.add_node("calculate_income", self.calculate_income_node)  # PART 2 - Phase 7
        workflow.add_node("generate_recommendations", self.generate_recommendations_node)
        workflow.add_node("prepare_highlighting", self.prepare_highlighting_node)
        workflow.add_node("llm_insights", self.llm_generate_insights_node)
        
        # Define workflow edges
        workflow.add_edge(START, "validate_input")
        workflow.add_edge("validate_input", "analyze_premiums")
        workflow.add_edge("analyze_premiums", "calculate_scores")  # PART 2: Add scoring step
        workflow.add_edge("calculate_scores", "select_primary")     # PART 2: Add primary selection
        workflow.add_edge("select_primary", "select_secondary")     # PART 2: Add secondary selection
        workflow.add_edge("select_secondary", "allocate_contracts") # PART 2: Add contract allocation
        workflow.add_edge("allocate_contracts", "calculate_income") # PART 2: Add income calculation
        workflow.add_edge("calculate_income", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "prepare_highlighting")
        workflow.add_edge("prepare_highlighting", "llm_insights")
        workflow.add_edge("llm_insights", END)
        
        return workflow.compile()
    
    # =============================================================================
    # 5. USER INTERFACE FUNCTIONS
    # =============================================================================
    
    def analyze(
        self,
        options_df: pd.DataFrame,
        delta_data: Optional[pd.DataFrame] = None,
        portfolio_data: Optional[Dict[str, int]] = None,
        current_date: Optional[str] = None,
        analysis_mode: str = "premium_only"
    ) -> Dict:
        """
        Main interface for strategy recommendation analysis
        
        Args:
            options_df: DataFrame with options data from Agent 1
                       Format: Stock | Strike_Price | Date1 | Date2 | Date3 | Date4 | Date5 | Date6
            delta_data: DataFrame with Delta values from Agent 1 (PART 2)
                       Format: Stock | Strike_Price | Date1 | Date2 | Date3 | Date4 | Date5 | Date6
            portfolio_data: Dictionary mapping stock symbols to shares owned (PART 2 - Phase 6)
                          Format: {"AAPL": 600, "TSLA": 400, "MSFT": 300}
            current_date: Current date for expiration filtering (YYYY-MM-DD format) (PART 2 - Phase 8)
                         If None, uses pd.Timestamp.now()
            analysis_mode: "premium_only" (Part 1) or "premium_delta" (Part 2)
        
        Returns:
            Dict with analysis results including:
            - recommendations: List of strategy recommendations
            - highlighted_cells: Cells to highlight in UI
            - llm_insights: Professional analysis
            - stock_analysis: Detailed metrics per stock
            - contract_allocations: Contract allocation per stock (PART 2)
            - income_projections: Income projections per stock (PART 2)
        """
        # Use current date if not provided
        if current_date is None:
            current_date = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        # Initialize state
        initial_state = StrategyAnalysisState(
            options_dataframe=options_df,
            delta_data=delta_data,
            portfolio_data=portfolio_data,  # PART 2 - Phase 6
            current_date=current_date,      # PART 2 - Phase 8
            analysis_mode=analysis_mode,
            validated_data=False,
            premium_analysis={},
            highest_premium_cells={},
            stock_analysis={},
            merged_data=None,
            primary_recommendations={},
            secondary_recommendations={},  # PART 2 - Phase 5
            contract_allocations={},       # PART 2 - Phase 6
            income_projections={},         # PART 2 - Phase 7
            recommendations=[],
            llm_insights=None,
            highlighted_cells={},
            scoring_config=self.default_scoring_config,
            messages=[],
            status="initializing",
            errors=[],
            analysis_timestamp=""
        )
        
        print(f"\n🚀 Starting Strategy Recommendation Analysis (LangGraph)...")
        print(f"📊 Input shape: {options_df.shape if options_df is not None else 'None'}")
        print(f"📅 Current date: {current_date}")
        print(f"🎯 Mode: {analysis_mode}")
        if portfolio_data:
            print(f"💼 Portfolio: {len(portfolio_data)} stock(s)")
        print("-" * 70)
        
        try:
            # Run the LangGraph workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Prepare response
            response = {
                "success": final_state["status"] == "analysis_complete",
                "status": final_state["status"],
                "highest_premium_cells": final_state.get("highest_premium_cells", {}),
                "stock_analysis": final_state.get("stock_analysis", {}),
                "recommendations": final_state.get("recommendations", []),
                "highlighted_cells": final_state.get("highlighted_cells", {}),
                "llm_insights": final_state.get("llm_insights"),
                "merged_data": final_state.get("merged_data"),  # PART 2: Include scored options
                "primary_recommendations": final_state.get("primary_recommendations", {}),  # PART 2: Phase 4
                "secondary_recommendations": final_state.get("secondary_recommendations", {}),  # PART 2: Phase 5
                "contract_allocations": final_state.get("contract_allocations", {}),  # PART 2: Phase 6
                "income_projections": final_state.get("income_projections", {}),  # PART 2: Phase 7
                "analysis_timestamp": final_state.get("analysis_timestamp", ""),
                "errors": final_state.get("errors", []),
                "messages": [msg.content for msg in final_state.get("messages", [])]
            }
            
            print("-" * 70)
            if response["success"]:
                print(f"✅ LangGraph workflow completed successfully!")
                print(f"💡 Recommendations: {len(response['recommendations'])}")
                print(f"🎨 Highlighted cells: {len(response['highlighted_cells'])}")
            else:
                print(f"❌ Workflow failed: {final_state['status']}")
                if final_state.get("errors"):
                    for error in final_state["errors"]:
                        print(f"   💥 {error}")
            
            return response
            
        except Exception as e:
            error_response = {
                "success": False,
                "status": "workflow_error",
                "error": str(e),
                "highest_premium_cells": {},
                "stock_analysis": {},
                "recommendations": [],
                "highlighted_cells": {},
                "llm_insights": None,
                "analysis_timestamp": "",
                "errors": [str(e)],
                "messages": []
            }
            print(f"❌ Workflow error: {e}")
            import traceback
            traceback.print_exc()
            return error_response
    
    def get_highlighted_dataframe(self, options_df: pd.DataFrame, analysis_results: Dict) -> pd.DataFrame:
        """
        Get the original dataframe (highlighting info is in analysis_results)
        
        Args:
            options_df: Original options DataFrame
            analysis_results: Results from analyze() method
        
        Returns:
            DataFrame (same as input - highlighting is handled separately)
        """
        return options_df.copy()
    
    def get_styling_function(self, highlighted_cells: Dict):
        """
        Returns a function that can be used with pandas.style.apply()
        to highlight the highest premium cells
        
        Args:
            highlighted_cells: Dict from analysis_results['highlighted_cells']
        
        Returns:
            Function for pandas styling
        """
        def highlight_max_premium(row):
            """Apply green background to cells with highest premium"""
            styles = [''] * len(row)
            
            # Check if this row should have any highlighted cells
            if row.name in highlighted_cells:
                cols_to_highlight = highlighted_cells[row.name]
                
                for col_name in cols_to_highlight:
                    if col_name in row.index:
                        col_idx = row.index.get_loc(col_name)
                        styles[col_idx] = 'background-color: #90EE90; color: black; font-weight: bold'
            
            return styles
        
        return highlight_max_premium
    
    def export_analysis_summary(self, analysis_results: Dict) -> str:
        """
        Export analysis summary as formatted string
        
        Args:
            analysis_results: Results from analyze() method
        
        Returns:
            Formatted string with analysis summary
        """
        if not analysis_results or not analysis_results.get("success"):
            return "No analysis results available"
        
        summary_lines = [
            "=" * 60,
            "AGENT 2: STRATEGY RECOMMENDATION ANALYSIS (LANGGRAPH)",
            "=" * 60,
            ""
        ]
        
        # Overall statistics
        summary_lines.append(f"Analysis Timestamp: {analysis_results.get('analysis_timestamp', 'N/A')}")
        summary_lines.append(f"Total Stocks Analyzed: {len(analysis_results.get('stock_analysis', {}))}")
        summary_lines.append("")
        
        # Per-stock analysis
        summary_lines.append("HIGHEST PREMIUM OPPORTUNITIES:")
        summary_lines.append("-" * 60)
        
        for stock, analysis in analysis_results.get('stock_analysis', {}).items():
            summary_lines.append(f"\n{stock}:")
            summary_lines.append(f"  • Highest Premium: ${analysis['highest_premium']:.2f}")
            summary_lines.append(f"  • Average Premium: ${analysis['avg_premium']:.2f}")
            summary_lines.append(f"  • Best Strike: ${analysis['best_strike']}")
            summary_lines.append(f"  • Best Expiration: {analysis['best_expiration']}")
        
        # Recommendations
        summary_lines.append("\n" + "=" * 60)
        summary_lines.append("RECOMMENDATIONS:")
        summary_lines.append("=" * 60)
        
        for i, rec in enumerate(analysis_results.get('recommendations', []), 1):
            summary_lines.append(f"\n{i}. {rec['stock']}:")
            summary_lines.append(f"   Strategy: {rec['strategy']}")
            summary_lines.append(f"   Strike: ${rec['strike_price']} | Expiration: {rec['expiration']}")
            summary_lines.append(f"   Premium: ${rec['premium']:.2f}")
            summary_lines.append(f"   Confidence: {rec['confidence']}")
            summary_lines.append(f"   Rationale: {rec['rationale']}")
        
        # LLM Insights
        if analysis_results.get('llm_insights'):
            summary_lines.append("\n" + "=" * 60)
            summary_lines.append("LLM PROFESSIONAL INSIGHTS:")
            summary_lines.append("=" * 60)
            summary_lines.append(analysis_results['llm_insights'])
        
        summary_lines.append("\n" + "=" * 60)
        
        return "\n".join(summary_lines)
    
    # =============================================================================
    # 6. PART 2: PLACEHOLDER METHODS FOR FUTURE ENHANCEMENTS
    # =============================================================================
    
    def configure_scoring_formula(self, formula_config: Dict):
        """
        PART 2: Configure custom scoring formula
        
        This method will be used to set up the scoring formula
        decided in the mentor meeting.
        
        Example config:
        {
            'use_delta': True,
            'weights': {
                'premium': 0.6,
                'delta': 0.4
            },
            'custom_formula': 'premium * 0.6 + abs(delta - 0.3) * 0.4'
        }
        """
        self.default_scoring_config.update(formula_config)
        print(f"✓ Scoring configuration updated: {self.default_scoring_config}")


# =============================================================================
# HELPER FUNCTIONS FOR UI INTEGRATION
# =============================================================================

def create_strategy_agent() -> StrategyRecommendationAgentLangGraph:
    """
    Factory function to create a new Strategy Recommendation Agent instance
    
    Returns:
        Initialized StrategyRecommendationAgentLangGraph
    """
    return StrategyRecommendationAgentLangGraph()


def analyze_and_highlight(options_df: pd.DataFrame):
    """
    Convenience function for UI integration
    
    Analyzes options data and returns results with highlighting info
    
    Args:
        options_df: Options data from Agent 1
    
    Returns:
        Tuple of (original_df, analysis_results, agent_instance)
    """
    # Create agent
    agent = create_strategy_agent()
    
    # Run analysis
    results = agent.analyze(options_df)
    
    return options_df, results, agent
