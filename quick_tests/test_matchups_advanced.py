#!/usr/bin/env python3
"""
Test script for offense vs defense play matchups.

Demonstrates how offensive and defensive plays interact, showing
strategic advantages and tactical decision-making for board game play.
"""

import sys

sys.path.append("src")

from pathlib import Path
from football2.football.play_loader import PlayLoader
from football2.football.yaml_loader import FormationLoader
from football2.football.matchup_analyzer import FormationMatchupAnalyzer


def load_all_plays():
    """Load all available offensive and defensive plays."""
    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)

    # Load plays
    offense_plays = play_loader.load_plays_from_directory(Path("data/plays/offense"))
    defense_plays = play_loader.load_plays_from_directory(Path("data/plays/defense"))

    print(f"📦 Loaded {len(offense_plays)} offensive plays")
    print(f"🛡️  Loaded {len(defense_plays)} defensive plays")

    return offense_plays, defense_plays, formation_loader, play_loader


def analyze_formation_matchup(off_play, def_play, analyzer):
    """Analyze the formation matchup between offensive and defensive plays."""
    try:
        matchup = analyzer.analyze_matchup(
            off_play.base_formation, def_play.base_formation
        )
        return matchup
    except ValueError:
        return None


def test_strategic_matchups():
    """Test various strategic matchups between plays."""
    print("🏈 OFFENSIVE vs DEFENSIVE PLAY MATCHUPS")
    print("=" * 60)

    offense_plays, defense_plays, formation_loader, play_loader = load_all_plays()
    analyzer = FormationMatchupAnalyzer()

    # Test specific interesting matchups
    matchup_scenarios = [
        # Power running vs run stopping
        {
            "name": "POWER vs RUN DEFENSE",
            "offense": "power_left",
            "defense": "bear46_run_commit",
            "scenario": "Goal line situation - offense needs 2 yards",
        },
        # Quick passing vs pressure
        {
            "name": "QUICK PASS vs BLITZ",
            "offense": "empty_slants",
            "defense": "nickel_doubleA_cover2",
            "scenario": "3rd and 8 - offense needs first down",
        },
        # Deep passing vs coverage
        {
            "name": "DEEP SHOTS vs PREVENT",
            "offense": "four_verts",
            "defense": "prevent_quarters",
            "scenario": "2-minute drill - offense down by 7",
        },
        # Motion vs reaction
        {
            "name": "MOTION vs ADJUSTMENT",
            "offense": "smash_concept_motion",
            "defense": "nickel_zone_blitz_showA",
            "scenario": "Red zone - offense at 15-yard line",
        },
        # Balanced vs balanced
        {
            "name": "BALANCED ATTACK vs BASE",
            "offense": "inside_zone_right",
            "defense": "43_cover3_base",
            "scenario": "1st and 10 - feeling out the defense",
        },
    ]

    for i, scenario in enumerate(matchup_scenarios, 1):
        print(f"\n🎯 MATCHUP {i}: {scenario['name']}")
        print("-" * 45)
        print(f"📍 Scenario: {scenario['scenario']}")

        off_play = offense_plays.get(scenario["offense"])
        def_play = defense_plays.get(scenario["defense"])

        if not off_play or not def_play:
            print(f"❌ Missing play: {scenario['offense']} or {scenario['defense']}")
            continue

        print(f"⚡ Offense: {off_play.label} ({off_play.base_formation})")
        print(f"🛡️  Defense: {def_play.label} ({def_play.base_formation})")

        # Analyze formation advantage
        matchup = analyze_formation_matchup(off_play, def_play, analyzer)

        if matchup:
            advantage_symbols = {
                3: "🟢🟢 MAJOR ADV",
                1: "🟢 MINOR ADV",
                0: "⚪ NEUTRAL",
                -1: "🔴 MINOR DIS",
                -3: "🔴🔴 MAJOR DIS",
            }

            run_adv = advantage_symbols.get(matchup.run_advantage.value, "❓")
            pass_adv = advantage_symbols.get(matchup.pass_advantage.value, "❓")
            overall_adv = advantage_symbols.get(matchup.overall_advantage.value, "❓")

            print("📊 Formation Analysis:")
            print(f"   Run Game: {run_adv}")
            print(f"   Pass Game: {pass_adv}")
            print(f"   Overall: {overall_adv}")

            if matchup.key_factors:
                print("🔍 Key Factors:")
                for factor in matchup.key_factors:
                    print(f"   • {factor}")

        # Analyze play characteristics
        print("🎮 Play Characteristics:")

        # Offensive play analysis
        off_assignments = {}
        for assignment in off_play.assignments:
            assignment_type = assignment.assignment_type.value
            off_assignments[assignment_type] = (
                off_assignments.get(assignment_type, 0) + 1
            )

        print(
            f"   Offense: {', '.join([f'{k}({v})' for k, v in off_assignments.items()])}"
        )

        # Defensive play analysis
        def_assignments = {}
        for assignment in def_play.assignments:
            assignment_type = assignment.assignment_type.value
            def_assignments[assignment_type] = (
                def_assignments.get(assignment_type, 0) + 1
            )

        print(
            f"   Defense: {', '.join([f'{k}({v})' for k, v in def_assignments.items()])}"
        )

        # Pre-snap dynamics
        pre_snap_info = []
        if off_play.pre_snap_shifts:
            pre_snap_info.append(f"OFF shifts: {len(off_play.pre_snap_shifts)}")
        if off_play.motion:
            pre_snap_info.append(f"Motion: {off_play.motion.player_position}")
        if def_play.pre_snap_shifts:
            pre_snap_info.append(f"DEF shifts: {len(def_play.pre_snap_shifts)}")

        if pre_snap_info:
            print(f"⚡ Pre-snap: {', '.join(pre_snap_info)}")


def show_play_inventory():
    """Show inventory of all available plays by formation."""
    print("\n\n📋 COMPLETE PLAY INVENTORY")
    print("=" * 50)

    offense_plays, defense_plays, _, _ = load_all_plays()

    # Group offensive plays by formation
    print("\n🏃 OFFENSIVE PLAYS BY FORMATION:")
    off_by_formation = {}
    for play in offense_plays.values():
        formation = play.base_formation
        if formation not in off_by_formation:
            off_by_formation[formation] = []
        off_by_formation[formation].append(f"{play.name} ({play.play_type})")

    for formation, plays in sorted(off_by_formation.items()):
        print(f"   {formation}: {len(plays)} plays")
        for play in plays:
            print(f"     • {play}")

    # Group defensive plays by formation
    print("\n🛡️  DEFENSIVE PLAYS BY FORMATION:")
    def_by_formation = {}
    for play in defense_plays.values():
        formation = play.base_formation
        if formation not in def_by_formation:
            def_by_formation[formation] = []
        def_by_formation[formation].append(f"{play.name} ({', '.join(play.tags)})")

    for formation, plays in sorted(def_by_formation.items()):
        print(f"   {formation}: {len(plays)} plays")
        for play in plays:
            print(f"     • {play}")


if __name__ == "__main__":
    print("🎲 FOOTBALL PLAY MATCHUP ANALYZER")
    print("Strategic warfare on the gridiron!")
    print()

    test_strategic_matchups()
    show_play_inventory()

    print("\n\n🏆 MATCHUP INSIGHTS:")
    print("• Power running works best against light coverage")
    print("• Quick passing beats blitz timing")
    print("• Deep routes challenge prevent defense patience")
    print("• Motion creates defensive communication issues")
    print("• Pre-snap shifts affect gap assignments")
    print("• Formation advantages matter but execution decides games!")
