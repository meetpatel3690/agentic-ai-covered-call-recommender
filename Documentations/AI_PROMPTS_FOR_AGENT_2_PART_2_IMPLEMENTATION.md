# AI Prompts for Agent 2 Part 2 Implementation

**Document Purpose:** This document contains AI prompts that can be used to implement the Agent 2 Part 2 functionality. These prompts are designed to guide AI assistants (like GitHub Copilot, ChatGPT, or Claude) in implementing the Delta-based scoring system for options trading recommendations.

**Target File:** `backend/strategy_recommendation_agent_langgraph.py`

**Reference Documents:**
- `AGENT_2_PART_2_IMPLEMENTATION_SPEC.md` - Complete technical specification
- `SYSTEM_FLOW_ANALYSIS.md` - System architecture overview

---

## **Phase 1: Preparation & Delta Integration**

### **Prompt 1.1: Update State Schema and Delta Integration**

```
I need to update the AgentState schema in strategy_recommendation_agent_langgraph.py to support Delta-based scoring. Please help me:

1. Add a new field `delta_data: pd.DataFrame` to the AgentState TypedDict to store Delta values
2. Update the `analyze()` method signature to accept `delta_data` parameter
3. Add a helper function `merge_premium_delta_data()` that:
   - Takes premium_matrix and delta_matrix as inputs
   - Merges them on Strike and Expiry
   - Returns a combined DataFrame with columns: Strike, Expiry, Premium, Delta
   - Handles cases where Delta might be None (treat None as 0)

Requirements:
- Don't break existing functionality
- Ensure backward compatibility if delta_data is not provided
- Add proper type hints
- Include docstrings for new functions

Current AgentState structure uses TypedDict with fields like formatted_matrix, selected_stocks, etc.
```

---

## **Phase 2: Scoring Implementation**

### **Prompt 2.1: Implement Delta-Based Scoring Function**

```
I need to implement the core scoring function for Agent 2 Part 2. The scoring formula is:
Score = Premium × (1 - Delta)

Please create a function `calculate_option_score()` that:

INPUT:
- premium: float (the option premium value)
- delta: float or None (the option delta value)

LOGIC:
- If delta is None, treat it as 0 (so Score = Premium × 1.0)
- If delta is provided, calculate: Score = Premium × (1 - Delta)
- Return both the score and a confidence level

OUTPUT:
- Returns tuple: (score: float, confidence: str)
- Confidence levels:
  - "HIGH" if delta is provided and valid
  - "MEDIUM" if delta is None (treated as 0)

EXAMPLE:
- Premium = 2.5, Delta = 0.3 → Score = 2.5 × (1 - 0.3) = 1.75, Confidence = HIGH
- Premium = 3.0, Delta = None → Score = 3.0 × 1.0 = 3.0, Confidence = MEDIUM

Add proper error handling for edge cases (negative values, invalid types, etc.)
```

### **Prompt 2.2: Replace Premium-Only Scoring with Delta-Based Scoring**

```
I need to replace the existing premium-only scoring logic in strategy_recommendation_agent_langgraph.py with the new Delta-based scoring.

Current behavior:
- The code currently sorts options by premium only (highest premium wins)
- Located in the node function that processes filtered options

New behavior:
- Use the calculate_option_score() function created earlier
- For each option row:
  1. Get premium from the row
  2. Get delta from the merged DataFrame (handle None values)
  3. Calculate score using: Score = Premium × (1 - Delta)
  4. Store score and confidence level
- Sort options by score (descending) instead of just premium
- Keep track of confidence level for each recommendation

Requirements:
- Preserve all existing data columns
- Add new columns: 'Score', 'Confidence'
- Don't remove the premium column (still needed for income calculation)
- Maintain the same DataFrame structure for compatibility with downstream code
```

---

## **Phase 3: Week Identification Logic**

### **Prompt 3.1: Implement Week Identification Function**

```
I need a function to identify which week of the month a given date falls into.

Create a function `get_week_of_month()` that:

INPUT:
- expiry_date: datetime or string (format: "YYYY-MM-DD")

LOGIC:
- The week number is based on the Friday's position within its OWN month
- Week 1: Days 1-7 of the month
- Week 2: Days 8-14 of the month
- Week 3: Days 15-21 of the month
- Week 4: Days 22-28 of the month
- Week 5: Days 29+ of the month

OUTPUT:
- Returns integer: 1, 2, 3, 4, or 5

EXAMPLES:
- "2024-12-06" (Dec 6) → Week 1 (day 6 is in days 1-7)
- "2024-12-13" (Dec 13) → Week 2 (day 13 is in days 8-14)
- "2024-12-20" (Dec 20) → Week 3 (day 20 is in days 15-21)
- "2024-12-27" (Dec 27) → Week 4 (day 27 is in days 22-28)

Edge cases to handle:
- String dates need to be converted to datetime
- Validate date format
- Handle invalid dates gracefully
```

---

## **Phase 4: Primary Recommendation Selection**

### **Prompt 4.1: Implement Primary Recommendation Logic**

```
I need to implement the logic for selecting the primary (best) recommendation from scored options.

Current state:
- Options are already scored using Score = Premium × (1 - Delta)
- Options are sorted by score (descending)
- Expired options are already filtered out

Requirements:
Create a function `select_primary_recommendation()` that:

INPUT:
- sorted_options: DataFrame with columns [Strike, Expiry, Premium, Delta, Score, Confidence]
- current_date: datetime (for date comparisons)

LOGIC:
1. Take the top-scored option (highest Score)
2. Identify its week using get_week_of_month() function
3. Mark it as "Primary" recommendation
4. Return the primary option with additional metadata

OUTPUT:
- Returns dictionary with:
  {
    'strike': float,
    'expiry': str,
    'premium': float,
    'delta': float or None,
    'score': float,
    'confidence': str,
    'week': int (1-5),
    'type': 'Primary'
  }

This will be used to determine if we need to look for a secondary trade.
```

---

## **Phase 5: Secondary Trade Logic**

### **Prompt 5.1: Implement Secondary Trade Selection Logic**

```
I need to implement the logic for finding a secondary trade opportunity based on the primary trade's week.

Multi-Trade Strategy Rules:
- If Primary is Week 1 or Week 2 → Look for secondary trade
- If Primary is Week 3, 4, or 5 → NO secondary trade (too late)

Create a function `select_secondary_recommendation()` that:

INPUT:
- primary_trade: dict (output from select_primary_recommendation)
- sorted_options: DataFrame (all scored options, sorted by Score)
- current_date: datetime

LOGIC:
1. Check primary_trade['week']
2. If week is 3, 4, or 5:
   - Return None (no secondary needed)
3. If week is 1 or 2:
   - Filter options where expiry_date >= (primary_expiry + 7 days)
   - This ensures secondary is at least 7 days after primary
   - From filtered options, pick the top-scored option
   - Mark it as "Secondary" recommendation
   - Return the secondary trade

OUTPUT:
- Returns dictionary (same structure as primary) OR None
  {
    'strike': float,
    'expiry': str,
    'premium': float,
    'delta': float or None,
    'score': float,
    'confidence': str,
    'week': int,
    'type': 'Secondary'
  }

EXAMPLE:
- Primary: Week 1, Expiry = Dec 6
- Secondary must have: Expiry >= Dec 13 (7 days later)
- Pick highest scoring option that meets this criteria
```

---

## **Phase 6: Contract Allocation Logic**

### **Prompt 6.1: Implement Contract Allocation Strategy**

```
I need to implement the contract allocation logic that determines how many contracts to recommend for each trade.

Buffer Strategy Rules:
- If available_contracts >= 3: Recommend (total - 1) contracts [keep 1 as buffer]
- If available_contracts < 3: Recommend ALL contracts [no buffer]

Create a function `calculate_contract_allocation()` that:

INPUT:
- total_shares: int (total shares available, e.g., 500)
- primary_trade: dict or None
- secondary_trade: dict or None

LOGIC:
1. Calculate total_contracts = total_shares // 100
   - Each contract represents 100 shares
2. Determine available_contracts:
   - If both primary and secondary exist:
     - Split evenly: available_for_primary = total_contracts // 2
     - Remaining: available_for_secondary = total_contracts - available_for_primary
   - If only primary exists:
     - available_for_primary = total_contracts
3. Apply buffer strategy for each trade:
   - If available >= 3: recommend (available - 1)
   - If available < 3: recommend available
4. Return contract allocation

OUTPUT:
- Returns dictionary:
  {
    'total_contracts': int,
    'primary_contracts': int,
    'secondary_contracts': int or 0,
    'buffer_kept': int
  }

EXAMPLES:
Example 1: 500 shares, Primary only
- total_contracts = 5
- available_for_primary = 5
- Since 5 >= 3 → recommend 4, keep 1 buffer
- Output: {total: 5, primary: 4, secondary: 0, buffer: 1}

Example 2: 500 shares, Primary + Secondary
- total_contracts = 5
- Split: primary gets 2, secondary gets 3
- Primary: 2 < 3 → recommend 2 (no buffer)
- Secondary: 3 >= 3 → recommend 2, keep 1 buffer
- Output: {total: 5, primary: 2, secondary: 2, buffer: 1}

Example 3: 200 shares, Primary only
- total_contracts = 2
- available_for_primary = 2
- Since 2 < 3 → recommend 2 (no buffer)
- Output: {total: 2, primary: 2, secondary: 0, buffer: 0}
```

---

## **Phase 7: Income Calculation**

### **Prompt 7.1: Implement Income Calculation Function**

```
I need to calculate the total income from recommendations based on premium and allocated contracts.

Income Formula: Income = Premium × Contracts × 100

Create a function `calculate_total_income()` that:

INPUT:
- primary_trade: dict (with 'premium' key)
- secondary_trade: dict or None (with 'premium' key)
- contract_allocation: dict (with 'primary_contracts' and 'secondary_contracts')

LOGIC:
1. Calculate primary_income:
   - primary_income = primary_trade['premium'] × contract_allocation['primary_contracts'] × 100
2. Calculate secondary_income (if secondary exists):
   - secondary_income = secondary_trade['premium'] × contract_allocation['secondary_contracts'] × 100
   - If no secondary, secondary_income = 0
3. Calculate total_income:
   - total_income = primary_income + secondary_income

OUTPUT:
- Returns dictionary:
  {
    'primary_income': float,
    'secondary_income': float,
    'total_income': float
  }

EXAMPLES:
Example 1: Primary only
- Primary Premium = 2.5, Contracts = 4
- Primary Income = 2.5 × 4 × 100 = $1,000
- Total = $1,000

Example 2: Primary + Secondary
- Primary Premium = 2.5, Contracts = 2
- Secondary Premium = 1.8, Contracts = 2
- Primary Income = 2.5 × 2 × 100 = $500
- Secondary Income = 1.8 × 2 × 100 = $360
- Total = $860

Add currency formatting (e.g., "$1,000.00") for better readability.
```

---

## **Phase 8: Complete Workflow Integration**

### **Prompt 8.1: Integrate All Components into Main Workflow**

```
I need to integrate all the implemented functions into the main LangGraph workflow for Agent 2.

Current workflow structure:
- Node functions process data step by step
- State is passed between nodes using AgentState TypedDict
- Each node updates specific fields in the state

Integration requirements:
Create or update the main processing node to orchestrate the complete flow:

STEP-BY-STEP FLOW:
1. Merge premium and delta data using merge_premium_delta_data()
2. Filter out expired options (expiry_date > current_date)
3. Calculate scores for all valid options using calculate_option_score()
4. Sort options by score (descending)
5. Select primary recommendation using select_primary_recommendation()
6. Determine if secondary is needed using select_secondary_recommendation()
7. Calculate contract allocation using calculate_contract_allocation()
8. Calculate income using calculate_total_income()
9. Format final output with all recommendations

State updates needed:
- Update state['recommendations'] with structured data
- Include: primary_trade, secondary_trade, contract_allocation, income_breakdown
- Add metadata: confidence_levels, week_numbers, scores

Error handling:
- Handle empty DataFrames (no valid options)
- Handle missing delta_data (fall back to premium-only if needed)
- Handle edge cases (all expired, no options available)

Return the updated state for the next node in the graph.
```

---

## **Phase 9: Output Formatting & UI Integration**

### **Prompt 9.1: Format Recommendations for UI Display**

```
I need to format the recommendations output in a structure that's easy for the Streamlit UI to consume.

Create a function `format_recommendations_for_ui()` that:

INPUT:
- state: AgentState (contains all recommendation data)
- stock_symbol: str (e.g., "AAPL")

OUTPUT FORMAT:
Returns a dictionary structured for UI display:

{
  'stock': str,
  'recommendations': [
    {
      'type': 'Primary' or 'Secondary',
      'strike': float,
      'expiry': str (formatted as "Mon DD, YYYY"),
      'premium': float,
      'delta': float or "N/A",
      'score': float,
      'confidence': 'HIGH' or 'MEDIUM',
      'week': int,
      'contracts': int,
      'income': float (formatted as "$X,XXX.XX")
    },
    ... (secondary if exists)
  ],
  'summary': {
    'total_contracts_recommended': int,
    'buffer_kept': int,
    'total_income': str (formatted as "$X,XXX.XX"),
    'confidence_level': 'HIGH' or 'MEDIUM' (based on recommendations)
  }
}

Formatting requirements:
- Date: Convert "2024-12-06" to "Dec 06, 2024"
- Currency: Format as "$1,234.56"
- Delta: Show as "0.XX" or "N/A" if None
- Score: Round to 2 decimal places

This structure will be passed to the UI for rendering in the recommendations panel.
```

### **Prompt 9.2: Update UI to Pass Delta Data and Display Recommendations**

```
I need to update the Streamlit UI (UI/pages/mainpage.py) to support the new Delta-based recommendations.

Required changes in mainpage.py:

PART 1: Pass delta_data to Agent 2
- Locate where strategy_recommendation_agent_langgraph.analyze() is called
- Add delta_df parameter to the function call
- delta_df is already available from Agent 1 (options_data_agent.py returns it)

Code change example:
# OLD:
result = analyze(formatted_matrix=options_df, selected_stocks=[stock])

# NEW:
result = analyze(
    formatted_matrix=options_df,
    delta_data=delta_df,
    selected_stocks=[stock]
)

PART 2: Display recommendations panel
Create a new section in the UI to display recommendations:

1. Add a new expander or section titled "📊 Options Recommendations"
2. For each stock's recommendations:
   - Display PRIMARY recommendation with GREEN highlight (st.success or custom CSS)
   - Display SECONDARY recommendation (if exists) with ORANGE highlight (st.warning or custom CSS)
   - Show: Strike, Expiry, Premium, Delta, Score, Confidence, Contracts, Income
3. Display summary section:
   - Total Contracts Recommended
   - Buffer Kept
   - Total Income
   - Overall Confidence Level

PART 3: Visual highlighting in options grid
- Add color coding to the grid cells:
  - GREEN background for primary recommendation
  - ORANGE background for secondary recommendation
- Use Streamlit's st.dataframe with styling or custom CSS

PART 4: Add legend
Add a legend explaining the color codes:
- 🟢 Green = Primary Recommendation (Best Score)
- 🟠 Orange = Secondary Recommendation (Week 1 or 2 only)
- Confidence: HIGH (Delta available) | MEDIUM (Delta estimated as 0)

Note: Do NOT display any warning messages for missing Delta values. Missing Delta is treated as 0 internally.
```

---

## **Phase 10: Testing & Validation**

### **Prompt 10.1: Create Comprehensive Test Cases**

```
I need to create comprehensive test cases to validate the Agent 2 Part 2 implementation.

Create a test suite that covers:

TEST CATEGORY 1: Scoring Logic
- Test 1.1: Premium = 2.5, Delta = 0.3 → Score = 1.75, Confidence = HIGH
- Test 1.2: Premium = 3.0, Delta = None → Score = 3.0, Confidence = MEDIUM
- Test 1.3: Premium = 1.5, Delta = 0.5 → Score = 0.75, Confidence = HIGH

TEST CATEGORY 2: Week Identification
- Test 2.1: "2024-12-06" → Week 1
- Test 2.2: "2024-12-13" → Week 2
- Test 2.3: "2024-12-20" → Week 3
- Test 2.4: "2024-12-27" → Week 4
- Test 2.5: "2024-12-31" → Week 5

TEST CATEGORY 3: Secondary Trade Logic
- Test 3.1: Primary Week 1 → Secondary should be found (>= 7 days later)
- Test 3.2: Primary Week 2 → Secondary should be found (>= 7 days later)
- Test 3.3: Primary Week 3 → NO secondary
- Test 3.4: Primary Week 4 → NO secondary
- Test 3.5: Primary Week 5 → NO secondary

TEST CATEGORY 4: Contract Allocation
- Test 4.1: 500 shares, Primary only, 5 contracts → Recommend 4 (keep 1)
- Test 4.2: 200 shares, Primary only, 2 contracts → Recommend 2 (no buffer)
- Test 4.3: 500 shares, Primary + Secondary → Split and apply buffer rules
- Test 4.4: 100 shares, Primary + Secondary → 1 contract total (edge case)

TEST CATEGORY 5: Income Calculation
- Test 5.1: Primary only (Premium=2.5, Contracts=4) → $1,000
- Test 5.2: Primary + Secondary → Sum both incomes correctly
- Test 5.3: Verify formatting (currency with $ and commas)

TEST CATEGORY 6: Edge Cases
- Test 6.1: All options expired → Return "No valid options"
- Test 6.2: All Deltas are None → All MEDIUM confidence, scores = premium × 1.0
- Test 6.3: Cross-month data (Nov 28 with Dec dates) → All dates analyzed fairly
- Test 6.4: Only 1 option available → Should be selected as primary
- Test 6.5: Empty DataFrame → Handle gracefully without errors

TEST CATEGORY 7: End-to-End Integration
- Test 7.1: Run full workflow with real sample data
- Test 7.2: Verify UI displays recommendations correctly
- Test 7.3: Verify color highlighting (GREEN for primary, ORANGE for secondary)
- Test 7.4: Verify backward compatibility (system works without delta_data)

For each test, provide:
- Input data
- Expected output
- Assertion to validate

Use pytest or unittest framework. Include fixtures for sample data.
```

### **Prompt 10.2: Validate Backward Compatibility**

```
I need to ensure that the new Delta-based implementation doesn't break existing functionality.

Validation checklist:

1. **Test with delta_data = None:**
   - System should fall back to premium-only scoring
   - All existing behavior should remain unchanged
   - Verify no errors or warnings are thrown

2. **Test with partial Delta data:**
   - Some rows have Delta, some have None
   - Verify mixed confidence levels (HIGH and MEDIUM)
   - Ensure scoring works correctly for both types

3. **Test existing UI features:**
   - Options grid still displays correctly
   - All columns are preserved (Strike, Expiry, Premium, etc.)
   - Filtering and sorting still work
   - No visual regressions

4. **Test data flow:**
   - Agent 1 → Agent 2 → UI pipeline intact
   - Data format consistency maintained
   - No breaking changes in function signatures (except new optional params)

5. **Performance validation:**
   - No significant slowdown in processing time
   - DataFrame operations optimized (no unnecessary loops)
   - UI remains responsive

Create a test script that:
- Runs all existing tests (if any)
- Runs new tests for Delta-based features
- Generates a report showing all tests passed
- Highlights any regressions or failures

Document any breaking changes (there should be none if implemented correctly).
```

---

## **Bonus: Advanced Prompts for Future Enhancements**

### **Bonus 1: Add Logging and Debugging**

```
Add comprehensive logging to the Agent 2 Part 2 implementation for better debugging and monitoring.

Requirements:
1. Import Python's logging module
2. Add log statements at key decision points:
   - "Merging premium and delta data: X rows"
   - "Filtered expired options: Y options remaining"
   - "Top scored option: Strike=XX, Expiry=YY, Score=ZZ"
   - "Primary selected: Week X"
   - "Secondary search: Week 1/2 detected, looking for secondary..."
   - "Secondary found/not found"
   - "Contract allocation: Primary=X, Secondary=Y, Buffer=Z"
   - "Total income calculated: $XXX"

3. Use appropriate log levels:
   - INFO: Normal workflow steps
   - DEBUG: Detailed data (scores, calculations)
   - WARNING: Edge cases (all deltas missing, no valid options)
   - ERROR: Unexpected failures

4. Make logging configurable (enable/disable via config or environment variable)

This will help troubleshoot issues in production and understand system behavior.
```

### **Bonus 2: Add Configuration Management**

```
Create a configuration system for Agent 2 Part 2 to make business rules easily adjustable without code changes.

Create a config file (YAML or JSON) with:

scoring:
  delta_missing_value: 0  # Treat None as 0
  confidence_high_threshold: "delta_present"
  confidence_medium_threshold: "delta_missing"

secondary_trade:
  enabled: true
  week_threshold: 2  # Look for secondary if primary week <= 2
  min_days_gap: 7    # Minimum days between primary and secondary

contract_allocation:
  buffer_threshold: 3     # Apply buffer if contracts >= 3
  buffer_amount: 1        # Keep 1 contract as buffer
  min_contracts_per_trade: 1

income:
  shares_per_contract: 100
  currency_symbol: "$"
  decimal_places: 2

Load this config in the code and use these values instead of hardcoded numbers.
This allows business users to adjust rules without developer involvement.
```

---

## **Usage Instructions**

### **How to Use These Prompts:**

1. **Sequential Execution:** Use prompts in order (Phase 1 → Phase 10) for systematic implementation
2. **Context Provision:** Always provide the AI with access to the current file content before using a prompt
3. **Customization:** Adjust prompts based on your specific codebase structure or naming conventions
4. **Testing After Each Phase:** Run tests after completing each phase before moving to the next
5. **Documentation:** Update code comments and docstrings as you implement each function

### **AI Assistant Compatibility:**

These prompts are designed to work with:
- ✅ GitHub Copilot Chat
- ✅ ChatGPT (GPT-4 or GPT-3.5)
- ✅ Claude (Anthropic)
- ✅ Any coding-focused AI assistant

### **Best Practices:**

- **One Phase at a Time:** Don't rush through all prompts at once
- **Review Generated Code:** Always review and test AI-generated code before committing
- **Iterative Refinement:** If the output isn't perfect, refine the prompt with more specific details
- **Keep Context:** Provide the AI with relevant file content and previous outputs for better results
- **Test Thoroughly:** Use the testing prompts (Phase 10) to validate each implementation

---

## **Troubleshooting Common Issues**

### **Issue 1: AI generates incorrect scoring formula**
**Solution:** Re-prompt with explicit formula: "The formula MUST be: Score = Premium × (1 - Delta), not Premium - Delta or any other variation"

### **Issue 2: Week calculation is wrong**
**Solution:** Provide examples in the prompt: "Week 1 is days 1-7, Week 2 is days 8-14, etc. Test with Dec 6 (day 6) should return 1"

### **Issue 3: Secondary logic not working**
**Solution:** Clarify the 7-day gap requirement: "The secondary expiry must be >= (primary expiry + 7 days), not just any later date"

### **Issue 4: Contract allocation doesn't match examples**
**Solution:** Provide exact numerical examples in the prompt and ask AI to verify its logic against them

### **Issue 5: UI integration breaks existing features**
**Solution:** Emphasize backward compatibility: "All existing UI features must remain unchanged. Only ADD new features, don't modify existing ones"

---

## **Document Maintenance**

- **Last Updated:** November 4, 2025
- **Version:** 1.0
- **Maintained By:** Development Team
- **Review Cycle:** Update after each major feature addition or business rule change

**Changelog:**
- v1.0 (Nov 4, 2025): Initial creation with all Phase 1-10 prompts, bonus prompts, and troubleshooting guide

