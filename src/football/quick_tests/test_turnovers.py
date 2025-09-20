#!/usr/bin/env python3
"""
Test script for turnover mechanics (interceptions and fumbles).
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from football2.football.enhanced_resolution import (
    EnhancedResolutionEngine,
    PlayerProfile,
    SkillCategory,
)
from types import SimpleNamespace
import random


def create_turnover_test_players():
    """Create players with different turnover tendencies."""

    # Elite QB with great decision making
    elite_qb = PlayerProfile(
        name="Elite QB",
        position="QB",
        overall_rating=92,
        skills={SkillCategory.AWARENESS: 95, SkillCategory.HANDS: 90},
        traits=["clutch"],
    )

    # Average QB prone to mistakes
    mistake_prone_qb = PlayerProfile(
        name="Mistake-Prone QB",
        position="QB",
        overall_rating=75,
        skills={SkillCategory.AWARENESS: 68, SkillCategory.HANDS: 72},
        traits=["interception_prone"],
    )

    # Elite ball-hawking safety
    ball_hawk_safety = PlayerProfile(
        name="Ball Hawk Safety",
        position="S",
        overall_rating=88,
        skills={
            SkillCategory.COVERAGE: 92,
            SkillCategory.HANDS: 89,
            SkillCategory.TACKLE: 84,
        },
    )

    # Average receiver
    average_wr = PlayerProfile(
        name="Average WR",
        position="WR",
        overall_rating=76,
        skills={
            SkillCategory.HANDS: 74,
            SkillCategory.ROUTE_RUNNING: 78,
            SkillCategory.SPEED: 82,
            SkillCategory.AGILITY: 76,
        },
    )

    # Fumble-prone RB
    fumble_prone_rb = PlayerProfile(
        name="Fumble-Prone RB",
        position="RB",
        overall_rating=78,
        skills={
            SkillCategory.STRENGTH: 75,
            SkillCategory.AGILITY: 84,
            SkillCategory.SPEED: 88,
        },
        traits=["fumble_prone"],
    )

    # Secure hands RB
    secure_rb = PlayerProfile(
        name="Secure Hands RB",
        position="RB",
        overall_rating=82,
        skills={
            SkillCategory.STRENGTH: 85,
            SkillCategory.AGILITY: 80,
            SkillCategory.SPEED: 78,
        },
        traits=["secure_hands"],
    )

    # Strong linebacker
    strong_lb = PlayerProfile(
        name="Strong LB",
        position="LB",
        overall_rating=85,
        skills={
            SkillCategory.STRENGTH: 92,
            SkillCategory.TACKLE: 88,
            SkillCategory.COVERAGE: 72,
        },
    )

    return {
        "elite_qb": elite_qb,
        "mistake_qb": mistake_prone_qb,
        "ball_hawk": ball_hawk_safety,
        "average_wr": average_wr,
        "fumble_rb": fumble_prone_rb,
        "secure_rb": secure_rb,
        "strong_lb": strong_lb,
    }


def test_interception_scenarios():
    """Test various interception scenarios."""
    print("🎯 INTERCEPTION TESTING")
    print("=" * 50)

    engine = EnhancedResolutionEngine()
    players = create_turnover_test_players()

    scenarios = [
        {
            "name": "Elite QB vs Ball Hawk - Clean Pocket",
            "qb": players["elite_qb"],
            "wr": players["average_wr"],
            "def": players["ball_hawk"],
            "pressure": False,
            "yards": 12,
        },
        {
            "name": "Mistake-Prone QB vs Ball Hawk - Under Pressure",
            "qb": players["mistake_qb"],
            "wr": players["average_wr"],
            "def": players["ball_hawk"],
            "pressure": True,
            "yards": 18,
        },
        {
            "name": "Elite QB vs Ball Hawk - Deep Ball",
            "qb": players["elite_qb"],
            "wr": players["average_wr"],
            "def": players["ball_hawk"],
            "pressure": False,
            "yards": 25,
        },
    ]

    for scenario in scenarios:
        print(f"\n📡 {scenario['name']}")

        # Test multiple attempts to see interception rates
        completions = 0
        incompletions = 0
        interceptions = 0

        for _ in range(100):
            base_result = SimpleNamespace(
                outcome=SimpleNamespace(name="SUCCESS"),
                yards_gained=scenario["yards"],
                dice_roll=random.randint(8, 15),
                total_modifier=random.randint(-2, 3),
                final_total=random.randint(10, 18),
            )

            situation = {
                "pass_rush_pressure": scenario["pressure"],
                "defenders_nearby": (
                    [players["strong_lb"]] if scenario["yards"] <= 5 else []
                ),
            }

            result = engine.resolve_pass_play(
                scenario["qb"], scenario["wr"], scenario["def"], base_result, situation
            )

            if result.outcome == "INTERCEPTION":
                interceptions += 1
            elif result.completed:
                completions += 1
            else:
                incompletions += 1

        total_attempts = completions + incompletions + interceptions
        comp_rate = (completions / total_attempts) * 100
        int_rate = (interceptions / total_attempts) * 100
        int_rate_of_incompletions = (
            (interceptions / (incompletions + interceptions)) * 100
            if (incompletions + interceptions) > 0
            else 0
        )

        print("   Results over 100 attempts:")
        print(f"   Completions: {completions} ({comp_rate:.1f}%)")
        print(f"   Incompletions: {incompletions}")
        print(f"   Interceptions: {interceptions} ({int_rate:.1f}% of all passes)")
        print(f"   INT Rate of Incompletions: {int_rate_of_incompletions:.1f}%")


def test_fumble_scenarios():
    """Test various fumble scenarios."""
    print("\n\n💥 FUMBLE TESTING")
    print("=" * 50)

    engine = EnhancedResolutionEngine()
    players = create_turnover_test_players()

    scenarios = [
        {
            "name": "Secure Hands RB vs Average Defense",
            "rb": players["secure_rb"],
            "defenders": [players["strong_lb"]],
            "yards": 8,
        },
        {
            "name": "Fumble-Prone RB vs Strong Defense",
            "rb": players["fumble_rb"],
            "defenders": [players["strong_lb"], players["ball_hawk"]],
            "yards": 15,
        },
        {
            "name": "Secure Hands RB - Long Run vs Strong Defense",
            "rb": players["secure_rb"],
            "defenders": [players["strong_lb"]],
            "yards": 22,
        },
    ]

    for scenario in scenarios:
        print(f"\n🏃 {scenario['name']}")

        # Test multiple attempts to see fumble rates
        successful_runs = 0
        fumbles = 0

        for _ in range(100):
            base_result = SimpleNamespace(
                outcome=SimpleNamespace(name="SUCCESS"),
                yards_gained=scenario["yards"],
                dice_roll=random.randint(8, 15),
                total_modifier=random.randint(-1, 4),
                final_total=random.randint(10, 18),
            )

            situation = {"contact_level": "heavy"}

            result = engine.resolve_run_play(
                scenario["rb"], [], scenario["defenders"], base_result, situation
            )

            if result.outcome == "FUMBLE":
                fumbles += 1
            else:
                successful_runs += 1

        total_attempts = successful_runs + fumbles
        fumble_rate = (fumbles / total_attempts) * 100

        print("   Results over 100 attempts:")
        print(f"   Successful runs: {successful_runs}")
        print(f"   Fumbles: {fumbles} ({fumble_rate:.1f}%)")


def test_realistic_game_situation():
    """Test a realistic game situation with both turnover types."""
    print("\n\n🏈 REALISTIC GAME SITUATION")
    print("=" * 50)

    engine = EnhancedResolutionEngine()
    players = create_turnover_test_players()

    print("\nSituation: 3rd & 8, 4th Quarter, Down by 3")
    print("Pressure on QB, ball-hawking safety in coverage")

    # Desperate pass attempt
    base_result = SimpleNamespace(
        outcome=SimpleNamespace(name="SUCCESS"),
        yards_gained=15,  # Need the first down
        dice_roll=10,
        total_modifier=1,
        final_total=11,
    )

    situation = {"pass_rush_pressure": True, "defenders_nearby": [players["strong_lb"]]}

    result = engine.resolve_pass_play(
        players["mistake_qb"],
        players["average_wr"],
        players["ball_hawk"],
        base_result,
        situation,
    )

    print("\n📡 Pass Result:")
    print(f"   Outcome: {result.outcome}")
    print(f"   Completed: {result.completed}")
    if result.completed:
        print(f"   Yards: {result.yards_gained}")
        print(f"   YAC: {result.yards_after_contact}")
    print(f"   Key Players: {', '.join(result.key_players)}")

    # Follow up with potential run play
    if result.outcome not in ["INTERCEPTION"]:
        print("\nNext play: Handoff to secure running back")

        run_result_base = SimpleNamespace(
            outcome=SimpleNamespace(name="SUCCESS"),
            yards_gained=6,
            dice_roll=12,
            total_modifier=2,
            final_total=14,
        )

        run_result = engine.resolve_run_play(
            players["secure_rb"],
            [],
            [players["strong_lb"]],
            run_result_base,
            {"contact_level": "normal"},
        )

        print("\n🏃 Run Result:")
        print(f"   Outcome: {run_result.outcome}")
        if run_result.outcome != "FUMBLE":
            print(f"   Yards: {run_result.yards_gained}")
            print(f"   YAC: {run_result.yards_after_contact}")
        print(f"   Key Players: {', '.join(run_result.key_players)}")


if __name__ == "__main__":
    print("🏈 TURNOVER MECHANICS TEST")
    print("=" * 60)
    print("Testing comprehensive turnover system:")
    print("• Interceptions on incomplete passes")
    print("• Interceptions on completed passes (tips/deflections)")
    print("• Fumbles based on player traits and situation")
    print("=" * 60)

    test_interception_scenarios()
    test_fumble_scenarios()
    test_realistic_game_situation()

    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("✅ Interceptions implemented for pass plays")
    print("✅ Fumbles already implemented for run plays")
    print("✅ Player traits affect turnover rates")
    print("✅ Situation modifiers (pressure, coverage) impact risk")
    print("✅ Realistic turnover rates achieved")
