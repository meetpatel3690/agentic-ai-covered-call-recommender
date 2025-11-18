"""
Test script for Phase 3: Week Identification Logic
Tests the get_week_of_month() function and integration into workflow
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from strategy_recommendation_agent_langgraph import StrategyRecommendationAgentLangGraph

def test_phase3():
    """Test Phase 3 implementation"""
    
    print("=" * 70)
    print("PHASE 3 TESTING: Week Identification Logic")
    print("=" * 70)
    
    # Initialize agent
    print("\n✅ Test 1: Initialize Agent")
    agent = StrategyRecommendationAgentLangGraph()
    print("   Agent initialized successfully!")
    
    # Test get_week_of_month function directly
    print("\n✅ Test 2: Test get_week_of_month() function")
    
    test_cases = [
        ("12/06", 1, "Week 1: Days 1-7"),
        ("12/01", 1, "Week 1: Day 1"),
        ("12/07", 1, "Week 1: Day 7"),
        ("12/13", 2, "Week 2: Days 8-14"),
        ("12/08", 2, "Week 2: Day 8"),
        ("12/14", 2, "Week 2: Day 14"),
        ("12/20", 3, "Week 3: Days 15-21"),
        ("12/15", 3, "Week 3: Day 15"),
        ("12/21", 3, "Week 3: Day 21"),
        ("12/27", 4, "Week 4: Days 22-28"),
        ("12/22", 4, "Week 4: Day 22"),
        ("12/28", 4, "Week 4: Day 28"),
        ("12/31", 5, "Week 5: Days 29+"),
        ("12/29", 5, "Week 5: Day 29"),
        ("01/03", 1, "January Week 1"),
    ]
    
    all_passed = True
    for date_str, expected_week, description in test_cases:
        result = agent.get_week_of_month(date_str)
        status = "✓" if result == expected_week else "✗"
        
        if result != expected_week:
            all_passed = False
            print(f"   {status} FAILED: {description}")
            print(f"      Date: {date_str}, Expected: Week {expected_week}, Got: Week {result}")
        else:
            print(f"   {status} PASSED: {description} - {date_str} → Week {result}")
    
    if not all_passed:
        print("\n   ❌ Some tests failed!")
        return False
    
    print("\n   ✅ All week identification tests passed!")
    
    # Test integrated workflow with week identification
    print("\n✅ Test 3: Test workflow integration with week identification")
    
    # Create sample data with specific dates across different weeks
    today = datetime.now()
    
    # Create dates for Week 1, Week 2, and Week 3
    week1_date = f"{today.month:02d}/06"  # Day 6 = Week 1
    week2_date = f"{today.month:02d}/13"  # Day 13 = Week 2
    week3_date = f"{today.month:02d}/20"  # Day 20 = Week 3
    
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
    
    print(f"   Running analysis with dates:")
    print(f"      {week1_date} (Week 1)")
    print(f"      {week2_date} (Week 2)")
    print(f"      {week3_date} (Week 3)")
    
    result = agent.analyze(premium_df, delta_data=delta_df, analysis_mode="premium_delta")
    
    print(f"\n   Analysis complete!")
    print(f"   Status: {result.get('status', 'N/A')}")
    
    # Check if merged_data has Week column
    if 'merged_data' in result and result['merged_data'] is not None:
        merged = result['merged_data']
        
        if 'Week' in merged.columns:
            print(f"   ✓ Week column exists in merged data")
            print(f"   ✓ Unique weeks found: {sorted(merged['Week'].unique().tolist())}")
            
            # Verify week assignments
            week_distribution = merged['Week'].value_counts().sort_index()
            print(f"   ✓ Week distribution:")
            for week, count in week_distribution.items():
                print(f"      Week {week}: {count} options")
            
            # Show sample with week information
            print(f"\n   📊 Sample scored options with weeks:")
            sample = merged.head(5)[['Stock', 'Strike', 'Expiry', 'Week', 'Score', 'Confidence']]
            for idx, row in sample.iterrows():
                print(f"      {row['Stock']} ${row['Strike']} exp {row['Expiry']} "
                      f"(Week {row['Week']}) - Score: ${row['Score']:.2f}")
            
            # Verify correct week assignment
            print(f"\n   🔍 Verifying week assignments:")
            for expiry in merged['Expiry'].unique():
                week = merged[merged['Expiry'] == expiry]['Week'].iloc[0]
                day = int(expiry.split('/')[1])
                
                # Verify logic
                if day <= 7:
                    expected = 1
                elif day <= 14:
                    expected = 2
                elif day <= 21:
                    expected = 3
                elif day <= 28:
                    expected = 4
                else:
                    expected = 5
                
                status = "✓" if week == expected else "✗"
                print(f"      {status} {expiry} (Day {day}) → Week {week} (expected {expected})")
                
                if week != expected:
                    print(f"         ❌ Week assignment mismatch!")
                    return False
        else:
            print("   ❌ Week column not found in merged data")
            return False
    else:
        print("   ❌ No merged_data in result")
        return False
    
    # Test edge cases
    print("\n✅ Test 4: Test edge cases")
    
    # Test with invalid date format
    print("   Test 4.1: Invalid date format")
    invalid_week = agent.get_week_of_month("invalid")
    print(f"      Invalid date → Week {invalid_week} (should be 0)")
    assert invalid_week == 0, "Invalid date should return 0"
    print("      ✓ PASSED")
    
    # Test with end of month dates
    print("   Test 4.2: End of month dates")
    end_dates = [
        ("01/31", 5, "January 31"),
        ("02/29", 5, "February 29 (leap year)"),
        ("12/30", 5, "December 30"),
    ]
    for date, expected, desc in end_dates:
        week = agent.get_week_of_month(date)
        status = "✓" if week == expected else "✗"
        print(f"      {status} {desc}: {date} → Week {week}")
        if week != expected:
            return False
    
    print("\n" + "=" * 70)
    print("✅ PHASE 3 TESTS PASSED!")
    print("=" * 70)
    print("\nPhase 3 Summary:")
    print("✓ get_week_of_month() function working correctly")
    print("✓ Week determination: Days 1-7=W1, 8-14=W2, 15-21=W3, 22-28=W4, 29+=W5")
    print("✓ Week column added to scored options DataFrame")
    print("✓ Week information displayed in console output")
    print("✓ Edge cases handled (invalid dates, month-end dates)")
    print("\nReady to proceed to Phase 4: Primary Recommendation Selection")
    
    return True

if __name__ == "__main__":
    try:
        success = test_phase3()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
