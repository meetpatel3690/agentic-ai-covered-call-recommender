# 🔄 Agent 2 - Node-to-Node Data Flow Analysis

## Complete Data Journey Through 10-Node LangGraph Pipeline

---

## 📊 State Schema Overview

**StrategyAnalysisState** - Single Source of Truth for All 10 Nodes

```python
{
    # INPUT DATA (From Agent 1 / User)
    'options_dataframe': pd.DataFrame,      # 6×6 premium grid
    'delta_data': pd.DataFrame,             # 6×6 delta grid
    'portfolio_data': Dict,                 # {stock: shares_owned}
    'current_date': str,                    # "YYYY-MM-DD"
    'analysis_mode': str,                   # "premium_delta"
    
    # PROCESSING STATES (Updated by Nodes)
    'validated_data': bool,                 # Node 1 output
    'merged_data': pd.DataFrame,            # Node 3 output
    'primary_recommendations': Dict,        # Node 4 output
    'secondary_recommendations': Dict,      # Node 5 output
    'contract_allocations': Dict,           # Node 6 output
    'income_projections': Dict,             # Node 7 output
    'recommendations': List[Dict],          # Node 8 output
    'highlighted_cells': Dict,              # Node 9 output
    'llm_insights': str,                    # Node 10 output
    
    # METADATA
    'status': str,                          # Workflow progress tracker
    'errors': List[str],                   # Error accumulator
    'messages': List[BaseMessage],         # LLM conversation history
    'analysis_timestamp': str              # ISO timestamp
}
```

---

## 🔄 Node-by-Node Data Flow

---

### **NODE 1: Validate Input Data**

**📥 INPUT (from state):**
```python
{
    'options_dataframe': pd.DataFrame,  # Shape: (N stocks, 6 expiry columns)
    'delta_data': pd.DataFrame,         # Shape: (N stocks, 6 expiry columns)
    'analysis_mode': "premium_delta"
}
```

**🔧 PROCESSING:**
1. Checks `options_dataframe` is not None and not empty
2. Validates both matrices have same shape (rows and columns match)
3. Verifies column names align (same expiry dates)
4. Confirms numeric data types for premiums and deltas
5. Detects missing/corrupt values

**📤 OUTPUT (updates state):**
```python
{
    'validated_data': True,             # ✅ Pass / ❌ Fail
    'status': "data_validated",         # Progress marker
    'errors': []                        # Empty if successful
}
```

**🔗 NEXT NODE:** If `validated_data == True` → **Node 2**  
**🔗 IF FAIL:** If `validated_data == False` → **END** (workflow terminates)

---

### **NODE 2: Analyze Options Data**

**📥 INPUT (from state):**
```python
{
    'options_dataframe': pd.DataFrame,  # Validated 6×6 premium grid
    'validated_data': True
}
```

**🔧 PROCESSING:**
1. Extracts all premium values from 6×6 matrix
2. Reshapes data from matrix → long format list
3. Creates records: `[{Stock, Strike, Expiry, Premium}, ...]`
4. Identifies highest premium per stock (preliminary)
5. Counts total valid options per stock

**📤 OUTPUT (updates state):**
```python
{
    'premium_analysis': {
        'AAPL': {'highest_premium': 5.50, 'count': 36, 'strikes': [...], 'expiries': [...]},
        'GOOGL': {'highest_premium': 8.20, 'count': 36, ...},
        ...
    },
    'status': "premium_analyzed"
}
```

**🔗 NEXT NODE:** → **Node 3** (Calculate Scores)

---

### **NODE 3: Calculate Scores (Premium × Delta)**

**📥 INPUT (from state):**
```python
{
    'options_dataframe': pd.DataFrame,  # Premium data
    'delta_data': pd.DataFrame,         # Delta data
    'current_date': "2025-12-02"
}
```

**🔧 PROCESSING:**
1. **Merges** premium + delta DataFrames on (Stock, Strike, Expiry)
   ```python
   merged_df = pd.merge(premium_df, delta_df, on=['Stock', 'Strike', 'Expiry'])
   ```

2. **Filters** expired options:
   ```python
   valid_options = merged_df[merged_df['Expiry_Date'] > current_date]
   ```

3. **Calculates scores** for each option:
   ```python
   Score = Premium × (1 - Delta)
   ```
   Example:
   - Premium=$5.00, Delta=0.3 → Score = 5.00 × 0.7 = **3.50**
   - Premium=$2.00, Delta=0.1 → Score = 2.00 × 0.9 = **1.80**

4. **Assigns confidence** levels:
   - `HIGH`: Delta present and < 0.3
   - `MEDIUM`: Delta 0.3-0.5
   - `LOW`: Delta > 0.5

5. **Sorts** by score descending (best first)

**📤 OUTPUT (updates state):**
```python
{
    'merged_data': pd.DataFrame([
        {'Stock': 'AAPL', 'Strike': 150, 'Expiry': '12/06/25', 'Premium': 5.0, 'Delta': 0.3, 'Score': 3.5, 'Confidence': 'HIGH', 'Week': 1},
        {'Stock': 'AAPL', 'Strike': 155, 'Expiry': '12/13/25', 'Premium': 3.0, 'Delta': 0.2, 'Score': 2.4, 'Confidence': 'HIGH', 'Week': 2},
        ...  # All options scored and sorted
    ]),
    'status': "scores_calculated"
}
```

**🔗 NEXT NODE:** → **Node 4** (Select Primary)

---

### **NODE 4: Select Primary Recommendation**

**📥 INPUT (from state):**
```python
{
    'merged_data': pd.DataFrame  # Scored options (sorted by score DESC)
}
```

**🔧 PROCESSING:**
1. **Groups** scored options by stock
2. For each stock, **selects top-scoring option** (first row per group)
3. Extracts: strike, expiry, premium, delta, score, confidence, week
4. Determines week number from expiry date (Week 1-5)

**📤 OUTPUT (updates state):**
```python
{
    'primary_recommendations': {
        'AAPL': {
            'type': 'Primary',
            'stock': 'AAPL',
            'strike': 150.0,
            'expiry': '12/06/25',
            'premium': 5.0,
            'delta': 0.3,
            'score': 3.5,
            'confidence': 'HIGH',
            'week': 1  # ← Important for Node 5
        },
        'GOOGL': {...},
        ...
    },
    'status': "primary_selected"
}
```

**🔗 NEXT NODE:** → **Node 5** (Select Secondary)

---

### **NODE 5: Select Secondary Recommendation (Week-Based Logic)**

**📥 INPUT (from state):**
```python
{
    'primary_recommendations': Dict,    # From Node 4
    'merged_data': pd.DataFrame        # All scored options
}
```

**🔧 PROCESSING:**
1. For each stock, **checks primary's week number**:
   - If Week 3, 4, or 5 → **SKIP** (no secondary)
   - If Week 1 or 2 → **PROCEED** to find secondary

2. **Filters options** for secondary eligibility:
   ```python
   # Must expire 7+ days AFTER primary
   secondary_candidates = scored_options[
       (expiry_date > primary_expiry + 7 days) &
       (option != primary)  # Exclude primary itself
   ]
   ```

3. **Selects highest-scored** secondary candidate

4. If no valid secondary exists → Returns `None` for that stock

**📤 OUTPUT (updates state):**
```python
{
    'secondary_recommendations': {
        'AAPL': {
            'type': 'Secondary',
            'stock': 'AAPL',
            'strike': 155.0,
            'expiry': '12/20/25',  # 14 days after primary
            'premium': 3.0,
            'delta': 0.2,
            'score': 2.4,
            'confidence': 'HIGH',
            'week': 3
        },
        'GOOGL': None,  # Primary was Week 3, no secondary
        ...
    },
    'status': "secondary_selected"
}
```

**🔗 NEXT NODE:** → **Node 6** (Allocate Contracts)

---

### **NODE 6: Allocate Capital & Calculate Contracts**

**📥 INPUT (from state):**
```python
{
    'primary_recommendations': Dict,
    'secondary_recommendations': Dict,
    'portfolio_data': {
        'AAPL': 500,    # User owns 500 shares
        'GOOGL': 300,   # User owns 300 shares
        ...
    }
}
```

**🔧 PROCESSING:**
1. For each stock with recommendations:
   ```python
   shares_owned = portfolio_data[stock]
   max_contracts = shares_owned // 100  # 1 contract = 100 shares
   ```

2. **Applies safety buffer** (80% rule):
   ```python
   safe_contracts = int(max_contracts * 0.8)
   ```

3. **Allocates contracts**:
   - If only primary: All safe_contracts to primary
   - If primary + secondary: Split (e.g., 60% primary, 40% secondary)

**📤 OUTPUT (updates state):**
```python
{
    'contract_allocations': {
        'AAPL': {
            'shares_owned': 500,
            'max_contracts': 5,
            'primary_contracts': 3,    # 60% of 5
            'secondary_contracts': 2   # 40% of 5
        },
        'GOOGL': {
            'shares_owned': 300,
            'max_contracts': 3,
            'primary_contracts': 3,
            'secondary_contracts': 0   # No secondary for GOOGL
        },
        ...
    },
    'status': "contracts_allocated"
}
```

**🔗 NEXT NODE:** → **Node 7** (Calculate Income)

---

### **NODE 7: Calculate Projected Income**

**📥 INPUT (from state):**
```python
{
    'primary_recommendations': Dict,    # Has premium values
    'secondary_recommendations': Dict,
    'contract_allocations': Dict        # Has contract counts
}
```

**🔧 PROCESSING:**
1. **Calculates income per recommendation**:
   ```python
   Income = Premium × Contracts × 100
   ```
   
   Example for AAPL primary:
   ```python
   Income = $5.00 × 3 contracts × 100 = $1,500
   ```

2. **Sums total income per stock**:
   ```python
   Total_Income = Primary_Income + Secondary_Income
   ```

**📤 OUTPUT (updates state):**
```python
{
    'income_projections': {
        'AAPL': {
            'primary_income': 1500.00,      # $5 × 3 × 100
            'secondary_income': 600.00,     # $3 × 2 × 100
            'total_income': 2100.00
        },
        'GOOGL': {
            'primary_income': 2460.00,      # $8.20 × 3 × 100
            'secondary_income': 0.00,
            'total_income': 2460.00
        },
        ...
    },
    'total_portfolio_income': 4560.00,  # Sum across all stocks
    'status': "income_calculated"
}
```

**🔗 NEXT NODE:** → **Node 8** (Generate Recommendations)

---

### **NODE 8: Generate Final Recommendations**

**📥 INPUT (from state):**
```python
{
    'primary_recommendations': Dict,
    'secondary_recommendations': Dict,
    'contract_allocations': Dict,
    'income_projections': Dict
}
```

**🔧 PROCESSING:**
1. **Compiles all data** into structured recommendation list
2. For each stock, creates 1-2 recommendation dictionaries
3. Adds metadata: type, confidence, income, contracts

**📤 OUTPUT (updates state):**
```python
{
    'recommendations': [
        {
            'type': 'Primary',
            'stock': 'AAPL',
            'strike': 150.0,
            'expiry': '12/06/25',
            'premium': 5.0,
            'delta': 0.3,
            'score': 3.5,
            'confidence': 'HIGH',
            'contracts': 3,
            'income': 1500.00,
            'week': 1
        },
        {
            'type': 'Secondary',
            'stock': 'AAPL',
            'strike': 155.0,
            'expiry': '12/20/25',
            'premium': 3.0,
            'delta': 0.2,
            'score': 2.4,
            'confidence': 'HIGH',
            'contracts': 2,
            'income': 600.00,
            'week': 3
        },
        # ... more recommendations for other stocks
    ],
    'status': "recommendations_generated"
}
```

**🔗 NEXT NODE:** → **Node 9** (Prepare Highlighting)

---

### **NODE 9: Prepare Cell Highlighting Data**

**📥 INPUT (from state):**
```python
{
    'recommendations': List[Dict],      # From Node 8
    'options_dataframe': pd.DataFrame   # Original 6×6 grid
}
```

**🔧 PROCESSING:**
1. **Maps recommendations back to matrix coordinates**:
   - Finds row index for each stock + strike combination
   - Identifies column name for each expiry date

2. **Creates highlighting dictionary**:
   ```python
   highlighted_cells = {
       row_index: [expiry_column_1, expiry_column_2, ...]
   }
   ```

**📤 OUTPUT (updates state):**
```python
{
    'highlighted_cells': {
        0: ['12/06/25'],           # AAPL primary at row 0
        0: ['12/06/25', '12/20/25'],  # Added AAPL secondary
        3: ['12/13/25'],           # GOOGL primary at row 3
        ...
    },
    'status': "highlighting_prepared"
}
```

**💡 NOTE:** This data tells the UI which cells to paint green in the 6×6 matrix display.

**🔗 NEXT NODE:** → **Node 10** (Generate LLM Insights)

---

### **NODE 10: Generate LLM Insights (AI-Powered Explanation)**

**📥 INPUT (from state):**
```python
{
    'recommendations': List[Dict],  # All recommendation data
    'messages': []                  # Empty conversation history
}
```

**🔧 PROCESSING:**
1. **Constructs GPT prompt** with structured data:
   ```python
   prompt = f"""
   Analyze these options recommendations:
   
   Stock: AAPL
   - Primary: Strike $150, Expiry 12/06, Premium $5.00, Delta 0.3
   - Secondary: Strike $155, Expiry 12/20, Premium $3.00, Delta 0.2
   
   Explain WHY these options were selected...
   """
   ```

2. **Calls GPT-3.5-turbo** with `temperature=0.3` (low creativity)

3. **Receives AI-generated explanation** in natural language

**📤 OUTPUT (updates state):**
```python
{
    'llm_insights': """
    These recommendations balance premium income with assignment risk:
    
    **AAPL Strategy:**
    - Primary ($150 strike, 12/06): Offers $5.00 premium with moderate 0.3 delta, 
      providing high income while staying out-of-the-money to reduce exercise risk.
    - Secondary ($155 strike, 12/20): Capitalizes on Week 1-2 timing with $3.00 
      premium and safer 0.2 delta, diversifying expiration dates.
    
    **Risk-Reward Analysis:**
    The scoring formula prioritized options with high premiums and low assignment 
    probability. The 7-day gap between primary and secondary ensures temporal 
    diversification...
    """,
    'status': "insights_generated",
    'messages': [
        HumanMessage(content="Analyze..."),
        AIMessage(content="These recommendations balance...")
    ]
}
```

**🔗 NEXT NODE:** → **END** (Workflow complete)

---

## 🔄 Complete Data Flow Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                         INPUT STATE                         │
├─────────────────────────────────────────────────────────────┤
│ options_dataframe: 6×6 premium grid                        │
│ delta_data: 6×6 delta grid                                 │
│ portfolio_data: {AAPL: 500, GOOGL: 300}                    │
│ current_date: "2025-12-02"                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 1: Validate Input Data                               │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: validated_data = True                             │
│          status = "data_validated"                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 2: Analyze Options Data                              │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: premium_analysis = {AAPL: {...}, GOOGL: {...}}   │
│          status = "premium_analyzed"                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 3: Calculate Scores (Premium × (1-Delta))            │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: merged_data = DataFrame with Score column         │
│          [All 36 options scored & sorted per stock]        │
│          status = "scores_calculated"                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 4: Select Primary Recommendation                     │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: primary_recommendations = {                       │
│            AAPL: {strike: 150, score: 3.5, week: 1},      │
│            GOOGL: {strike: 2800, score: 6.6, week: 3}     │
│          }                                                  │
│          status = "primary_selected"                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 5: Select Secondary Recommendation (Week 1-2 only)   │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: secondary_recommendations = {                     │
│            AAPL: {strike: 155, week: 3},  ← Has secondary │
│            GOOGL: None  ← Primary Week 3, no secondary    │
│          }                                                  │
│          status = "secondary_selected"                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 6: Allocate Contracts                                │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: contract_allocations = {                          │
│            AAPL: {primary: 3, secondary: 2},              │
│            GOOGL: {primary: 3, secondary: 0}              │
│          }                                                  │
│          status = "contracts_allocated"                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 7: Calculate Projected Income                        │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: income_projections = {                            │
│            AAPL: {primary: $1500, secondary: $600},       │
│            GOOGL: {primary: $2460, secondary: $0}         │
│          }                                                  │
│          total_portfolio_income = $4560                    │
│          status = "income_calculated"                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 8: Generate Final Recommendations                    │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: recommendations = [                               │
│            {type: Primary, stock: AAPL, contracts: 3...}, │
│            {type: Secondary, stock: AAPL, contracts: 2...} │
│            {type: Primary, stock: GOOGL, contracts: 3...} │
│          ]                                                  │
│          status = "recommendations_generated"              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 9: Prepare Cell Highlighting                         │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: highlighted_cells = {                             │
│            0: ['12/06/25', '12/20/25'],  ← AAPL row       │
│            3: ['12/13/25']  ← GOOGL row                   │
│          }                                                  │
│          status = "highlighting_prepared"                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  NODE 10: Generate LLM Insights                            │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: llm_insights = "These recommendations balance..." │
│          messages = [HumanMessage(...), AIMessage(...)]   │
│          status = "insights_generated"                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                       FINAL STATE                          │
├─────────────────────────────────────────────────────────────┤
│ ✅ recommendations: List of 1-2 trades per stock           │
│ ✅ highlighted_cells: Matrix coordinates for UI            │
│ ✅ llm_insights: Natural language explanation              │
│ ✅ income_projections: Dollar amounts per recommendation   │
│ ✅ status: "insights_generated"                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Key Data Transformations

### **Transformation 1: Matrix → Long Format (Node 2)**
```python
# INPUT (6×6 Matrix)
        12/06  12/13  12/20  12/27  01/03  01/10
AAPL    5.00   3.50   2.80   ...    ...    ...
GOOGL   8.20   6.50   5.10   ...    ...    ...

# OUTPUT (Long Format)
[
    {Stock: AAPL, Strike: 150, Expiry: 12/06, Premium: 5.00},
    {Stock: AAPL, Strike: 150, Expiry: 12/13, Premium: 3.50},
    {Stock: AAPL, Strike: 155, Expiry: 12/06, Premium: 4.50},
    ...
]
```

### **Transformation 2: Premium + Delta → Scored (Node 3)**
```python
# INPUT (Two Separate DataFrames)
Premium_DF: {Stock, Strike, Expiry, Premium}
Delta_DF:   {Stock, Strike, Expiry, Delta}

# MERGE
Merged_DF:  {Stock, Strike, Expiry, Premium, Delta}

# CALCULATE
Merged_DF['Score'] = Merged_DF['Premium'] × (1 - Merged_DF['Delta'])

# OUTPUT
{Stock: AAPL, Strike: 150, Expiry: 12/06, Premium: 5.0, Delta: 0.3, Score: 3.5}
```

### **Transformation 3: Scored Options → Recommendations (Nodes 4-5)**
```python
# INPUT (All Scored Options - 36 per stock)
[
    {Stock: AAPL, Score: 3.5, Week: 1},  ← Best
    {Stock: AAPL, Score: 2.4, Week: 3},  ← 2nd best (7+ days gap)
    {Stock: AAPL, Score: 2.1, Week: 2},
    {Stock: AAPL, Score: 1.8, Week: 4},
    ...
]

# SELECTION LOGIC
Primary = Top 1 (Score: 3.5, Week: 1)
Secondary = Top from options with expiry > Primary + 7 days (Score: 2.4, Week: 3)

# OUTPUT
primary_recommendations = {AAPL: {Score: 3.5, Week: 1}}
secondary_recommendations = {AAPL: {Score: 2.4, Week: 3}}
```

---

## 📊 State Evolution Timeline

```
Time   Node   Status Field Value
─────────────────────────────────────────────────────────────
T0     START  "initialized"
T1     N1     "data_validated"
T2     N2     "premium_analyzed"
T3     N3     "scores_calculated"
T4     N4     "primary_selected"
T5     N5     "secondary_selected"
T6     N6     "contracts_allocated"
T7     N7     "income_calculated"
T8     N8     "recommendations_generated"
T9     N9     "highlighting_prepared"
T10    N10    "insights_generated"  ← FINAL
```

---

## 🎯 Critical Data Dependencies

| Node | Requires (from state)          | Produces (to state)           |
|------|--------------------------------|-------------------------------|
| N1   | `options_dataframe`, `delta_data` | `validated_data`          |
| N2   | `options_dataframe`            | `premium_analysis`            |
| N3   | `options_dataframe`, `delta_data` | `merged_data` (scored)    |
| N4   | `merged_data`                  | `primary_recommendations`     |
| N5   | `primary_recommendations`, `merged_data` | `secondary_recommendations` |
| N6   | `primary/secondary`, `portfolio_data` | `contract_allocations` |
| N7   | `primary/secondary`, `contract_allocations` | `income_projections` |
| N8   | `primary/secondary`, `contracts`, `income` | `recommendations` |
| N9   | `recommendations`, `options_dataframe` | `highlighted_cells`   |
| N10  | `recommendations`              | `llm_insights`, `messages`    |

---

## 💡 Data Persistence Notes

1. **Immutable State Updates**: Each node receives the full state, modifies specific fields, and returns the updated state. Original inputs remain unchanged.

2. **Checkpoint Recovery**: LangGraph can save state after each node, enabling restart from any point if a crash occurs.

3. **Parallel Execution Potential**: Nodes 6 and 7 could theoretically run in parallel since Node 6 doesn't depend on Node 7's output (future optimization).

4. **Error Propagation**: If any node fails, it updates `state['errors']` and `state['status']`, preventing subsequent nodes from executing bad data.

---

## 🚀 Performance Characteristics

- **Total State Size**: ~50-100 KB (for 10 stocks with 36 options each)
- **Node Execution Times**:
  - N1-N2: <0.1s (validation/analysis)
  - N3: ~0.5s (scoring 360 options)
  - N4-N9: <0.2s each (selection/allocation)
  - N10: ~2-3s (GPT API call)
- **End-to-End Latency**: ~4-5 seconds for 10 stocks

---

## 📝 Example Full State at END

```python
{
    # INPUT (unchanged)
    'options_dataframe': <DataFrame 10×6>,
    'delta_data': <DataFrame 10×6>,
    'portfolio_data': {'AAPL': 500, 'GOOGL': 300, ...},
    'current_date': '2025-12-02',
    'analysis_mode': 'premium_delta',
    
    # PROCESSING ARTIFACTS
    'validated_data': True,
    'premium_analysis': {...},
    'merged_data': <DataFrame 360 rows>,
    'primary_recommendations': {10 stocks: {...}},
    'secondary_recommendations': {4 stocks: {...}, 6 stocks: None},
    'contract_allocations': {10 stocks: {...}},
    'income_projections': {10 stocks: {...}, 'total': 15600.00},
    
    # OUTPUT
    'recommendations': [14 recommendation dicts],  # 10 primary + 4 secondary
    'highlighted_cells': {10 row_indices: [expiry_cols]},
    'llm_insights': "These recommendations balance...",
    
    # METADATA
    'messages': [HumanMessage, AIMessage],
    'status': 'insights_generated',
    'errors': [],
    'analysis_timestamp': '2025-12-02T14:35:22Z'
}
```
