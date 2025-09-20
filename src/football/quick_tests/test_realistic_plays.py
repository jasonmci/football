#!/usr/bin/env python3
"""
Test script to verify realistic play outcomes after tuning.
Tests trap plays and power plays to ensure realistic yardage gains.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import necessary modules - ALL from football2
from football2.football.play_resolution import (
    PlayResolutionEngine,
    create_realistic_config,
)
from football2.football.plays import FootballPlay
import statistics
import yaml


def create_simple_defensive_play():
    """Create a simple defensive play for testing."""
    return FootballPlay(
        name="base_defense",
        label="Base Defense",
        play_type="defense",
        base_formation="4-3",
        personnel=["Base"],
        assignments=[],
    )


def load_play_yaml(team: str, play_name: str):
    """Load a play YAML file directly."""
    play_file = (
        f"/Users/jasonmcinerney/repos/football/data/plays/{team}/{play_name}.yaml"
    )
    with open(play_file, "r") as f:
        return yaml.safe_load(f)


def test_realistic_plays():
    """Test trap and power plays for realistic outcomes."""

    # Use realistic config
    config = create_realistic_config()
    resolution_engine = PlayResolutionEngine(config)

    # Create a simple defensive play for all tests
    defense = create_simple_defensive_play()

    # Test scenarios
    test_scenarios = [
        {
            "name": "Trap Right - 1st & 10",
            "play_file": "trap_right",
            "situation": {"down": 1, "distance": 10, "field_position": 25},
        },
        {
            "name": "Power Right - 3rd & 2",
            "play_file": "power_right",
            "situation": {"down": 3, "distance": 2, "field_position": 45},
        },
    ]

    print("🏈 Testing Realistic Play Outcomes")
    print("=" * 50)

    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"   Play: {scenario['play_file']}")
        print(
            f"   Situation: {scenario['situation']['down']} & {scenario['situation']['distance']}"
        )

        try:
            # Load the offensive play YAML
            play_data = load_play_yaml("offense", scenario["play_file"])

            # Convert to FootballPlay object
            offense = FootballPlay(
                name=scenario["play_file"],
                label=play_data.get("label", scenario["play_file"].title()),
                play_type="run",
                base_formation=play_data.get("formation", "I-formation"),
                personnel=play_data.get("personnel", ["I-formation"]),
                assignments=play_data.get("assignments", []),
            )

            results = []
            outcomes = []

            # Run 20 simulations
            for i in range(20):
                try:
                    # Resolve the play
                    result = resolution_engine.resolve_play(
                        offensive_play=offense,
                        defensive_play=defense,
                        situation=scenario["situation"],
                    )

                    results.append(result.yards_gained)
                    outcomes.append(result.outcome.name)

                except Exception as e:
                    print(f"   ❌ Error on simulation {i+1}: {e}")
                    continue

            if results:
                avg_yards = statistics.mean(results)
                median_yards = statistics.median(results)
                min_yards = min(results)
                max_yards = max(results)

                print(f"   📊 Results from {len(results)} simulations:")
                print(f"      Average: {avg_yards:.1f} yards")
                print(f"      Median:  {median_yards:.1f} yards")
                print(f"      Range:   {min_yards} to {max_yards} yards")

                # Count outcomes
                outcome_counts = {}
                for outcome in outcomes:
                    outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

                print("   🎯 Outcome distribution:")
                for outcome, count in sorted(outcome_counts.items()):
                    percentage = (count / len(outcomes)) * 100
                    print(f"      {outcome}: {count} ({percentage:.0f}%)")

                # Realism check
                if avg_yards > 10:
                    print(
                        f"   ⚠️  HIGH AVERAGE: {avg_yards:.1f} yards may be unrealistic"
                    )
                elif avg_yards > 6:
                    print(
                        f"   ✅ GOOD AVERAGE: {avg_yards:.1f} yards is realistic for quality run"
                    )
                else:
                    print(f"   ✅ CONSERVATIVE: {avg_yards:.1f} yards is realistic")

                if max_yards > 25:
                    print(f"   ⚠️  LONG PLAY: {max_yards} yard max may be too explosive")
                else:
                    print(
                        f"   ✅ MAX REALISTIC: {max_yards} yard maximum is reasonable"
                    )

        except Exception as e:
            print(f"   ❌ Failed to load play '{scenario['play_file']}': {e}")


if __name__ == "__main__":
    test_realistic_plays()
