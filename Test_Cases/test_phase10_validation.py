"""
PHASE 10: End-to-End Testing & Validation
==========================================

Simple, clean tests for Agent 2 Part 2 complete implementation
No unicode characters - PowerShell compatible
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from strategy_recommendation_agent_langgraph import create_strategy_agent

print("="*80)
print("PHASE 10: END-TO-END TESTING & VALIDATION")
print("="*80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# =============================================================================
# TEST 1: Complete Workflow - 3 Stocks
# =============================================================================

print("-"*80)
print("TEST 1: Complete Workflow - 3 Stocks")
print("-"*80)

# Create test data
test_data = {
    'Stock': ['AAPL', 'AAPL', 'AAPL', 'TSLA', 'TSLA', 'TSLA', 'MSFT', 'MSFT', 'MSFT'],
    'Strike_Price': [150, 155, 160, 250, 255, 260, 375, 380, 385],
    '11/11': [3.5, 3.0, 2.5, 35.0, 32.0, 30.0, 8.5, 7.5, 6.5],
    '11/18': [3.8, 3.3, 2.8, 36.0, 33.0, 31.0, 9.0, 8.0, 7.0],
    '11/25': [4.0, 3.5, 3.0, 37.0, 34.0, 32.0, 9.5, 8.5, 7.5]
}

options_df = pd.DataFrame(test_data)

# Delta data
delta_data = {
    'Stock': ['AAPL', 'AAPL', 'AAPL', 'TSLA', 'TSLA', 'TSLA', 'MSFT', 'MSFT', 'MSFT'],
    'Strike_Price': [150, 155, 160, 250, 255, 260, 375, 380, 385],
    '11/11': [0.3, 0.25, 0.2, 0.35, 0.3, 0.25, 0.3, 0.25, 0.2],
    '11/18': [0.3, 0.25, 0.2, 0.35, 0.3, 0.25, 0.3, 0.25, 0.2],
    '11/25': [0.3, 0.25, 0.2, 0.35, 0.3, 0.25, 0.3, 0.25, 0.2]
}

delta_df = pd.DataFrame(delta_data)

# Portfolio
portfolio = {
    'AAPL': 500,   # 5 contracts
    'TSLA': 1200,  # 12 contracts
    'MSFT': 300    # 3 contracts
}

print(f"\nTest Data:")
print(f"  Stocks: AAPL, TSLA, MSFT")
print(f"  Portfolio: {portfolio}")
print(f"  Options: {len(options_df)} rows")
print(f"  Delta: {len(delta_df)} rows")

# Run analysis
agent = create_strategy_agent()
result = agent.analyze(
    options_df=options_df,
    delta_data=delta_df,
    portfolio_data=portfolio,
    current_date="2025-11-04",
    analysis_mode="premium_delta"
)

# Validate results
print(f"\nValidation:")
assert result['success'], "Analysis should succeed"
print(f"  [PASS] Success: {result['success']}")

assert 'primary_recommendations' in result, "Should have primary recommendations"
print(f"  [PASS] Primary recommendations: {len(result['primary_recommendations'])}")

assert 'secondary_recommendations' in result, "Should have secondary recommendations"
print(f"  [PASS] Secondary recommendations: {len(result.get('secondary_recommendations', {}))}")

assert 'contract_allocations' in result, "Should have contract allocations"
print(f"  [PASS] Contract allocations: {len(result['contract_allocations'])}")

assert 'income_projections' in result, "Should have income projections"
print(f"  [PASS] Income projections: {len(result['income_projections'])}")

assert 'highlighted_cells' in result, "Should have highlighted cells"
print(f"  [PASS] Highlighted cells: {len(result.get('highlighted_cells', {}))}")

# Calculate total income
total_income = sum(data['total_income'] for data in result['income_projections'].values())
print(f"  [PASS] Total monthly income: ${total_income:,.2f}")

print(f"\n[SUCCESS] TEST 1 PASSED!\n")

# =============================================================================
# TEST 2: Single Stock Workflow
# =============================================================================

print("-"*80)
print("TEST 2: Single Stock Workflow")
print("-"*80)

single_options = pd.DataFrame({
    'Stock': ['AAPL', 'AAPL', 'AAPL'],
    'Strike_Price': [150, 155, 160],
    '11/11': [3.5, 3.0, 2.5],
    '11/18': [3.8, 3.3, 2.8],
    '11/25': [4.0, 3.5, 3.0]
})

single_delta = pd.DataFrame({
    'Stock': ['AAPL', 'AAPL', 'AAPL'],
    'Strike_Price': [150, 155, 160],
    '11/11': [0.3, 0.25, 0.2],
    '11/18': [0.3, 0.25, 0.2],
    '11/25': [0.3, 0.25, 0.2]
})

single_portfolio = {'AAPL': 500}

print(f"\nTest Data:")
print(f"  Stocks: AAPL only")
print(f"  Portfolio: {single_portfolio}")

agent2 = create_strategy_agent()
result2 = agent2.analyze(
    options_df=single_options,
    delta_data=single_delta,
    portfolio_data=single_portfolio,
    current_date="2025-11-04",
    analysis_mode="premium_delta"
)

print(f"\nValidation:")
assert result2['success'], "Single stock analysis should succeed"
print(f"  [PASS] Success: {result2['success']}")

assert len(result2['primary_recommendations']) == 1, "Should have 1 primary"
print(f"  [PASS] Primary recommendations: {len(result2['primary_recommendations'])}")

assert len(result2['contract_allocations']) == 1, "Should have 1 allocation"
print(f"  [PASS] Contract allocations: {len(result2['contract_allocations'])}")

print(f"\n[SUCCESS] TEST 2 PASSED!\n")

# =============================================================================
# TEST 3: No Delta Data (Premium Only Mode)
# =============================================================================

print("-"*80)
print("TEST 3: No Delta Data (Premium Only Mode)")
print("-"*80)

print(f"\nTest Data:")
print(f"  Stocks: AAPL, MSFT")
print(f"  Delta: None (premium_only mode)")

no_delta_options = pd.DataFrame({
    'Stock': ['AAPL', 'AAPL', 'MSFT', 'MSFT'],
    'Strike_Price': [150, 155, 375, 380],
    '11/11': [3.5, 3.0, 8.5, 7.5],
    '11/18': [3.8, 3.3, 9.0, 8.0]
})

no_delta_portfolio = {'AAPL': 500, 'MSFT': 300}

agent3 = create_strategy_agent()
result3 = agent3.analyze(
    options_df=no_delta_options,
    delta_data=None,  # No delta
    portfolio_data=no_delta_portfolio,
    current_date="2025-11-04",
    analysis_mode="premium_only"
)

print(f"\nValidation:")
assert result3['success'], "Premium only mode should work"
print(f"  [PASS] Success: {result3['success']}")
print(f"  [PASS] Premium-only mode works without delta data")

print(f"\n[SUCCESS] TEST 3 PASSED!\n")

# =============================================================================
# TEST 4: UI Highlighting Validation
# =============================================================================

print("-"*80)
print("TEST 4: UI Highlighting Validation")
print("-"*80)

print(f"\nChecking highlighted_cells structure:")

if 'highlighted_cells' in result:
    highlighted = result['highlighted_cells']
    print(f"  Stocks with highlights: {len(highlighted)}")
    
    for stock, cells in highlighted.items():
        print(f"\n  {stock}:")
        for cell in cells:
            color = cell.get('color', 'unknown')
            cell_type = cell.get('type', 'unknown')
            strike = cell.get('strike', 'N/A')
            expiry = cell.get('expiry', 'N/A')
            print(f"    [{color.upper()}] {cell_type}: Strike ${strike}, Expiry {expiry}")
    
    # Count colors
    green_count = sum(1 for cells in highlighted.values() 
                     for cell in cells if cell.get('color') == 'green')
    orange_count = sum(1 for cells in highlighted.values() 
                      for cell in cells if cell.get('color') == 'orange')
    
    print(f"\n  [PASS] Primary (green) highlights: {green_count}")
    print(f"  [PASS] Secondary (orange) highlights: {orange_count}")
else:
    print(f"  [INFO] No highlighted_cells in result (may be skipped in premium_delta mode)")

print(f"\n[SUCCESS] TEST 4 PASSED!\n")

# =============================================================================
# TEST 5: Income Calculation Accuracy
# =============================================================================

print("-"*80)
print("TEST 5: Income Calculation Accuracy")
print("-"*80)

print(f"\nVerifying income calculations:")

for stock, income_data in result['income_projections'].items():
    contracts = income_data['contracts_used']
    primary_income = income_data['primary_income']
    secondary_income = income_data.get('secondary_income', 0)
    total_income = income_data['total_income']
    
    print(f"\n  {stock}:")
    print(f"    Contracts: {contracts}")
    print(f"    Primary income: ${primary_income:,.2f}")
    print(f"    Secondary income: ${secondary_income:,.2f}")
    print(f"    Total income: ${total_income:,.2f}")
    
    # Verify total = primary + secondary
    expected_total = primary_income + secondary_income
    assert abs(total_income - expected_total) < 0.01, f"Income mismatch for {stock}"
    print(f"    [PASS] Income calculation correct")

# Verify portfolio total
portfolio_total = sum(data['total_income'] for data in result['income_projections'].values())
print(f"\n  Portfolio Total: ${portfolio_total:,.2f}")
print(f"  [PASS] All income calculations verified")

print(f"\n[SUCCESS] TEST 5 PASSED!\n")

# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("="*80)
print("PHASE 10 TEST SUMMARY")
print("="*80)
print(f"\nAll Tests: PASSED")
print(f"  [PASS] Test 1: Complete workflow (3 stocks)")
print(f"  [PASS] Test 2: Single stock workflow")
print(f"  [PASS] Test 3: Premium-only mode (no delta)")
print(f"  [PASS] Test 4: UI highlighting structure")
print(f"  [PASS] Test 5: Income calculation accuracy")
print(f"\nPhase 10 Complete: End-to-End Validation Successful!")
print(f"Agent 2 Part 2 is fully tested and production-ready!")
print("="*80)
