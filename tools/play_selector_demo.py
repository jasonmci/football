#!/usr/bin/env python3
"""
Demo of Interactive Play Selector - Shows example simulation without user input
"""

import sys
import yaml
from pathlib import Path

# from typing import Dict, List, Any, Optional
import random

# Add the src directory to Python path

from football.enhanced_resolution import (
    EnhancedResolutionEngine,
)

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class PlaySelectorDemo:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.engine = EnhancedResolutionEngine()

    def list_plays(self, play_type):
        """List available plays of given type (offense/defense)"""
        plays_dir = self.repo_root / "data" / "plays" / play_type
        play_files = [f.stem for f in plays_dir.glob("*.yaml")]
        return sorted(play_files)

    def load_play_data(self, play_name, play_type):
        """Load play data from YAML file"""
        try:
            play_file = (
                self.repo_root / "data" / "plays" / play_type / f"{play_name}.yaml"
            )
            with open(play_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading play {play_name}: {e}")
            return None

    def show_play_details(self, play_name, play_type):
        """Show details of the selected play"""
        play_data = self.load_play_data(play_name, play_type)
        if not play_data:
            return

        print(f"\n{play_type.upper()} PLAY DETAILS:")
        print("=" * 50)
        print(f"Name: {play_data.get('name', play_name)}")
        print(f"Formation: {play_data.get('formation', 'Unknown')}")
        print(f"Personnel: {play_data.get('personnel', 'Unknown')}")

        if "description" in play_data:
            print(f"Description: {play_data['description']}")

        if "tactical_advantages" in play_data:
            print(f"Tactical Advantages: {', '.join(play_data['tactical_advantages'])}")

        if "execution_notes" in play_data:
            print(f"Execution: {play_data['execution_notes']}")

    def _simulate_single_play(self, offense_data, defense_data):
        """Simple simulation logic for a single play"""
        play_type = self._determine_play_type(offense_data)
        off_advantages = offense_data.get("tactical_advantages", [])
        def_advantages = defense_data.get("tactical_advantages", [])

        if play_type == "run":
            base_yards, outcomes, weights = self._run_play_adjustments(
                off_advantages, def_advantages
            )
        elif play_type == "pass":
            base_yards, outcomes, weights = self._pass_play_adjustments(
                off_advantages, def_advantages
            )
        else:
            base_yards, outcomes, weights = self._special_play_adjustments()

        outcome = random.choices(outcomes, weights=weights)[0]

        # Adjust yards based on outcome
        if outcome in ["stuffed", "failed", "sack"]:
            base_yards = min(base_yards, random.randint(-3, 1))
        elif outcome in ["big_gain", "big_play"]:
            base_yards = max(base_yards, random.randint(8, 25))
        elif outcome in ["fumble", "interception", "turnover"]:
            base_yards = random.randint(-5, 0)

        return {"yards": base_yards, "outcome": outcome}

    def _run_play_adjustments(self, off_advantages, def_advantages):
        base_yards = random.randint(-2, 8)
        outcomes = ["successful_run", "stuffed", "big_gain", "fumble"]
        weights = [60, 25, 13, 2]

        if "goal_line_power" in off_advantages and "goal_line_stop" in def_advantages:
            base_yards -= 1  # Even matchup
        elif (
            "outside_speed" in off_advantages
            and "edge_discipline" not in def_advantages
        ):
            base_yards += 2  # Advantage to offense
        elif "gap_control" in def_advantages and "power_running" in off_advantages:
            base_yards -= 1  # Advantage to defense

        return base_yards, outcomes, weights

    def _pass_play_adjustments(self, off_advantages, def_advantages):
        base_yards = random.randint(-1, 12)
        outcomes = ["complete", "incomplete", "interception", "sack"]
        weights = [45, 40, 8, 7]

        if "deep_threat" in off_advantages and "deep_coverage" in def_advantages:
            base_yards += 1  # Even but slight edge to offense
        elif "quick_timing" in off_advantages and "pass_rush" in def_advantages:
            weights = [50, 35, 5, 10]  # More sacks
        elif "mismatch_creation" in off_advantages:
            base_yards += 3  # Good advantage

        return base_yards, outcomes, weights

    def _special_play_adjustments(self):
        base_yards = random.randint(-3, 15)
        outcomes = ["successful", "failed", "turnover", "big_play"]
        weights = [50, 35, 10, 5]
        return base_yards, outcomes, weights

    def _determine_play_type(self, offense_data):
        """Determine if play is run, pass, or special based on play data"""
        name = offense_data.get("name", "").lower()
        description = offense_data.get("description", "").lower()
        execution = offense_data.get("execution_notes", "").lower()

        # Check for run indicators
        run_keywords = [
            "run",
            "zone",
            "power",
            "draw",
            "sweep",
            "dive",
            "trap",
            "counter",
        ]
        pass_keywords = [
            "pass",
            "slant",
            "route",
            "throw",
            "reception",
            "vert",
            "screen",
        ]

        text_to_check = f"{name} {description} {execution}"

        run_count = sum(1 for keyword in run_keywords if keyword in text_to_check)
        pass_count = sum(1 for keyword in pass_keywords if keyword in text_to_check)

        if run_count > pass_count:
            return "run"
        elif pass_count > run_count:
            return "pass"
        else:
            return "special"

    def run_demo_simulation(self, offensive_play, defensive_play):
        """Run a demo simulation with the specified plays"""
        offense_data = self.load_play_data(offensive_play, "offense")
        defense_data = self.load_play_data(defensive_play, "defense")

        if not offense_data or not defense_data:
            print("Could not load play data")
            return None

        print(f"\n{'='*60}")
        print(
            f"DEMO SIMULATION: {offensive_play.replace('_', ' ').title()} vs {defensive_play.replace('_', ' ').title()}"
        )
        print(f"{'='*60}")

        # Show play details
        self.show_play_details(offensive_play, "offense")
        self.show_play_details(defensive_play, "defense")

        print(f"\n{'SIMULATION RESULTS':^60}")
        print("-" * 60)

        # Run multiple simulations to show variance
        results = []
        for i in range(10):
            result = self._simulate_single_play(offense_data, defense_data)
            results.append(result)
            outcome = result["outcome"]
            yards = result["yards"]
            print(f"Sim {i+1:2d}: {yards:+3d} yards - {outcome}")

        # Show summary statistics
        total_yards = sum(r["yards"] for r in results)
        avg_yards = total_yards / len(results)
        max_yards = max(r["yards"] for r in results)
        min_yards = min(r["yards"] for r in results)

        # Count outcomes
        outcomes = {}
        for result in results:
            outcomes[result["outcome"]] = outcomes.get(result["outcome"], 0) + 1

        print("-" * 60)
        print(f"SUMMARY ({len(results)} simulations):")
        print(f"  Average: {avg_yards:+5.1f} yards")
        print(f"  Range: {min_yards:+3d} to {max_yards:+3d} yards")
        print(f"  Total: {total_yards:+4d} yards")

        print("\nOUTCOME BREAKDOWN:")
        for outcome, count in sorted(outcomes.items()):
            percentage = (count / len(results)) * 100
            print(f"  {outcome}: {count}/{len(results)} ({percentage:.0f}%)")

        return results


if __name__ == "__main__":
    demo = PlaySelectorDemo()

    # Show available plays
    offense_plays = demo.list_plays("offense")
    defense_plays = demo.list_plays("defense")

    print("=" * 60)
    print("FOOTBALL PLAY SIMULATOR - Demo Mode")
    print("=" * 60)
    print(f"Available Offensive Plays: {len(offense_plays)}")
    print(f"Available Defensive Plays: {len(defense_plays)}")

    # Run a few example simulations
    examples = [
        ("power_right", "bear46_run_commit"),  # Power run vs run-stopping defense
        ("te_seam_concept", "cover2_robber_te"),  # TE route vs TE coverage
        ("draw_right", "nickel_zone_blitz_anti_draw"),  # Draw vs anti-draw blitz
        ("four_verts", "dime_cover4_quarters"),  # Deep passing vs deep coverage
    ]

    for off_play, def_play in examples:
        demo.run_demo_simulation(off_play, def_play)
        print("\n" + "=" * 60)
        input("Press Enter to continue to next simulation...")
