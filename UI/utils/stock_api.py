"""
Stock API Integration - Live Data Only (Finnhub & Alpha Vantage)
Requires API key to function - no mock data fallback
"""
import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

class StockAPI:
    """
    Stock market API wrapper for live data
    Supports Finnhub (primary) and Alpha Vantage (backup)
    """
    
    def __init__(self):
        self.finnhub_base_url = 'https://finnhub.io/api/v1'
        self.alpha_vantage_base_url = 'https://www.alphavantage.co/query'
        self.api_configured = bool(FINNHUB_API_KEY or ALPHA_VANTAGE_API_KEY)
        
        # Log API status
        if not self.api_configured:
            print("⚠️  WARNING: No API key configured!")
            print("    Add FINNHUB_API_KEY or ALPHA_VANTAGE_API_KEY to .env file")
        elif FINNHUB_API_KEY:
            print("✅ Finnhub API configured")
        elif ALPHA_VANTAGE_API_KEY:
            print("✅ Alpha Vantage API configured")
    
    def search_stocks_finnhub(self, query: str) -> List[Dict]:
        """
        Search stocks using Finnhub API
        
        Args:
            query: Search term (stock name or symbol)
            
        Returns:
            List of stock dictionaries with symbol, name, and type
            
        Raises:
            ValueError: If API key not configured
            requests.RequestException: If API request fails
        """
        if not FINNHUB_API_KEY:
            raise ValueError(
                "Finnhub API key not configured. "
                "Add FINNHUB_API_KEY to .env file. "
                "Get free key at: https://finnhub.io/register"
            )
        
        try:
            response = requests.get(
                f'{self.finnhub_base_url}/search',
                params={
                    'q': query,
                    'token': FINNHUB_API_KEY
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Filter and format results
            stocks = []
            for item in data.get('result', []):
                # Filter for common stocks and ETPs
                if item.get('type') in ['Common Stock', 'ETP', 'Stock', 'Equity']:
                    stocks.append({
                        'symbol': item.get('symbol', ''),
                        'name': item.get('description', ''),
                        'type': 'Stock'
                    })
            
            # Limit to top 10 results
            return stocks[:10]
            
        except requests.exceptions.Timeout:
            raise Exception("API request timed out. Please try again.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise Exception("API rate limit reached. Please wait a moment and try again.")
            elif e.response.status_code == 401:
                raise Exception("Invalid API key. Please check your FINNHUB_API_KEY in .env file.")
            else:
                raise Exception(f"API error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def search_stocks_alpha_vantage(self, query: str) -> List[Dict]:
        """
        Search stocks using Alpha Vantage API
        
        Args:
            query: Search term (stock name or symbol)
            
        Returns:
            List of stock dictionaries with symbol, name, and type
            
        Raises:
            ValueError: If API key not configured
            requests.RequestException: If API request fails
        """
        if not ALPHA_VANTAGE_API_KEY:
            raise ValueError(
                "Alpha Vantage API key not configured. "
                "Add ALPHA_VANTAGE_API_KEY to .env file. "
                "Get free key at: https://www.alphavantage.co/support/#api-key"
            )
        
        try:
            response = requests.get(
                self.alpha_vantage_base_url,
                params={
                    'function': 'SYMBOL_SEARCH',
                    'keywords': query,
                    'apikey': ALPHA_VANTAGE_API_KEY
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for error messages
            if 'Error Message' in data:
                raise Exception(f"API error: {data['Error Message']}")
            
            if 'Note' in data:
                raise Exception("API rate limit reached. Free tier: 25 requests/day, 5 requests/minute.")
            
            # Format results
            stocks = []
            for item in data.get('bestMatches', []):
                stocks.append({
                    'symbol': item.get('1. symbol', ''),
                    'name': item.get('2. name', ''),
                    'type': 'Stock'
                })
            
            # Limit to top 10 results
            return stocks[:10]
            
        except requests.exceptions.Timeout:
            raise Exception("API request timed out. Please try again.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise Exception("API rate limit reached. Free tier: 25 requests/day.")
            else:
                raise Exception(f"API error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def search_stocks(self, query: str) -> List[Dict]:
        """
        Search stocks using available API
        Tries Finnhub first, then Alpha Vantage as backup
        
        Args:
            query: Search term (stock name or symbol)
            
        Returns:
            List of stock dictionaries
            
        Raises:
            ValueError: If no API key configured
        """
        if not query or len(query.strip()) == 0:
            return []
        
        # Check if any API is configured
        if not self.api_configured:
            raise ValueError(
                "No API key configured. Please add one of the following to your .env file:\n"
                "  - FINNHUB_API_KEY (get at https://finnhub.io/register)\n"
                "  - ALPHA_VANTAGE_API_KEY (get at https://www.alphavantage.co/support/#api-key)"
            )
        
        try:
            # Try Finnhub first (better free tier)
            if FINNHUB_API_KEY:
                return self.search_stocks_finnhub(query)
            # Fall back to Alpha Vantage
            elif ALPHA_VANTAGE_API_KEY:
                return self.search_stocks_alpha_vantage(query)
        except Exception as e:
            # Log error and re-raise
            print(f"❌ Search error: {str(e)}")
            raise
    
    def get_stock_price_finnhub(self, symbol: str) -> Optional[float]:
        """
        Get current stock price using Finnhub API
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Current price as float, or None if error
        """
        if not FINNHUB_API_KEY:
            print("⚠️  Finnhub API key not configured")
            return None
        
        try:
            response = requests.get(
                f'{self.finnhub_base_url}/quote',
                params={
                    'symbol': symbol,
                    'token': FINNHUB_API_KEY
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Get current price (c = current price)
            price = data.get('c')
            
            if price and price > 0:
                return float(price)
            else:
                print(f"⚠️  No price data for {symbol}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Price fetch error for {symbol}: {str(e)}")
            return None
    
    def get_stock_price_alpha_vantage(self, symbol: str) -> Optional[float]:
        """
        Get current stock price using Alpha Vantage API
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Current price as float, or None if error
        """
        if not ALPHA_VANTAGE_API_KEY:
            print("⚠️  Alpha Vantage API key not configured")
            return None
        
        try:
            response = requests.get(
                self.alpha_vantage_base_url,
                params={
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': ALPHA_VANTAGE_API_KEY
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for errors
            if 'Error Message' in data:
                print(f"⚠️  API error for {symbol}: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                print("⚠️  API rate limit reached")
                return None
            
            # Get price from response
            quote = data.get('Global Quote', {})
            price_str = quote.get('05. price')
            
            if price_str:
                return float(price_str)
            else:
                print(f"⚠️  No price data for {symbol}")
                return None
                
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"❌ Price fetch error for {symbol}: {str(e)}")
            return None
    
    def get_stock_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price using available API
        Tries Finnhub first, then Alpha Vantage as backup
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Current price as float, or None if not available
        """
        if not self.api_configured:
            print("⚠️  No API configured - cannot fetch price")
            return None
        
        try:
            # Try Finnhub first
            if FINNHUB_API_KEY:
                price = self.get_stock_price_finnhub(symbol)
                if price:
                    return price
            
            # Fall back to Alpha Vantage
            if ALPHA_VANTAGE_API_KEY:
                price = self.get_stock_price_alpha_vantage(symbol)
                if price:
                    return price
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting price for {symbol}: {str(e)}")
            return None


# Create singleton instance
_api_instance = None

def get_stock_api() -> StockAPI:
    """Get or create StockAPI singleton instance"""
    global _api_instance
    if _api_instance is None:
        _api_instance = StockAPI()
    return _api_instance