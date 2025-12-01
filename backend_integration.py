import sys
import os
from pathlib import Path
import json
import pandas as pd
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Verify API keys are loaded
if not os.getenv('ALPHA_VANTAGE_API_KEY'):
    print("⚠️ Warning: ALPHA_VANTAGE_API_KEY not found in .env")
if not os.getenv('OPENAI_API_KEY'):
    print("⚠️ Warning: OPENAI_API_KEY not found in .env")

# Add backend directory to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from options_data_agent import LLMOptionsAgent

class OptionsDataFetcher:
    """
    Handles fetching and processing options data from the backend agent
    """
    
    def __init__(self):
        """Initialize the options agent"""
        try:
            self.agent = LLMOptionsAgent()
            print(" Backend agent initialized successfully")
        except Exception as e:
            print(f" Failed to initialize backend agent: {e}")
            raise
    
    def load_portfolio_from_json(self, json_file: str = "UI/portfolio_data.json") -> Dict:
        """
        Load portfolio data from JSON file in UI folder
        
        Args:
            json_file: Path to portfolio JSON file (default: UI/portfolio_data.json)
            
        Returns:
            Dict with portfolio data
        """
        try:
            # Convert relative path to absolute path from project root
            if not os.path.isabs(json_file):
                project_root = Path(__file__).parent
                json_file = project_root / json_file
            
            with open(json_file, 'r') as f:
                portfolio = json.load(f)
            print(f" Loaded {len(portfolio)} stocks from {json_file}")
            return portfolio
        except FileNotFoundError:
            print(f" Portfolio file {json_file} not found")
            return []
        except Exception as e:
            print(f" Error loading portfolio: {e}")
            return []
    
    def prepare_symbols_for_agent(self, portfolio: List[Dict]) -> str:
        """
        Convert portfolio list to comma-separated symbols for agent
        
        Args:
            portfolio: List of portfolio stocks
            
        Returns:
            Comma-separated string of symbols
        """
        symbols = [stock['symbol'] for stock in portfolio]
        return ", ".join(symbols)
    
    def fetch_options_data(self, portfolio: List[Dict]) -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Fetch options data for portfolio stocks
        
        Args:
            portfolio: List of portfolio stocks
            
        Returns:
            Tuple of (options_dataframe, delta_dataframe) or (None, None) if failed
        """
        if not portfolio:
            print(" Empty portfolio provided")
            return None, None
        
        try:
            # Prepare symbols
            symbols_str = self.prepare_symbols_for_agent(portfolio)
            print(f" Fetching options data for: {symbols_str}")
            
            # Call the agent - get full result to access delta_matrix
            result = self.agent.analyze(symbols_str)
            
            if result["success"] and result["formatted_matrix"] is not None:
                options_df = result["formatted_matrix"]
                delta_df = result.get("delta_matrix")
                
                print(f" Received options data: {options_df.shape}")
                if delta_df is not None:
                    print(f" Received Delta data: {delta_df.shape}")
                
                return options_df, delta_df
            else:
                print(" No options data returned from agent")
                return None, None
                
        except Exception as e:
            print(f" Error fetching options data: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def calculate_portfolio_metrics(self, portfolio: List[Dict], options_df: Optional[pd.DataFrame]) -> Dict:
        """
        Calculate summary metrics for the portfolio
        100 shares = 1 contract
        
        Args:
            portfolio: List of portfolio stocks
            options_df: Options data DataFrame
            
        Returns:
            Dict with metrics
        """
        metrics = {
            'total_contracts': 0,
            'total_income': 0.0,
            'available_capital': 550000.0,
            'diversification': {},
            'stock_contracts': {}  # Contracts per stock based on shares/100
        }
        
        if not portfolio:
            return metrics
        
        # Calculate contracts based on shares (100 shares = 1 contract)
        print("\n Calculating contracts (100 shares = 1 contract):")
        for stock in portfolio:
            symbol = stock['symbol']
            shares = stock['shares']
            contracts = shares // 100  # Integer division: 256 shares = 2 contracts
            
            if contracts > 0:
                metrics['stock_contracts'][symbol] = contracts
                print(f"   {symbol}: {shares} shares = {contracts} contract{'s' if contracts != 1 else ''}")
            else:
                print(f"   {symbol}: {shares} shares = 0 contracts (need min 100 shares)")
        
        # Calculate total contracts
        metrics['total_contracts'] = sum(metrics['stock_contracts'].values())
        print(f"   Total Contracts: {metrics['total_contracts']}\n")
        
        # Calculate diversification (number of strike prices available per stock)
        if options_df is not None and not options_df.empty:
            stock_counts = options_df['Stock'].value_counts().to_dict()
            metrics['diversification'] = stock_counts
            
            # Calculate potential income from premiums
            date_columns = [col for col in options_df.columns if '/' in col]
            if date_columns:
                for col in date_columns:
                    premiums = pd.to_numeric(options_df[col], errors='coerce').fillna(0)
                    metrics['total_income'] += premiums.sum()
        
        return metrics


def fetch_live_options_data() -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Dict, List[Dict]]:
    """
    Main function to fetch live options data
    
    Returns:
        Tuple of (options_dataframe, delta_dataframe, metrics_dict, portfolio_list)
    """
    try:
        # Initialize fetcher
        fetcher = OptionsDataFetcher()
        
        # Load portfolio from UI/portfolio_data.json
        portfolio = fetcher.load_portfolio_from_json("UI/portfolio_data.json")
        
        if not portfolio:
            print(" No portfolio data found")
            return None, None, {}, []
        
        # Fetch options data (now returns both premium and delta matrices)
        options_df, delta_df = fetcher.fetch_options_data(portfolio)
        
        # Calculate metrics (with correct contract calculation)
        metrics = fetcher.calculate_portfolio_metrics(portfolio, options_df)
        
        return options_df, delta_df, metrics, portfolio
        
    except Exception as e:
        print(f" Error in fetch_live_options_data: {e}")
        import traceback
        traceback.print_exc()
        return None, None, {}, []