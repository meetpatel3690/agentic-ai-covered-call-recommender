# LLM-Orchestrated Options Analysis Agent (test.py)

An advanced Python-based options analysis system featuring sophisticated LLM orchestration for intelligent options premium matrix generation. The system uses OpenAI GPT-3.5-turbo as the central orchestrator to convert natural language inputs to structured financial data, automatically format raw Alpha Vantage options data into clean 6×6 matrices, and generate professional trading insights.

## 🚀 Key Features

- **🤖 LLM Central Orchestration**: GPT-3.5-turbo acts as the intelligent coordinator for the entire workflow
- **🔤 Natural Language Processing**: Converts free text company names to ticker symbols intelligently
- **📊 Automatic Matrix Formatting**: LLM structures raw options data into clean 6×6 premium grids
- **📈 Real-time Financial Data**: Fetches current stock prices and historical options data from Alpha Vantage
- **🕒 Smart Date Selection**: Automatically uses the most recent trading day with available options data
- **🧠 Intelligent Analysis**: Generates professional options trading insights and recommendations
- **🎯 Production Ready**: Clean interface with comprehensive error handling and state management

## 📋 System Requirements

- Python 3.13+
- Alpha Vantage API Key (premium tier recommended for higher rate limits)
- OpenAI API Key
- Internet connection for real-time API calls
- Required Python packages: langgraph, langchain-openai, alpha-vantage, pandas, python-dotenv

## 🛠 Installation & Setup

### 1. Environment Setup
Create a `.env` file in the project root:
```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
OPENAI_API_KEY=your_openai_key_here
```

**Get API Keys:**
- Alpha Vantage: [Get API key](https://www.alphavantage.co/support/#api-key)
- OpenAI: [Get API key](https://platform.openai.com/api-keys)

### 2. Install Dependencies
```bash
pip install langgraph langchain-openai alpha-vantage pandas python-dotenv
```

### 3. Run the Agent
```bash
python test.py
```

## 🏗 Architecture Overview

The LLM-Orchestrated Options Analysis Agent (`test.py`) implements a sophisticated workflow where the LLM acts as the central orchestrator for all major processing steps:

```
Natural Language Input → LLM Parse & Convert → Financial Data Fetch → LLM Format Matrix → LLM Generate Analysis → Structured Output
```

### Core Components

#### 1. **LLMOptionsAgent Class**
The main orchestrator that coordinates the entire analysis workflow.

#### 2. **State Management**
```python
class OptionsAnalysisState(TypedDict):
    user_input: str                     # Original natural language input
    symbols: List[str]                  # Raw symbols/company names
    date: Optional[str]                 # Analysis date
    converted_tickers: List[str]        # LLM-converted ticker symbols
    spot_prices: dict                   # Current stock prices
    raw_options_data: dict              # Raw Alpha Vantage response
    formatted_options_data: pd.DataFrame # LLM-formatted 6x6 matrix
    messages: List[BaseMessage]         # Conversation history
    status: str                         # Current processing status
    errors: List[str]                   # Error tracking
```

#### 3. **LLM-Orchestrated Workflow Nodes**

**🧠 LLM Parse & Convert Node**
- Parses natural language input using GPT-3.5-turbo
- Intelligently converts company names to ticker symbols
- Handles mixed input formats (companies + tickers)
- Provides conversion tracking and validation

**📊 Financial Data Fetch Node**
- Retrieves real-time stock prices from Alpha Vantage
- Fetches historical options data for analysis date
- Implements robust error handling for API calls
- Filters and prepares data for LLM processing

**🎨 LLM Format Matrix Node**
- **Intelligent Filtering**: Pre-processes options data to reduce token usage
- **6×6 Matrix Creation**: Generates exactly 6 strikes × 6 Friday expirations
- **Strike Selection**: Chooses strikes above current price for covered call strategies
- **Premium Optimization**: Uses bid prices with fallback to mark/ask prices

**🧠 LLM Analysis Node**
- Generates professional trading insights and recommendations
- Analyzes premium levels, time decay patterns, and opportunities
- Provides actionable covered call strategy recommendations
- Assesses risk considerations and market conditions

## 🚀 Quick Start

### Automatic Execution (Built-in Test)
```bash
python test.py
```
This automatically analyzes "Apple, Tesla Motors, Microsoft" and displays the complete 6×6 options matrix.

## 📊 Output Format

The agent generates a standardized 6×6 options premium matrix with the following structure:

### DataFrame Schema
```
DataFrame Shape: (N×6 rows × 9 columns) where N = number of stocks
```

**Columns:**
- `Stock`: Ticker symbol (AAPL, TSLA, MSFT, etc.)
- `Strike_Price`: Option strike prices (6 strikes above current price per stock)
- `MM/DD/YY` columns (6): Premium values for next 6 Friday expirations
- `Current_Price`: Current stock price (displayed only in first row per stock)

### Example Output
```
   Stock Strike_Price 10/11/25 10/18/25 10/25/25 11/01/25 11/08/25 11/15/25 Current_Price
0   AAPL        260.0     0.40     2.16     3.35     4.50     6.70     7.50       $258.02
1   AAPL        262.5     0.11     1.35     2.50     3.65     5.45     6.20            
2   AAPL        265.0     0.05     0.85     1.90     2.85     4.25     5.10            
3   AAPL        267.5     0.02     0.50     1.40     2.15     3.25     4.05            
4   AAPL        270.0     0.01     0.28     1.05     1.65     2.45     3.15            
5   AAPL        272.5     0.00     0.15     0.75     1.25     1.85     2.40            
6   TSLA        430.0     9.70    17.65    22.80    30.85    34.05    37.50       $429.83
7   TSLA        435.0     7.15    14.90    19.25    26.40    29.85    32.90            
...
```

### Key Features of the Output:
- **Organized by Stock**: Each stock gets exactly 6 rows (6 strike prices)
- **Call Options Only**: Focuses on covered call strategies
- **Strikes Above Current**: All strikes are above current stock price
- **Friday Expirations**: Uses next 6 Friday expiration dates
- **Premium Values**: Shows bid prices (fallback to mark/ask if needed)
- **Current Price Context**: Displays current stock price for reference

## 🔍 Input Examples

The LLM orchestrator handles various natural language input formats:

```python
# Company names
"Apple, Tesla Motors, Microsoft"
"Apple Inc, Tesla, Microsoft Corporation"

# Ticker symbols  
"AAPL, TSLA, MSFT"

# Mixed format
"Apple, TSLA, Microsoft"

# Single stock
"AAPL"
"Apple Inc"

# Natural language
"I want to analyze options for Apple and Tesla"
"Show me Microsoft and Amazon options"
```

## ⚙️ Smart Configuration

### Automatic Date Selection
The agent automatically selects the most recent trading day with available options data:

```python
def get_most_recent_trading_day() -> str:
    """Get the most recent trading day with likely options data availability"""
    today = datetime.now()
    days_back = 4  # Account for data availability lag
    target_date = today - timedelta(days=days_back)
    
    # Ensure it's a weekday
    while target_date.weekday() > 4:
        target_date = target_date - timedelta(days=1)
    
    return target_date.strftime("%Y-%m-%d")
```

### Intelligent Strike Selection
- Automatically selects 6 strikes above current stock price
- Optimized for covered call strategies
- Ensures relevant and tradeable strike prices

### Friday Expiration Logic
- Automatically finds next 6 Friday expiration dates
- Filters for dates >= current date
- Handles market holidays and irregular trading schedules

## 🧠 LLM Orchestration Details

### Symbol Conversion Process
The LLM uses sophisticated prompting to convert company names to ticker symbols:

```python
prompt = """
You are a financial data analyst. Parse the user input and convert any company names to stock ticker symbols.

OUTPUT FORMAT:
{
    "symbols": ["AAPL", "TSLA", "MSFT"],
    "conversions": [
        {"input": "Apple", "ticker": "AAPL", "converted": true},
        {"input": "TSLA", "ticker": "TSLA", "converted": false},
        {"input": "Microsoft", "ticker": "MSFT", "converted": true}
    ]
}
"""
```

### Matrix Formatting Intelligence
The agent pre-filters options data to optimize LLM processing:

1. **Call Options Only**: Filters for call options suitable for covered call strategies
2. **Relevant Strikes**: Selects strikes above current price
3. **Friday Expirations**: Identifies next 6 Friday expiration dates
4. **Essential Data**: Reduces data to essential columns (strike, expiration, bid, ask, mark)

### Professional Analysis Generation
The LLM generates comprehensive trading insights covering:
- Premium level assessment (high/low/fair value)
- Most attractive strikes for covered calls
- Time decay patterns across expirations
- Notable opportunities and patterns
- Risk considerations and market conditions

## 🚨 Error Handling & Robustness

### Comprehensive Error Tracking
```python
class OptionsAnalysisState(TypedDict):
    errors: List[str]  # Tracks all errors throughout workflow
    status: str        # Current processing status
```

### Fallback Mechanisms
- **LLM Parsing Failure**: Falls back to simple comma-separated parsing
- **API Failures**: Graceful degradation with detailed error messages
- **Missing Data**: Handles partial data availability
- **Invalid Symbols**: Reports unknown symbols without breaking workflow

### Status Monitoring
The agent provides detailed status tracking:
- `initializing` → `llm_converted` → `data_fetched` → `matrix_created` → `analysis_complete`

## 📈 Performance Characteristics

### Execution Time
- **Symbol Conversion**: 1-2 seconds (LLM processing)
- **Data Fetching**: 2-5 seconds per stock (Alpha Vantage API)
- **Matrix Formatting**: 1-2 seconds (optimized filtering + LLM)
- **Analysis Generation**: 2-3 seconds (LLM insights)
- **Total Time**: ~8-15 seconds for 3 stocks

### Memory Usage
- **Minimal Memory Footprint**: Pre-filtering reduces data size
- **Efficient Processing**: Only relevant options data kept in memory
- **Clean State Management**: Structured state prevents memory leaks

### API Efficiency
- **Optimized Requests**: Minimal API calls per stock
- **Token Optimization**: Pre-filtering reduces LLM token usage
- **Rate Limit Awareness**: Built-in handling for API constraints

## 🔒 Security & Best Practices

### API Key Management
```python
# Secure environment variable loading
load_dotenv()
self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
self.openai_key = os.getenv('OPENAI_API_KEY')
```

### Error Handling
- No sensitive data in error messages
- Graceful failures without exposing internals
- Comprehensive logging for debugging

### Rate Limiting
- Respects Alpha Vantage API limits
- OpenAI usage optimized to minimize costs
- Built-in retry logic for transient failures

## 🧪 Testing & Examples

### Automatic Test Execution
The `test.py` file includes a built-in test that automatically runs when executed:

```python
def main():
    """Main function - automatically runs DataFrame generation"""
    agent = LLMOptionsAgent()
    user_input = "Apple, Tesla Motors, Microsoft"
    
    # Get DataFrame directly
    df = agent.get_options_dataframe(user_input)
    
    if not df.empty:
        print(f"✅ Successfully generated 6x6 options matrix!")
        print(f"📈 DataFrame shape: {df.shape}")
        print(df.to_string(index=True))
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### "No module named 'langgraph'"
```bash
pip install langgraph langchain-openai alpha-vantage pandas python-dotenv
```

#### "API Key not found"
- Ensure `.env` file exists in project root
- Check API keys are correctly formatted (no quotes in .env)
- Verify API keys are active and have necessary permissions

#### "No options data available"
- Options data has 2-4 day availability lag
- System automatically adjusts to most recent available trading day
- Verify the stock has active options trading
- Check if it's a weekend/holiday (system auto-adjusts)

#### "LLM parsing failed, using fallback"
- Usually harmless - system falls back to simple parsing
- Check OpenAI API key and account credits
- Verify internet connectivity

#### Empty DataFrame returned
- Check if input symbols are valid stock tickers
- Verify stocks have options trading available
- Check Alpha Vantage API rate limits (25 requests/day on free tier)

### Debug Mode
Enable detailed logging by examining the `status` and `errors` fields:

```python
result = agent.analyze("AAPL")
print(f"Status: {result['status']}")
print(f"Errors: {result['errors']}")
```

## 📊 API Rate Limits & Costs

### Alpha Vantage
- **Free Tier**: 25 requests/day, 5 requests/minute
- **Premium Tiers**: Higher limits available
- **Usage per Analysis**: 2 API calls per stock (quote + options data)

### OpenAI
- **GPT-3.5-turbo**: ~$0.001-0.002 per analysis
- **Token Usage**: Optimized through pre-filtering
- **Cost per Analysis**: Typically <$0.01 for 3 stocks

## � Advanced Usage Patterns

### Batch Processing
```python
agent = LLMOptionsAgent()

stocks_list = [
    "Apple, Microsoft, Google",
    "Tesla, Amazon, Netflix", 
    "Meta, NVIDIA, Adobe"
]

results = []
for stocks in stocks_list:
    df = agent.get_options_dataframe(stocks)
    results.append(df)
    
# Combine all results
combined_df = pd.concat(results, ignore_index=True)
```


## 🤝 Contributing & Development

### Code Structure
The `test.py` file is organized into clear sections:
1. **State Schema**: TypedDict definitions for workflow state
2. **LLM Agent Class**: Main orchestrator with initialization
3. **Helper Functions**: Utility functions for data processing
4. **Workflow Nodes**: Individual LLM-orchestrated processing steps
5. **Workflow Building**: LangGraph workflow construction
6. **Main Interface**: Public API methods
7. **Testing**: Built-in test functionality

### Extending the Agent
To add new functionality:

```python
# Add new node to workflow
def custom_analysis_node(self, state: OptionsAnalysisState) -> OptionsAnalysisState:
    # Your custom logic here
    return state

# Update workflow in _build_llm_workflow()
workflow.add_node("custom_analysis", self.custom_analysis_node)
workflow.add_edge("llm_analyze", "custom_analysis")
```

### Development Guidelines
1. **State Management**: Always use the OptionsAnalysisState schema
2. **Error Handling**: Add errors to `state["errors"]` list
3. **Status Tracking**: Update `state["status"]` at each step
4. **LLM Integration**: Use consistent prompting patterns
5. **Testing**: Include test cases for new functionality

## 📝 Implementation Notes

### Why LLM Orchestration?
1. **Intelligence**: LLM makes smart decisions about data formatting
2. **Flexibility**: Handles various input formats naturally
3. **Scalability**: Easy to extend with new analysis types
4. **User Experience**: Natural language interaction
5. **Robustness**: Intelligent error handling and recovery

### Technical Architecture Decisions
- **LangGraph**: Provides robust workflow orchestration
- **StateGraph**: Ensures consistent state management
- **Pre-filtering**: Optimizes LLM token usage
- **Pandas Integration**: Leverages powerful data manipulation
- **Error Tracking**: Comprehensive error handling throughout

### Performance Optimizations
- **Data Pre-filtering**: Reduces LLM processing load
- **Efficient API Usage**: Minimizes external API calls
- **Memory Management**: Processes data in optimal chunks
- **Caching**: Future extension point for repeated analyses

## 🔄 Version History & Roadmap

### Current Version (test.py)
- ✅ LLM-orchestrated workflow
- ✅ Automatic date selection
- ✅ Intelligent symbol conversion
- ✅ 6×6 matrix generation
- ✅ Professional analysis insights
- ✅ Comprehensive error handling

### Future Enhancements
- 🔄 Caching for repeated analyses
- 🔄 Multiple matrix size options
- 🔄 Put options analysis
- 🔄 Historical trend analysis
- 🔄 Advanced trading signal generation
- 🔄 Portfolio-level analysis

## 📖 References & Documentation

### API Documentation
- [Alpha Vantage Options API](https://www.alphavantage.co/documentation/#options)
- [OpenAI GPT-3.5-turbo](https://platform.openai.com/docs/models/gpt-3-5-turbo)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

### Financial Concepts
- **Covered Calls**: Selling call options against owned stock positions
- **Strike Prices**: The price at which options can be exercised
- **Premium**: The price paid/received for an options contract
- **Time Decay**: The reduction in option value as expiration approaches

---

*Built with ❤️ using Python, OpenAI GPT-3.5-turbo, Alpha Vantage API, and LangGraph*

**Key Technologies:**
- 🤖 **OpenAI GPT-3.5-turbo**: Central LLM orchestrator
- 📊 **Alpha Vantage**: Real-time financial data
- 🔄 **LangGraph**: Workflow orchestration framework
- 🐼 **Pandas**: Data manipulation and analysis
- 🛠 **Python 3.13+**: Modern Python features
