# 🎯 AGENT 2 - VISUAL FLOW DIAGRAM

## 📊 Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │  Main Page       │         │  Options Grid    │              │
│  │  (app.py)        │────────▶│  (mainpage.py)   │             │
│  │                  │         │                  │              │
│  │ • Enter Portfolio│         │ • Display Grid   │              │
│  │ • Click "Get     │         │ • Agent 2 Button │              │
│  │   Recommendations"│         │ • Show Highlights│              │
│  └──────────────────┘         └──────────────────┘             │
│                                       │                          │
└───────────────────────────────────────┼──────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND INTEGRATION                          │
│                  (backend_integration.py)                        │
│                                                                  │
│  • Load portfolio from JSON                                      │
│  • Convert to Agent 1 format                                     │
│  • Pass to Agent 1                                               │
└───────────────────────────────────────┼──────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT 1: OPTIONS DATA                      │
│              (backend/options_data_agent.py)                     │
│                                                                  │
│  INPUT:  "WMT, UPS"                                             │
│  PROCESS:                                                        │
│    1. Convert to ticker symbols                                  │
│    2. Fetch options data from Alpha Vantage                     │
│    3. Format into 6×6 grid                                      │
│  OUTPUT:                                                         │
│    ┌──────────────────────────────────────────┐                │
│    │ Stock │ Strike │ 11/15 │ 11/22 │ ... │   │                │
│    │ WMT   │  $105  │ $4.20 │ $4.50 │ ... │   │                │
│    │ WMT   │  $110  │ $5.25 │ $5.10 │ ... │   │                │
│    │ WMT   │  $115  │ $3.80 │ $4.00 │ ... │   │                │
│    │ UPS   │   $85  │ $3.50 │ $3.80 │ ... │   │                │
│    │ ...   │  ...   │  ...  │  ...  │ ... │   │                │
│    └──────────────────────────────────────────┘                │
└───────────────────────────────────────┼──────────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                    ▼                                       ▼
        ┌─────────────────────┐              ┌─────────────────────┐
        │   DISPLAY IN UI     │              │  USER CLICKS        │
        │   (mainpage.py)     │              │  "Run Agent 2"      │
        │                     │              │  BUTTON             │
        │  6×6 Grid Shown     │              └──────────┬──────────┘
        └─────────────────────┘                         │
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│               AGENT 2: STRATEGY RECOMMENDATION                   │
│         (backend/strategy_recommendation_agent.py)               │
│                                                                  │
│  INPUT: 6×6 Options Grid from Agent 1                           │
│                                                                  │
│  PROCESS (PART 1):                                               │
│    For each stock (WMT, UPS):                                    │
│      ┌─────────────────────────────────────┐                   │
│      │ Analyze all 36 options:             │                    │
│      │   • 6 strike prices                 │                    │
│      │   • 6 expiration dates              │                    │
│      │   • Compare all premium values      │                    │
│      │   • Find the HIGHEST premium        │                    │
│      │   • Record: strike, date, premium   │                    │
│      └─────────────────────────────────────┘                   │
│                                                                  │
│  OUTPUT:                                                         │
│    {                                                             │
│      'WMT': {                                                    │
│        'highest_premium': 5.25,                                  │
│        'best_strike': 110,                                       │
│        'best_expiration': '11/15/2024',                          │
│        'row_index': 1,  ← For highlighting                      │
│        'column': '11/15'                                         │
│      },                                                          │
│      'UPS': { ... }                                              │
│    }                                                             │
│                                                                  │
│  SCALABLE DESIGN (PART 2 - Ready):                              │
│    ┌────────────────────────────────────────┐                  │
│    │ scoring_config = {                     │                   │
│    │   'use_premium': True,   ← PART 1      │                   │
│    │   'use_delta': False,    ← PART 2      │                   │
│    │   'use_gamma': False,    ← PART 2      │                   │
│    │   'custom_formula': None ← PART 2      │                   │
│    │ }                                       │                   │
│    └────────────────────────────────────────┘                  │
└───────────────────────────────────────┼──────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   UI: DISPLAY RESULTS                            │
│                    (mainpage.py)                                 │
│                                                                  │
│  VISUAL HIGHLIGHTING:                                            │
│    ┌──────────────────────────────────────────┐                │
│    │ Stock │ Strike │ 11/15 │ 11/22 │ ... │   │                │
│    │ WMT   │  $105  │ $4.20 │ $4.50 │ ... │   │                │
│    │ WMT   │  $110  │ 🟧$5.25│ $5.10 │ ... │   │ ← ORANGE!     │
│    │ WMT   │  $115  │ $3.80 │ $4.00 │ ... │   │                │
│    │ UPS   │   $85  │ $3.50 │ 🟧$3.80│ ... │   │ ← ORANGE!     │
│    │ ...   │  ...   │  ...  │  ...  │ ... │   │                │
│    └──────────────────────────────────────────┘                │
│                                                                  │
│  ANALYSIS SUMMARY (Expandable):                                 │
│    ┌────────────────────────────────────────────┐              │
│    │ AGENT 2: STRATEGY RECOMMENDATION           │               │
│    │ ════════════════════════════════════════   │               │
│    │                                             │               │
│    │ WMT:                                        │               │
│    │   • Highest Premium: $5.25                 │               │
│    │   • Best Strike: $110                      │               │
│    │   • Best Expiration: 11/15/2024            │               │
│    │                                             │               │
│    │ UPS:                                        │               │
│    │   • Highest Premium: $4.80                 │               │
│    │   • Best Strike: $90                       │               │
│    │   • Best Expiration: 11/22/2024            │               │
│    │                                             │               │
│    │ RECOMMENDATIONS:                            │               │
│    │ 1. WMT: Sell Covered Call                  │               │
│    │    Strike: $110 | Premium: $5.25           │               │
│    │ 2. UPS: Sell Covered Call                  │               │
│    │    Strike: $90 | Premium: $4.80            │               │
│    └────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow (Simplified)

```
Portfolio → Agent 1 → 6×6 Grid → [Agent 2 Button] → Agent 2 → Highlighted Grid + Analysis
```

---

## 🎯 PART 1 vs PART 2 Comparison

```
╔════════════════════════════════════════════════════════════════╗
║                         PART 1 (NOW)                           ║
╚════════════════════════════════════════════════════════════════╝

Analysis Criteria:   Premium ONLY
                     ↓
         Find HIGHEST premium per stock
                     ↓
         Highlight that cell in ORANGE
                     ↓
         Recommend: "Sell at this strike/date"

┌────────────────────────────────────────────────────────────────┐
│ EXAMPLE:                                                        │
│                                                                 │
│ WMT has 36 options:                                             │
│   $105 strike, 11/15: $4.20                                     │
│   $110 strike, 11/15: $5.25  ← HIGHEST! (Orange)               │
│   $115 strike, 11/15: $3.80                                     │
│   ... (33 more options)                                         │
│                                                                 │
│ Result: Recommend selling $110 strike on 11/15 for $5.25       │
└────────────────────────────────────────────────────────────────┘


╔════════════════════════════════════════════════════════════════╗
║                      PART 2 (WEDNESDAY)                        ║
╚════════════════════════════════════════════════════════════════╝

Analysis Criteria:   Premium + Delta + Custom Formula
                     ↓
         Calculate SCORE for each option
         Score = (Premium × 0.6) + (|Delta - 0.3| × 0.4)
                     ↓
         Find HIGHEST score per stock
                     ↓
         Highlight that cell in ORANGE
                     ↓
         Recommend: "Best risk-adjusted opportunity"

┌────────────────────────────────────────────────────────────────┐
│ EXAMPLE:                                                        │
│                                                                 │
│ WMT has 36 options:                                             │
│   $105, 11/15: Premium=$4.20, Delta=0.65, Score=3.66           │
│   $110, 11/15: Premium=$5.25, Delta=0.45, Score=3.21           │
│   $115, 11/15: Premium=$3.80, Delta=0.25, Score=2.30           │
│   $112, 11/22: Premium=$4.50, Delta=0.32, Score=2.71 ← HIGHEST!│
│   ... (32 more options)                                         │
│                                                                 │
│ Result: Recommend $112 strike on 11/22 (best risk/reward)      │
│                                                                 │
│ NOTE: Different from PART 1! More sophisticated analysis       │
└────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                      (Streamlit UI)                          │
│                                                              │
│  • Displays grids                                            │
│  • Shows buttons                                             │
│  • Handles highlighting                                      │
│  • Renders summaries                                         │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                          │
│                (backend_integration.py)                      │
│                                                              │
│  • Loads portfolio                                           │
│  • Coordinates agents                                        │
│  • Formats data                                              │
│  • Calculates metrics                                        │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│                  (Backend Agents)                            │
│                                                              │
│  ┌─────────────────────┐       ┌──────────────────────┐    │
│  │ Agent 1:            │       │ Agent 2:             │     │
│  │ Options Data        │──────▶│ Strategy Recommend   │     │
│  │                     │       │                      │     │
│  │ • Fetch data        │       │ • Analyze options    │     │
│  │ • Format grid       │       │ • Score strategies   │     │
│  │ • Return 6×6        │       │ • Generate recs      │     │
│  └─────────────────────┘       └──────────────────────┘    │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│                                                              │
│  • Alpha Vantage API                                         │
│  • Portfolio JSON                                            │
│  • Session State                                             │
│  • Configuration                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 User Experience Flow

```
Step 1: ENTER PORTFOLIO
┌───────────────────────┐
│ Main Page             │
│                       │
│ Symbol: WMT ✓         │
│ Shares: 200           │
│ [Add to Portfolio]    │
│                       │
│ Symbol: UPS ✓         │
│ Shares: 250           │
│ [Add to Portfolio]    │
│                       │
│ [Get Recommendations] │ ← Click
└───────────────────────┘

Step 2: SEE OPTIONS GRID (Agent 1)
┌──────────────────────────────────────┐
│ 📊 Strike Price Details              │
│                                      │
│ Stock │ Strike │ 11/15 │ 11/22 │... │
│ WMT   │  $105  │ $4.20 │ $4.50 │    │
│ WMT   │  $110  │ $5.25 │ $5.10 │    │
│ WMT   │  $115  │ $3.80 │ $4.00 │    │
│ UPS   │   $85  │ $3.50 │ $3.80 │    │
│ ...   │  ...   │  ...  │  ...  │    │
│                                      │
│ ┌──────────────────────────────────┐│
│ │🎯 Run Agent 2: Strategy Recommend││ ← Click
│ └──────────────────────────────────┘│
└──────────────────────────────────────┘

Step 3: AGENT 2 PROCESSING
┌──────────────────────────────────────┐
│ 🤖 Agent 2 is analyzing options      │
│    and finding best premiums...      │
│                                      │
│    [Spinner animation]               │
└──────────────────────────────────────┘

Step 4: SEE HIGHLIGHTED RESULTS
┌──────────────────────────────────────┐
│ ✅ Agent 2 Analysis Complete!        │
│                                      │
│ Stock │ Strike │ 11/15 │ 11/22 │... │
│ WMT   │  $105  │ $4.20 │ $4.50 │    │
│ WMT   │  $110  │🟧$5.25│ $5.10 │    │ ← Orange!
│ WMT   │  $115  │ $3.80 │ $4.00 │    │
│ UPS   │   $85  │ $3.50 │🟧$3.80│    │ ← Orange!
│ ...   │  ...   │  ...  │  ...  │    │
│                                      │
│ 🟧 Orange = Highest premium per stock│
│                                      │
│ ┌─ 📊 View Analysis Summary ────────┐│
│ │ [Click to expand]                 ││ ← Expandable
│ └────────────────────────────────────┘│
└──────────────────────────────────────┘

Step 5: VIEW DETAILED ANALYSIS
┌──────────────────────────────────────┐
│ ┌─ 📊 View Analysis Summary ────────┐│
│ │                                   ││
│ │ AGENT 2: STRATEGY RECOMMENDATION  ││
│ │ ══════════════════════════════════││
│ │                                   ││
│ │ WMT:                              ││
│ │   • Highest Premium: $5.25        ││
│ │   • Best Strike: $110             ││
│ │   • Best Expiration: 11/15/2024   ││
│ │                                   ││
│ │ RECOMMENDATIONS:                  ││
│ │ 1. WMT: Sell Covered Call         ││
│ │    Premium: $5.25                 ││
│ │                                   ││
│ └────────────────────────────────────┘│
└──────────────────────────────────────┘
```

---

## 🚀 Scalability Diagram

```
CURRENT STATE (PART 1):
┌──────────────┐
│   Premium    │──────▶ Find Highest ──────▶ Orange Highlight
└──────────────┘

FUTURE STATE (PART 2):
┌──────────────┐
│   Premium    │───┐
└──────────────┘   │
┌──────────────┐   │
│    Delta     │───┤
└──────────────┘   │
┌──────────────┐   ├──▶ Calculate Score ──▶ Orange Highlight
│    Gamma     │───┤
└──────────────┘   │
┌──────────────┐   │
│    Theta     │───┤
└──────────────┘   │
┌──────────────┐   │
│Custom Formula│───┘
└──────────────┘

SCORING FORMULA (Configurable):
Score = (Premium × W₁) + (|Delta - Target| × W₂) + (Gamma × W₃) + ...

WHERE:
W₁, W₂, W₃ = Weights (set by mentors)
Target = Optimal delta (e.g., 0.3 for ~30% probability)
```

---

## 🎯 Tomorrow's Demo Path

```
START
  │
  ▼
[Show Portfolio Entry]
  │
  ▼
[Click "Get Recommendations"]
  │
  ▼
[Agent 1 runs - show grid]
  │
  ▼
[Explain: "36 options per stock - which is best?"]
  │
  ▼
[Click "🎯 Run Agent 2"]
  │
  ▼
[Wait 2-3 seconds]
  │
  ▼
[Point to orange cells: "These are the best!"]
  │
  ▼
[Expand analysis summary]
  │
  ▼
[Explain the recommendations]
  │
  ▼
[Discuss scalability: "Ready for Delta..."]
  │
  ▼
[Ask: "What formula should we use?"]
  │
  ▼
END (Get mentor feedback)
```

---

**This visual guide should help you understand and explain the system flow! 🎯**
