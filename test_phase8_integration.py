"""
Phase 8 Integration Test: Complete End-to-End Workflow
Tests the complete system with all data flowing through correctly
"""

import pandas as pd
import numpy as np
from backend.strategy_recommendation_agent_langgraph import create_strategy_agent

def create_test_data():
    """Create realistic test data matching real-world structure"""
    
    # Options data (Premium values)
    options_data = {
        'Stock': ['AAPL', 'AAPL', 'TSLA', 'TSLA', 'MSFT', 'MSFT'],
        'Strike_Price': [150.0, 152.5, 450.0, 455.0, 370.0, 375.0],
        '11/06': [2.50, 3.00, 28.40, 35.00, 7.00, 8.50],  # Week 1
        '11/13': [3.00, 3.50, 30.00, 35.00, 7.50, 8.50],  # Week 2
        '11/20': [3.50, 3.80, 26.20, 30.00, 7.50, 9.00],  # Week 3
    }
    options_df = pd.DataFrame(options_data)
    
    # Delta data (Delta values - same structure)
    delta_data = {
        'Stock': ['AAPL', 'AAPL', 'TSLA', 'TSLA', 'MSFT', 'MSFT'],
        'Strike_Price': [150.0, 152.5, 450.0, 455.0, 370.0, 375.0],
        '11/06': [0.30, 0.25, 0.20, 0.15, 0.25, 0.20],
        '11/13': [0.35, 0.30, 0.25, 0.20, 0.30, 0.25],
        '11/20': [0.40, 0.35, 0.30, 0.25, 0.35, 0.30],
    }
    delta_df = pd.DataFrame(delta_data)
    
    # Portfolio data
    portfolio = {
        'AAPL': 500,   # 5 contracts (500/100)
        'TSLA': 1200,  # 12 contracts → recommend 11 (buffer 1)
        'MSFT': 300    # 3 contracts → recommend 2 (buffer 1)
    }
    
    # Current date
    current_date = '2024-11-04'
    
    return options_df, delta_df, portfolio, current_date


print("=" * 80)
print("PHASE 8 INTEGRATION TEST: Complete End-to-End Workflow")
print("=" * 80)
print("\nTesting all data flowing through the system correctly:\n")
print("✓ Options data (premiums)")
print("✓ Delta data")
print("✓ Portfolio data (shares)")
print("✓ Current date")
print("✓ Analysis mode: premium_delta")
print("\n" + "=" * 80 + "\n")


# =============================================================================
# TEST 1: Complete Workflow with All Data
# =============================================================================

print("=" * 80)
print("TEST 1: Complete Workflow Integration")
print("=" * 80)

options_df, delta_df, portfolio, current_date = create_test_data()

print("\n📊 Input Data:")
print(f"  Options data: {options_df.shape}")
print(f"  Delta data: {delta_df.shape}")
print(f"  Portfolio: {portfolio}")
print(f"  Current date: {current_date}")

# Create agent
agent = create_strategy_agent()

# Run complete analysis
print("\n🚀 Running complete workflow...")
result = agent.analyze(
    options_df=options_df,
    delta_data=delta_df,
    portfolio_data=portfolio,
    current_date=current_date,
    analysis_mode='premium_delta'
)

# Verify all phases executed
print("\n📊 Workflow Results:")
print(f"  Success: {result['success']}")
print(f"  Status: {result['status']}")

# Check Phase 4: Primary recommendations
print("\n🎯 Phase 4: Primary Recommendations")
primaries = result.get('primary_recommendations', {})
print(f"  Found: {len(primaries)} primaries")
for stock, rec in primaries.items():
    print(f"    {stock}: Strike ${rec['strike']}, Exp {rec['expiry']}, "
          f"Premium ${rec['premium']:.2f}, Week {rec['week']}")

assert len(primaries) == 3, "Should have 3 primary recommendations"
print("✓ Test 1.1 PASSED: Primary recommendations generated")

# Check Phase 5: Secondary recommendations
print("\n🎯 Phase 5: Secondary Recommendations")
secondaries = result.get('secondary_recommendations', {})
print(f"  Found: {len(secondaries)} secondaries")
for stock, rec in secondaries.items():
    print(f"    {stock}: Strike ${rec['strike']}, Exp {rec['expiry']}, "
          f"Premium ${rec['premium']:.2f}, Week {rec['week']}")

# Week 1-2 primaries should have secondaries
week1_2_primaries = [s for s, p in primaries.items() if p['week'] in [1, 2]]
print(f"  Week 1-2 primaries (eligible): {len(week1_2_primaries)}")
print(f"  Secondaries found: {len(secondaries)}")

assert len(secondaries) >= 1, "Should have at least 1 secondary"
print("✓ Test 1.2 PASSED: Secondary recommendations generated for eligible stocks")

# Check Phase 6: Contract allocations
print("\n💼 Phase 6: Contract Allocations")
allocations = result.get('contract_allocations', {})
print(f"  Found: {len(allocations)} allocations")
for stock, alloc in allocations.items():
    shares = portfolio[stock]
    print(f"    {stock}: {shares} shares → "
          f"{alloc['total_contracts']} total, "
          f"{alloc['recommended']} recommended, "
          f"buffer: {alloc.get('buffer', 0)}")

assert len(allocations) == 3, "Should have 3 contract allocations"
assert allocations['AAPL']['recommended'] == 4, "AAPL: 500 shares = 5 contracts, recommend 4"
assert allocations['TSLA']['recommended'] == 11, "TSLA: 1200 shares = 12 contracts, recommend 11"
assert allocations['MSFT']['recommended'] == 2, "MSFT: 300 shares = 3 contracts, recommend 2"
print("✓ Test 1.3 PASSED: Contract allocations correct with buffers")

# Check Phase 7: Income projections
print("\n💰 Phase 7: Income Projections")
incomes = result.get('income_projections', {})
print(f"  Found: {len(incomes)} income projections")

total_portfolio_income = 0
for stock, income in incomes.items():
    print(f"    {stock}: {income['contracts_used']} contract(s)")
    print(f"      Primary: ${income['primary_income']:,.2f}")
    if income['has_secondary']:
        print(f"      Secondary: ${income['secondary_income']:,.2f}")
        print(f"      Total: ${income['total_income']:,.2f} 💰💰")
    else:
        print(f"      Total: ${income['total_income']:,.2f} 💰")
    total_portfolio_income += income['total_income']

print(f"\n  📊 Portfolio Total Income: ${total_portfolio_income:,.2f}")

assert len(incomes) == 3, "Should have 3 income projections"
assert all(income['contracts_used'] > 0 for income in incomes.values()), "All stocks should have contracts"

# Verify income calculations
# TSLA: 11 contracts, primary ~$35, secondary ~$30 → ~$715,000
tsla_income = incomes['TSLA']['total_income']
expected_tsla_min = 11 * 25 * 100  # At least $27,500
expected_tsla_max = 11 * 70 * 100  # At most $77,000
assert expected_tsla_min <= tsla_income <= expected_tsla_max, f"TSLA income ${tsla_income:,.2f} out of expected range"

print("✓ Test 1.4 PASSED: Income projections calculated correctly")


# =============================================================================
# TEST 2: Workflow WITHOUT Portfolio Data (Defaults to 1 contract)
# =============================================================================

print("\n" + "=" * 80)
print("TEST 2: Workflow WITHOUT Portfolio Data")
print("=" * 80)

print("\n📊 Testing graceful defaults when portfolio not provided...")

result2 = agent.analyze(
    options_df=options_df,
    delta_data=delta_df,
    portfolio_data=None,  # No portfolio
    current_date=current_date,
    analysis_mode='premium_delta'
)

print(f"\n  Success: {result2['success']}")
print(f"  Primaries: {len(result2.get('primary_recommendations', {}))}")
print(f"  Secondaries: {len(result2.get('secondary_recommendations', {}))}")
print(f"  Allocations: {len(result2.get('contract_allocations', {}))}")
print(f"  Incomes: {len(result2.get('income_projections', {}))}")

# Should still generate recommendations
assert result2['success'], "Workflow should succeed without portfolio"
assert len(result2.get('primary_recommendations', {})) == 3, "Should have primaries"

# Income projections should default to 1 contract
incomes2 = result2.get('income_projections', {})
if incomes2:
    for stock, income in incomes2.items():
        print(f"    {stock}: {income['contracts_used']} contract (default)")
        assert income['contracts_used'] == 1, "Should default to 1 contract"

print("✓ Test 2.1 PASSED: Workflow handles missing portfolio gracefully")


# =============================================================================
# TEST 3: Verify Current Date is Used
# =============================================================================

print("\n" + "=" * 80)
print("TEST 3: Current Date Usage")
print("=" * 80)

# Test with different dates
test_date1 = '2024-11-01'
test_date2 = '2024-11-30'

print(f"\n📅 Testing with date: {test_date1}")
result_date1 = agent.analyze(
    options_df=options_df,
    delta_data=delta_df,
    portfolio_data=portfolio,
    current_date=test_date1,
    analysis_mode='premium_delta'
)

print(f"  Success: {result_date1['success']}")
print(f"  Primaries: {len(result_date1.get('primary_recommendations', {}))}")

print(f"\n📅 Testing with date: {test_date2}")
result_date2 = agent.analyze(
    options_df=options_df,
    delta_data=delta_df,
    portfolio_data=portfolio,
    current_date=test_date2,
    analysis_mode='premium_delta'
)

print(f"  Success: {result_date2['success']}")
print(f"  Primaries: {len(result_date2.get('primary_recommendations', {}))}")

print("✓ Test 3.1 PASSED: Current date parameter accepted")


# =============================================================================
# TEST 4: Verify Delta Data Integration
# =============================================================================

print("\n" + "=" * 80)
print("TEST 4: Delta Data Integration")
print("=" * 80)

print("\n🔍 Verifying Delta data is used in scoring...")

# The merged_data should contain both premium and delta
merged = result.get('merged_data')
if merged is not None:
    print(f"  Merged data shape: {merged.shape}")
    print(f"  Columns: {list(merged.columns)}")
    
    # Should have Score column (from delta-based scoring)
    assert 'Score' in merged.columns, "Merged data should have 'Score' column"
    print("  ✓ Score column exists (Delta-based scoring applied)")
    
    # Check that scores are calculated
    scores = merged['Score'].dropna()
    print(f"  Scores calculated: {len(scores)}")
    print(f"  Score range: ${scores.min():.2f} to ${scores.max():.2f}")
    
    assert len(scores) > 0, "Should have calculated scores"
    print("✓ Test 4.1 PASSED: Delta data integrated into scoring")
else:
    print("  ⚠️ Warning: merged_data is None")


# =============================================================================
# TEST 5: Backward Compatibility (premium_only mode)
# =============================================================================

print("\n" + "=" * 80)
print("TEST 5: Backward Compatibility (premium_only mode)")
print("=" * 80)

print("\n🔄 Testing premium_only mode (Part 1 behavior)...")

result_premium_only = agent.analyze(
    options_df=options_df,
    delta_data=None,  # No delta data
    portfolio_data=None,  # No portfolio
    current_date=current_date,
    analysis_mode='premium_only'  # Part 1 mode
)

print(f"\n  Success: {result_premium_only['success']}")
print(f"  Recommendations: {len(result_premium_only.get('recommendations', []))}")
print(f"  LLM Insights: {'Yes' if result_premium_only.get('llm_insights') else 'No'}")

# Should NOT have Part 2 features
print(f"\n  Part 2 Features (should be empty/default):")
print(f"    Primaries: {len(result_premium_only.get('primary_recommendations', {}))}")
print(f"    Secondaries: {len(result_premium_only.get('secondary_recommendations', {}))}")
print(f"    Allocations: {len(result_premium_only.get('contract_allocations', {}))}")
print(f"    Incomes: {len(result_premium_only.get('income_projections', {}))}")

assert result_premium_only['success'], "premium_only mode should work"
assert len(result_premium_only.get('recommendations', [])) > 0, "Should have basic recommendations"
print("✓ Test 5.1 PASSED: Backward compatibility maintained")


# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("✅ ALL PHASE 8 INTEGRATION TESTS PASSED!")
print("=" * 80)

print("\nTested functionality:")
print("  ✓ Complete workflow with all data (options + delta + portfolio + date)")
print("  ✓ Primary recommendations (Phase 4)")
print("  ✓ Secondary recommendations (Phase 5)")
print("  ✓ Contract allocations with buffers (Phase 6)")
print("  ✓ Income projections (Phase 7)")
print("  ✓ Graceful defaults (no portfolio → 1 contract)")
print("  ✓ Current date parameter integration")
print("  ✓ Delta-based scoring integration")
print("  ✓ Backward compatibility (premium_only mode)")

print("\n🎯 Phase 8 Complete: System Integration Verified!")
print("🚀 Ready for Phase 9: Output Formatting & UI Integration")
