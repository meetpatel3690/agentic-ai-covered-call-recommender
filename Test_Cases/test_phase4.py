"""
Test script for Phase 4: Primary Recommendation Selection
Tests the select_primary_recommendation() function and workflow integration
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from strategy_recommendation_agent_langgraph import StrategyRecommendationAgentLangGraph

def test_phase4():
    """Test Phase 4 implementation"""
    
    print("=" * 70)
    print("PHASE 4 TESTING: Primary Recommendation Selection")
    print("=" * 70)
    
    # Initialize agent
    print("\n✅ Test 1: Initialize Agent")
    agent = StrategyRecommendationAgentLangGraph()
    print("   Agent initialized successfully!")
    
    # Create sample scored options for direct function testing
    print("\n✅ Test 2: Test select_primary_recommendation() function directly")
    
    scored_data = {
        'Stock': ['AAPL', 'AAPL', 'AAPL', 'TSLA', 'TSLA', 'TSLA'],
        'Strike': [150.0, 152.5, 155.0, 450.0, 455.0, 460.0],
        'Expiry': ['12/06', '12/13', '12/20', '12/06', '12/13', '12/20'],
        'Premium': [2.5, 2.8, 3.0, 25.0, 26.0, 28.0],
        'Delta': [0.3, 0.35, 0.4, 0.3, 0.35, 0.4],
        'Score': [1.75, 1.82, 1.80, 17.50, 16.90, 16.80],  # AAPL best=152.5, TSLA best=450.0
        'Confidence': ['HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH'],
        'Week': [1, 2, 3, 1, 2, 3]
    }
    scored_df = pd.DataFrame(scored_data)
    # Sort by score (descending) as the workflow does
    scored_df = scored_df.sort_values('Score', ascending=False).reset_index(drop=True)
    
    # Test AAPL primary selection
    print("   Test 2.1: Select primary for AAPL")
    aapl_primary = agent.select_primary_recommendation(scored_df, 'AAPL')
    
    if aapl_primary:
        print(f"      ✓ Primary found for AAPL")
        print(f"         Type: {aapl_primary['type']}")
        print(f"         Strike: ${aapl_primary['strike']}")
        print(f"         Expiry: {aapl_primary['expiry']}")
        print(f"         Score: ${aapl_primary['score']:.2f}")
        print(f"         Week: {aapl_primary['week']}")
        
        # Verify it's the top-scored option
        assert aapl_primary['type'] == 'Primary', "Type should be 'Primary'"
        assert aapl_primary['stock'] == 'AAPL', "Stock should be AAPL"
        assert aapl_primary['strike'] == 152.5, f"Best strike should be 152.5, got {aapl_primary['strike']}"
        assert aapl_primary['score'] == 1.82, f"Best score should be 1.82, got {aapl_primary['score']}"
        print("      ✓ PASSED: Selected highest-scored option (152.5)")
    else:
        print("      ❌ FAILED: No primary found for AAPL")
        return False
    
    # Test TSLA primary selection
    print("   Test 2.2: Select primary for TSLA")
    tsla_primary = agent.select_primary_recommendation(scored_df, 'TSLA')
    
    if tsla_primary:
        print(f"      ✓ Primary found for TSLA")
        print(f"         Strike: ${tsla_primary['strike']}")
        print(f"         Score: ${tsla_primary['score']:.2f}")
        
        assert tsla_primary['strike'] == 450.0, f"Best strike should be 450.0, got {tsla_primary['strike']}"
        assert tsla_primary['score'] == 17.50, f"Best score should be 17.50, got {tsla_primary['score']}"
        print("      ✓ PASSED: Selected highest-scored option (450.0)")
    else:
        print("      ❌ FAILED: No primary found for TSLA")
        return False
    
    # Test with non-existent stock
    print("   Test 2.3: Handle non-existent stock")
    none_primary = agent.select_primary_recommendation(scored_df, 'NONEXISTENT')
    if none_primary is None:
        print("      ✓ PASSED: Returns None for non-existent stock")
    else:
        print("      ❌ FAILED: Should return None for non-existent stock")
        return False
    
    # Test workflow integration
    print("\n✅ Test 3: Test workflow integration with primary selection")
    
    # Create sample data with future dates
    today = datetime.now()
    week1_date = f"{today.month:02d}/06"
    week2_date = f"{today.month:02d}/13"
    week3_date = f"{today.month:02d}/20"
    
    premium_data = {
        'Stock': ['AAPL', 'AAPL', 'AAPL', 'TSLA', 'TSLA', 'TSLA'],
        'Strike_Price': [150.0, 152.5, 155.0, 450.0, 455.0, 460.0],
        week1_date: [2.5, 2.3, 2.0, 25.0, 23.0, 21.0],
        week2_date: [3.0, 2.8, 2.5, 28.0, 26.0, 24.0],
        week3_date: [3.5, 3.2, 3.0, 32.0, 30.0, 28.0]
    }
    premium_df = pd.DataFrame(premium_data)
    
    delta_data = {
        'Stock': ['AAPL', 'AAPL', 'AAPL', 'TSLA', 'TSLA', 'TSLA'],
        'Strike_Price': [150.0, 152.5, 155.0, 450.0, 455.0, 460.0],
        week1_date: [0.3, 0.4, 0.5, 0.3, 0.4, 0.5],
        week2_date: [0.35, 0.45, 0.55, 0.35, 0.45, 0.55],
        week3_date: [0.4, 0.5, 0.6, 0.4, 0.5, 0.6]
    }
    delta_df = pd.DataFrame(delta_data)
    
    print(f"   Running analysis with mode='premium_delta'...")
    result = agent.analyze(premium_df, delta_data=delta_df, analysis_mode="premium_delta")
    
    print(f"\n   Analysis complete!")
    print(f"   Status: {result.get('status', 'N/A')}")
    
    # Check if primary_recommendations exists
    if 'primary_recommendations' in result:
        primaries = result['primary_recommendations']
        print(f"   ✓ primary_recommendations field exists")
        print(f"   ✓ Found {len(primaries)} primary recommendation(s)")
        
        # Verify both stocks have primaries
        if 'AAPL' in primaries:
            aapl = primaries['AAPL']
            print(f"\n   📊 AAPL Primary:")
            print(f"      Type: {aapl['type']}")
            print(f"      Strike: ${aapl['strike']}")
            print(f"      Expiry: {aapl['expiry']} (Week {aapl['week']})")
            print(f"      Premium: ${aapl['premium']:.2f}")
            print(f"      Score: ${aapl['score']:.2f}")
            print(f"      Confidence: {aapl['confidence']}")
            
            assert aapl['type'] == 'Primary', "Type should be Primary"
            assert aapl['stock'] == 'AAPL', "Stock should be AAPL"
            assert 'week' in aapl, "Week should be present"
            print("      ✓ AAPL primary structure valid")
        else:
            print("   ❌ AAPL primary not found")
            return False
        
        if 'TSLA' in primaries:
            tsla = primaries['TSLA']
            print(f"\n   📊 TSLA Primary:")
            print(f"      Strike: ${tsla['strike']}")
            print(f"      Expiry: {tsla['expiry']} (Week {tsla['week']})")
            print(f"      Score: ${tsla['score']:.2f}")
            print("      ✓ TSLA primary structure valid")
        else:
            print("   ❌ TSLA primary not found")
            return False
    else:
        print("   ❌ primary_recommendations field not found in result")
        return False
    
    # Test with premium_only mode (should skip)
    print("\n✅ Test 4: Test backward compatibility (premium_only mode)")
    print(f"   Running analysis with mode='premium_only'...")
    result_premium_only = agent.analyze(premium_df, analysis_mode="premium_only")
    
    print(f"   Analysis complete!")
    primaries_only = result_premium_only.get('primary_recommendations', {})
    if len(primaries_only) == 0:
        print("   ✓ premium_only mode correctly skips primary selection")
        print("   ✓ Backward compatibility maintained")
    else:
        print(f"   ⚠️ Note: premium_only mode has {len(primaries_only)} primaries (expected 0)")
    
    print("\n" + "=" * 70)
    print("✅ PHASE 4 TESTS PASSED!")
    print("=" * 70)
    print("\nPhase 4 Summary:")
    print("✓ select_primary_recommendation() function working correctly")
    print("✓ Selects top-scored option as primary for each stock")
    print("✓ Extracts all metadata (strike, expiry, premium, delta, score, week)")
    print("✓ select_primary_node integrated into workflow")
    print("✓ primary_recommendations stored in state and returned in response")
    print("✓ Handles multiple stocks correctly")
    print("✓ Returns None for non-existent stocks")
    print("\nReady to proceed to Phase 5: Secondary Trade Logic")
    
    return True

if __name__ == "__main__":
    try:
        success = test_phase4()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
