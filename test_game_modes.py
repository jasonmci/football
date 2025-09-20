#!/usr/bin/env python3
"""
Advanced Play Resolution Configuration Demo

Shows how to create different "game modes" with varying difficulty,
scoring tendencies, and strategic emphasis through configuration.
"""

import sys
sys.path.append('src')

from pathlib import Path
from football.play_loader import PlayLoader
from football.yaml_loader import FormationLoader
from football.play_resolution import (
    PlayResolutionEngine, ResolutionConfig, PlayOutcome, PlayType
)


def create_arcade_config() -> ResolutionConfig:
    """High-scoring, explosive play configuration for arcade-style games."""
    config = ResolutionConfig()

    # More explosive dice
    config.base_dice = {
        PlayType.RUN: "3d6",      # More dice = higher variance
        PlayType.PASS: "2d10",    # Higher ceiling for passes
        PlayType.SPECIAL: "1d20"  # Wild card potential
    }

    # Lower thresholds for big plays
    config.thresholds[PlayOutcome.EXPLOSIVE_SUCCESS] = 14
    config.thresholds[PlayOutcome.BIG_SUCCESS] = 11
    config.thresholds[PlayOutcome.SUCCESS] = 8

    # Bigger yardage ranges
    config.yardage_ranges[PlayOutcome.EXPLOSIVE_SUCCESS] = (20, 60)
    config.yardage_ranges[PlayOutcome.BIG_SUCCESS] = (12, 25)

    # Formation advantages matter more
    config.formation_bonuses = {3: +8, 1: +4, 0: 0, -1: -4, -3: -8}

    return config


def create_simulation_config() -> ResolutionConfig:
    """Realistic NFL-style configuration with moderate scoring."""
    config = ResolutionConfig()

    # Standard dice but more conservative thresholds
    config.thresholds[PlayOutcome.EXPLOSIVE_SUCCESS] = 20
    config.thresholds[PlayOutcome.BIG_SUCCESS] = 16
    config.thresholds[PlayOutcome.SUCCESS] = 13

    # Realistic yardage ranges
    config.yardage_ranges[PlayOutcome.EXPLOSIVE_SUCCESS] = (12, 30)
    config.yardage_ranges[PlayOutcome.BIG_SUCCESS] = (6, 12)
    config.yardage_ranges[PlayOutcome.SUCCESS] = (3, 6)

    # Moderate formation impact
    config.formation_bonuses = {3: +3, 1: +1, 0: 0, -1: -1, -3: -3}

    return config


def create_defensive_slugfest_config() -> ResolutionConfig:
    """Low-scoring, defensive-minded configuration."""
    config = ResolutionConfig()

    # Lower variance dice
    config.base_dice = {
        PlayType.RUN: "1d8",
        PlayType.PASS: "1d10",
        PlayType.SPECIAL: "1d8"
    }

    # Very high thresholds
    config.thresholds[PlayOutcome.EXPLOSIVE_SUCCESS] = 25
    config.thresholds[PlayOutcome.BIG_SUCCESS] = 20
    config.thresholds[PlayOutcome.SUCCESS] = 16
    config.thresholds[PlayOutcome.MODERATE_GAIN] = 12

    # Conservative yardage
    config.yardage_ranges[PlayOutcome.EXPLOSIVE_SUCCESS] = (8, 18)
    config.yardage_ranges[PlayOutcome.BIG_SUCCESS] = (4, 8)
    config.yardage_ranges[PlayOutcome.SUCCESS] = (2, 4)
    config.yardage_ranges[PlayOutcome.MODERATE_GAIN] = (1, 2)

    return config


def run_game_mode_comparison():
    """Compare the same plays across different game modes."""
    print("🎮 GAME MODE COMPARISON")
    print("=" * 50)

    # Load plays
    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)
    offense_plays = play_loader.load_plays_from_directory(Path("data/plays/offense"))
    defense_plays = play_loader.load_plays_from_directory(Path("data/plays/defense"))

    # Create engines with different configs
    engines = {
        "🕹️  Arcade": PlayResolutionEngine(create_arcade_config(), seed=100),
        "🏈 Simulation": PlayResolutionEngine(create_simulation_config(), seed=100),
        "🛡️  Slugfest": PlayResolutionEngine(create_defensive_slugfest_config(), seed=100)
    }

    # Test the same play in all modes
    test_scenarios = [
        {
            "name": "Power Running",
            "offense": "power_left",
            "defense": "43_cover3_base",
            "situation": {"down": 1, "distance": 10, "field_position": 50}
        },
        {
            "name": "Deep Passing",
            "offense": "four_verts",
            "defense": "dime_quarters_drop8",
            "situation": {"down": 2, "distance": 10, "field_position": 30}
        },
        {
            "name": "Short Yardage",
            "offense": "singleback_dive",
            "defense": "bear46_run_commit",
            "situation": {"down": 3, "distance": 1, "field_position": 5}
        }
    ]

    for scenario in test_scenarios:
        print(f"\n🎯 {scenario['name']} Scenario")
        print("-" * 30)

        off_play = offense_plays[scenario['offense']]
        def_play = defense_plays[scenario['defense']]

        print(f"   {off_play.label} vs {def_play.label}")

        for mode_name, engine in engines.items():
            # Run multiple attempts to show variance
            results = []
            for _ in range(5):
                result = engine.resolve_play(off_play, def_play, scenario['situation'])
                results.append(result.yards_gained)

            avg_yards = sum(results) / len(results)
            print(f"   {mode_name}: {results} (avg: {avg_yards:.1f})")


def demonstrate_situational_awareness():
    """Show how different situations affect outcomes."""
    print("\n\n⏱️  SITUATIONAL AWARENESS")
    print("=" * 35)

    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)
    offense_plays = play_loader.load_plays_from_directory(Path("data/plays/offense"))
    defense_plays = play_loader.load_plays_from_directory(Path("data/plays/defense"))

    engine = PlayResolutionEngine(seed=200)

    off_play = offense_plays["inside_zone_right"]
    def_play = defense_plays["43_cover3_base"]

    situations = [
        {"name": "1st & 10 (Midfield)", "down": 1, "distance": 10, "field_position": 50},
        {"name": "3rd & 1 (Goal Line)", "down": 3, "distance": 1, "field_position": 2},
        {"name": "2nd & Long", "down": 2, "distance": 15, "field_position": 30},
        {"name": "4th & 2", "down": 4, "distance": 2, "field_position": 40},
    ]

    print(f"\n🏃 {off_play.label} vs {def_play.label}")

    for situation in situations:
        sit_data = {k: v for k, v in situation.items() if k != "name"}
        result = engine.resolve_play(off_play, def_play, sit_data)

        print(f"\n📍 {situation['name']}:")
        print(f"   {result.description}")
        print(f"   Dice: {result.dice_roll} + {result.total_modifier} = {result.final_total}")

        # Show situation-specific modifier
        sit_mod = result.details["modifiers"].get("situation", 0)
        if sit_mod != 0:
            sign = "+" if sit_mod > 0 else ""
            print(f"   Situation modifier: {sign}{sit_mod}")


def show_configuration_options():
    """Display the full range of configuration options."""
    print("\n\n⚙️  CONFIGURATION SYSTEM")
    print("=" * 40)

    print("🎲 Dice Expressions:")
    print("   • Run plays: 1d6, 2d6, 3d6, 1d8, 2d8...")
    print("   • Pass plays: 1d8, 2d8, 1d10, 2d10...")
    print("   • Special: 1d12, 1d20, 2d10...")

    print("\n🎯 Outcome Thresholds:")
    print("   • Explosive Success: 14-25 (lower = more explosive)")
    print("   • Big Success: 11-20")
    print("   • Success: 8-16")
    print("   • Each threshold can be independently tuned")

    print("\n📏 Yardage Ranges:")
    print("   • Explosive: (8-18) to (20-60) yards")
    print("   • Big Success: (4-8) to (12-25) yards")
    print("   • Success: (2-4) to (4-7) yards")

    print("\n⚖️  Formation Bonuses:")
    print("   • Major Advantage: +3 to +8")
    print("   • Minor Advantage: +1 to +4")
    print("   • Neutral: 0")
    print("   • Disadvantages: negative values")

    print("\n🏈 Situational Modifiers:")
    print("   • Goal line: +2 (easier to score)")
    print("   • 3rd & short: +2 (determination)")
    print("   • 3rd & long: -2 (desperation)")
    print("   • 4th down: -3 (pressure)")

    print("\n🎮 Game Mode Examples:")
    print("   🕹️  Arcade: High variance, big plays, explosive action")
    print("   🏈 Simulation: Realistic NFL-style balanced gameplay")
    print("   🛡️  Slugfest: Low-scoring defensive battles")
    print("   🎯 Custom: Mix and match any settings")


if __name__ == "__main__":
    run_game_mode_comparison()
    demonstrate_situational_awareness()
    show_configuration_options()

    print("\n\n🌟 KEY BENEFITS:")
    print("• One engine, infinite game styles through configuration")
    print("• Realistic football strategy with dice excitement")
    print("• Formation advantages translate to mechanical benefits")
    print("• Situational awareness affects every play resolution")
    print("• Computer speed allows complex multi-roll resolution")
    print("• Configurable for any desired game balance")
