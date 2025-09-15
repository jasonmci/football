#!/usr/bin/env python3
"""
Formation library summary - shows the strategic diversity of our formations.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import football2
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from football2.football.yaml_loader import load_all_formations


def analyze_formation_strategy():
    """Analyze the strategic characteristics of our formation library."""

    formations_path = Path("data/formations")
    all_formations = load_all_formations(formations_path)

    print("🏈 FOOTBALL FORMATION STRATEGY ANALYSIS")
    print("=" * 50)

    # Offensive Analysis
    print("\n📈 OFFENSIVE FORMATIONS")
    print("-" * 25)

    offense = all_formations.get("offense", {})
    for name, formation in offense.items():
        # Count skill positions
        position_counts = {}
        for role in formation.roles.values():
            pos_name = role.position.name
            position_counts[pos_name] = position_counts.get(pos_name, 0) + 1

        wr_count = position_counts.get("WR", 0)
        rb_count = position_counts.get("RB", 0) + position_counts.get("FB", 0)
        te_count = position_counts.get("TE", 0)

        # Determine strategy
        if wr_count >= 4:
            strategy = "📡 PASS HEAVY"
        elif wr_count >= 3:
            strategy = "⚖️  BALANCED"
        elif rb_count >= 2:
            strategy = "🏃 RUN HEAVY"
        else:
            strategy = "🎯 BALANCED"

        print(f"  {formation.name:15} | {wr_count}WR {rb_count}RB {te_count}TE | {strategy}")

    # Defensive Analysis
    print("\n🛡️  DEFENSIVE FORMATIONS")
    print("-" * 25)

    defense = all_formations.get("defense", {})
    for name, formation in defense.items():
        # Count defenders
        position_counts = {}
        for role in formation.roles.values():
            pos_name = role.position.name
            position_counts[pos_name] = position_counts.get(pos_name, 0) + 1

        dl_count = position_counts.get("DL", 0)
        lb_count = position_counts.get("LB", 0)
        db_count = (position_counts.get("CB", 0) +
                   position_counts.get("S", 0) +
                   position_counts.get("NB", 0))

        # Determine strategy
        if dl_count >= 6:
            strategy = "🚧 GOAL LINE"
        elif dl_count >= 5:
            strategy = "💪 RUN STOP"
        elif db_count >= 6:
            strategy = "🌊 PASS DEFENSE"
        elif db_count >= 5:
            strategy = "🎯 PASS COVERAGE"
        else:
            strategy = "⚖️  BALANCED"

        print(f"  {formation.name:15} | {dl_count}DL {lb_count}LB {db_count}DB | {strategy}")

    # Matchup Examples
    print("\n🎮 STRATEGIC MATCHUPS")
    print("-" * 20)
    print("Empty Backfield (5WR) vs Dime Defense (6DB)     - Air Raid!")
    print("Strong I (2RB,2TE) vs Goal Line (6DL,2LB)      - Power Running!")
    print("Shotgun 11 (3WR,1TE) vs 3-4 Defense (4LB)      - Balanced Attack!")
    print("Spread 10 (4WR) vs Nickel (5DB)                - Modern Passing!")

    print("\n📊 FORMATION SUMMARY")
    print("-" * 20)
    print(f"Total Formations: {len(offense) + len(defense)}")
    print(f"Offensive Options: {len(offense)}")
    print(f"Defensive Options: {len(defense)}")
    print("Strategic Diversity: ⭐⭐⭐⭐⭐")


if __name__ == "__main__":
    analyze_formation_strategy()
