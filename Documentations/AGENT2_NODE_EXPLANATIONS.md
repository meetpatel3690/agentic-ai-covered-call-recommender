# 🎯 Agent 2 - Node-by-Node Explanation (5-6 Lines Each)

## Agent 2: Strategy Recommendation Agent - 10 Node Breakdown

---

### **Node 1: Validate Input Data**

**Responsibility**: Ensures the data received from Agent 1 is complete and correctly formatted before processing.

**What it does:**
- Checks if the 6×6 premium matrix and delta matrix exist and are not empty
- Validates that both matrices have the same structure (6 strikes × 6 expiration dates)
- Verifies data types are correct (premiums are numbers, dates are valid)
- Confirms there are no missing or corrupt values that would break downstream processing
- Sets validation status to TRUE/FALSE, which determines if subsequent nodes run
- If validation fails, stops the workflow and returns an error message to the user

---

### **Node 2: Analyze Options Data**

**Responsibility**: Extracts and organizes premium values from the 6×6 matrix to prepare for scoring.

**What it does:**
- Parses the premium matrix to extract individual option entries (strike price, expiration date, premium value)
- Creates a structured list of all 36 options per stock with their premium amounts
- Identifies the option with the highest premium for each stock (preliminary analysis)
- Organizes options by expiration week (Week 1-5 of the month) for later filtering
- Stores the analyzed premium data in the state for use by the scoring node
- Provides a summary count of valid options available for each stock

---

### **Node 3: Calculate Scores (Premium × Delta Formula)**

**Responsibility**: Applies the scoring formula to rank all options from best to worst based on risk-adjusted return.

**What it does:**
- Combines premium values with delta values for each option using the formula: **Score = Premium × (1 - Delta)**
- Assigns a confidence level (HIGH/MEDIUM/LOW) based on the delta value: HIGH if delta < 0.3, MEDIUM if 0.3-0.5, LOW if > 0.5
- Filters out expired options by comparing expiration dates to the current date
- Sorts all remaining options by score in descending order (highest score first)
- Creates a ranked DataFrame with columns: Stock, Strike, Expiry, Premium, Delta, Score, Confidence, Week
- Stores the scored and sorted options for the selection nodes to pick the best recommendations

---

### **Node 4: Select Primary Recommendation**

**Responsibility**: Chooses the single best option (highest score) as the primary trade recommendation for each stock.

**What it does:**
- Filters the scored options to get only the highest-ranked option for the stock
- Extracts the primary recommendation details: strike price, expiration date, premium, delta, score, confidence level
- Identifies which week of the month this option expires in (important for secondary selection)
- Creates a structured primary recommendation dictionary with all relevant trading details
- Stores this as the guaranteed first trade that will be shown to the user
- Passes the primary information to Node 5 to determine if a secondary trade is possible

---

### **Node 5: Select Secondary Recommendation (Week-Based Logic)**

**Responsibility**: Determines if a second trade opportunity exists based on the primary trade's timing and the 7-day gap rule.

**What it does:**
- Checks if the primary trade is in Week 1 or 2 (early month); if Week 3+, skips secondary and returns None
- If eligible, searches for options that expire at least 7 days after the primary expiration date
- Filters out the primary option itself to avoid recommending the same trade twice
- Selects the highest-scored option among those meeting the 7-day gap requirement
- Creates a secondary recommendation dictionary with the same structure as the primary
- If no valid secondary exists (no 7-day gap options), returns None to indicate single-trade strategy

---

### **Node 6: Allocate Capital & Calculate Contracts**

**Responsibility**: Determines how many option contracts to sell based on the user's portfolio holdings.

**What it does:**
- Loads the user's current portfolio data to see how many shares they own of each stock
- Calculates the maximum contracts possible: 1 contract = 100 shares (e.g., 500 shares = 5 contracts max)
- Applies a safety buffer to avoid selling all holdings (typically sells contracts for 80% of shares)
- Allocates contracts separately for primary and secondary recommendations based on available shares
- Ensures contract allocation doesn't exceed portfolio holdings or risk limits
- Stores the contract count for each recommendation to calculate projected income in the next node

---

### **Node 7: Calculate Projected Income**

**Responsibility**: Computes the total income the user will earn from executing the recommended trades.

**What it does:**
- Uses the formula: **Income = Premium × Contracts × 100** (each contract covers 100 shares)
- Calculates income for the primary recommendation (e.g., $2.50 premium × 2 contracts × 100 = $500)
- If a secondary exists, calculates its income separately and adds to the total
- Sums up the total projected monthly income from all recommended trades for the stock
- Stores income projections per recommendation and total income in the state
- Provides this financial data to the user so they can see expected earnings before executing trades

---

### **Node 8: Generate Final Recommendations**

**Responsibility**: Packages all analysis results into a structured, user-friendly recommendation format ready for display.

**What it does:**
- Compiles primary and secondary recommendations (if exists) into a single cohesive structure
- Adds contract allocations and income projections to each recommendation
- Formats all data into a list of dictionaries with clear labels (type, stock, strike, expiry, premium, delta, score, contracts, income)
- Includes metadata like confidence levels, week numbers, and timestamps for tracking
- Prepares the recommendations for both UI display and potential export/storage
- Creates a complete recommendation package that the UI can render as cards, tables, or charts

---

### **Node 9: Prepare Cell Highlighting Data**

**Responsibility**: Identifies which cells in the 6×6 matrix should be visually highlighted in the UI to show the recommended options.

**What it does:**
- Maps the primary and secondary recommendations back to their positions in the original 6×6 matrix
- Creates a highlighting dictionary with keys as (strike, expiry) coordinates and values as highlight colors/styles
- Marks the primary recommendation cell with a distinct color (e.g., green for highest priority)
- If a secondary exists, marks its cell with a different color (e.g., light green or yellow)
- Stores the highlighting data in the state so the UI can apply visual emphasis to recommended cells
- Enables users to visually see at a glance which options in the matrix are recommended for trading

---

### **Node 10: Generate LLM Insights (AI-Powered Explanation)**

**Responsibility**: Uses GPT to generate a natural language explanation of WHY these specific options were recommended.

**What it does:**
- Sends the recommendation details (strikes, premiums, deltas, scores) to GPT-3.5-turbo with a specialized prompt
- Asks the LLM to explain the trade logic in plain English: why these strikes, why these dates, what's the risk/reward
- Receives AI-generated insights that explain the scoring rationale and market context (e.g., "These options balance high premium income with low assignment risk")
- Adds educational value by helping users understand the strategy, not just follow it blindly
- Stores the LLM insights as a text block that displays alongside the recommendations in the UI
- Provides transparency and builds user trust by explaining the "why" behind each recommendation

---

## 🔄 Data Flow Summary

```
Node 1: Validate → Checks data quality
Node 2: Analyze → Extracts premiums
Node 3: Score → Applies Premium × (1-Delta) formula
Node 4: Primary → Picks best option
Node 5: Secondary → Finds 2nd trade (if Week 1-2)
Node 6: Allocate → Calculates contracts
Node 7: Income → Computes earnings
Node 8: Recommendations → Packages results
Node 9: Highlight → Marks matrix cells
Node 10: LLM Insights → Explains "why"
```

**Final Output**: 1-2 trade recommendations per stock with contract counts, income projections, matrix highlighting, and AI-generated explanations.
