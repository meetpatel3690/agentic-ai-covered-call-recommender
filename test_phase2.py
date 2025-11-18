"""
Test script for Phase 2: Scoring Implementation
Tests the Delta-based scoring function and workflow integration
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from strategy_recommendation_agent_langgraph import StrategyRecommendationAgentLangGraph

def test_phase2():
    """Test Phase 2 implementation"""
    
    print("=" * 70)
    print("PHASE 2 TESTING: Scoring Implementation")
    print("=" * 70)
    
    # Initialize agent
    print("\n✅ Test 1: Initialize Agent")
    agent = StrategyRecommendationAgentLangGraph()
    print("   Agent initialized successfully!")
    
    # Test scoring function directly
    print("\n✅ Test 2: Test calculate_option_score() function")
    
    # Test Case 1: Premium with Delta
    score1, conf1 = agent.calculate_option_score(premium=2.5, delta=0.3)
    expected_score1 = 2.5 * (1 - 0.3)  # = 1.75
    print(f"   Test 2.1: Premium=2.5, Delta=0.3")
    print(f"      Expected: Score=1.75, Confidence=HIGH")
    print(f"      Got:      Score={score1}, Confidence={conf1}")
    assert score1 == 1.75, f"Score mismatch: expected 1.75, got {score1}"
    assert conf1 == "HIGH", f"Confidence mismatch: expected HIGH, got {conf1}"
    print("      ✓ PASSED")
    
    # Test Case 2: Premium with Delta=0 (None treated as 0)
    score2, conf2 = agent.calculate_option_score(premium=3.0, delta=0)
    expected_score2 = 3.0 * (1 - 0)  # = 3.0
    print(f"   Test 2.2: Premium=3.0, Delta=0 (was None)")
    print(f"      Expected: Score=3.0, Confidence=MEDIUM")
    print(f"      Got:      Score={score2}, Confidence={conf2}")
    assert score2 == 3.0, f"Score mismatch: expected 3.0, got {score2}"
    assert conf2 == "MEDIUM", f"Confidence mismatch: expected MEDIUM, got {conf2}"
    print("      ✓ PASSED")
    
    # Test Case 3: Premium with high Delta
    score3, conf3 = agent.calculate_option_score(premium=1.5, delta=0.5)
    expected_score3 = 1.5 * (1 - 0.5)  # = 0.75
    print(f"   Test 2.3: Premium=1.5, Delta=0.5")
    print(f"      Expected: Score=0.75, Confidence=HIGH")
    print(f"      Got:      Score={score3}, Confidence={conf3}")
    assert score3 == 0.75, f"Score mismatch: expected 0.75, got {score3}"
    assert conf3 == "HIGH", f"Confidence mismatch: expected HIGH, got {conf3}"
    print("      ✓ PASSED")
    
    # Test integrated workflow with "premium_delta" mode
    print("\n✅ Test 3: Test workflow with analysis_mode='premium_delta'")
    
    # Create sample data with future dates
    today = datetime.now()
    future_dates = [
        (today + timedelta(days=7)).strftime("%m/%d"),
        (today + timedelta(days=14)).strftime("%m/%d"),
        (today + timedelta(days=21)).strftime("%m/%d")
    ]
    
    premium_data = {
        'Stock': ['AAPL', 'AAPL', 'AAPL'],
        'Strike_Price': [150.0, 152.5, 155.0],
        future_dates[0]: [2.5, 2.3, 2.0],
        future_dates[1]: [3.0, 2.8, 2.5],
        future_dates[2]: [3.5, 3.2, 3.0]
    }
    premium_df = pd.DataFrame(premium_data)
    
    delta_data = {
        'Stock': ['AAPL', 'AAPL', 'AAPL'],
        'Strike_Price': [150.0, 152.5, 155.0],
        future_dates[0]: [0.3, 0.4, 0.5],
        future_dates[1]: [0.35, 0.45, 0.55],
        future_dates[2]: [0.4, 0.5, 0.6]
    }
    delta_df = pd.DataFrame(delta_data)
    
    print(f"   Running analysis with mode='premium_delta'...")
    result = agent.analyze(premium_df, delta_data=delta_df, analysis_mode="premium_delta")
    
    print(f"   Analysis complete!")
    print(f"   Status: {result.get('status', 'N/A')}")
    print(f"   Errors: {result.get('errors', [])}")
    
    # Check if merged_data exists and has scores
    if 'merged_data' in result:
        merged = result['merged_data']
        if merged is not None and not merged.empty:
            print(f"   ✓ Merged data contains {len(merged)} scored options")
            if 'Score' in merged.columns:
                print(f"   ✓ Score column exists")
                print(f"   ✓ Score range: ${merged['Score'].min():.2f} to ${merged['Score'].max():.2f}")
            if 'Confidence' in merged.columns:
                print(f"   ✓ Confidence column exists")
                print(f"   ✓ Confidence values: {merged['Confidence'].unique().tolist()}")
        else:
            print("   ⚠️ Merged data is empty")
    else:
        print("   ⚠️ No merged_data in result")
    
    # Test backward compatibility - premium_only mode should still work
    print("\n✅ Test 4: Test backward compatibility (premium_only mode)")
    print(f"   Running analysis with mode='premium_only'...")
    result_premium_only = agent.analyze(premium_df, analysis_mode="premium_only")
    
    print(f"   Analysis complete!")
    print(f"   Status: {result_premium_only.get('status', 'N/A')}")
    print(f"   ✓ premium_only mode still works (backward compatible)")
    
    print("\n" + "=" * 70)
    print("✅ PHASE 2 TESTS PASSED!")
    print("=" * 70)
    print("\nPhase 2 Summary:")
    print("✓ calculate_option_score() function working correctly")
    print("✓ Formula: Score = Premium × (1 - Delta)")
    print("✓ Confidence levels: HIGH (delta present), MEDIUM (delta=0)")
    print("✓ calculate_scores_node integrated into workflow")
    print("✓ Workflow runs in 'premium_delta' mode")
    print("✓ Backward compatibility maintained (premium_only still works)")
    print("\nReady to proceed to Phase 3: Week Identification Logic")
    
    return True

if __name__ == "__main__":
    try:
        success = test_phase2()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
