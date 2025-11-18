# Complete AI Prompts & Application Information Guide

**Document Purpose:** Centralized reference for all AI prompts, system architecture, and application details used in the Options Trading Strategy Recommendation System.

**Last Updated:** October 31, 2025  
**Project:** Agentic AI Stock Recommendation System  
**Owner:** Meet Patel (@meetpatel3690)

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Application Architecture](#application-architecture)
3. [Agent 1: Options Data Agent - AI Prompts](#agent-1-options-data-agent---ai-prompts)
4. [Agent 2: Strategy Recommendation Agent - AI Prompts](#agent-2-strategy-recommendation-agent---ai-prompts)
5. [Data Flow & Processing](#data-flow--processing)
6. [API Integration Details](#api-integration-details)
7. [UI Components & Streamlit Integration](#ui-components--streamlit-integration)
8. [Future Enhancements (Part 2)](#future-enhancements-part-2)

---

## System Overview

### Purpose
A dual-agent AI system that:
- **Agent 1:** Fetches and formats options chain data into a 6×6 grid
- **Agent 2:** Analyzes the grid and recommends optimal trading strategies

### Technology Stack
- **Framework:** LangGraph (orchestration), Streamlit (UI)
- **Language:** Python 3.x
- **LLM:** OpenAI GPT-4
- **APIs:** Alpha Vantage (options data + Greeks), Yahoo Finance (stock search)
- **Libraries:** pandas, langchain, streamlit, requests

### Key Features
- Real-time options chain data retrieval
- 6×6 matrix visualization (6 strikes × 6 expiration dates)
- Premium-based strategy recommendations (Part 1)
- Visual highlighting of highest premium opportunities
- Portfolio management system
- Delta integration ready (Part 2)

---

## Application Architecture

### Directory Structure
```
Agentic---AI---Stock---Recommendation/
├── backend/
│   ├── options_data_agent.py         # Agent 1: Data fetching & formatting
│   ├── strategy_recommendation_agent.py  # Agent 2: Analysis & recommendations
│   └── __init__.py
├── UI/
│   ├── app.py                         # Portfolio management page
│   ├── pages/
│   │   └── mainpage.py                # Main options analysis page
│   └── utils/
│       └── stock_api.py               # Yahoo Finance integration
├── backend_integration.py             # LangGraph workflow orchestration
├── portfolio_data.json                # Portfolio storage
└── Documentations/
    ├── data_flow_analysis.md          # Agent 1 flow documentation
    ├── visual_data_flow.md            # Agent 1 visual diagrams
    ├── AGENT2_data_flow_analysis.md   # Agent 2 flow documentation
    └── AGENT2_visual_data_flow.md     # Agent 2 visual diagrams
```

### System Flow
```
User Input (Stock Ticker)
    ↓
[Agent 1: Options Data Agent]
    ↓
LangGraph Pipeline (4 Nodes):
  1. Parse & Convert Ticker → Validate symbol
  2. Fetch Financial Data → Get options + Greeks from Alpha Vantage
  3. Format Options Matrix → Create 6×6 grid
  4. Generate Analysis → LLM creates professional summary
    ↓
6×6 DataFrame (Stock | Strike | Date1-6)
    ↓
[Agent 2: Strategy Recommendation Agent]
    ↓
Premium Analysis:
  - Identify highest premium per stock
  - Generate strategy recommendations
  - Highlight optimal cells (green)
    ↓
UI Display (Streamlit)
```

---

## Agent 1: Options Data Agent - AI Prompts

### 1. Ticker Parsing & Conversion Prompt

**Function:** `llm_parse_and_convert_node()`  
**Purpose:** Convert user input into valid stock ticker symbol

```python
PROMPT = """
You are a financial data expert. Your task is to convert the given stock input 
into a valid stock ticker symbol.

INPUT: {user_input}

INSTRUCTIONS:
1. If the input is already a valid ticker (e.g., "AAPL", "TSLA"), return it as-is
2. If the input is a company name (e.g., "Apple", "Tesla"), convert it to ticker
3. Handle common variations:
   - "Apple Inc." → "AAPL"
   - "Microsoft Corporation" → "MSFT"
   - "Tesla Motors" → "TSLA"
4. If uncertain, return your best guess with high confidence
5. Return ONLY the ticker symbol, nothing else

EXAMPLES:
- Input: "Apple" → Output: "AAPL"
- Input: "TSLA" → Output: "TSLA"
- Input: "Microsoft" → Output: "MSFT"

OUTPUT FORMAT: Just the ticker symbol (e.g., "AAPL")
"""
```

**Expected Output:** Single ticker string (e.g., "AAPL")

---

### 2. Options Matrix Formatting Prompt

**Function:** `llm_format_options_matrix_node()`  
**Purpose:** Create a structured 6×6 options grid from raw Alpha Vantage data

```python
PROMPT = """
You are a financial data formatting specialist. Your task is to create a clean, 
structured options matrix from raw options chain data.

INPUT DATA:
{options_data}

REQUIRED OUTPUT FORMAT:
Create a DataFrame with the following structure:
- Column 1: "Stock" (ticker symbol)
- Column 2: "Strike_Price" (strike price as float)
- Columns 3-8: Expiration dates (format: "MM/DD" e.g., "11/15")
- Values: Premium prices (bid price as float, 2 decimal places)

FORMATTING RULES:
1. Select 6 consecutive expiration dates (nearest to current date)
2. Select 6 strike prices:
   - 3 strikes BELOW current stock price (Out-of-the-money puts)
   - 3 strikes ABOVE current stock price (Out-of-the-money calls)
   - Evenly spaced (e.g., $5 or $10 intervals depending on stock price)
3. Use BID prices for premiums
4. Each row = one strike price across 6 expiration dates
5. Total: 6 rows × 8 columns (Stock + Strike + 6 dates)

EXAMPLE OUTPUT:
Stock | Strike_Price | 11/15 | 11/22 | 11/29 | 12/06 | 12/13 | 12/20
AAPL  | 170.00      | 2.45  | 3.10  | 3.75  | 4.20  | 4.80  | 5.30
AAPL  | 175.00      | 1.85  | 2.50  | 3.15  | 3.60  | 4.15  | 4.70
...

Return the data as a clean, structured format that can be converted to pandas DataFrame.
"""
```

**Expected Output:** JSON or dict format convertible to pandas DataFrame

---

### 3. Analysis Generation Prompt

**Function:** `llm_generate_analysis_node()`  
**Purpose:** Generate professional trading analysis from formatted options data

```python
PROMPT = """
You are a professional options trading analyst. Generate a comprehensive analysis 
of the options chain data provided.

OPTIONS DATA:
{options_matrix}

STOCK INFORMATION:
- Ticker: {ticker}
- Current Price: {current_price}
- Analysis Date: {current_date}

ANALYSIS REQUIREMENTS:
Generate a professional report covering:

1. MARKET OVERVIEW
   - Current stock price context
   - Overall options market activity
   - Implied volatility trends (if available)

2. PREMIUM ANALYSIS
   - Identify highest premium opportunities
   - Compare near-term vs. long-term premiums
   - Highlight any unusual premium patterns

3. STRIKE PRICE ANALYSIS
   - Evaluate OTM (out-of-the-money) opportunities
   - Identify optimal strikes for covered calls
   - Note any strikes with exceptional value

4. TIME DECAY CONSIDERATIONS
   - Compare premiums across expiration dates
   - Identify sweet spots for time decay optimization
   - Suggest optimal holding periods

5. STRATEGY RECOMMENDATIONS
   - Suggest 2-3 concrete trading strategies
   - Include specific strikes and expirations
   - Provide risk/reward considerations

FORMATTING:
- Use professional financial language
- Include specific numbers and percentages
- Keep paragraphs concise (3-4 sentences max)
- Use bullet points for key takeaways
- Total length: 300-500 words

OUTPUT FORMAT: Professional markdown-formatted analysis
"""
```

**Expected Output:** Markdown-formatted professional trading analysis (300-500 words)

---

### 4. Financial Data Fetching Prompt

**Function:** `fetch_financial_data_node()`  
**Purpose:** Enhanced error handling and data validation for Alpha Vantage API

```python
SYSTEM_PROMPT = """
You are a financial data retrieval specialist. Your role is to:

1. VALIDATE API RESPONSES
   - Check for HTTP errors (timeout, 5xx, 4xx)
   - Verify JSON structure integrity
   - Confirm data completeness

2. HANDLE EDGE CASES
   - Missing expiration dates → Select next available
   - No Greeks data → Fall back to premium-only analysis
   - Insufficient strikes → Adjust selection criteria
   - API rate limits → Implement retry logic

3. DATA QUALITY CHECKS
   - Premium values > 0
   - Strike prices reasonable (within 50% of current price)
   - Expiration dates in future
   - No duplicate entries

4. ERROR MESSAGES
   - Clear, actionable error messages for users
   - Log technical details for debugging
   - Suggest alternatives when data unavailable

RESPONSE FORMAT:
{
    "status": "success" | "error",
    "data": {...} | null,
    "message": "Descriptive message",
    "fallback_available": true | false
}
"""
```

**Expected Output:** Structured API response with error handling

---

## Agent 2: Strategy Recommendation Agent - AI Prompts

### 5. Premium Analysis Prompt (Part 1)

**Function:** `analyze_options_grid()`  
**Purpose:** Identify highest premium opportunities across the 6×6 grid

```python
ANALYSIS_PROMPT = """
You are an options strategy specialist. Analyze the provided 6×6 options matrix 
to identify the highest premium opportunities.

INPUT MATRIX:
{options_dataframe}

ANALYSIS TASKS:

1. FOR EACH STOCK:
   - Scan all 36 cells (6 strikes × 6 expirations)
   - Identify the cell with HIGHEST premium
   - Record: Strike, Expiration, Premium value

2. PREMIUM COMPARISON:
   - Calculate average premium across all cells
   - Identify outliers (premiums > 1.5x average)
   - Note any patterns (e.g., longer dates = higher premiums)

3. STRATEGY RECOMMENDATION:
   - For highest premium cell: Recommend "Sell Covered Call"
   - Explain rationale: "Maximum income potential"
   - Calculate potential return: (Premium / Strike Price) × 100

4. CONFIDENCE SCORING:
   - HIGH: Premium > 1.5x average
   - MEDIUM: Premium > 1.0x average
   - LOW: Premium < 1.0x average

OUTPUT FORMAT:
{
    "stock": "TICKER",
    "highest_premium_cell": {
        "strike": 175.00,
        "expiration": "11/22",
        "premium": 3.50
    },
    "strategy": "Sell Covered Call",
    "rationale": "Highest premium of $3.50 offers best income",
    "confidence": "HIGH",
    "expected_return": "2.0%"
}
"""
```

**Expected Output:** JSON with highest premium analysis per stock

---

### 6. Delta Integration Prompt (Part 2 - Future)

**Function:** `analyze_with_delta()` (Placeholder for Part 2)  
**Purpose:** Incorporate Delta values for directional risk analysis

```python
DELTA_ANALYSIS_PROMPT = """
You are an advanced options strategist specializing in Delta-neutral strategies. 
Analyze the options data with Delta values to optimize risk-adjusted returns.

INPUT DATA:
- Options Matrix: {options_dataframe}
- Delta Values: {delta_data}
- Current Stock Price: {current_price}

DELTA ANALYSIS FRAMEWORK:

1. OPTIMAL DELTA TARGETING
   - For Covered Calls: Target Delta ~0.30 (30% ITM probability)
   - For Cash-Secured Puts: Target Delta ~0.30 (30% assignment risk)
   - Avoid Delta > 0.50 (too close to at-the-money)

2. SCORING FORMULA OPTIONS (To be decided with mentors):

   **Option A: Simple Ratio**
   Score = Premium / Delta
   - Higher score = better risk-adjusted return
   - Example: $3.50 premium / 0.30 delta = 11.67

   **Option B: Weighted Score (70/30)**
   Score = (Premium × 0.70) + ((1 - |Delta - 0.30|) × 0.30)
   - 70% weight on premium, 30% on Delta optimality
   - Favors premiums near target Delta of 0.30

   **Option C: Filter + Premium**
   Step 1: Filter options with 0.20 ≤ Delta ≤ 0.40
   Step 2: Select highest premium from filtered set
   - Simple, conservative approach

   **Option D: Expected Value**
   Score = Premium × (1 - Delta)
   - Probability-weighted premium
   - Accounts for likelihood of keeping premium

3. RISK ASSESSMENT
   - Low Risk: Delta 0.20-0.30
   - Medium Risk: Delta 0.30-0.40
   - High Risk: Delta > 0.40

4. MULTI-TRADE STRATEGIES (To be decided):
   - 7-Day Trades: Quick premium capture
   - 10-14 Day Trades: Balance of premium and time
   - 14-Day Holds: Maximum premium optimization
   - Hybrid: Mix of timeframes for diversification

OUTPUT FORMAT:
{
    "stock": "TICKER",
    "recommended_option": {
        "strike": 175.00,
        "expiration": "11/22",
        "premium": 3.50,
        "delta": 0.32,
        "score": 10.94,
        "formula_used": "Option A: Simple Ratio"
    },
    "risk_level": "Low",
    "confidence": "HIGH",
    "expected_return": "2.0%",
    "probability_profit": "68%"
}
"""
```

**Expected Output:** JSON with Delta-enhanced recommendations (Part 2)

---

## Data Flow & Processing

### Agent 1 Data Flow (6 Stages)

**Stage 1: User Input**
- Input: Stock ticker or company name
- Processing: Validation and normalization
- Output: Validated ticker symbol

**Stage 2: LLM Parsing**
- Input: Raw user text
- Processing: GPT-4 converts to ticker
- Output: Standard ticker format

**Stage 3: API Data Retrieval**
- Input: Validated ticker
- Processing: Alpha Vantage API call
- Output: Raw JSON with 100+ options contracts

**Stage 4: Data Filtering**
- Input: Raw API response
- Processing: Filter to 6 strikes × 6 dates
- Output: 36 selected options

**Stage 5: Matrix Formation**
- Input: Filtered options
- Processing: LLM formats into 6×6 grid
- Output: Pandas DataFrame (6 rows × 8 columns)

**Stage 6: Analysis Generation**
- Input: Formatted DataFrame
- Processing: LLM generates professional report
- Output: 300-500 word trading analysis

---

### Agent 2 Data Flow (4 Stages)

**Stage 1: Grid Reception**
- Input: 6×6 DataFrame from Agent 1
- Processing: Validation and parsing
- Output: Confirmed 36 premium values

**Stage 2: Premium Analysis**
- Input: 36 premium values per stock
- Processing: Iterate through all cells, track maximum
- Output: Highest premium cell per stock

**Stage 3: Recommendation Generation**
- Input: Highest premium cells
- Processing: Apply strategy logic (Part 1: Simple premium-based)
- Output: Strategy recommendations with rationale

**Stage 4: Highlighting & Display**
- Input: Analysis results
- Processing: Mark cells for UI highlighting
- Output: Styled DataFrame with green highlights

---

## API Integration Details

### Alpha Vantage API

**Endpoint:** `https://www.alphavantage.co/query`

**Options Chain Request:**
```python
params = {
    'function': 'HISTORICAL_OPTIONS',
    'symbol': ticker,
    'apikey': API_KEY
}
```

**Response Structure:**
```json
{
    "data": [
        {
            "contractID": "AAPL231115C00175000",
            "symbol": "AAPL",
            "expiration": "2023-11-15",
            "strike": "175.00",
            "type": "call",
            "bid": "3.50",
            "ask": "3.55",
            "delta": "0.32",
            "gamma": "0.05",
            ...
        },
        ...
    ]
}
```

**Greeks Available:**
- Delta: Directional risk (0-1 for calls, 0 to -1 for puts)
- Gamma: Rate of Delta change
- Theta: Time decay per day
- Vega: Volatility sensitivity
- (Part 2 will incorporate Delta values)

---

### Yahoo Finance API (Stock Search)

**Purpose:** Search and validate stock tickers

**Endpoint:** `https://query2.finance.yahoo.com/v1/finance/search`

**Request:**
```python
params = {
    'q': search_query,
    'quotesCount': 10,
    'newsCount': 0
}
```

**Response:**
```json
{
    "quotes": [
        {
            "symbol": "AAPL",
            "shortname": "Apple Inc.",
            "quoteType": "EQUITY",
            "exchange": "NASDAQ"
        }
    ]
}
```

---

## UI Components & Streamlit Integration

### Main Page (mainpage.py)

**Session State Variables:**
```python
st.session_state.options_data       # Agent 1 output (6×6 DataFrame)
st.session_state.portfolio          # List of stock tickers
st.session_state.agent2_analysis    # Agent 2 recommendations
st.session_state.highlighted_cells  # Cells to highlight (green)
st.session_state.show_highlights    # Toggle for highlighting
st.session_state.agent2_instance    # Agent 2 object reference
```

**Key UI Flow:**
1. User enters stock ticker → Agent 1 runs
2. Display 6×6 grid with professional analysis
3. User clicks "Options Strategy Recommendation" → Agent 2 runs
4. Highest premium cells highlighted in green
5. Recommendations displayed below grid

**Highlighting Implementation:**
```python
def highlight_cells(row):
    if row.name in st.session_state.highlighted_cells:
        cols = st.session_state.highlighted_cells[row.name]
        return ['background-color: #90EE90' if col in cols else '' 
                for col in row.index]
    return [''] * len(row)

styled_df = df.style.apply(highlight_cells, axis=1)
```

---

### Portfolio Page (app.py)

**Features:**
- Add/remove stocks from portfolio
- Search stocks using Yahoo Finance API
- "Get Recommendations" button for batch analysis
- Portfolio persistence (portfolio_data.json)

**Data Storage:**
```json
{
    "stocks": ["AAPL", "MSFT", "TSLA"],
    "last_updated": "2025-10-31T10:30:00"
}
```

---

## Future Enhancements (Part 2)

### Delta Integration Framework

**Awaiting Mentor Decision:**

1. **Delta Scoring Formula** (4 options being evaluated)
2. **Multi-Trade Strategy** (4 timeframe options being evaluated)
3. **Risk Management Rules**
4. **Portfolio Optimization Logic**

**Implementation Plan:**
- Step 1: Mentor approval on formulas (email sent Oct 31)
- Step 2: Update `analyze_with_delta()` method
- Step 3: Modify scoring configuration
- Step 4: Update UI to display Delta values
- Step 5: Add Delta column to 6×6 grid
- Step 6: Test with historical data

**Scalable Design:**
```python
# Current configuration (Part 1)
scoring_config = {
    'use_premium': True,
    'use_delta': False,
    'weights': {'premium': 1.0, 'delta': 0.0}
}

# Future configuration (Part 2)
scoring_config = {
    'use_premium': True,
    'use_delta': True,
    'weights': {'premium': 0.7, 'delta': 0.3},
    'custom_formula': 'selected_after_mentor_meeting'
}
```

---

## Appendix: Complete Prompt Templates

### Template 1: Generic Analysis Prompt
```
You are a [ROLE]. Your task is to [OBJECTIVE].

INPUT:
{input_data}

REQUIREMENTS:
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

OUTPUT FORMAT:
[Expected format]

EXAMPLES:
- Input: [Example input] → Output: [Example output]
```

### Template 2: Error Handling Prompt
```
You are handling an error in [CONTEXT].

ERROR DETAILS:
- Type: {error_type}
- Message: {error_message}
- Context: {additional_context}

RESPONSE REQUIRED:
1. User-friendly message: [What went wrong in plain English]
2. Suggested action: [What user should do next]
3. Technical details: [For logging/debugging]

FORMAT: JSON with status, message, suggestion fields
```

---

## Document Metadata

**Version:** 1.0  
**Created:** October 31, 2025  
**Author:** Meet Patel (@meetpatel3690)  
**AI Assistant:** GitHub Copilot  
**Last Review:** October 31, 2025

**Related Documents:**
- `data_flow_analysis.md` - Agent 1 detailed flow
- `AGENT2_data_flow_analysis.md` - Agent 2 detailed flow
- `ai_prompts_documentation.md` - Original prompts documentation
- `MENTOR_EMAIL.md` - Part 2 enhancement proposals
- `SYSTEM_FLOW_ANALYSIS.md` - Overall system architecture

**Change Log:**
- Oct 31, 2025: Initial comprehensive document created
- Consolidated all prompts from various source files
- Added application architecture overview
- Included API integration details
- Documented UI components and data flow
- Added Part 2 enhancement framework

---

**End of Document**
