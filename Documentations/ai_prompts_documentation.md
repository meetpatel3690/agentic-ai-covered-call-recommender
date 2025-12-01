# 📝 **Natural Language Prompts for AI-Generated Functions**

*Documentation of prompts provided by Meet Patel  to AI Assistant*

---

## 🎯 **PURPOSE**

This document contains the exact natural language prompts that Meet Patel provided to the AI Assistant (GitHub Copilot) to generate specific functions. These prompts demonstrate that all AI-generated code was based on Meet's detailed specifications and requirements.

---

## 🤖 **AI-GENERATED FUNCTIONS WITH ORIGINAL PROMPTS**

### **1. `llm_parse_and_convert_node()` Function**

**Meet Patel's Prompt:**
```
"I need a function that takes user input like 'Apple, Tesla Motors, Microsoft' and uses OpenAI's LLM to intelligently convert company names to stock ticker symbols. The function should:

1. Send a detailed prompt to the LLM asking it to parse the input and convert company names to tickers
2. The LLM should return a JSON response with the conversion results
3. Handle cases where input is already a ticker vs company name
4. Extract the JSON from the LLM response and save the results to the state
5. Include fallback parsing if LLM fails (simple comma splitting)
6. Add proper error handling for API failures
7. Track the conversation messages for logging
8. Set a default analysis date if none provided

The function should be robust and handle both perfect LLM responses and edge cases where the AI doesn't return proper JSON."
```

**Expected Output:** Function that uses LLM for intelligent company name to ticker conversion with JSON parsing and fallback mechanisms.

---

### **2. `llm_format_options_matrix_node()` Function**

**Meet Patel's Prompt:**
```
"I need a complex function that takes raw options data from Alpha Vantage and creates a clean 6×6 matrix for covered call analysis. The requirements are:

1. Filter only call options (not puts) with strikes above current stock price
2. Select exactly 6 strikes - the lowest 6 strikes above current price
3. Select exactly 6 expiration dates - the next 6 Fridays from today
4. Create a matrix where rows are strikes and columns are expiration dates
5. Fill each cell with the option premium (use bid price, fallback to mark, then ask)
6. Handle multiple stocks by creating separate 6×6 sections for each
7. Include current stock price in the first row
8. Format dates as MM/DD/YY
9. Format strikes and premiums to 2 decimal places
10. Handle cases where no option exists for a strike/date combination
11. Return everything as a clean pandas DataFrame

The function should be highly optimized for covered call strategies and handle real-world data inconsistencies."
```

**Expected Output:** Sophisticated data processing function that creates structured 6×6 options premium matrices.

---

### **3. `llm_generate_analysis_node()` Function**

**Meet Patel's Prompt:**
```
"I need a function that sends the 6×6 options matrix to OpenAI's LLM and gets professional trading analysis. The function should:

1. Create a detailed prompt for the LLM that includes the options matrix and current stock prices
2. Ask the LLM to analyze the data as a professional options trader
3. Request specific analysis on:
   - Premium levels (high/low/fair assessment)
   - Most attractive strikes for covered calls
   - Time decay patterns across expirations
   - Notable patterns or opportunities
   - Risk considerations
4. Handle LLM API errors gracefully
5. Save the analysis text to the state
6. Add a success message to the conversation log

The analysis should be practical and actionable for covered call strategies."
```

**Expected Output:** Function that generates professional options trading insights using LLM analysis.

---


### **4. Enhanced `fetch_financial_data_node()` Function**

**Meet Patel's Prompt:**
```
"I have a basic fetch function, but I need AI to enhance it with:

1. Better error handling for each ticker individually
2. Skip 'UNKNOWN' tickers from failed conversions
3. Structured data storage with spot_price, options_data, and columns
4. Progress feedback showing data retrieval for each symbol
5. Graceful handling when no options data is available
6. Convert options DataFrame to dictionary format for downstream processing
7. Comprehensive error tracking in the state

Keep the basic structure I wrote but make it production-ready with professional error handling."
```

**Expected Output:** Enhanced data fetching with robust error handling and structured data storage.

---

### **5. Enhanced `analyze()` Function**

**Meet Patel's Prompt:**
```
"I need to enhance my basic analyze function with:

1. Proper state initialization with all required fields
2. Professional progress logging and status updates
3. Workflow invocation and state management
4. Comprehensive response packaging with all results
5. Success/failure determination logic
6. Professional error handling with detailed error responses
7. Clean separation of successful vs failed analysis results

The function should be the main entry point that orchestrates everything and returns a complete analysis package."
```

**Expected Output:** Professional main interface function with comprehensive state management.

---

### **6. `display_results()` Function**

**Meet Patel's Prompt:**
```
"I need a function that takes the analysis results and displays them in a beautiful, professional format with:

1. Clear section headers with emojis and formatting
2. Show the LLM conversion results (input → ticker mappings)
3. Display current market prices in a clean list
4. Show the 6×6 options matrix in table format
5. Display the LLM trading analysis and insights
6. Include a summary of what was accomplished
7. Handle error cases with clear error messages
8. Use consistent formatting with lines and separators

Make it look like a professional financial report that would impress clients."
```

**Expected Output:** Professional results display function with formatted output and visual appeal.

---


---

## 🎯 **AGENT 2: STRATEGY RECOMMENDATION SYSTEM**

*Advanced AI-Generated Functionality for Premium Analysis and Visual Highlighting*

---

### **7. `StrategyRecommendationAgent` Class - Complete Backend System**

**Meet Patel's Prompt:**
```
"I need to create Agent 2 - a Strategy Recommendation Agent that analyzes the 6×6 options grid from Agent 1. This is for tomorrow's mentor meeting demo. Requirements:

CORE FUNCTIONALITY:
1. Create a class StrategyRecommendationAgent that analyzes ALL 36 options (6 strikes × 6 dates) per stock
2. For each stock, find which option has the HIGHEST premium among all 36 options
3. Store detailed results: highest premium, strike price, expiration date, row/column for highlighting
4. Generate recommendations with strategy, strike, expiration, premium, and rationale
5. Include methods:
   - analyze_options_grid() - main analysis function
   - get_highlighted_dataframe() - prepare data for UI highlighting  
   - export_analysis_summary() - create formatted text summary

SCALABLE ARCHITECTURE (for Part 2):
6. Add a scoring_config dictionary with:
   - use_premium: True (active now)
   - use_delta: False (ready for Part 2)
   - weights: configurable weights for premium and delta
   - custom_formula: accepts mentor-approved formulas
7. Create placeholder methods ready for Part 2:
   - configure_scoring_formula() - set custom formulas
   - analyze_with_delta() - incorporate Delta values for risk analysis
   - calculate_custom_score() - apply premium + delta formula
8. Design so Part 2 just requires enabling Delta in config, no code rewrite

ERROR HANDLING:
9. Handle edge cases: empty dataframes, non-numeric values, missing columns
10. Comprehensive logging showing progress for each stock
11. Return structured dictionary format for easy UI consumption

The system must work perfectly for Part 1 demo and be ready to scale for Part 2 Wednesday."
```

**Expected Output:** Complete backend agent with analysis, recommendations, scalable architecture focused on Delta integration for Part 2.

---

### **8. UI Integration - Button, Highlighting, and User Experience**

**Meet Patel's Prompt:**
```
"I need complete UI integration for Agent 2 in Streamlit with professional UX. Requirements:

BUTTON AND INTERACTION:
1. Add button: '🎯 Run Agent 2: Strategy Recommendation'
   - Center it above the options grid
   - Make it primary type (prominent blue)
   - Disable if no options data loaded
2. On button click:
   - Show spinner: '🤖 Agent 2 is analyzing options and finding best premiums...'
   - Call Agent 2 backend
   - Store results in session state (agent2_analysis, highlighted_cells, show_highlights)
   - Show success message
   - Display expandable analysis summary

CELL HIGHLIGHTING WITH ORANGE COLOR:
3. Create highlight_max_premium() function that:
   - Takes a pandas row
   - Checks highlighted_cells dictionary for which cells to color
   - Applies ORANGE color (hex #8eeb29ff) with black text and bold font
   - Returns CSS style list for each cell
   - Format: 'background-color: #8eeb29ff; color: black; font-weight: bold'
4. Apply to dataframe using pandas .style.apply()
5. Show legend: '🟢 Green cells indicate the highest premium for each stock'

SESSION STATE AND ERROR HANDLING:
6. Initialize session state variables: agent2_analysis, highlighted_cells, show_highlights
7. Wrap in try-catch with user-friendly error messages
8. Show informative messages: warnings, success confirmations, guidance
9. Two display modes:
   - Before Agent 2: plain grid with "Click Run Agent 2" message
   - After Agent 2: styled grid with orange highlights

Make it smooth, professional, and impressive for the mentor demo."
```

**Expected Output:** Complete UI integration with button, orange highlighting (#FFA500), session state, error handling, and professional user experience.

---

### **9. Helper Function and Documentation**

**Meet Patel's Prompt:**
```
"I need two final pieces for Agent 2:

HELPER FUNCTION:
1. Create analyze_and_highlight() convenience function that:
   - Takes options dataframe as input
   - Creates StrategyRecommendationAgent instance
   - Runs analysis automatically
   - Returns tuple: (highlighted_df, analysis_results, agent_instance)
   - One-line solution for UI integration

DOCUMENTATION:
2. Add comprehensive docstrings explaining:
   - Module purpose and Agent 2 capabilities
   - Part 1 (demo) vs Part 2 (scalable) architecture
   - Class and method documentation with args/returns
   - Inline comments for complex logic
   - Attribution to Meet Patel for requirements and architecture
3. Create separate guide files:
   - AGENT_2_IMPLEMENTATION_GUIDE.md - technical details
   - DEMO_QUICK_GUIDE.md - demo script for meeting
   - QUICK_REFERENCE.md - one-page summary

Make documentation clear enough for anyone to understand and extend for Part 2."
```

**Expected Output:** Helper function for easy integration and comprehensive documentation for demo and future development.

---

## 🎯 **KEY INSIGHTS FOR MENTORS**

### **Meet Patel's Role as Prompt Engineer:**
1. **Detailed Requirements**: Every AI function had specific, detailed requirements
2. **Business Logic Specification**: All trading logic and financial rules came from Meet
3. **Error Handling Requirements**: Comprehensive error scenarios specified
4. **User Experience Design**: All UX requirements and formatting specified
5. **Integration Architecture**: How components should work together specified
6. **Scalability Planning**: Part 1 and Part 2 architecture designed upfront
7. **Visual Design Choices**: Specific color selection (Orange #FFA500) for highlighting
8. **Demo Strategy**: Clear vision for mentor meeting presentation

### **AI Assistant's Role as Implementation Engine:**
1. **Code Generation**: Converting requirements to working code
2. **Best Practices**: Applying professional coding patterns
3. **Error Handling**: Implementing robust error management
4. **Documentation**: Adding comprehensive code comments
5. **Architecture Implementation**: Building scalable, modular systems
6. **UI/UX Implementation**: Creating professional Streamlit interfaces

---

## 📊 **AGENT 2 ARCHITECTURE BREAKDOWN**

### **Part 1 (Demo-Ready):**
- ✅ Premium-based analysis (working now)
- ✅ Orange cell highlighting (#FFA500)
- ✅ Detailed recommendations
- ✅ Analysis summaries
- ✅ UI button integration
- ✅ Session state management
- ✅ Error handling and user feedback

### **Part 2 (Scalable Design):**
- 🔜 Delta analysis (code ready, needs enabling)
- 🔜 Custom scoring formulas (premium + delta weights)
- 🔜 Risk-adjusted recommendations (Delta-based)
- 🔜 Optimal Delta targeting (~0.30 for covered calls)

---

## 🎨 **COLOR SPECIFICATION DETAILS**

**Meet Patel's Color Choice for Agent 2:**
- **Color Name**: Orange
- **Hex Code**: #8eeb29ff
- **Purpose**: Highlight cells with highest premium
- **Visual Impact**: High contrast, attention-grabbing, professional
- **Accessibility**: Good readability with black text
- **Alternative Options Considered**: 
  - Green (#32CD32) - too similar to profit indicators
  - Blue (#1E90FF) - less attention-grabbing
  - Yellow (#FFD700) - hard to read text
  - Red (#FF0000) - implies danger/loss
  - **Decision**: Orange for optimal visibility and professional appearance

---

## 💡 **DEMONSTRATION**

To prove this works, any of these prompts could be given to an AI assistant and would generate similar functionality. This shows that **Meet Patel was the architect and requirements engineer** for every piece of AI-generated code.

**Example Test:**
Give the `llm_parse_and_convert_node` prompt above to any AI assistant and it will generate a function with the same core functionality, proving that the requirements and specifications came from Meet Patel.

---

*This document demonstrates that Meet Patel provided detailed specifications and requirements for every AI-generated function, maintaining full control over the system architecture and business logic.*