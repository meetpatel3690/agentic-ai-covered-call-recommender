import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StockAPI:
    """Wrapper for Alpha Vantage API to search stocks"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            print("⚠️ Warning: ALPHA_VANTAGE_API_KEY not found in .env file")
        self.base_url = "https://www.alphavantage.co/query"
    
    def search_stocks(self, keywords):
        """
        Search for stocks by keywords (company name or symbol)
        
        Args:
            keywords (str): Search term
            
        Returns:
            list: List of matching stocks with name and symbol
        """
        if not keywords or len(keywords) < 1:
            return []
        
        try:
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': keywords,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'bestMatches' in data:
                results = []
                for match in data['bestMatches'][:10]:  # Limit to top 10
                    results.append({
                        'symbol': match.get('1. symbol', ''),
                        'name': match.get('2. name', ''),
                        'type': match.get('3. type', ''),
                        'region': match.get('4. region', ''),
                    })
                return results
            
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching stocks: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
