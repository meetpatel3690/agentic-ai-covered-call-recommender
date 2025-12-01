# 🔄 **Data Flow Analysis - Strategy Recommendation Agent (Agent 2)**

*How data moves and transforms through the premium analysis system*

---

## 🎯 **WHAT IS AGENT 2?**

Agent 2 (Strategy Recommendation Agent) takes the clean 6×6 options matrix from Agent 1 and analyzes it to identify the **highest premium opportunities** for each stock. It then highlights these cells visually (in green) and provides actionable trading recommendations.

**Think of it like**: A financial advisor reviewing a spreadsheet of options prices and circling the best deals for you.

---

## 📊 **COMPLETE DATA FLOW DIAGRAM**

```
[Agent 1 Output: Options Matrix]
    ↓
[Agent 2 Input Processing]
    ↓
[Premium Analysis & Comparison]
    ↓
[Identify Highest Premium Cells]
    ↓
[Generate Recommendations]
    ↓
[Return Highlighted Results + Analysis]
    ↓
[UI Display with Green Highlighting]
```

---

## 🔄 **DETAILED DATA FLOW BY PROCESSING STAGE**

### **STAGE 0: Pre-Agent 2 (Agent 1 Output)**

**What Agent 2 Receives:**
```python
options_df = DataFrame[
    # Columns: Stock | Strike_Price | 10/10/25 | 10/17/25 | 10/24/25 | 10/31/25 | 11/07/25 | 11/14/25 | Current_Price
    
    # WMT (Walmart) - 6 rows
    ['WMT', 260.0, 2.16, 3.35, 4.50, 6.70, 7.50, 6.75, '$258.02'],
    ['WMT', 262.5, 1.35, 2.50, 3.60, 5.45, 6.30, 5.90, ''],
    ['WMT', 265.0, 0.80, 1.75, 2.60, 4.55, 5.35, 5.80, ''],
    ['WMT', 267.5, 0.49, 1.18, 1.85, 3.80, 4.50, 4.20, ''],
    ['WMT', 270.0, 0.30, 0.85, 1.37, 3.10, 3.80, 3.30, ''],
    ['WMT', 272.5, 0.19, 0.58, 0.95, 2.55, 3.20, 2.85, ''],
    
    # UPS (United Parcel Service) - 6 rows
    ['UPS', 430.0, 17.65, 22.80, 30.85, 34.05, 37.50, 40.10, '$429.83'],
    ['UPS', 432.5, 16.30, 21.50, 29.40, 32.75, 36.20, 38.90, ''],
    # ... 4 more UPS rows ...
    
    # Total: 12-18 rows (2-3 stocks × 6 strikes each)
]

# Metadata available in session state:
portfolio = [
    {'symbol': 'WMT', 'shares': 200, 'price': 258.02, 'name': 'Walmart Inc.'},
    {'symbol': 'UPS', 'shares': 250, 'price': 429.83, 'name': 'United Parcel Service'}
]
```

**Data Characteristics:**
- **Structure**: Clean 6×6 matrix per stock (from Agent 1's Node 3)
- **Size**: 12-18 rows, 9 columns
- **Content**: Premium values (prices) in dollar amounts
- **Data Points**: 72-108 premium values across all stocks

---

### **STAGE 1: Input Processing (`analyze_options_grid()` - Lines 57-165)**

**INPUT DATA:**
```python
options_df: DataFrame  # From Agent 1
    - Shape: (18 rows × 9 columns) for 3 stocks
    - Columns: ['Stock', 'Strike_Price', '10/10/25', '10/17/25', '10/24/25', '10/31/25', '11/07/25', '11/14/25', 'Current_Price']
```

**PROCESSING STEPS:**

1. **Validation Check** (Lines 73-82):
   ```python
   if options_df is None or options_df.empty:
       return error_response
   ```

2. **Extract Date Columns** (Line 84):
   ```python
   date_columns = [col for col in options_df.columns if '/' in col]
   # Result: ['10/10/25', '10/17/25', '10/24/25', '10/31/25', '11/07/25', '11/14/25']
   ```

3. **Identify Unique Stocks** (Line 97):
   ```python
   stocks = options_df['Stock'].unique()
   # Result: ['WMT', 'UPS']
   ```

**OUTPUT FROM STAGE 1:**
```python
# Extracted metadata:
date_columns = ['10/10/25', '10/17/25', '10/24/25', '10/31/25', '11/07/25', '11/14/25']  # 6 dates
stocks = ['WMT', 'UPS']  # 2 stocks
total_cells_to_analyze = 2 stocks × 6 strikes × 6 dates = 72 cells
```

---

### **STAGE 2: Premium Analysis & Comparison (Lines 103-147)**

**INPUT DATA:**
- `stocks`: List of stock symbols
- `options_df`: Full options matrix
- `date_columns`: List of expiration dates

**PROCESSING LOGIC:**

For each stock (WMT, UPS):
```python
for stock in stocks:  # Loop through each stock
    # Step 1: Filter data for current stock
    stock_data = options_df[options_df['Stock'] == stock]
    # For WMT: 6 rows (6 strikes)
    
    # Step 2: Initialize tracking variables
    max_premium = -1
    max_cell = None
    all_premiums = []
    
    # Step 3: Iterate through ALL cells (6 strikes × 6 dates = 36 cells per stock)
    for idx, row in stock_data.iterrows():
        strike_price = row['Strike_Price']
        
        for date_col in date_columns:
            premium = float(row[date_col])
            all_premiums.append(premium)
            
            # Step 4: Track maximum premium
            if premium > max_premium:
                max_premium = premium
                max_cell = {
                    'row_index': idx,
                    'stock': stock,
                    'strike_price': strike_price,
                    'expiration_date': date_col,
                    'premium': premium
                }
```

**EXAMPLE WALKTHROUGH (WMT):**
```
Cell Analysis for WMT:
─────────────────────────────────────────
Strike $260.0:
  10/10/25: $2.16  ← Check if max
  10/17/25: $3.35  ← Check if max
  10/24/25: $4.50  ← Check if max
  10/31/25: $6.70  ← Check if max
  11/07/25: $7.50  ← NEW MAX! 🎯
  11/14/25: $6.75  ← Check if max

Strike $262.5:
  10/10/25: $1.35  ← Check if max
  ... (continue for all 36 cells)

RESULT: 
  Max Premium Found: $7.50
  At Strike: $260.0
  Expiration: 11/07/25
  Row Index: 0 (first row in DataFrame)
```

**OUTPUT FROM STAGE 2:**
```python
# For WMT:
highest_premium_cells['WMT'] = {
    'row_index': 0,
    'stock': 'WMT',
    'strike_price': 260.0,
    'expiration_date': '11/07/25',
    'premium': 7.50
}

stock_analysis['WMT'] = {
    'highest_premium': 7.50,
    'avg_premium': 3.24,  # Average of all 36 cells
    'total_options': 36,   # 6 strikes × 6 dates
    'best_strike': 260.0,
    'best_expiration': '11/07/25'
}

# Similarly for UPS:
highest_premium_cells['UPS'] = {
    'row_index': 6,
    'stock': 'UPS',
    'strike_price': 430.0,
    'expiration_date': '11/14/25',
    'premium': 40.10
}

stock_analysis['UPS'] = {
    'highest_premium': 40.10,
    'avg_premium': 28.65,
    'total_options': 36,
    'best_strike': 430.0,
    'best_expiration': '11/14/25'
}
```

---

### **STAGE 3: Generate Recommendations (Lines 167-208)**

**INPUT DATA:**
```python
highest_premium_cells = {
    'WMT': {'premium': 7.50, 'strike_price': 260.0, 'expiration_date': '11/07/25', ...},
    'UPS': {'premium': 40.10, 'strike_price': 430.0, 'expiration_date': '11/14/25', ...}
}

stock_analysis = {
    'WMT': {'highest_premium': 7.50, 'avg_premium': 3.24, ...},
    'UPS': {'highest_premium': 40.10, 'avg_premium': 28.65, ...}
}
```

**PROCESSING:**
```python
recommendations = []

for stock, cell_info in highest_premium_cells.items():
    recommendations.append({
        'stock': stock,
        'strategy': 'Sell Covered Call',
        'strike_price': cell_info['strike_price'],
        'expiration': cell_info['expiration_date'],
        'premium': cell_info['premium'],
        'rationale': f"Highest premium of ${cell_info['premium']:.2f} available",
        'confidence': 'HIGH',
        # Placeholders for PART 2:
        'delta': None,
        'expected_return': None,
        'risk_score': None
    })

# Sort by premium (highest first)
recommendations.sort(key=lambda x: x['premium'], reverse=True)
```

**OUTPUT FROM STAGE 3:**
```python
recommendations = [
    {
        'stock': 'UPS',
        'strategy': 'Sell Covered Call',
        'strike_price': 430.0,
        'expiration': '11/14/25',
        'premium': 40.10,
        'rationale': 'Highest premium of $40.10 available',
        'confidence': 'HIGH',
        'delta': None,  # Future: Part 2
        'expected_return': None,  # Future: Part 2
        'risk_score': None  # Future: Part 2
    },
    {
        'stock': 'WMT',
        'strategy': 'Sell Covered Call',
        'strike_price': 260.0,
        'expiration': '11/07/25',
        'premium': 7.50,
        'rationale': 'Highest premium of $7.50 available',
        'confidence': 'HIGH',
        'delta': None,
        'expected_return': None,
        'risk_score': None
    }
]
```

---

### **STAGE 4: Store Results (Lines 153-162)**

**INPUT DATA:**
- `highest_premium_cells`: Dict with max premium per stock
- `stock_analysis`: Dict with statistics per stock
- `recommendations`: List of recommendation objects

**PROCESSING:**
```python
self.analysis_results = {
    'status': 'success',
    'highest_premium_cells': highest_premium_cells,
    'stock_analysis': stock_analysis,
    'recommendations': recommendations,
    'analysis_timestamp': datetime.now().isoformat()
}
```

**FINAL OUTPUT (Stored in Agent Instance):**
```python
self.analysis_results = {
    'status': 'success',
    'highest_premium_cells': {
        'WMT': {...},  # Contains row_index, strike, date, premium
        'UPS': {...}
    },
    'stock_analysis': {
        'WMT': {...},  # Contains stats: max, avg, best strike/date
        'UPS': {...}
    },
    'recommendations': [
        {...},  # UPS recommendation (highest premium)
        {...}   # WMT recommendation
    ],
    'analysis_timestamp': '2025-10-28T14:35:22.123456'
}
```

---

### **STAGE 5: Create Highlighting Information (Lines 210-243)**

**INPUT DATA:**
```python
options_df  # Original DataFrame from Agent 1
self.analysis_results['highest_premium_cells']  # Results from Stage 4
```

**PROCESSING:**
```python
highlighted_cells = {}

for stock, cell_info in highest_premium_cells.items():
    row_idx = cell_info['row_index']  # Which row in DataFrame
    expiration_col = cell_info['expiration_date']  # Which column
    
    # Store: "Row 0 should highlight column '11/07/25'"
    if row_idx not in highlight_info:
        highlight_info[row_idx] = []
    highlight_info[row_idx].append(expiration_col)

self.highlighted_cells = highlight_info
```

**OUTPUT FROM STAGE 5:**
```python
self.highlighted_cells = {
    0: ['11/07/25'],   # Row 0 (WMT $260): highlight 11/07/25 column
    6: ['11/14/25']    # Row 6 (UPS $430): highlight 11/14/25 column
}
```

---

### **STAGE 6: UI Integration & Display (mainpage.py Lines 233-246)**

**INPUT DATA:**
```python
agent.highlighted_cells = {
    0: ['11/07/25'],
    6: ['11/14/25']
}
```

**PROCESSING (UI Styling Function):**
```python
def highlight_max_premium(row):
    """Apply green background to cells with highest premium"""
    styles = [''] * len(row)  # Empty styles for all cells
    
    # Check if this row should have highlighting
    if row.name in highlighted_cells:
        cols_to_highlight = highlighted_cells[row.name]
        
        for col_name in cols_to_highlight:
            if col_name in row.index:
                col_idx = row.index.get_loc(col_name)
                styles[col_idx] = 'background-color: #90EE90; color: black; font-weight: bold'
    
    return styles

# Apply to DataFrame
styled_df = options_df.style.apply(highlight_max_premium, axis=1)
```

**FINAL OUTPUT (Displayed in UI):**
```
┌───────┬─────────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┐
│ Stock │ Strike_Price│ 10/10/25 │ 10/17/25 │ 10/24/25 │ 10/31/25 │ 11/07/25 │ 11/14/25 │ Current_Price│
├───────┼─────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────────┤
│  WMT  │    260.0    │   2.16   │   3.35   │   4.50   │   6.70   │ ⭐ 7.50 │   6.75   │   $258.02    │ ← Green highlight!
│  WMT  │    262.5    │   1.35   │   2.50   │   3.60   │   5.45   │   6.30   │   5.90   │              │
│  ...  │     ...     │   ...    │   ...    │   ...    │   ...    │   ...    │   ...    │     ...      │
├───────┼─────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────────┤
│  UPS  │    430.0    │  17.65   │  22.80   │  30.85   │  34.05   │  37.50   │ ⭐ 40.10│   $429.83    │ ← Green highlight!
│  UPS  │    432.5    │  16.30   │  21.50   │  29.40   │  32.75   │  36.20   │  38.90   │              │
│  ...  │     ...     │   ...    │   ...    │   ...    │   ...    │   ...    │   ...    │     ...      │
└───────┴─────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────────┘
```

---

## 📈 **DATA VOLUME TRANSFORMATION**

| **Stage** | **Data Type** | **Volume** | **Format** |
|-----------|---------------|------------|------------|
| **Input (Agent 1 Output)** | Options Matrix | 18 rows × 9 cols = 162 data points | Pandas DataFrame |
| **After Stage 1** | Extracted Metadata | 6 dates + 2 stocks = 8 items | Python lists |
| **After Stage 2** | Premium Analysis | 72 cells analyzed → 2 max values | Dictionaries |
| **After Stage 3** | Recommendations | 2 recommendation objects | List of dicts |
| **After Stage 4** | Complete Results | All above + timestamp | Nested dictionary |
| **After Stage 5** | Highlighting Map | 2 row indices → 2 column names | Simple dictionary |
| **Final Output** | Styled Display | Same 162 points + 2 green cells | Styled DataFrame |

---

## 🔄 **STATE MANAGEMENT PATTERN**

**Agent 2 Internal State Evolution:**

```python
# Initialization
agent = StrategyRecommendationAgent()
agent.analysis_results = {}        # Empty
agent.highlighted_cells = {}       # Empty

# After analyze_options_grid()
agent.analysis_results = {
    'status': 'success',
    'highest_premium_cells': {...},
    'stock_analysis': {...},
    'recommendations': [...],
    'analysis_timestamp': '...'
}

# After get_highlighted_dataframe()
agent.highlighted_cells = {
    0: ['11/07/25'],
    6: ['11/14/25']
}
```

**UI Session State:**

```python
# Before Agent 2 execution
st.session_state.agent2_analysis = None
st.session_state.highlighted_cells = {}
st.session_state.show_highlights = False

# After Agent 2 execution
st.session_state.agent2_analysis = agent.analysis_results
st.session_state.highlighted_cells = agent.highlighted_cells
st.session_state.show_highlights = True
```

---

## 🎯 **BUSINESS LOGIC FLOW**

```
Options Matrix (6×6 per stock)
    ↓ (Compare 36 cells per stock)
Identify Maximum Premium Cell
    ↓ (Calculate statistics)
Generate Stock Analysis
    ↓ (Create recommendation)
Build Trading Strategy
    ↓ (Map to DataFrame positions)
Create Highlighting Instructions
    ↓ (Apply CSS styling)
Visual Display with Green Highlights
```

---

## 💡 **KEY INSIGHTS FOR MENTOR PRESENTATION**

### **What This Demonstrates:**

1. **Automated Analysis** - Agent processes 72+ cells and identifies best opportunities automatically
2. **Data-Driven Decisions** - Recommendations based on quantitative premium analysis
3. **Visual Communication** - Green highlighting makes insights immediately visible
4. **Structured Output** - Clean, organized results ready for decision-making
5. **Scalable Architecture** - Designed for easy Delta integration (Part 2)

### **Technical Excellence:**

- ✅ **Efficient Iteration** - Nested loops to analyze all strike/date combinations
- ✅ **State Preservation** - Results stored for UI access and export
- ✅ **Separation of Concerns** - Analysis logic separate from UI styling
- ✅ **Error Handling** - Graceful handling of missing/invalid data
- ✅ **Future-Proof Design** - Placeholder methods ready for Delta integration

### **Real-World Value:**

- **Time Savings**: Manually reviewing 72 cells → Instant automated analysis
- **Consistency**: Objective premium comparison across all options
- **Visual Clarity**: Green highlights immediately show best opportunities
- **Actionable Output**: Clear recommendations with rationale

---

## 🔍 **COMPARISON: Agent 1 vs Agent 2**

| **Aspect** | **Agent 1 (Options Data)** | **Agent 2 (Strategy Recommendation)** |
|------------|---------------------------|---------------------------------------|
| **Input** | User text (stock names) | Agent 1's options matrix |
| **Processing** | 4 nodes (Parse → Fetch → Format → Analyze) | Single analysis function |
| **Data Volume** | 11,228 contracts → 162 points | 162 points → 2 highlights |
| **Output** | Clean 6×6 matrix | Highlighted cells + recommendations |
| **Complexity** | External API calls, LLM parsing | Pure data analysis (no API calls) |
| **Purpose** | **Data Acquisition** | **Decision Support** |

---

*This data flow documentation demonstrates Meet Patel's ability to build intelligent analysis agents that transform raw data into actionable trading insights!* 🚀
