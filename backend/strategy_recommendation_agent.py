# -*- coding: utf-8 -*-
"""
Strategy Recommendation Agent (Agent 2)
A sophisticated agent that analyzes options data and recommends optimal strategies.

PART 1 (Tomorrow's Demo):
- Analyzes the 6x6 options grid from Agent 1
- Highlights cells with highest premium for each stock (orange color)
- Provides visual feedback on which options have the best premiums

PART 2 (Future Enhancement - Scalable Design):
- The architecture is designed to be easily extended
- Can incorporate Delta values for directional risk analysis
- Supports custom scoring formulas that can be finalized with mentors
- Modular design allows adding Delta analysis without breaking existing functionality

=============================================================================
ATTRIBUTION:
=============================================================================
- Project Concept & Requirements: Meet Patel (@meetpatel3690)
- Agent 2 Architecture & Implementation: AI Assistant (GitHub Copilot)
- Scalable Design for Future Enhancements: AI Assistant (GitHub Copilot)
=============================================================================
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class StrategyRecommendationAgent:
    """
    Agent 2: Analyzes options data and recommends optimal strategies
    
    This agent is designed with scalability in mind:
    - PART 1: Premium-based analysis (for tomorrow's demo)
    - PART 2: Will support Delta values with configurable formulas
    """
    
    def __init__(self):
        """Initialize the Strategy Recommendation Agent"""
        self.analysis_results = {}
        self.highlighted_cells = {}
        
        # Scalable configuration for future enhancements (PART 2)
        self.scoring_config = {
            'use_premium': True,      # PART 1: Premium analysis
            'use_delta': False,       # PART 2: Delta analysis (to be enabled)
            'custom_formula': None,   # PART 2: Custom formula from mentors
            'weights': {              # PART 2: Configurable weights
                'premium': 1.0,
                'delta': 0.0          # Will be configured after mentor meeting
            }
        }
    
    def analyze_options_grid(self, options_df: pd.DataFrame) -> Dict:
        """
        PART 1: Analyze the 6x6 options grid and identify highest premiums
        
        This method is designed to be scalable:
        - Currently analyzes premiums only
        - Can be extended to include Delta values
        - Returns structured data that can accommodate future metrics
        
        Args:
            options_df: DataFrame with options data from Agent 1
                       Format: Stock | Strike_Price | Date1 | Date2 | Date3 | Date4 | Date5 | Date6
        
        Returns:
            Dict with analysis results including:
            - highest_premium_cells: Cells with max premium per stock
            - stock_analysis: Detailed analysis per stock
            - recommendations: Strategy recommendations (scalable for PART 2)
        """
        if options_df is None or options_df.empty:
            return {
                'status': 'error',
                'message': 'No options data provided',
                'highest_premium_cells': {},
                'stock_analysis': {},
                'recommendations': []
            }
        
        # Get date columns (these contain premium values)
        date_columns = [col for col in options_df.columns if '/' in col]
        
        if not date_columns:
            return {
                'status': 'error',
                'message': 'No date columns found in options data',
                'highest_premium_cells': {},
                'stock_analysis': {},
                'recommendations': []
            }
        
        # Initialize results
        highest_premium_cells = {}
        stock_analysis = {}
        
        # Get unique stocks
        stocks = options_df['Stock'].unique()
        
        print(f"\n🔍 Agent 2: Analyzing {len(stocks)} stocks across {len(date_columns)} expiration dates...")
        
        # Analyze each stock
        for stock in stocks:
            stock_data = options_df[options_df['Stock'] == stock].copy()
            
            # Find the cell with highest premium for this stock
            max_premium = -1
            max_cell = None
            all_premiums = []
            
            # Iterate through all cells for this stock
            for idx, row in stock_data.iterrows():
                strike_price = row['Strike_Price']
                
                for date_col in date_columns:
                    try:
                        premium = float(row[date_col])
                        all_premiums.append(premium)
                        
                        if premium > max_premium:
                            max_premium = premium
                            max_cell = {
                                'row_index': idx,
                                'stock': stock,
                                'strike_price': strike_price,
                                'expiration_date': date_col,
                                'premium': premium
                            }
                    except (ValueError, TypeError):
                        # Skip non-numeric values
                        continue
            
            # Store results for this stock
            if max_cell:
                highest_premium_cells[stock] = max_cell
                stock_analysis[stock] = {
                    'highest_premium': max_premium,
                    'avg_premium': np.mean(all_premiums) if all_premiums else 0,
                    'total_options': len(stock_data) * len(date_columns),
                    'best_strike': max_cell['strike_price'],
                    'best_expiration': max_cell['expiration_date']
                }
                
                print(f"  ✓ {stock}: Best premium ${max_premium:.2f} at strike ${max_cell['strike_price']} expiring {max_cell['expiration_date']}")
        
        # Generate recommendations (PART 1: Simple premium-based)
        recommendations = self._generate_recommendations_part1(highest_premium_cells, stock_analysis)
        
        # Store results
        self.analysis_results = {
            'status': 'success',
            'highest_premium_cells': highest_premium_cells,
            'stock_analysis': stock_analysis,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        print(f"\n✅ Agent 2: Analysis complete! Found {len(highest_premium_cells)} opportunities\n")
        
        return self.analysis_results
    
    def _generate_recommendations_part1(self, highest_premium_cells: Dict, stock_analysis: Dict) -> List[Dict]:
        """
        PART 1: Generate simple premium-based recommendations
        
        This is a placeholder that will be enhanced in PART 2 with:
        - Delta-neutral strategies
        - Spread strategies
        - Custom formulas from mentors
        
        Args:
            highest_premium_cells: Dict of highest premium cells per stock
            stock_analysis: Dict of analysis per stock
        
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        for stock, cell_info in highest_premium_cells.items():
            recommendations.append({
                'stock': stock,
                'strategy': 'Sell Covered Call',  # Simple strategy for PART 1
                'strike_price': cell_info['strike_price'],
                'expiration': cell_info['expiration_date'],
                'premium': cell_info['premium'],
                'rationale': f"Highest premium of ${cell_info['premium']:.2f} available",
                'confidence': 'HIGH',  # PART 2 will have calculated confidence scores
                # Placeholders for PART 2 enhancements
                'delta': None,  # Will be populated in PART 2
                'expected_return': None,  # Will be calculated in PART 2
                'risk_score': None  # Will be calculated in PART 2
            })
        
        # Sort by premium (highest first)
        recommendations.sort(key=lambda x: x['premium'], reverse=True)
        
        return recommendations
    
    def get_highlighted_dataframe(self, options_df: pd.DataFrame) -> pd.DataFrame:
        """
        PART 1: Create a styled DataFrame with highest premium cells highlighted in orange
        
        This method marks which cells should be highlighted.
        The actual styling will be done in the UI layer.
        
        Args:
            options_df: Original options DataFrame
        
        Returns:
            DataFrame with same structure, includes highlighting info
        """
        if not self.analysis_results or 'highest_premium_cells' not in self.analysis_results:
            print("⚠️ No analysis results available. Run analyze_options_grid() first.")
            return options_df
        
        # Create a copy to avoid modifying original
        styled_df = options_df.copy()
        
        # Store highlighting information
        highlight_info = {}
        
        for stock, cell_info in self.analysis_results['highest_premium_cells'].items():
            row_idx = cell_info['row_index']
            expiration_col = cell_info['expiration_date']
            
            # Store which cell to highlight
            if row_idx not in highlight_info:
                highlight_info[row_idx] = []
            highlight_info[row_idx].append(expiration_col)
        
        self.highlighted_cells = highlight_info
        
        return styled_df
    
    def get_styling_function(self):
        """
        Returns a function that can be used with pandas.style.apply()
        to highlight the highest premium cells in orange
        """
        def highlight_max_premium(row):
            """Apply orange background to cells with highest premium"""
            styles = [''] * len(row)
            
            # Check if this row should have any highlighted cells
            if row.name in self.highlighted_cells:
                cols_to_highlight = self.highlighted_cells[row.name]
                
                for col_name in cols_to_highlight:
                    if col_name in row.index:
                        col_idx = row.index.get_loc(col_name)
                        styles[col_idx] = 'background-color: orange; color: black; font-weight: bold'
            
            return styles
        
        return highlight_max_premium
    
    def export_analysis_summary(self) -> str:
        """
        Export analysis summary as formatted string
        Useful for displaying in the UI or logging
        """
        if not self.analysis_results:
            return "No analysis results available"
        
        summary_lines = [
            "=" * 60,
            "AGENT 2: STRATEGY RECOMMENDATION ANALYSIS",
            "=" * 60,
            ""
        ]
        
        # Overall statistics
        summary_lines.append(f"Analysis Timestamp: {self.analysis_results.get('analysis_timestamp', 'N/A')}")
        summary_lines.append(f"Total Stocks Analyzed: {len(self.analysis_results.get('stock_analysis', {}))}")
        summary_lines.append("")
        
        # Per-stock analysis
        summary_lines.append("HIGHEST PREMIUM OPPORTUNITIES:")
        summary_lines.append("-" * 60)
        
        for stock, analysis in self.analysis_results.get('stock_analysis', {}).items():
            summary_lines.append(f"\n{stock}:")
            summary_lines.append(f"  • Highest Premium: ${analysis['highest_premium']:.2f}")
            summary_lines.append(f"  • Average Premium: ${analysis['avg_premium']:.2f}")
            summary_lines.append(f"  • Best Strike: ${analysis['best_strike']}")
            summary_lines.append(f"  • Best Expiration: {analysis['best_expiration']}")
        
        # Recommendations
        summary_lines.append("\n" + "=" * 60)
        summary_lines.append("RECOMMENDATIONS:")
        summary_lines.append("=" * 60)
        
        for i, rec in enumerate(self.analysis_results.get('recommendations', []), 1):
            summary_lines.append(f"\n{i}. {rec['stock']}:")
            summary_lines.append(f"   Strategy: {rec['strategy']}")
            summary_lines.append(f"   Strike: ${rec['strike_price']} | Expiration: {rec['expiration']}")
            summary_lines.append(f"   Premium: ${rec['premium']:.2f}")
            summary_lines.append(f"   Rationale: {rec['rationale']}")
        
        summary_lines.append("\n" + "=" * 60)
        
        return "\n".join(summary_lines)
    
    # =========================================================================
    # PART 2: PLACEHOLDER METHODS FOR FUTURE ENHANCEMENTS
    # These will be implemented after finalizing formulas with mentors
    # =========================================================================
    
    def configure_scoring_formula(self, formula_config: Dict):
        """
        PART 2: Configure custom scoring formula
        
        This method will be used to set up the scoring formula
        decided in the mentor meeting.
        
        Example config:
        {
            'use_delta': True,
            'weights': {
                'premium': 0.6,
                'delta': 0.4
            },
            'custom_formula': 'premium * 0.6 + abs(delta - 0.3) * 0.4'
        }
        """
        self.scoring_config.update(formula_config)
        print(f"✓ Scoring configuration updated: {self.scoring_config}")
    
    def analyze_with_delta(self, options_df: pd.DataFrame, delta_data: Dict) -> Dict:
        """
        PART 2: Analyze options considering Delta values
        
        This will be implemented after the mentor meeting to incorporate:
        - Delta values for directional risk analysis
        - Optimal Delta targeting (e.g., ~0.30 for covered calls)
        - Risk-adjusted premium scoring
        
        Args:
            options_df: Options data from Agent 1
            delta_data: Dictionary with Delta values for each option
        
        Returns:
            Enhanced analysis results with Delta-based recommendations
        """
        # Placeholder for PART 2 implementation
        print("⚠️ Delta-based analysis will be implemented in PART 2")
        return self.analysis_results
    
    def calculate_custom_score(self, premium: float, delta: float = None) -> float:
        """
        PART 2: Calculate custom score based on mentor-approved formula
        
        This placeholder will be replaced with the actual formula
        after the mentor meeting.
        
        Args:
            premium: Option premium
            delta: Delta value (optional for now)
        
        Returns:
            Calculated score
        """
        # PART 1: Simple premium-based score
        if not self.scoring_config['use_delta']:
            return premium
        
        # PART 2: Will implement Delta-based formula here
        weights = self.scoring_config['weights']
        score = premium * weights['premium']
        
        if delta is not None:
            # Target delta ~0.30 for covered calls (30% probability of being in the money)
            score += abs(delta - 0.3) * weights['delta']
        
        return score


# =============================================================================
# HELPER FUNCTIONS FOR UI INTEGRATION
# =============================================================================

def create_strategy_agent() -> StrategyRecommendationAgent:
    """
    Factory function to create a new Strategy Recommendation Agent instance
    
    Returns:
        Initialized StrategyRecommendationAgent
    """
    return StrategyRecommendationAgent()


def analyze_and_highlight(options_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict, StrategyRecommendationAgent]:
    """
    Convenience function for UI integration
    
    Analyzes options data and returns highlighted DataFrame with results
    
    Args:
        options_df: Options data from Agent 1
    
    Returns:
        Tuple of (highlighted_df, analysis_results, agent_instance)
    """
    # Create agent
    agent = create_strategy_agent()
    
    # Run analysis
    results = agent.analyze_options_grid(options_df)
    
    # Get highlighted dataframe
    highlighted_df = agent.get_highlighted_dataframe(options_df)
    
    return highlighted_df, results, agent
