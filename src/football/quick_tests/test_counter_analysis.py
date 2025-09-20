#!/usr/bin/env python3
"""Quick test to show counter play analysis."""

import sys

sys.path.append("src")
from pathlib import Path
from football2.football.play_loader import PlayLoader
from football2.football.yaml_loader import FormationLoader
from football2.football.play_analyzer import PlayAnalyzer
from football2.football.play_resolution import PlayResolutionEngine

# Load plays
formation_loader = FormationLoader()
play_loader = PlayLoader(formation_loader)
offensive_plays = play_loader.load_plays_from_directory(Path("data/plays/offense"))
defensive_plays = play_loader.load_plays_from_directory(Path("data/plays/defense"))

# Find counter play
counter_play = offensive_plays.get("counter_right")
if counter_play:
    print(f"🔄 COUNTER PLAY ANALYSIS: {counter_play.label}")
    print("=" * 50)

    # Show assignments with tactical significance
    for assign in counter_play.assignments:
        details = assign.details or {}
        if isinstance(details, str):
            details = {}
        extra = ""
        if details.get("scheme") == "pull":
            extra = " 🎯 (PULLING!)"
        elif details.get("technique") == "crack":
            extra = " 🎯 (CRACK!)"
        elif assign.assignment_type.value == "lead_block":
            extra = " 🎯 (LEAD!)"

        scheme = details.get("scheme", "")
        technique = details.get("technique", "")
        print(
            f"  {assign.player_position}: {assign.assignment_type.value} {scheme} {technique}{extra}"
        )

    # Test against a basic defense
    basic_def = list(defensive_plays.values())[0]  # Get any defense
    print(f"\n🛡️ VS {basic_def.label}")

    analyzer = PlayAnalyzer()
    analysis = analyzer.analyze_play_matchup(counter_play, basic_def)

    print(f"\nTactical Analysis: {analysis.net_impact:+d} net impact")
    for adv in analysis.advantages:
        print(f"✅ {adv.description} ({adv.impact:+d})")

    # Show resolution
    engine = PlayResolutionEngine(seed=42)
    result = engine.resolve_play(counter_play, basic_def)
    print(f"\n🎲 Result: {result.outcome.value} for {result.yards_gained:+d} yards")
    print(f"Description: {result.description}")
else:
    print("Counter play not found in offensive plays")
    print("Available plays:", list(offensive_plays.keys()))
