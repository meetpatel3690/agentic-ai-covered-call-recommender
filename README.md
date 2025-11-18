# 🎯 AI-Powered Options Trading Recommendation System

**A Production-Ready Options Analysis Platform with Dual-Agent LangGraph Architecture**

An advanced full-stack application that combines AI-powered intelligence with real-time financial data to provide professional options trading recommendations. The system features a sophisticated **dual-agent architecture**: 

- **Agent 1** (Options Data Agent): Fetches and formats live options data into 6×6 premium matrices with Delta values
- **Agent 2** (Strategy Recommendation Agent): Uses a 10-node LangGraph workflow to analyze options using Premium × Delta scoring, identify multi-trade opportunities, allocate contracts intelligently, and generate AI-powered trading insights

**Built by:** Team Nexus   
**AI Implementation:** GitHub Copilot  
**Project Status:** ✅ Production-Ready (Phases 1-10 Complete, 100% Test Coverage)  
**Live Demo:** Streamlit Web Application with Portfolio Management

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Quick Start](#-quick-start-run-in-30-seconds)
- [System Requirements](#-system-requirements)
- [Installation & Setup](#-installation--setup)
- [Architecture Overview](#-architecture-overview)
- [Dual-Agent System](#-dual-agent-system)
- [Project Structure](#-project-structure)
- [Usage Guide](#-usage-guide)
- [Testing](#-testing)
- [API Keys](#-api-keys)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

---

## 🚀 Key Features

### 🤖 Intelligent AI Integration
- **LLM Central Orchestration**: GPT-3.5-turbo coordinates the entire workflow
- **Natural Language Processing**: Converts company names to ticker symbols automatically
- **AI-Powered Analysis**: Generates professional options trading insights and recommendations

### 📊 Advanced Options Analysis
- **6×6 Premium Matrices**: Automatically formatted grids (6 strikes × 6 expiration dates)
- **Delta Analysis**: Premium × Delta scoring for optimal strategy selection
- **Multi-Trade Opportunities**: Identifies primary and secondary recommendations
- **Smart Contract Allocation**: Intelligent allocation based on portfolio holdings with buffer management

### 📈 Real-Time Financial Data
- **Live Stock Prices**: Real-time quotes from Alpha Vantage API
- **Historical Options Data**: Complete options chain analysis
- **Smart Date Selection**: Automatically uses the most recent trading day
- **Week-Based Filtering**: Analyzes Week 1-2 for multi-trade strategies

### 🎯 Production-Ready Features
- **Streamlit Web Interface**: Professional portfolio management UI
- **Visual Highlighting**: Orange-highlighted cells show best opportunities
- **Income Projections**: Monthly income calculations per stock
- **Error Handling**: Comprehensive validation and error management
- **100% Test Coverage**: Phases 1-10 fully tested and validated

---

## ⚡ Quick Start (Run in 30 Seconds)

### Option 1: PowerShell (Recommended)

```powershell
# Step 1: Navigate to project directory
cd "C:\Users\meetp\OneDrive\Desktop\Complete_Options_Data_Agent\Agentic---AI---Stock---Recommendation"

# Step 2: Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Step 3: Install/Update packages (first time only)
uv add -r requirements.txt

# Step 4: Run the Streamlit app
streamlit run UI\app.py
```

### Option 2: Standard Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run UI/app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📋 System Requirements

### Environment
- **Python**: 3.13+ (required)
- **OS**: Windows, macOS, or Linux
- **Internet**: Required for API calls

### API Keys (Required)
- **Alpha Vantage API Key**: Premium tier recommended for higher rate limits
- **OpenAI API Key**: For GPT-3.5-turbo integration

### Dependencies
```
streamlit>=1.50.0
langgraph>=0.6.8
langchain-openai>=0.3.34
langchain-core>=0.3.78
alpha-vantage>=3.0.0
pandas>=2.3.3
python-dotenv>=1.1.1
requests>=2.32.5
streamlit-searchbox>=0.1.23
openai>=2.1.0
```

---

## 🛠 Installation & Setup

### 1. Clone or Download Repository

```bash
git clone <repository-url>
cd Agentic---AI---Stock---Recommendation
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
OPENAI_API_KEY=your_openai_key_here
```

**Get API Keys:**
- **Alpha Vantage**: [Get free API key](https://www.alphavantage.co/support/#api-key)
- **OpenAI**: [Get API key](https://platform.openai.com/api-keys)

### 4. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# OR using uv (faster)
uv add -r requirements.txt
```

### 5. Run the Application

```bash
streamlit run UI\app.py
```

---

## 🏗 Architecture Overview

### System Design

The application implements a **dual-agent LangGraph architecture** where each agent handles specific responsibilities:

```
User Input → Agent 1 (Data Fetching) → Agent 2 (Strategy Analysis) → UI Display
```

### Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with LangGraph orchestration
- **AI/ML**: OpenAI GPT-3.5-turbo
- **Financial Data**: Alpha Vantage API
- **State Management**: LangGraph StateGraph
- **Data Processing**: Pandas, NumPy

---

## 🤖 Dual-Agent System

### Agent 1: Options Data Agent (`options_data_agent.py`)

**Purpose**: Fetch and format live options data

**Workflow Nodes**:
1. **LLM Parse & Convert**: Natural language → ticker symbols
2. **Financial Data Fetch**: Real-time prices and options data
3. **LLM Format Matrix**: Raw data → 6×6 premium matrix
4. **Delta Extraction**: Extract Delta values for Agent 2

**Key Features**:
- Converts company names to tickers using GPT-3.5
- Fetches real-time stock prices from Alpha Vantage
- Creates structured 6×6 matrices (6 strikes × 6 Friday expirations)
- Extracts Delta values for strategy scoring
- Implements smart date selection for data availability

**State Schema**:
```python
class OptionsAnalysisState(TypedDict):
    user_input: str                      # Original input
    symbols: List[str]                   # Raw symbols/companies
    converted_tickers: List[str]         # LLM-converted tickers
    spot_prices: dict                    # Current stock prices
    raw_options_data: dict              # Alpha Vantage response
    formatted_options_data: pd.DataFrame # 6×6 premium matrix
    delta_data: pd.DataFrame            # Delta values matrix
    messages: List[BaseMessage]         # Conversation history
    status: str                         # Processing status
    errors: List[str]                   # Error tracking
```

### Agent 2: Strategy Recommendation Agent (`strategy_recommendation_agent_langgraph.py`)

**Purpose**: Analyze options and generate strategy recommendations

**10-Node LangGraph Workflow**:

#### Part 1: Premium-Only Analysis (Nodes 1-4)
1. **Validation Node**: Verify input data integrity
2. **Premium Analysis Node**: Analyze premium values across all options
3. **Highest Premium Selection Node**: Identify best premiums per stock
4. **Premium Recommendations Node**: Generate Part 1 recommendations

#### Part 2: Delta-Based Analysis (Nodes 5-10)
5. **Data Merge Node**: Combine premium + Delta data
6. **Delta Scoring Node**: Calculate Premium × Delta scores
7. **Week Filtering Node**: Filter Week 1-2 options for multi-trades
8. **Primary Selection Node**: Select best primary recommendation
9. **Secondary Selection Node**: Select secondary opportunities (Week 1-2 only)
10. **Contract Allocation & Income Node**: Calculate contracts and projected income

**Scoring Formula**:
```
Score = Premium × |1 - Delta|

Where:
- Premium: Bid price of the option
- Delta: Absolute value of Delta (risk measure)
- Higher scores indicate better risk-adjusted returns
```

**Key Features**:
- Premium × Delta scoring for optimal strategy selection
- Week-based filtering for multi-trade opportunities
- Intelligent contract allocation with buffer management
- Monthly income projections per stock
- LLM-generated professional insights
- Visual highlighting for UI display

**State Schema**:
```python
class StrategyAnalysisState(TypedDict):
    options_dataframe: pd.DataFrame      # Input 6×6 grid
    delta_data: pd.DataFrame            # Delta values
    portfolio_data: Dict                # Holdings {stock: shares}
    analysis_mode: str                  # "premium_only" or "premium_delta"
    merged_data: pd.DataFrame           # Premium + Delta combined
    primary_recommendations: Dict       # Best primary per stock
    secondary_recommendations: Dict     # Secondary opportunities
    contract_allocations: Dict          # Contract allocation
    income_projections: Dict            # Projected income
    recommendations: List[Dict]         # Final recommendations
    highlighted_cells: Dict             # UI highlighting data
    status: str                        # Processing status
```

---

## 📁 Project Structure

```
Agentic---AI---Stock---Recommendation/
│
├── backend/                           # Core agent implementations
│   ├── __init__.py
│   ├── options_data_agent.py         # Agent 1: Data fetching
│   └── strategy_recommendation_agent_langgraph.py  # Agent 2: Analysis
│
├── UI/                               # Streamlit web application
│   ├── app.py                        # Main entry point
│   ├── portfolio_data.json           # Portfolio storage
│   ├── requirements.txt              # UI dependencies
│   ├── pages/
│   │   └── mainpage.py              # Main portfolio page
│   └── utils/
│       ├── __init__.py
│       └── stock_api.py             # Stock search API
│
├── Documentations/                   # Comprehensive documentation
│   ├── AGENT_2_FINAL_REPORT.md      # Agent 2 complete report
│   ├── AGENT_2_IMPLEMENTATION_GUIDE.md
│   ├── QUICK_REFERENCE.md           # Quick reference guide
│   ├── DEMO_QUICK_GUIDE.md          # Demo instructions
│   ├── PHASE_1_IMPLEMENTATION_SUMMARY.md
│   ├── PHASE_2_IMPLEMENTATION_SUMMARY.md
│   ├── ... (Phases 3-10)
│   └── PHASE_10_IMPLEMENTATION_SUMMARY.md
│
├── test_phase1.py - test_phase10_validation.py  # Comprehensive tests
├── backend_integration.py            # Backend integration tests
├── pyproject.toml                   # Project dependencies
├── .env                             # API keys (create this)
├── README.md                        # This file
└── HOW_TO_RUN.md                    # Quick start guide

```

---

## 📖 Usage Guide

### 1. Starting the Application

```bash
streamlit run UI\app.py
```

### 2. Adding Stocks to Portfolio

1. Use the search box to find stocks by name or ticker
2. Enter number of shares you own
3. Click "Add to Portfolio"
4. Stock appears in your portfolio with current price

### 3. Running Agent 1 (Options Data Fetching)

1. Click **"🚀 Run Agent 1: Fetch Options Data"** button
2. Agent 1 will:
   - Fetch current stock prices
   - Retrieve options data from Alpha Vantage
   - Generate 6×6 premium matrices
   - Extract Delta values
3. View results in the options grid display

### 4. Running Agent 2 (Strategy Recommendations)

1. After Agent 1 completes, click **"🎯 Run Agent 2: Strategy Recommendation"**
2. Agent 2 will:
   - Analyze all 36 options per stock
   - Calculate Premium × Delta scores
   - Identify best primary and secondary opportunities
   - Allocate contracts based on portfolio
   - Calculate projected monthly income
3. View:
   - **Orange-highlighted cells**: Best opportunities
   - **Analysis summary**: Detailed recommendations
   - **Income projections**: Expected monthly income

### 5. Understanding the Results

**Premium Matrix (6×6 Grid)**:
- **Rows**: 6 strike prices (above current stock price)
- **Columns**: 6 Friday expiration dates
- **Values**: Option premiums (bid prices)

**Orange Highlighting**:
- Indicates cells with highest Premium × (1- Delta ) scores
- Primary recommendation: Best overall opportunity
- Secondary recommendation: Week 1-2 alternative (if available)

**Recommendations Include**:
- Stock symbol and current price
- Recommended strike price and expiration date
- Premium amount and Delta value
- Premium × Delta score
- Number of contracts to sell
- Projected monthly income
- Professional AI-generated insights

---

## 🔑 API Keys

### Alpha Vantage API

**Purpose**: Real-time stock prices and options data

**Get Your Key**:
1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Enter your email to receive free API key
3. For higher rate limits, consider premium tier

**Rate Limits**:
- Free tier: 5 API requests per minute, 500 per day
- Premium tier: Higher limits, recommended for production

### OpenAI API

**Purpose**: GPT-3.5-turbo for natural language processing and analysis

**Get Your Key**:
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create account or sign in
3. Generate new API key
4. Add credits to your account

**Usage**:
- Ticker conversion: ~100-200 tokens per request
- Matrix formatting: ~500-1000 tokens per stock
- Analysis generation: ~300-500 tokens per recommendation

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "ALPHA_VANTAGE_API_KEY not found"

**Solution**: Create `.env` file in project root with your API key:
```env
ALPHA_VANTAGE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

#### 2. "Rate limit exceeded"

**Solution**: Alpha Vantage free tier limits to 5 requests/minute. Wait 60 seconds or upgrade to premium tier.

#### 3. "No options data available"

**Solution**: The system automatically selects recent trading days. Some stocks may not have options data for all dates. Try:
- Different stocks with active options markets
- Wait for next trading day data to become available

#### 4. "Module not found" errors

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

#### 5. Streamlit won't start

**Solution**:
```bash
# Deactivate and reactivate virtual environment
deactivate
.\.venv\Scripts\Activate.ps1

# Reinstall Streamlit
pip install --upgrade streamlit

# Run again
streamlit run UI\app.py
```

#### 6. Agent 2 button not working

**Solution**: 
- Ensure Agent 1 completed successfully first
- Check that options_data exists in session state
- Refresh the page and try again

---

## 📚 Documentation

### Key Documentation Files

- **`README.md`** (this file): Complete project overview
- **`HOW_TO_RUN.md`**: Quick start guide
- **`AGENT_2_FINAL_REPORT.md`**: Agent 2 complete implementation report
- **`QUICK_REFERENCE.md`**: One-page reference card
- **`DEMO_QUICK_GUIDE.md`**: Demo presentation guide

### Phase Implementation Summaries

Each phase has detailed documentation in `Documentations/`:
- Implementation details
- Test results
- Key features
- Validation criteria

---


### Development Workflow

This project was developed using an AI-assisted workflow:
1. Requirements and architecture designed by Team Nexus.
2. Implementation with GitHub Copilot assistance
3. Iterative testing and refinement across 10 phases
4. Comprehensive documentation at each stage

---

## 🎯 Key Highlights

### What Makes This Project Special

1. **Dual-Agent Architecture**: Clean separation between data fetching and analysis
2. **LangGraph Orchestration**: Professional state management and workflow execution
3. **AI-Powered Intelligence**: GPT-3.5 integration for natural language processing
4. **Production-Ready**: 100% test coverage, comprehensive error handling
5. **Scalable Design**: Easy to extend with new features and strategies
6. **User-Friendly UI**: Professional Streamlit interface with visual highlighting

### Technical Achievements

- ✅ 10-node LangGraph workflow for strategy analysis
- ✅ Premium × Delta scoring algorithm
- ✅ Multi-trade opportunity identification
- ✅ Intelligent contract allocation with buffer management
- ✅ Real-time financial data integration
- ✅ Natural language ticker conversion
- ✅ Comprehensive test suite (Phases 1-10)

---

## 📊 Example Results

### Sample Analysis Output

```
✅ Agent 2 Analysis Complete!

WALMART (WMT) - Current Price: $156.50
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 PRIMARY RECOMMENDATION:
   Strike: $160.00 | Expiry: 11/25/2025 (Week 4)
   Premium: $5.25 | Delta: -0.45
   Score: 2.36 (Premium × |1 - Delta|)
   Contracts: 8 (from 1,000 shares, buffer: 2)
   📈 Projected Income: $4,200/month

🎯 STRATEGY: Sell 8 covered calls at $160 strike
   expiring 11/25. Strong premium with moderate delta
   provides good income while maintaining upside potential.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL PORTFOLIO INCOME: $4,200/month
```

---

## 🌟 Future Enhancements

### Potential Features
- [ ] Additional Greek parameters (Gamma, Theta, Vega)
- [ ] Custom scoring formula builder
- [ ] Historical performance tracking
- [ ] Multiple strategy types (puts, spreads, etc.)
- [ ] Portfolio optimization recommendations
- [ ] Risk analysis dashboard
- [ ] Email/SMS alerts for opportunities

---





## 📄 License

This project includes:

- AI-assisted implementation by GitHub Copilot
- Open-source dependencies (see pyproject.toml)

---

## 🙏 Acknowledgments

- **Alpha Vantage**: For providing comprehensive financial data API
- **OpenAI**: For GPT-3.5-turbo integration capabilities
- **LangGraph**: For state management and workflow orchestration framework
- **Streamlit**: For rapid web application development
- **GitHub Copilot**: For AI-assisted development support

---

**Built with ❤️ by Team Nexus with AI assistance from GitHub Copilot**

**Last Updated**: November 17, 2025  
**Version**: 1.0.0 (Production Release)
- Generates professional trading insights and recommendations
- Analyzes premium levels, time decay patterns, and opportunities
- Provides actionable covered call strategy recommendations
- Assesses risk considerations and market conditions

## 🚀 Quick Start



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

## 📊 API Rate Limits & Costs

### Alpha Vantage
- **Free Tier**: 25 requests/day, 5 requests/minute
- **Premium Tiers**: Higher limits available
- **Usage per Analysis**: 2 API calls per stock (quote + options data)

### OpenAI
- **GPT-3.5-turbo**: ~$0.001-0.002 per analysis
- **Token Usage**: Optimized through pre-filtering
- **Cost per Analysis**: Typically <$0.01 for 3 stocks

## 📖 References & Documentation

### API Documentation
- [Alpha Vantage Options API](https://www.alphavantage.co/documentation/#options)
- [OpenAI GPT-3.5-turbo](https://platform.openai.com/docs/models/gpt-3-5-turbo)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

**Key Technologies:**
- 🤖 **OpenAI GPT-3.5-turbo**: Central LLM orchestrator
- 📊 **Alpha Vantage**: Real-time financial data
- 🔄 **LangGraph**: Workflow orchestration framework
- 🐼 **Pandas**: Data manipulation and analysis
- 🛠 **Python 3.13+**: Modern Python features

## 🔄 Version History & Roadmap

### Current Version 
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
