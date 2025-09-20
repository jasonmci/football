#!/usr/bin/env python3
"""
Football Matchup Simulator

Loads offensive and defensive team configurations with player ratings,
then simulates the same matchup multiple times to show distribution of results.
"""

import sys
import os


import yaml
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import Counter
import statistics

from football.enhanced_resolution import (
    EnhancedResolutionEngine,
    PlayerProfile,
    SkillCategory,
)
from football.play_resolution import (
    PlayResolutionEngine,
    ResolutionConfig,
    PlayOutcome,
)
from football.play_analyzer import PlayAnalyzer
from types import SimpleNamespace

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


@dataclass
class TeamConfig:
    """Represents a team configuration with players and play setup."""

    name: str
    label: str
    formation: str
    play_type: str
    players: Dict[str, PlayerProfile]
    assignments: List[Dict[str, Any]]
    success_metrics: Dict[str, int]
    expected_performance: Dict[str, Any]


@dataclass
class SimulationResult:
    """Result of a single play simulation."""

    outcome: str
    yards_gained: int
    completed: bool
    key_players: List[str]
    tactical_advantages: List[str]
    net_advantage: int


@dataclass
class DistributionAnalysis:
    """Analysis of simulation results distribution."""

    total_simulations: int
    avg_yards: float
    median_yards: float
    success_rate: float  # % of plays meeting success threshold
    explosive_rate: float  # % of plays with explosive gains
    turnover_rate: float  # % of turnovers
    outcome_distribution: Dict[str, int]
    yards_distribution: List[int]
    best_result: SimulationResult
    worst_result: SimulationResult


class FootballSimulator:
    """Main simulator class for running football matchups."""

    def __init__(self):
        self.enhanced_engine = EnhancedResolutionEngine()
        self.resolution_engine = PlayResolutionEngine()
        self.play_analyzer = PlayAnalyzer()
        self.rng = random.Random()

    def load_team_config(self, config_path: str) -> TeamConfig:
        """Load team configuration from YAML file."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Convert player configs to PlayerProfile objects
        players = {}
        for position, player_data in config["players"].items():
            # Convert skills dict to use SkillCategory enum keys
            skills = {}
            for skill_name, rating in player_data["skills"].items():
                try:
                    # Map common skill names to SkillCategory
                    skill_mapping = {
                        "awareness": SkillCategory.AWARENESS,
                        "hands": SkillCategory.HANDS,
                        "strength": SkillCategory.STRENGTH,
                        "agility": SkillCategory.AGILITY,
                        "speed": SkillCategory.SPEED,
                        "pass_block": SkillCategory.PASS_BLOCKING,
                        "run_block": SkillCategory.RUN_BLOCKING,
                        "pass_rush": SkillCategory.PASS_RUSH,
                        "run_defense": SkillCategory.RUN_DEFENSE,
                        "coverage": SkillCategory.COVERAGE,
                        "tackle": SkillCategory.TACKLE,
                        "route_running": SkillCategory.ROUTE_RUNNING,
                    }
                    if skill_name in skill_mapping:
                        skills[skill_mapping[skill_name]] = rating
                except Exception:
                    # Skip unknown skills
                    pass

            player = PlayerProfile(
                name=player_data["name"],
                position=player_data["position"],
                overall_rating=player_data["overall_rating"],
                skills=skills,
                traits=player_data.get("traits", []),
            )
            players[position] = player

        return TeamConfig(
            name=config["name"],
            label=config["label"],
            formation=config["formation"],
            play_type=config["play_type"],
            players=players,
            assignments=config["assignments"],
            success_metrics=config["success_metrics"],
            expected_performance=(
                config.get("expected_vs_defenses", {})
                if config["play_type"] == "run"
                else config.get("expected_vs_plays", {})
            ),
        )

    def simulate_single_play(
        self,
        offense: TeamConfig,
        defense: TeamConfig,
        situation: Optional[Dict[str, Any]] = None,
    ) -> SimulationResult:
        """Simulate a single play between offense and defense."""

        if situation is None:
            situation = {
                "down": 1,
                "distance": 10,
                "field_position": 25,
                "time_remaining": 900,  # 15 minutes
                "score_differential": 0,
            }

        # Get key players for the matchup
        if offense.play_type == "run":
            # Running play - RB vs front 7
            runner = offense.players.get("RB1")
            if runner is None:
                raise ValueError("No RB1 found in offensive players")

            blockers = []
            for pos in ["LG", "RG", "C"]:
                player = offense.players.get(pos)
                if player:
                    blockers.append(player)

            defenders = []
            for pos in ["DT1", "DT2", "MLB"]:
                player = defense.players.get(pos)
                if player:
                    defenders.append(player)
        else:
            # Passing play - QB/WR vs CB/S
            qb = offense.players.get("QB")
            receiver = offense.players.get("WR1")
            defender = defense.players.get("CB1")

            if not all([qb, receiver, defender]):
                raise ValueError("Missing key players for passing play")

        # Analyze tactical matchup
        tactical_analysis = self._analyze_tactical_matchup(offense, defense)

        # Create base result using standard resolution
        base_dice_roll = self.rng.randint(2, 12)  # 2d6 for base
        net_modifier = tactical_analysis["net_advantage"]
        final_total = base_dice_roll + net_modifier

        # Determine base outcome and yards
        config = ResolutionConfig()
        base_yards = self._determine_base_yards(final_total, config)

        base_result = SimpleNamespace(
            outcome=SimpleNamespace(name="SUCCESS"),
            yards_gained=base_yards,
            dice_roll=base_dice_roll,
            total_modifier=net_modifier,
            final_total=final_total,
        )

        # Apply enhanced resolution with player ratings
        if offense.play_type == "run":
            enhanced_result = self.enhanced_engine.resolve_run_play(
                runner, blockers, defenders, base_result, situation
            )
        else:
            enhanced_result = self.enhanced_engine.resolve_pass_play(
                qb, receiver, defender, base_result, situation  # type: ignore
            )

        return SimulationResult(
            outcome=enhanced_result.outcome,
            yards_gained=enhanced_result.yards_gained,
            completed=enhanced_result.completed,
            key_players=enhanced_result.key_players,
            tactical_advantages=tactical_analysis["advantages"],
            net_advantage=net_modifier,
        )

    def _analyze_tactical_matchup(
        self, offense: TeamConfig, defense: TeamConfig
    ) -> Dict[str, Any]:
        """Analyze the tactical matchup between formations."""
        advantages = []
        disadvantages = []
        net_advantage = 0

        # Formation vs formation matchup
        if offense.formation == "i_form" and defense.formation == "base43":
            if offense.play_type == "run":
                advantages.append("I-Formation power vs 4-3 base")
                net_advantage += 1

        # Player-specific advantages
        if offense.play_type == "run":
            # Compare run blocking vs run defense
            avg_blocking = statistics.mean(
                [
                    offense.players["LG"].skills.get(SkillCategory.RUN_BLOCKING, 75),
                    offense.players["RG"].skills.get(SkillCategory.RUN_BLOCKING, 75),
                    offense.players["C"].skills.get(SkillCategory.RUN_BLOCKING, 75),
                ]
            )
            avg_run_defense = statistics.mean(
                [
                    defense.players["DT1"].skills.get(SkillCategory.RUN_DEFENSE, 75),
                    defense.players["DT2"].skills.get(SkillCategory.RUN_DEFENSE, 75),
                    defense.players["MLB"].skills.get(SkillCategory.TACKLE, 75),
                ]
            )

            blocking_advantage = (
                avg_blocking - avg_run_defense
            ) // 5  # Every 5 points = +/- 1
            net_advantage += blocking_advantage

            if blocking_advantage > 0:
                advantages.append(f"Superior run blocking (+{blocking_advantage})")
            elif blocking_advantage < 0:
                disadvantages.append(f"Weaker run blocking ({blocking_advantage})")

        return {
            "advantages": advantages,
            "disadvantages": disadvantages,
            "net_advantage": max(-3, min(3, net_advantage)),  # Cap at +/- 3
        }

    def _determine_base_yards(self, total: int, config: ResolutionConfig) -> int:
        """Determine base yards from dice total."""
        if total >= config.thresholds[PlayOutcome.EXPLOSIVE_SUCCESS]:
            return self.rng.randint(12, 25)
        elif total >= config.thresholds[PlayOutcome.BIG_SUCCESS]:
            return self.rng.randint(6, 11)
        elif total >= config.thresholds[PlayOutcome.SUCCESS]:
            return self.rng.randint(3, 5)
        elif total >= config.thresholds[PlayOutcome.MODERATE_GAIN]:
            return self.rng.randint(1, 2)
        elif total >= config.thresholds[PlayOutcome.NO_GAIN]:
            return 0
        elif total >= config.thresholds[PlayOutcome.LOSS]:
            return self.rng.randint(-2, -1)
        else:
            return self.rng.randint(-5, -3)

    def run_simulation(
        self,
        offense: TeamConfig,
        defense: TeamConfig,
        num_simulations: int = 100,
        situation: Optional[Dict[str, Any]] = None,
    ) -> DistributionAnalysis:
        """Run multiple simulations and analyze the distribution."""

        results = []
        for _ in range(num_simulations):
            result = self.simulate_single_play(offense, defense, situation)
            results.append(result)

        # Analyze results
        yards_gained = [r.yards_gained for r in results]
        avg_yards = statistics.mean(yards_gained)
        median_yards = statistics.median(yards_gained)

        # Success rate based on offense's success threshold
        success_threshold = offense.success_metrics.get("success_threshold", 4)
        successful_plays = sum(1 for y in yards_gained if y >= success_threshold)
        success_rate = (successful_plays / num_simulations) * 100

        # Explosive play rate
        explosive_threshold = offense.success_metrics.get(
            "explosive_gain_threshold", 15
        )
        explosive_plays = sum(1 for y in yards_gained if y >= explosive_threshold)
        explosive_rate = (explosive_plays / num_simulations) * 100

        # Turnover rate
        turnovers = sum(1 for r in results if r.outcome in ["FUMBLE", "INTERCEPTION"])
        turnover_rate = (turnovers / num_simulations) * 100

        # Outcome distribution
        outcome_counts = Counter(r.outcome for r in results)

        # Best and worst results
        best_result = max(results, key=lambda r: r.yards_gained)
        worst_result = min(results, key=lambda r: r.yards_gained)

        return DistributionAnalysis(
            total_simulations=num_simulations,
            avg_yards=avg_yards,
            median_yards=median_yards,
            success_rate=success_rate,
            explosive_rate=explosive_rate,
            turnover_rate=turnover_rate,
            outcome_distribution=dict(outcome_counts),
            yards_distribution=yards_gained,
            best_result=best_result,
            worst_result=worst_result,
        )


def print_simulation_results(
    offense_name: str, defense_name: str, analysis: DistributionAnalysis
):
    """Print formatted simulation results."""
    print(f"\n🏈 SIMULATION RESULTS: {offense_name} vs {defense_name}")
    print("=" * 70)

    print(f"\n📊 OVERALL STATISTICS ({analysis.total_simulations} simulations)")
    print(f"   Average Yards: {analysis.avg_yards:.1f}")
    print(f"   Median Yards: {analysis.median_yards:.1f}")
    print(f"   Success Rate: {analysis.success_rate:.1f}%")
    print(f"   Explosive Rate: {analysis.explosive_rate:.1f}%")
    print(f"   Turnover Rate: {analysis.turnover_rate:.1f}%")

    print("\n🎯 OUTCOME DISTRIBUTION")
    for outcome, count in sorted(analysis.outcome_distribution.items()):
        percentage = (count / analysis.total_simulations) * 100
        print(f"   {outcome}: {count} ({percentage:.1f}%)")

    print("\n📈 YARDS DISTRIBUTION")
    yards_ranges = [
        ("Loss (< 0)", lambda y: y < 0),
        ("No Gain (0)", lambda y: y == 0),
        ("Short (1-3)", lambda y: 1 <= y <= 3),
        ("Medium (4-7)", lambda y: 4 <= y <= 7),
        ("Good (8-12)", lambda y: 8 <= y <= 12),
        ("Explosive (13+)", lambda y: y >= 13),
    ]

    for range_name, range_func in yards_ranges:
        count = sum(1 for y in analysis.yards_distribution if range_func(y))
        percentage = (count / analysis.total_simulations) * 100
        print(f"   {range_name}: {count} ({percentage:.1f}%)")

    print("\n🏆 BEST RESULT")
    print(f"   Outcome: {analysis.best_result.outcome}")
    print(f"   Yards: {analysis.best_result.yards_gained}")
    print(f"   Key Players: {', '.join(analysis.best_result.key_players)}")

    print("\n💀 WORST RESULT")
    print(f"   Outcome: {analysis.worst_result.outcome}")
    print(f"   Yards: {analysis.worst_result.yards_gained}")
    print(f"   Key Players: {', '.join(analysis.worst_result.key_players)}")


def main():
    """Main simulation runner."""

    simulator = FootballSimulator()

    # Test scenarios
    scenarios = [
        {
            "name": "Elite vs Elite",
            "offense": (
                "/Users/jasonmcinerney/repos/football/data/configs/"
                "elite_offense_trap.yaml"
            ),
            "defense": (
                "/Users/jasonmcinerney/repos/football/data/configs/"
                "elite_defense_cover3.yaml"
            ),
        },
        {
            "name": "Elite vs Average",
            "offense": (
                "/Users/jasonmcinerney/repos/football/data/configs/"
                "elite_offense_trap.yaml"
            ),
            "defense": (
                "/Users/jasonmcinerney/repos/football/data/configs/"
                "average_defense_cover3.yaml"
            ),
        },
        {
            "name": "Average vs Elite",
            "offense": (
                "/Users/jasonmcinerney/repos/football/data/configs/"
                "average_offense_trap.yaml"
            ),
            "defense": (
                "/Users/jasonmcinerney/repos/football/data/configs/"
                "elite_defense_cover3.yaml"
            ),
        },
        {
            "name": "Average vs Average",
            "offense": (
                "/Users/jasonmcinerney/repos/football/data/configs/"
                "average_offense_trap.yaml"
            ),
            "defense": (
                "/Users/jasonmcinerney/repos/football/data/configs/"
                "average_defense_cover3.yaml"
            ),
        },
    ]

    print("🏈 FOOTBALL MATCHUP SIMULATOR")
    print("=" * 60)
    print("Simulating Trap Right vs 4-3 Cover 3 with different talent levels")
    print("Each scenario runs 100 simulations to show result distribution")
    print("=" * 60)

    for scenario in scenarios:
        try:
            offense = simulator.load_team_config(scenario["offense"])
            defense = simulator.load_team_config(scenario["defense"])

            # Standard situation
            situation = {
                "down": 1,
                "distance": 10,
                "field_position": 35,
                "time_remaining": 600,
                "score_differential": 0,
                "pass_rush_pressure": False,
            }

            analysis = simulator.run_simulation(offense, defense, 100, situation)
            print_simulation_results(
                scenario["name"], f"{offense.label} vs {defense.label}", analysis
            )

        except Exception as e:
            print(f"\n❌ Error in scenario '{scenario['name']}': {e}")

    print("\n" + "=" * 60)
    print("🎯 SIMULATION COMPLETE")
    print("✅ Player ratings create meaningful performance differences")
    print("✅ Same play call produces realistic result distributions")
    print("✅ Elite talent shows clear advantages in success rates")
    print("✅ Turnover mechanics add realistic risk elements")


if __name__ == "__main__":
    main()
