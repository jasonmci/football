#!/usr/bin/env python3
"""
Demo of Enhanced Play Selector with Dice-Based Resolution
Shows examples of the new outcome table system
"""

import sys
import yaml
from pathlib import Path
import random
from typing import Dict, List, Any, Optional, Tuple

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class EnhancedPlaySelectorDemo:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent

        # Load outcome configuration from shared file
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
        """Create default outcome configuration file if needed"""
        # This shouldn't be needed since we have the config file
        pass

    def _roll_dice(self, dice_spec: str = "2d6") -> int:
        """Roll dice according to specification"""
        if "d" not in dice_spec:
            return int(dice_spec)

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

        if play_category == "rpo":
            return self._modifiers_rpo(off_advantages, def_advantages, mod_config)
        elif play_category in ["inside_run", "outside_run"]:
            return self._modifiers_run(
                off_advantages, def_advantages, mod_config, play_category
            )
        elif play_category == "draw_play":
            return self._modifiers_draw(def_advantages, mod_config)
        elif play_category in ["short_pass", "deep_pass", "te_route"]:
            return self._modifiers_pass(off_advantages, def_advantages, mod_config)
        else:
            return []

    def _modifiers_rpo(self, off_advantages, def_advantages, mod_config):
        modifiers = []
        if "rpo_disrupt" in def_advantages or "mesh_disruption" in def_advantages:
            modifiers.append(mod_config["tactical_disadvantage"])
        if "slant_jumper" in def_advantages:
            modifiers.append(mod_config["tactical_disadvantage"])
        if "bubble_coverage" in def_advantages:
            modifiers.append(mod_config["tactical_disadvantage"])
        if "rpo_stress" in off_advantages:
            modifiers.append(mod_config["tactical_advantage"])
        if "run_pass_conflict" in off_advantages:
            modifiers.append(mod_config["tactical_advantage"])
        return modifiers

    def _modifiers_run(self, off_advantages, def_advantages, mod_config, play_category):
        modifiers = []
        if "power_running" in off_advantages and "gap_control" in def_advantages:
            modifiers.append(mod_config["tactical_disadvantage"])
        elif (
            "outside_speed" in off_advantages
            and "edge_discipline" not in def_advantages
        ):
            modifiers.append(mod_config["tactical_advantage"])
        elif play_category == "outside_run" and "sweep_stop" in def_advantages:
            modifiers.append(mod_config["perfect_counter"])
        elif play_category == "outside_run" and "eight_man_box" in def_advantages:
            modifiers.append(mod_config["tactical_disadvantage"])
        return modifiers

    def _modifiers_draw(self, def_advantages, mod_config):
        modifiers = []
        if "blitz" in def_advantages:
            modifiers.append(-mod_config["perfect_counter"])
        return modifiers

    def _modifiers_pass(self, off_advantages, def_advantages, mod_config):
        modifiers = []
        if "mismatch_creation" in off_advantages:
            modifiers.append(mod_config["mismatch_bonus"])
        elif "pass_rush" in def_advantages and "quick_timing" not in off_advantages:
            modifiers.append(mod_config["tactical_disadvantage"])
        return modifiers

    def _check_turnover(
        self, effective_roll: int, play_category: str
    ) -> Optional[Tuple[str, int]]:
        """Check if play results in turnover"""
        turnover_config = self.config["turnovers"]

        if play_category in ["short_pass", "deep_pass", "te_route", "rpo"]:
            int_config = turnover_config["pass_interception"]
            if effective_roll <= 3:
                chance = int_config.get("eff3", int_config["base"])
            elif effective_roll <= 4:
                chance = int_config.get("eff4", int_config["base"])
            else:
                chance = int_config["base"]

            if random.random() < chance:
                return ("interception", random.randint(-2, 0))

        elif play_category in ["inside_run", "outside_run", "draw_play", "rpo"]:
            fumble_config = turnover_config["run_fumble"]
            if effective_roll <= 3:
                chance = fumble_config.get("eff3", fumble_config["base"])
            else:
                chance = fumble_config["base"]

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
        if "tactical_advantages" in play_data:
            print(f"Tactical Advantages: {', '.join(play_data['tactical_advantages'])}")

    def run_demo_simulation(self, offensive_play, defensive_play, description):
        """Run a demo simulation with the specified plays"""
        offense_data = self.load_play_data(offensive_play, "offense")
        defense_data = self.load_play_data(defensive_play, "defense")

        if not offense_data or not defense_data:
            print("Could not load play data")
            return None

        print(f"\n{'='*75}")
        print(f"{description.upper()}")
        print(
            (
                f"SIMULATION: {offensive_play.replace('_', ' ').title()} "
                f"vs {defensive_play.replace('_', ' ').title()}"
            )
        )
        print(f"{'='*75}")

        # Show play details
        self.show_play_details(offensive_play, "offense")
        self.show_play_details(defensive_play, "defense")

        # Determine play category
        play_category = self._determine_play_category(offense_data)
        table = self.config["outcome_tables"].get(play_category, {})

        print(f"\nPlay Category: {play_category}")
        print("Outcome Table:")
        for roll, data in table.items():
            decision_str = (
                f" [{data.get('decision', '').upper()}]"
                if data.get("decision") and play_category == "rpo"
                else ""
            )
            print(
                (
                    f"  {roll}: {data['kind']} "
                    f"({data['y'][0]} to {data['y'][1]} yards)"
                    f"{decision_str}"
                )
            )

        print(f"\n{'DICE-BASED SIMULATION RESULTS (2d6)':^75}")
        print("-" * 75)

        # Run simulations
        results = []
        rpo_decisions = {}
        for i in range(10):
            result = self._resolve_play_outcome(offense_data, defense_data)
            results.append(result)

            yards = result["yards"]
            outcome = result["outcome"]
            roll = result["roll"]
            eff_roll = result["effective_roll"]
            mods = result["modifiers"]
            rpo_decision = result.get("rpo_decision")

            # Track RPO decisions
            if rpo_decision:
                rpo_decisions[rpo_decision] = rpo_decisions.get(rpo_decision, 0) + 1

            mod_str = (
                f"(+{sum(mods)})"
                if sum(mods) > 0
                else f"({sum(mods)})" if sum(mods) < 0 else ""
            )
            rpo_str = f" [{rpo_decision.upper()}]" if rpo_decision else ""
            print(
                f"Sim {i+1:2d}: {yards:+3d} yards - {outcome:>12}{rpo_str} | "
                f"Dice: {roll} → {eff_roll} {mod_str}"
            )

        # Show summary
        total_yards = sum(r["yards"] for r in results)
        avg_yards = total_yards / len(results)
        max_yards = max(r["yards"] for r in results)
        min_yards = min(r["yards"] for r in results)

        outcomes = {}
        for result in results:
            outcomes[result["outcome"]] = outcomes.get(result["outcome"], 0) + 1

        print("-" * 75)
        print("SUMMARY:")
        print(
            f"  Average: {avg_yards:+5.1f} yards  |  Range: {min_yards:+3d} "
            f"to {max_yards:+3d} yards"
        )
        print(
            (
                "  Outcomes: "
                + ", ".join(
                    f"{outcome}({count})" for outcome, count in sorted(outcomes.items())
                )
            )
        )

        # Show RPO decision breakdown if applicable
        if rpo_decisions:
            print(
                "  RPO Decisions: "
                + ", ".join(
                    f"{decision}({count})"
                    for decision, count in sorted(rpo_decisions.items())
                )
            )

        return results


if __name__ == "__main__":
    demo = EnhancedPlaySelectorDemo()

    print("=" * 75)
    print("ENHANCED FOOTBALL SIMULATOR - Dice-Based Outcome Tables Demo")
    print("=" * 75)
    print("Using 2d6 dice system with configurable outcome tables")
    print("Bell curve distribution: 7 is most common, 2&12 are rare")

    # Demo examples
    examples = [
        ("power_right", "bear46_run_commit", "Power Running vs Run Defense"),
        ("draw_right", "nickel_zone_blitz_anti_draw", "Draw vs Anti-Draw Blitz"),
        ("te_seam_concept", "cover2_robber_te", "TE Route vs TE Coverage"),
        ("four_verts", "dime_cover4_quarters", "Deep Passing vs Deep Coverage"),
        ("sweep_right", "eight_man_box_sweep_stop", "Outside Run vs Edge Defense"),
        ("rpo_bubble_screen", "nickel_zone_blitz_rpo_stop", "RPO vs Zone Blitz"),
        ("rpo_slant_zone", "dime_zone_fire", "RPO vs Zone Fire Pressure"),
    ]

    for off_play, def_play, description in examples:
        demo.run_demo_simulation(off_play, def_play, description)

    print(f"\n{'='*75}")
    print("DEMO COMPLETE!")
    print("The outcome tables provide:")
    print("• Normal distribution results (2d6 bell curve)")
    print("• Configurable yard ranges per dice result")
    print("• Tactical modifiers based on play matchups")
    print("• Turnover chances on low rolls")
    print("• YAML-configurable for easy tuning")
    print("=" * 75)
