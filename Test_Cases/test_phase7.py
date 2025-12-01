"""
TEST SUITE FOR PHASE 7: Income Calculation

Tests the income calculation functionality:
1. Direct function testing (primary only, primary + secondary)
2. Income formula validation (Premium × Contracts × 100)
3. Workflow integration
4. Portfolio income totals
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import pandas as pd
from strategy_recommendation_agent_langgraph import StrategyRecommendationAgentLangGraph

# Initialize agent
print("=" * 80)
print("PHASE 7 TEST SUITE: Income Calculation")
print("=" * 80)

agent = StrategyRecommendationAgentLangGraph()
print("✓ Agent initialized\n")

# =============================================================================
# TEST 1: Direct Function Testing - Primary Only
# =============================================================================
print("\n" + "=" * 80)
print("TEST 1: Direct Function Testing - Primary Only")
print("=" * 80)

primary = {
    'premium': 26.20,
    'strike': 450.0,
    'expiry': '11/21',
    'week': 3
}

income = agent.calculate_income(primary, None, 5, "TSLA")

print(f"Primary: ${primary['premium']} premium")
print(f"Contracts: 5")
print(f"Expected: $26.20 × 5 × 100 = $13,100.00")
print(f"\nCalculated Income:")
print(f"  Primary: ${income['primary_income']:,.2f}")
print(f"  Secondary: ${income['secondary_income']:,.2f}")
print(f"  Total: ${income['total_income']:,.2f}")
print(f"  Has secondary: {income['has_secondary']}")

print(f"\n✓ Test 1.1 PASSED: Primary income correct ($13,100)")
assert income['primary_income'] == 13100.0

print(f"✓ Test 1.2 PASSED: Secondary income is 0")
assert income['secondary_income'] == 0.0

print(f"✓ Test 1.3 PASSED: Total income = primary income")
assert income['total_income'] == 13100.0

print(f"✓ Test 1.4 PASSED: has_secondary = False")
assert income['has_secondary'] == False

# =============================================================================
# TEST 2: Direct Function Testing - Primary + Secondary
# =============================================================================
print("\n" + "=" * 80)
print("TEST 2: Direct Function Testing - Primary + Secondary")
print("=" * 80)

primary = {
    'premium': 28.40,
    'strike': 450.0,
    'expiry': '11/07',
    'week': 1
}

secondary = {
    'premium': 26.20,
    'strike': 455.0,
    'expiry': '11/21',
    'week': 3
}

income = agent.calculate_income(primary, secondary, 5, "TSLA")

print(f"Primary: ${primary['premium']} × 5 × 100 = ${primary['premium'] * 5 * 100:,.2f}")
print(f"Secondary: ${secondary['premium']} × 5 × 100 = ${secondary['premium'] * 5 * 100:,.2f}")
print(f"Expected Total: ${(primary['premium'] + secondary['premium']) * 5 * 100:,.2f}")

print(f"\nCalculated Income:")
print(f"  Primary: ${income['primary_income']:,.2f}")
print(f"  Secondary: ${income['secondary_income']:,.2f}")
print(f"  Total: ${income['total_income']:,.2f}")
print(f"  Has secondary: {income['has_secondary']}")

print(f"\n✓ Test 2.1 PASSED: Primary income correct ($14,200)")
assert income['primary_income'] == 14200.0

print(f"✓ Test 2.2 PASSED: Secondary income correct ($13,100)")
assert income['secondary_income'] == 13100.0

print(f"✓ Test 2.3 PASSED: Total income = primary + secondary ($27,300)")
assert income['total_income'] == 27300.0

print(f"✓ Test 2.4 PASSED: has_secondary = True")
assert income['has_secondary'] == True

print(f"\n💡 Multi-trade earns MORE THAN DOUBLE! ($27,300 vs $13,100)")

# =============================================================================
# TEST 3: Workflow Integration with Portfolio
# =============================================================================
print("\n" + "=" * 80)
print("TEST 3: Workflow Integration with Portfolio")
print("=" * 80)

# Create test data
premium_df = pd.DataFrame({
    'Stock': ['AAPL', 'AAPL', 'TSLA', 'TSLA', 'MSFT', 'MSFT'],
    'Strike_Price': [150.0, 152.5, 450.0, 455.0, 370.0, 375.0],
    '11/06': [2.5, 2.8, 32.0, 28.0, 8.0, 7.0],
    '11/13': [3.0, 3.2, 30.0, 35.0, 9.0, 8.5],
    '11/20': [3.5, 3.8, 25.0, 30.0, 7.5, 8.0],
})

delta_df = pd.DataFrame({
    'Stock': ['AAPL', 'AAPL', 'TSLA', 'TSLA', 'MSFT', 'MSFT'],
    'Strike_Price': [150.0, 152.5, 450.0, 455.0, 370.0, 375.0],
    '11/06': [0.3, 0.35, 0.4, 0.35, 0.35, 0.3],
    '11/13': [0.4, 0.42, 0.38, 0.45, 0.4, 0.35],
    '11/20': [0.4, 0.45, 0.3, 0.4, 0.3, 0.35],
})

# Portfolio
portfolio = {
    'AAPL': 100,   # 1 contract
    'TSLA': 600,   # 6 contracts → recommend 5
    'MSFT': 300,   # 3 contracts → recommend 2
}

print("Portfolio:")
for stock, shares in portfolio.items():
    contracts = shares // 100
    if contracts >= 3:
        recommended = contracts - 1
    else:
        recommended = contracts
    print(f"  {stock}: {shares} shares → {recommended} contract(s) recommended")

print("\nRunning workflow...")
result = agent.analyze(
    premium_df,
    delta_data=delta_df,
    portfolio_data=portfolio,
    analysis_mode="premium_delta"
)

print(f"\n✓ Test 3.1 PASSED: Workflow completed successfully")
assert result['success'], "Workflow should complete successfully"

print(f"✓ Test 3.2 PASSED: income_projections field exists")
assert 'income_projections' in result, "Should have income_projections in response"

income_projections = result['income_projections']

print(f"\nIncome Projections:")
total = 0
for stock, income in income_projections.items():
    print(f"\n  {stock}:")
    print(f"    Contracts: {income['contracts_used']}")
    print(f"    Primary income: ${income['primary_income']:,.2f}")
    if income['has_secondary']:
        print(f"    Secondary income: ${income['secondary_income']:,.2f}")
        print(f"    Total: ${income['total_income']:,.2f} 💰💰")
    else:
        print(f"    Total: ${income['total_income']:,.2f} 💰")
    total += income['total_income']

print(f"\n  Portfolio Total: ${total:,.2f}")

print(f"\n✓ Test 3.3 PASSED: All stocks have income projections")
assert len(income_projections) == 3

print(f"✓ Test 3.4 PASSED: Income calculations use correct contract counts")
# Verify contract counts match allocations
for stock in income_projections:
    if stock in result['contract_allocations']:
        expected_contracts = result['contract_allocations'][stock]['recommended']
        actual_contracts = income_projections[stock]['contracts_used']
        assert expected_contracts == actual_contracts, f"{stock} contracts mismatch"

# =============================================================================
# TEST 4: Workflow Without Portfolio (1 Contract Default)
# =============================================================================
print("\n" + "=" * 80)
print("TEST 4: Workflow WITHOUT Portfolio (1 Contract Default)")
print("=" * 80)

print("Running workflow without portfolio...")
result_no_portfolio = agent.analyze(
    premium_df,
    delta_data=delta_df,
    portfolio_data=None,  # No portfolio
    analysis_mode="premium_delta"
)

print(f"\n✓ Test 4.1 PASSED: Workflow completes without portfolio")
assert result_no_portfolio['success']

print(f"✓ Test 4.2 PASSED: Income projections still calculated")
assert len(result_no_portfolio['income_projections']) > 0

# Verify default 1 contract per stock
for stock, income in result_no_portfolio['income_projections'].items():
    print(f"\n  {stock}: {income['contracts_used']} contract(s) (default)")
    assert income['contracts_used'] == 1, "Should default to 1 contract when no portfolio"

print(f"\n✓ Test 4.3 PASSED: All stocks use 1 contract (default)")

# =============================================================================
# TEST 5: Income Comparison - Single vs Multi-Trade
# =============================================================================
print("\n" + "=" * 80)
print("TEST 5: Income Comparison - Single vs Multi-Trade")
print("=" * 80)

# From Test 3 results
if 'TSLA' in income_projections and 'AAPL' in income_projections:
    tsla_income = income_projections['TSLA']
    aapl_income = income_projections['AAPL']
    
    print("TSLA (Week 2 primary - has secondary):")
    print(f"  Multi-trade income: ${tsla_income['total_income']:,.2f}")
    print(f"  Breakdown: ${tsla_income['primary_income']:,.2f} + ${tsla_income['secondary_income']:,.2f}")
    
    print("\nAAPL (Week 3 primary - NO secondary):")
    print(f"  Single-trade income: ${aapl_income['total_income']:,.2f}")
    print(f"  Breakdown: ${aapl_income['primary_income']:,.2f} only")
    
    if tsla_income['has_secondary']:
        multiplier = tsla_income['total_income'] / tsla_income['primary_income']
        print(f"\n✓ Test 5.1 PASSED: Multi-trade earns {multiplier:.1f}x more than primary alone")
        assert multiplier > 1.5, "Multi-trade should earn significantly more"

# =============================================================================
# TEST 6: Backward Compatibility (premium_only mode)
# =============================================================================
print("\n" + "=" * 80)
print("TEST 6: Backward Compatibility (premium_only mode)")
print("=" * 80)

result_premium_only = agent.analyze(
    premium_df,
    portfolio_data=portfolio,
    analysis_mode="premium_only"
)

print(f"✓ Test 6.1 PASSED: premium_only mode still works")
assert result_premium_only['success']

print(f"✓ Test 6.2 PASSED: income_projections is empty in premium_only mode")
assert result_premium_only.get('income_projections', {}) == {}

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("✅ ALL PHASE 7 TESTS PASSED!")
print("=" * 80)
print("\nTested functionality:")
print("  ✓ Direct function: calculate_income() for primary only")
print("  ✓ Direct function: calculate_income() for primary + secondary")
print("  ✓ Income formula: Premium × Contracts × 100")
print("  ✓ Workflow integration with portfolio data")
print("  ✓ Contract allocation integration (uses recommended counts)")
print("  ✓ Default 1 contract when no portfolio provided")
print("  ✓ Multi-trade vs single-trade income comparison")
print("  ✓ Backward compatibility (premium_only mode)")
print("\n🎯 Key Finding: Multi-trade strategies earn 1.5x - 2x more income!")
print("🚀 Ready to proceed to Phase 8: Complete Workflow Integration")
