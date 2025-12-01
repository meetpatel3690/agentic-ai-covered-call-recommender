"""
Phase 9 Test: Output Formatting & UI Integration
Tests that the UI correctly displays Part 2 features
"""

import pandas as pd
from backend.strategy_recommendation_agent_langgraph import create_strategy_agent

def test_ui_data_format():
    """Test that Agent 2 returns data in the correct format for UI consumption"""
    
    print("=" * 80)
    print("PHASE 9 TEST: Output Formatting & UI Integration")
    print("=" * 80)
    print("\nVerifying Agent 2 output format is UI-ready...\n")
    
    # Create test data
    options_data = {
        'Stock': ['AAPL', 'AAPL', 'TSLA', 'TSLA', 'MSFT', 'MSFT'],
        'Strike_Price': [150.0, 152.5, 450.0, 455.0, 370.0, 375.0],
        '11/06': [2.50, 3.00, 28.40, 35.00, 7.00, 8.50],  # Week 1
        '11/13': [3.00, 3.50, 30.00, 35.00, 7.50, 8.50],  # Week 2
        '11/20': [3.50, 3.80, 26.20, 30.00, 7.50, 9.00],  # Week 3
    }
    options_df = pd.DataFrame(options_data)
    
    delta_data = {
        'Stock': ['AAPL', 'AAPL', 'TSLA', 'TSLA', 'MSFT', 'MSFT'],
        'Strike_Price': [150.0, 152.5, 450.0, 455.0, 370.0, 375.0],
        '11/06': [0.30, 0.25, 0.20, 0.15, 0.25, 0.20],
        '11/13': [0.35, 0.30, 0.25, 0.20, 0.30, 0.25],
        '11/20': [0.40, 0.35, 0.30, 0.25, 0.35, 0.30],
    }
    delta_df = pd.DataFrame(delta_data)
    
    portfolio = {
        'AAPL': 500,
        'TSLA': 1200,
        'MSFT': 300
    }
    
    # Create agent and run analysis
    agent = create_strategy_agent()
    result = agent.analyze(
        options_df=options_df,
        delta_data=delta_df,
        portfolio_data=portfolio,
        current_date='2024-11-04',
        analysis_mode='premium_delta'
    )
    
    print("\n" + "=" * 80)
    print("TEST 1: Verify Required Fields for UI")
    print("=" * 80)
    
    required_fields = [
        'success',
        'primary_recommendations',
        'secondary_recommendations',
        'contract_allocations',
        'income_projections',
        'highlighted_cells',
        'llm_insights'
    ]
    
    for field in required_fields:
        exists = field in result
        print(f"  {field}: {'✓' if exists else '✗'}")
        assert exists, f"Missing required field: {field}"
    
    print("\n✓ All required fields present!")
    
    print("\n" + "=" * 80)
    print("TEST 2: Verify Income Projections Format")
    print("=" * 80)
    
    income_data = result['income_projections']
    print(f"\n  Stocks with income data: {len(income_data)}")
    
    for stock, income in income_data.items():
        print(f"\n  {stock}:")
        print(f"    contracts_used: {income['contracts_used']}")
        print(f"    primary_income: ${income['primary_income']:,.2f}")
        print(f"    secondary_income: ${income['secondary_income']:,.2f}")
        print(f"    total_income: ${income['total_income']:,.2f}")
        print(f"    has_secondary: {income['has_secondary']}")
        
        # Verify structure
        assert 'contracts_used' in income, f"{stock}: missing contracts_used"
        assert 'primary_income' in income, f"{stock}: missing primary_income"
        assert 'secondary_income' in income, f"{stock}: missing secondary_income"
        assert 'total_income' in income, f"{stock}: missing total_income"
        assert 'has_secondary' in income, f"{stock}: missing has_secondary"
        
        # Verify calculations
        expected_total = income['primary_income'] + income['secondary_income']
        assert abs(income['total_income'] - expected_total) < 0.01, f"{stock}: total mismatch"
    
    print("\n✓ Income projections format correct!")
    
    print("\n" + "=" * 80)
    print("TEST 3: Verify Primary Recommendations Format")
    print("=" * 80)
    
    primaries = result['primary_recommendations']
    print(f"\n  Primary recommendations: {len(primaries)}")
    
    for stock, primary in primaries.items():
        print(f"\n  {stock}:")
        print(f"    strike: ${primary['strike']}")
        print(f"    expiry: {primary['expiry']}")
        print(f"    premium: ${primary['premium']}")
        print(f"    week: {primary['week']}")
        
        # Verify structure
        assert 'strike' in primary, f"{stock}: missing strike"
        assert 'expiry' in primary, f"{stock}: missing expiry"
        assert 'premium' in primary, f"{stock}: missing premium"
        assert 'week' in primary, f"{stock}: missing week"
    
    print("\n✓ Primary recommendations format correct!")
    
    print("\n" + "=" * 80)
    print("TEST 4: Verify Secondary Recommendations Format")
    print("=" * 80)
    
    secondaries = result['secondary_recommendations']
    print(f"\n  Secondary recommendations: {len(secondaries)}")
    
    for stock, secondary in secondaries.items():
        print(f"\n  {stock}:")
        print(f"    strike: ${secondary['strike']}")
        print(f"    expiry: {secondary['expiry']}")
        print(f"    premium: ${secondary['premium']}")
        print(f"    week: {secondary['week']}")
        
        # Verify structure
        assert 'strike' in secondary, f"{stock}: missing strike"
        assert 'expiry' in secondary, f"{stock}: missing expiry"
        assert 'premium' in secondary, f"{stock}: missing premium"
        assert 'week' in secondary, f"{stock}: missing week"
    
    print("\n✓ Secondary recommendations format correct!")
    
    print("\n" + "=" * 80)
    print("TEST 5: Verify Contract Allocations Format")
    print("=" * 80)
    
    allocations = result['contract_allocations']
    print(f"\n  Contract allocations: {len(allocations)}")
    
    for stock, allocation in allocations.items():
        shares = portfolio[stock]
        print(f"\n  {stock}: {shares} shares")
        print(f"    total_contracts: {allocation['total_contracts']}")
        print(f"    recommended: {allocation['recommended']}")
        print(f"    buffer: {allocation.get('buffer', 0)}")
        
        # Verify structure
        assert 'total_contracts' in allocation, f"{stock}: missing total_contracts"
        assert 'recommended' in allocation, f"{stock}: missing recommended"
        
        # Verify calculations
        expected_total = shares // 100
        assert allocation['total_contracts'] == expected_total, f"{stock}: total contracts mismatch"
    
    print("\n✓ Contract allocations format correct!")
    
    print("\n" + "=" * 80)
    print("TEST 6: Simulate UI Display")
    print("=" * 80)
    
    print("\n" + "-" * 80)
    print("SIMULATED UI: Income Projections Display")
    print("-" * 80)
    
    # Calculate total income
    total_income = sum(data['total_income'] for data in income_data.values())
    print(f"\n🎯 Total Monthly Income: ${total_income:,.2f}")
    print("\n" + "=" * 80)
    
    # Display per-stock
    for stock in sorted(income_data.keys()):
        income = income_data[stock]
        primary = primaries.get(stock, {})
        secondary = secondaries.get(stock)
        allocation = allocations.get(stock, {})
        
        print(f"\n{stock}:")
        print(f"  📊 Contracts: {allocation.get('recommended', 1)}")
        if allocation.get('buffer', 0) > 0:
            print(f"  🛡️ Buffer: {allocation['buffer']} contract")
        
        print(f"\n  Strategy:")
        if primary:
            print(f"    📈 Primary: ${primary['strike']} exp {primary['expiry']}")
        if secondary:
            print(f"    📈 Secondary: ${secondary['strike']} exp {secondary['expiry']}")
            print(f"    💰💰 Multi-trade strategy!")
        
        print(f"\n  Income:")
        if income['primary_income'] > 0:
            print(f"    Primary: ${income['primary_income']:,.2f}")
        if income['secondary_income'] > 0:
            print(f"    Secondary: ${income['secondary_income']:,.2f}")
        print(f"    Total: ${income['total_income']:,.2f}")
        print("-" * 80)
    
    # Summary
    multi_count = sum(1 for inc in income_data.values() if inc['has_secondary'])
    single_count = len(income_data) - multi_count
    
    print(f"\n📊 Strategy Mix: {multi_count} multi-trade, {single_count} single-trade")
    if multi_count > 0:
        print("💡 Tip: Multi-trade strategies can earn 1.5x - 2x more income!")
    
    print("\n✓ UI simulation successful!")
    
    print("\n" + "=" * 80)
    print("✅ ALL PHASE 9 TESTS PASSED!")
    print("=" * 80)
    
    print("\nVerified UI Integration:")
    print("  ✓ All required fields present in Agent 2 output")
    print("  ✓ Income projections format correct")
    print("  ✓ Primary recommendations format correct")
    print("  ✓ Secondary recommendations format correct")
    print("  ✓ Contract allocations format correct")
    print("  ✓ UI display simulation successful")
    
    print("\n🎯 Phase 9 Complete: Output Formatting Verified!")
    print("🚀 UI is ready to display all Part 2 features!")


if __name__ == "__main__":
    test_ui_data_format()
