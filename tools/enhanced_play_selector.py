#!/usr/bin/env python3
"""
Enhanced Interactive Play Selector with YAML-configurable outcome tables
Uses dice-based resolution with normal distribution curves for realistic results
"""

import sys
import yaml
from pathlib import Path
import random
from typing import Dict, List, Any, Optional, Tuple

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class EnhancedPlaySelector:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent

        # Load outcome configuration
        self.config = self._load_outcome_config()

    def _load_outcome_config(self):
        """Load outcome tables from YAML configuration"""
        config_file = self.repo_root / "tools" / "play_outcome_config.yaml"

        # If config doesn't exist, create it with default values
        if not config_file.exists():
            self._create_default_config(config_file)

        with open(config_file, "r") as f:
            return yaml.safe_load(f)

    def _create_default_config(self, config_file):
        """Create default outcome configuration file"""
        default_config = {
            "dice": {
                "core": "2d6",  # 2d6 gives nice bell curve (7 most common)
                "advantage_bonus": 1,
                "disadvantage_penalty": 1,
            },
            "weights": {"eff_min": 3, "eff_max": 12},
            "modifiers": {
                "tactical_advantage": 1,
                "tactical_disadvantage": -1,
                "elite_vs_average": 1,
                "average_vs_elite": -1,
                "mismatch_bonus": 2,
                "perfect_counter": -2,
            },
            "turnovers": {
                "pass_interception": {
                    "base": 0.02,
                    "eff3": 0.08,
                    "eff4": 0.05,
                    "eff5": 0.03,
                    "pressure_bonus": 0.02,
                },
                "run_fumble": {
                    "base": 0.01,
                    "eff3": 0.04,
                    "eff4": 0.02,
                    "contact_bonus": 0.005,
                },
            },
            "outcome_tables": {
                "inside_run": {
                    "3": {"kind": "stuff", "y": [-3, 0]},
                    "4": {"kind": "stuff", "y": [-2, 1]},
                    "5": {"kind": "gain", "y": [0, 3]},
                    "6": {"kind": "gain", "y": [1, 4]},
                    "7": {"kind": "gain", "y": [2, 6]},
                    "8": {"kind": "gain", "y": [3, 8]},
                    "9": {"kind": "gain", "y": [4, 10]},
                    "10": {"kind": "gain", "y": [5, 12]},
                    "11": {"kind": "break", "y": [8, 20]},
                    "12": {"kind": "break", "y": [10, 30]},
                },
                "outside_run": {
                    "3": {"kind": "loss", "y": [-4, -1]},
                    "4": {"kind": "stuff", "y": [-1, 2]},
                    "5": {"kind": "gain", "y": [1, 4]},
                    "6": {"kind": "gain", "y": [2, 5]},
                    "7": {"kind": "gain", "y": [3, 7]},
                    "8": {"kind": "gain", "y": [4, 9]},
                    "9": {"kind": "gain", "y": [6, 12]},
                    "10": {"kind": "gain", "y": [8, 15]},
                    "11": {"kind": "break", "y": [12, 25]},
                    "12": {"kind": "break", "y": [15, 35]},
                },
                "draw_play": {
                    "3": {"kind": "sack", "y": [-5, -2]},
                    "4": {"kind": "stuff", "y": [-1, 1]},
                    "5": {"kind": "gain", "y": [0, 3]},
                    "6": {"kind": "gain", "y": [2, 5]},
                    "7": {"kind": "gain", "y": [3, 7]},
                    "8": {"kind": "gain", "y": [4, 9]},
                    "9": {"kind": "gain", "y": [5, 11]},
                    "10": {"kind": "gain", "y": [6, 13]},
                    "11": {"kind": "break", "y": [10, 22]},
                    "12": {"kind": "break", "y": [12, 28]},
                },
                "short_pass": {
                    "3": {"kind": "sack", "y": [-7, -3]},
                    "4": {"kind": "inc", "y": [0, 0]},
                    "5": {"kind": "inc", "y": [0, 0]},
                    "6": {"kind": "gain", "y": [3, 6]},
                    "7": {"kind": "gain", "y": [4, 9]},
                    "8": {"kind": "gain", "y": [6, 12]},
                    "9": {"kind": "gain", "y": [7, 14]},
                    "10": {"kind": "gain", "y": [9, 16]},
                    "11": {"kind": "gain", "y": [10, 20]},
                    "12": {"kind": "gain", "y": [12, 24]},
                },
                "deep_pass": {
                    "3": {"kind": "sack", "y": [-9, -4]},
                    "4": {"kind": "inc", "y": [0, 0]},
                    "5": {"kind": "inc", "y": [0, 0]},
                    "6": {"kind": "gain", "y": [10, 16]},
                    "7": {"kind": "gain", "y": [14, 20]},
                    "8": {"kind": "gain", "y": [18, 26]},
                    "9": {"kind": "gain", "y": [22, 32]},
                    "10": {"kind": "gain", "y": [28, 40]},
                    "11": {"kind": "gain", "y": [34, 48]},
                    "12": {"kind": "gain", "y": [40, 60]},
                },
                "screen_pass": {
                    "3": {"kind": "loss", "y": [-3, 0]},
                    "4": {"kind": "stuff", "y": [0, 2]},
                    "5": {"kind": "gain", "y": [1, 4]},
                    "6": {"kind": "gain", "y": [3, 7]},
                    "7": {"kind": "gain", "y": [5, 10]},
                    "8": {"kind": "gain", "y": [7, 13]},
                    "9": {"kind": "gain", "y": [9, 16]},
                    "10": {"kind": "gain", "y": [11, 19]},
                    "11": {"kind": "break", "y": [15, 30]},
                    "12": {"kind": "break", "y": [20, 40]},
                },
                "te_route": {
                    "3": {"kind": "sack", "y": [-6, -2]},
                    "4": {"kind": "inc", "y": [0, 0]},
                    "5": {"kind": "inc", "y": [0, 0]},
                    "6": {"kind": "gain", "y": [4, 8]},
                    "7": {"kind": "gain", "y": [6, 12]},
                    "8": {"kind": "gain", "y": [8, 15]},
                    "9": {"kind": "gain", "y": [10, 18]},
                    "10": {"kind": "gain", "y": [12, 22]},
                    "11": {"kind": "gain", "y": [15, 28]},
                    "12": {"kind": "gain", "y": [18, 35]},
                },
            },
        }

        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)

        print(f"Created default outcome configuration at: {config_file}")
        return default_config

    def _roll_dice(self, dice_spec: str = "2d6") -> int:
        """Roll dice according to specification (e.g., '2d6', '1d10', '3d6')"""
        if "d" not in dice_spec:
            return int(dice_spec)  # Static number

        num_dice, die_size = dice_spec.split("d")
        num_dice = int(num_dice)
        die_size = int(die_size)

        return sum(random.randint(1, die_size) for _ in range(num_dice))

    def _get_effective_roll(self, base_roll: int, modifiers: List[int]) -> int:
        """Apply modifiers and clamp to valid range"""
        eff = base_roll + sum(modifiers)
        min_val = self.config["weights"]["eff_min"]
        max_val = self.config["weights"]["eff_max"]
        return max(min_val, min(max_val, eff))

    def _determine_play_category(self, offense_data) -> str:
        """Determine play category for outcome table lookup"""
        name = offense_data.get("name", "").lower()
        description = offense_data.get("description", "").lower()
        execution = offense_data.get("execution_notes", "").lower()
        play_type = offense_data.get("play_type", "").lower()
        text = f"{name} {description} {execution} {play_type}"

        # Check for specific play types - order matters!
        # Check RPO plays first (special category)
        if play_type == "rpo" or any(word in text for word in ["rpo"]):
            return "rpo"
        # Check running plays
        elif any(word in text for word in ["draw"]):
            return "draw_play"
        elif any(word in text for word in ["sweep", "outside", "edge"]):
            return "outside_run"
        elif any(
            word in text
            for word in ["power", "dive", "inside", "zone", "trap", "counter"]
        ):
            return "inside_run"
        # Check passing plays
        elif any(word in text for word in ["screen", "bubble"]):
            return "screen_pass"
        elif any(word in text for word in ["te_", "tight_end"]) or name.startswith(
            "te_"
        ):
            return "te_route"
        elif any(
            word in text for word in ["deep", "vert", "vertical", "go", "four_verts"]
        ):
            return "deep_pass"
        elif any(
            word in text for word in ["slant", "quick", "short", "hitch", "empty"]
        ):
            return "short_pass"
        elif any(word in text for word in ["pass", "throw", "route", "concept"]):
            return "short_pass"  # Default passing
        else:
            return "inside_run"  # Default running

    def _calculate_modifiers(
        self, offense_data, defense_data, play_category
    ) -> List[int]:
        """Calculate modifiers based on tactical matchups"""
        off_advantages = offense_data.get("tactical_advantages", [])
        def_advantages = defense_data.get("tactical_advantages", [])
        mod_config = self.config["modifiers"]
        modifiers = []

        if play_category == "rpo":
            modifiers += self._modifiers_rpo(off_advantages, def_advantages, mod_config)
        elif play_category in ["inside_run", "outside_run", "draw_play"]:
            modifiers += self._modifiers_run(
                off_advantages, def_advantages, play_category, mod_config
            )
        elif play_category in ["short_pass", "deep_pass", "te_route", "screen_pass"]:
            modifiers += self._modifiers_pass(
                off_advantages, def_advantages, mod_config
            )

        # Check for perfect counters
        if "blitz" in def_advantages and play_category == "draw_play":
            # Draw vs blitz is good for offense
            modifiers.append(-mod_config["perfect_counter"])
        elif "run_commit" in def_advantages and play_category in [
            "inside_run",
            "outside_run",
        ]:
            # Run commit vs run is good for defense
            modifiers.append(mod_config["perfect_counter"])

        return modifiers

    def _modifiers_rpo(self, off_advantages, def_advantages, mod_config):
        modifiers = []
        has_offensive_advantage = False
        has_defensive_advantage = False

        if "rpo_disrupt" in def_advantages or "mesh_disruption" in def_advantages:
            has_defensive_advantage = True
            modifiers.append(mod_config["tactical_disadvantage"])
        elif "slant_jumper" in def_advantages:
            has_defensive_advantage = True
        elif "bubble_coverage" in def_advantages:
            has_defensive_advantage = True
        elif "rpo_stress" in off_advantages:
            has_offensive_advantage = True
        elif "run_pass_conflict" in off_advantages:
            has_offensive_advantage = True

        if has_offensive_advantage:
            modifiers.append(mod_config["tactical_advantage"])
        elif has_defensive_advantage:
            modifiers.append(mod_config["tactical_disadvantage"])
        return modifiers

    def _modifiers_run(self, off_advantages, def_advantages, play_category, mod_config):
        modifiers = []
        has_offensive_advantage = False
        has_defensive_advantage = False

        if "power_running" in off_advantages and "gap_control" in def_advantages:
            has_defensive_advantage = True
        elif (
            "outside_speed" in off_advantages
            and "edge_discipline" not in def_advantages
        ):
            has_offensive_advantage = True
        elif "goal_line_power" in off_advantages and "goal_line_stop" in def_advantages:
            pass  # Even matchup
        elif (
            "misdirection" in off_advantages
            and "disciplined_pursuit" not in def_advantages
        ):
            has_offensive_advantage = True
        elif play_category == "outside_run" and "sweep_stop" in def_advantages:
            has_defensive_advantage = True
            modifiers.append(mod_config["perfect_counter"])
        elif play_category == "outside_run" and "eight_man_box" in def_advantages:
            has_defensive_advantage = True
            modifiers.append(mod_config["tactical_disadvantage"])

        if has_offensive_advantage:
            modifiers.append(mod_config["tactical_advantage"])
        elif has_defensive_advantage:
            modifiers.append(mod_config["tactical_disadvantage"])
        return modifiers

    def _modifiers_pass(self, off_advantages, def_advantages, mod_config):
        modifiers = []
        has_offensive_advantage = False
        has_defensive_advantage = False

        if "deep_threat" in off_advantages and "deep_coverage" in def_advantages:
            pass  # Even matchup
        elif "quick_timing" in off_advantages and "pass_rush" in def_advantages:
            has_defensive_advantage = True
        elif "mismatch_creation" in off_advantages:
            has_offensive_advantage = True
            modifiers.append(mod_config["mismatch_bonus"])
        elif (
            "pattern_matching" in def_advantages and "bunch_formation" in off_advantages
        ):
            has_defensive_advantage = True

        if has_offensive_advantage:
            modifiers.append(mod_config["tactical_advantage"])
        elif has_defensive_advantage:
            modifiers.append(mod_config["tactical_disadvantage"])
        return modifiers

    def _check_turnover(
        self, effective_roll: int, play_category: str
    ) -> Optional[Tuple[str, int]]:
        """Check if play results in turnover"""
        turnover_config = self.config["turnovers"]

        if play_category in [
            "short_pass",
            "deep_pass",
            "te_route",
            "screen_pass",
            "rpo",
        ]:
            # Check for interception
            int_config = turnover_config["pass_interception"]
            base_chance = int_config["base"]

            # Higher chance on low rolls
            if effective_roll <= 3:
                chance = int_config.get("eff3", base_chance)
            elif effective_roll <= 4:
                chance = int_config.get("eff4", base_chance)
            elif effective_roll <= 5:
                chance = int_config.get("eff5", base_chance)
            else:
                chance = base_chance

            if random.random() < chance:
                return ("interception", random.randint(-2, 0))

        elif play_category in ["inside_run", "outside_run", "draw_play", "rpo"]:
            # Check for fumble
            fumble_config = turnover_config["run_fumble"]
            base_chance = fumble_config["base"]

            if effective_roll <= 3:
                chance = fumble_config.get("eff3", base_chance)
            elif effective_roll <= 4:
                chance = fumble_config.get("eff4", base_chance)
            else:
                chance = base_chance

            if random.random() < chance:
                return ("fumble", random.randint(-3, 0))

        return None

    def _resolve_play_outcome(self, offense_data, defense_data) -> Dict[str, Any]:
        """Resolve play using dice-based outcome tables"""
        play_category = self._determine_play_category(offense_data)

        # Roll dice
        dice_spec = self.config["dice"]["core"]
        base_roll = self._roll_dice(dice_spec)

        # Calculate modifiers
        modifiers = self._calculate_modifiers(offense_data, defense_data, play_category)

        # Get effective roll
        effective_roll = self._get_effective_roll(base_roll, modifiers)

        # Check for turnover first
        turnover = self._check_turnover(effective_roll, play_category)
        if turnover:
            return {
                "yards": turnover[1],
                "outcome": turnover[0],
                "roll": base_roll,
                "effective_roll": effective_roll,
                "modifiers": modifiers,
                "play_category": play_category,
            }

        # Look up outcome in table
        outcome_table = self.config["outcome_tables"].get(play_category, {})
        outcome_data = outcome_table.get(str(effective_roll))

        if not outcome_data:
            # Fallback for missing table entries
            outcome_data = {"kind": "gain", "y": [0, 3]}

        # Generate yards within range
        yard_range = outcome_data["y"]
        yards = random.randint(yard_range[0], yard_range[1])

        # For RPO, track the decision made
        rpo_decision = None
        if play_category == "rpo":
            rpo_decision = outcome_data.get(
                "decision", "run"
            )  # Default to run if not specified

        return {
            "yards": yards,
            "outcome": outcome_data["kind"],
            "roll": base_roll,
            "effective_roll": effective_roll,
            "modifiers": modifiers,
            "play_category": play_category,
            "rpo_decision": rpo_decision,
        }

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

    def display_play_options(self, play_type):
        """Display numbered list of plays for selection"""
        plays = self.list_plays(play_type)
        print(f"\n{play_type.upper()} PLAYS:")
        print("-" * 40)
        for i, play in enumerate(plays, 1):
            print(f"{i:2d}. {play.replace('_', ' ').title()}")
        return plays

    def get_play_choice(self, play_type):
        """Get user's play selection"""
        plays = self.display_play_options(play_type)

        while True:
            try:
                choice = input(f"\nSelect {play_type} play (1-{len(plays)}): ").strip()
                if choice.lower() in ["q", "quit", "exit"]:
                    return None

                choice_num = int(choice)
                if 1 <= choice_num <= len(plays):
                    selected_play = plays[choice_num - 1]
                    print(f"Selected: {selected_play.replace('_', ' ').title()}")
                    return selected_play
                else:
                    print(f"Please enter a number between 1 and {len(plays)}")
            except ValueError:
                print("Please enter a valid number (or 'q' to quit)")

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

    def simulate_play_matchup(self, offensive_play, defensive_play):
        """Simulate the selected plays using dice-based resolution"""
        try:
            offense_data = self.load_play_data(offensive_play, "offense")
            defense_data = self.load_play_data(defensive_play, "defense")

            if not offense_data or not defense_data:
                return None

            print(f"\n{'=' * 70}")
            print(
                f"SIMULATION: {offensive_play.replace('_', ' ').title()} vs "
                f"{defensive_play.replace('_', ' ').title()}"
            )
            print(f"{'=' * 70}")

            # Show play details
            self.show_play_details(offensive_play, "offense")
            self.show_play_details(defensive_play, "defense")

            print(f"\n{'DICE-BASED SIMULATION RESULTS':^70}")
            print("-" * 70)

            # Run multiple simulations
            results = []
            for i in range(10):
                result = self._resolve_play_outcome(offense_data, defense_data)
                results.append(result)

                # Display result with dice info
                yards = result["yards"]
                outcome = result["outcome"]
                roll = result["roll"]
                eff_roll = result["effective_roll"]
                mods = result["modifiers"]
                rpo_decision = result.get("rpo_decision")

                mod_str = (
                    f"(+{sum(mods)})"
                    if sum(mods) > 0
                    else f"({sum(mods)})"
                    if sum(mods) < 0
                    else ""
                )

                # Add RPO decision to display
                rpo_str = f" [{rpo_decision.upper()}]" if rpo_decision else ""

                print(
                    f"Sim {i + 1:2d}: {yards:+3d} yards - {outcome:>12}{rpo_str} | "
                    f"Roll: {roll} → {eff_roll} {mod_str}"
                )

            # Show summary statistics
            total_yards = sum(r["yards"] for r in results)
            avg_yards = total_yards / len(results)
            max_yards = max(r["yards"] for r in results)
            min_yards = min(r["yards"] for r in results)

            # Count outcomes and RPO decisions
            outcomes = {}
            rpo_decisions = {}
            for result in results:
                outcomes[result["outcome"]] = outcomes.get(result["outcome"], 0) + 1
                if result.get("rpo_decision"):
                    decision = result["rpo_decision"]
                    rpo_decisions[decision] = rpo_decisions.get(decision, 0) + 1

            print("-" * 70)
            print(
                f"SUMMARY ({len(results)} simulations using "
                f"{self.config['dice']['core']}):"
            )
            print(f"  Average: {avg_yards:+5.1f} yards")
            print(f"  Range: {min_yards:+3d} to {max_yards:+3d} yards")
            print(f"  Total: {total_yards:+4d} yards")

            print("\nOUTCOME BREAKDOWN:")
            for outcome, count in sorted(outcomes.items()):
                percentage = (count / len(results)) * 100
                print(f"  {outcome}: {count}/{len(results)} ({percentage:.0f}%)")

            # Show RPO decision breakdown if applicable
            if rpo_decisions:
                print("\nRPO DECISIONS:")
                for decision, count in sorted(rpo_decisions.items()):
                    percentage = (count / len(results)) * 100
                    print(f"  {decision}: {count}/{len(results)} ({percentage:.0f}%)")

            return results

        except Exception as e:
            print(f"Error simulating play: {e}")
            return None

    def run_interactive_session(self):
        """Main interactive loop"""
        print("=" * 70)
        print("ENHANCED FOOTBALL PLAY SIMULATOR - Dice-Based Resolution")
        print("=" * 70)
        print("Choose offensive and defensive plays to simulate!")
        print(f"Using {self.config['dice']['core']} dice system with outcome tables")
        print("Type 'q' at any prompt to quit")

        while True:
            print("\n" + "=" * 70)

            # Get offensive play choice
            offensive_play = self.get_play_choice("offense")
            if offensive_play is None:
                break

            # Get defensive play choice
            defensive_play = self.get_play_choice("defense")
            if defensive_play is None:
                break

            # Ask if user wants to continue
            print("\n" + "-" * 70)
            continue_choice = input("Run another simulation? (y/n): ").strip().lower()
            if continue_choice in ["n", "no", "q", "quit"]:
                break

        print("\nThanks for using the Enhanced Football Play Simulator!")
        print(f"Configuration file: {self.repo_root}/tools/play_outcome_config.yaml")


if __name__ == "__main__":
    selector = EnhancedPlaySelector()
    selector.run_interactive_session()
