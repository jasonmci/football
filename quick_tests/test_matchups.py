#!/usr/bin/env python3
"""
Test script for formation matchup analysis.

Demonstrates strategic analysis between offensive and defensive formations,
showing how the system can provide tactical insights for board game play.
"""

import sys

sys.path.append("src")

from football2.football.matchup_analyzer import (
    FormationMatchupAnalyzer,
    MatchupAdvantage,
)


def print_advantage(advantage: MatchupAdvantage) -> str:
    """Convert advantage enum to colored display string."""
    symbols = {
        MatchupAdvantage.MAJOR_ADVANTAGE: "🟢🟢",
        MatchupAdvantage.MINOR_ADVANTAGE: "🟢",
        MatchupAdvantage.NEUTRAL: "⚪",
        MatchupAdvantage.MINOR_DISADVANTAGE: "🔴",
        MatchupAdvantage.MAJOR_DISADVANTAGE: "🔴🔴",
    }
    return f"{symbols[advantage]} {advantage.name.replace('_', ' ')}"


def test_specific_matchups():
    """Test some interesting specific matchups."""
    analyzer = FormationMatchupAnalyzer()

    print("🏈 FORMATION MATCHUP ANALYSIS")
    print("=" * 50)

    # Classic power vs power matchup
    print("\n💪 POWER VS POWER: I-Formation vs 3-4 Defense")
    print("-" * 45)
    result = analyzer.analyze_matchup("i_form", "34_defense")
    print(f"Run Game: {print_advantage(result.run_advantage)}")
    print(f"Pass Game: {print_advantage(result.pass_advantage)}")
    print(f"Overall: {print_advantage(result.overall_advantage)}")
    print("Key Factors:")
    for factor in result.key_factors:
        print(f"  • {factor}")
    print(f"Recommended Plays: {[play.value for play in result.recommended_plays]}")

    # Spread vs nickel - modern matchup
    print("\n🏃 SPEED VS COVERAGE: Spread vs Nickel")
    print("-" * 40)
    result = analyzer.analyze_matchup("spread_10", "nickel")
    print(f"Run Game: {print_advantage(result.run_advantage)}")
    print(f"Pass Game: {print_advantage(result.pass_advantage)}")
    print(f"Overall: {print_advantage(result.overall_advantage)}")
    print("Key Factors:")
    for factor in result.key_factors:
        print(f"  • {factor}")
    print(f"Recommended Plays: {[play.value for play in result.recommended_plays]}")

    # Empty backfield vs prevent - obvious passing down
    print("\n🎯 OBVIOUS PASS: Empty Backfield vs Prevent")
    print("-" * 45)
    result = analyzer.analyze_matchup("empty_backfield", "prevent_defense")
    print(f"Run Game: {print_advantage(result.run_advantage)}")
    print(f"Pass Game: {print_advantage(result.pass_advantage)}")
    print(f"Overall: {print_advantage(result.overall_advantage)}")
    print("Key Factors:")
    for factor in result.key_factors:
        print(f"  • {factor}")
    print(f"Recommended Plays: {[play.value for play in result.recommended_plays]}")

    # Goal line scenario
    print("\n🥅 GOAL LINE: Strong I vs Goal Line Defense")
    print("-" * 45)
    result = analyzer.analyze_matchup("strong_i", "goalline_defense")
    print(f"Run Game: {print_advantage(result.run_advantage)}")
    print(f"Pass Game: {print_advantage(result.pass_advantage)}")
    print(f"Overall: {print_advantage(result.overall_advantage)}")
    print("Key Factors:")
    for factor in result.key_factors:
        print(f"  • {factor}")
    print(f"Recommended Plays: {[play.value for play in result.recommended_plays]}")


def create_matchup_matrix():
    """Create a complete matchup matrix showing all combinations."""
    analyzer = FormationMatchupAnalyzer()

    offensive_formations = [
        "empty_backfield",
        "spread_10",
        "i_form",
        "strong_i",
        "pistol_11",
        "shotgun_11",
        "singleback_11",
    ]
    defensive_formations = [
        "34_defense",
        "dime",
        "prevent_defense",
        "goalline_defense",
        "base43",
        "nickel",
        "bear46",
    ]

    print("\n\n📊 COMPLETE MATCHUP MATRIX")
    print("=" * 60)
    print("Overall advantages (Offense perspective):")
    print("🟢🟢 = Major Advantage  🟢 = Minor Advantage  ⚪ = Neutral")
    print("🔴 = Minor Disadvantage  🔴🔴 = Major Disadvantage")
    print()

    # Header
    header = "Formation".ljust(15)
    for def_form in defensive_formations:
        header += def_form[:8].ljust(10)
    print(header)
    print("-" * len(header))

    # Matrix rows
    for off_form in offensive_formations:
        row = off_form[:14].ljust(15)
        for def_form in defensive_formations:
            result = analyzer.analyze_matchup(off_form, def_form)
            symbol = {
                MatchupAdvantage.MAJOR_ADVANTAGE: "🟢🟢",
                MatchupAdvantage.MINOR_ADVANTAGE: "🟢",
                MatchupAdvantage.NEUTRAL: "⚪",
                MatchupAdvantage.MINOR_DISADVANTAGE: "🔴",
                MatchupAdvantage.MAJOR_DISADVANTAGE: "🔴🔴",
            }[result.overall_advantage]
            row += symbol.ljust(10)
        print(row)


def show_formation_profiles():
    """Display the strength profiles of all formations."""
    analyzer = FormationMatchupAnalyzer()

    print("\n\n📋 FORMATION STRENGTH PROFILES")
    print("=" * 50)

    print("\n🏃 OFFENSIVE FORMATIONS:")
    print("-" * 25)
    offensive_formations = [
        "empty_backfield",
        "spread_10",
        "i_form",
        "strong_i",
        "pistol_11",
        "shotgun_11",
        "singleback_11",
    ]

    for formation in offensive_formations:
        profile = analyzer.get_formation_summary(formation, is_offense=True)
        if profile:
            print(f"\n{profile['name'].upper().replace('_', ' ')}")
            print(
                f"  Run Block: {profile['run_blocking']}/5  Pass Pro: {profile['pass_protection']}/5"
            )
            print(
                f"  Routes: {profile['route_diversity']}/5     Misdirect: {profile['misdirection']}/5"
            )
            print(f"  Best For: {', '.join(profile['optimal_plays'])}")

    print("\n\n🛡️  DEFENSIVE FORMATIONS:")
    print("-" * 25)
    defensive_formations = [
        "34_defense",
        "dime",
        "prevent_defense",
        "goalline_defense",
        "base43",
        "nickel",
        "bear46",
    ]

    for formation in defensive_formations:
        profile = analyzer.get_formation_summary(formation, is_offense=False)
        if profile:
            print(f"\n{profile['name'].upper().replace('_', ' ')}")
            print(
                f"  Run Def: {profile['run_defense']}/5    Pass Rush: {profile['pass_rush']}/5"
            )
            print(
                f"  Coverage: {profile['pass_coverage']}/5   Gap Ctrl: {profile['gap_control']}/5"
            )
            print(f"  Counters: {', '.join(profile['counters'])}")


if __name__ == "__main__":
    print("🎲 FOOTBALL FORMATION STRATEGY ANALYZER")
    print("Bringing board game tactics to digital football!")
    print()

    test_specific_matchups()
    create_matchup_matrix()
    show_formation_profiles()

    print("\n\n🎯 STRATEGIC INSIGHTS:")
    print("• Empty backfield struggles against heavy pass rush")
    print("• I-Formation excels in power running situations")
    print("• Spread formations create mismatches in coverage")
    print("• Goal line defense stops everything but gives up big plays")
    print("• Nickel balances run/pass but can be exploited by power")
