#!/usr/bin/env python3
"""Test trap and power plays with the enhanced analyzer."""

import sys
sys.path.append('src')
from pathlib import Path
from football2.football.play_loader import PlayLoader
from football2.football.yaml_loader import FormationLoader
from football2.football.play_analyzer import PlayAnalyzer
from football2.football.play_resolution import PlayResolutionEngine

def test_new_run_concepts():
    """Test trap and power plays."""
    print("🏈 TESTING NEW RUN CONCEPTS")
    print("=" * 50)

    # Load plays
    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)
    offensive_plays = play_loader.load_plays_from_directory(Path('data/plays/offense'))
    defensive_plays = play_loader.load_plays_from_directory(Path('data/plays/defense'))

    # Get a basic defense to test against
    basic_def = list(defensive_plays.values())[0]

    # Test trap plays
    trap_plays = [name for name in offensive_plays.keys() if 'trap' in name.lower()]
    power_plays = [name for name in offensive_plays.keys() if 'power' in name.lower()]

    analyzer = PlayAnalyzer()
    engine = PlayResolutionEngine(seed=42)

    for play_name in trap_plays:
        test_run_concept(offensive_plays[play_name], basic_def, analyzer, engine, "TRAP")

    for play_name in power_plays:
        test_run_concept(offensive_plays[play_name], basic_def, analyzer, engine, "POWER")

def test_run_concept(off_play, def_play, analyzer, engine, concept_type):
    """Test a specific run concept."""
    print(f"\n🔥 {concept_type} CONCEPT: {off_play.label}")
    print("-" * 40)

    # Show key assignments
    print("Key Assignments:")
    for assign in off_play.assignments:
        details = assign.details or {}
        if isinstance(details, str):
            details = {}

        # Highlight tactical elements
        highlights = []
        if details.get("scheme") == "pull":
            highlights.append("🔄 PULLING")
        if details.get("technique") == "trap_block":
            highlights.append("🪤 TRAP")
        if details.get("technique") == "invite_penetration":
            highlights.append("🚪 INVITE")
        if details.get("scheme") == "double_team":
            highlights.append("💪 DOUBLE")
        if assign.assignment_type.value == "lead_block":
            highlights.append("🏃 LEAD")

        if highlights:
            print(f"  {assign.player_position}: {assign.assignment_type.value} {' '.join(highlights)}")

    # Analyze tactical advantages
    analysis = analyzer.analyze_play_matchup(off_play, def_play)

    print(f"\nTactical Analysis: {analysis.net_impact:+d} net advantage")
    for adv in analysis.advantages:
        print(f"  ✅ {adv.description} ({adv.impact:+d})")

    # Run resolution
    result = engine.resolve_play(off_play, def_play, {
        "down": 2,
        "distance": 5,
        "field_position": 35
    })

    print(f"\n🎲 Resolution: {result.outcome.value} for {result.yards_gained:+d} yards")
    print(f"   Total: {result.final_total} (dice: {result.dice_roll} + mods: {result.total_modifier})")
    print(f"   {result.description}")

if __name__ == "__main__":
    test_new_run_concepts()

    print("\n\n🎯 TRAP VS POWER CONCEPTS")
    print("=" * 50)
    print("🪤 TRAP PLAYS:")
    print("  • Use deception - let defender penetrate, then trap")
    print("  • Guard 'invites penetration' then pulling guard traps")
    print("  • Creates misdirection and confusion")
    print("  • Best vs aggressive defensive tackles")
    print("\n💪 POWER PLAYS:")
    print("  • Use brute force - double teams and extra blockers")
    print("  • Multiple combo blocks create push")
    print("  • Fullback provides extra gap protection")
    print("  • Best vs lighter, speed-based defenses")
    print("\n🎮 Both concepts now provide realistic tactical advantages!")
