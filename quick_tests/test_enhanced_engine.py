#!/usr/bin/env python3
"""
Test the enhanced resolution engine directly.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from football.enhanced_resolution import (
    EnhancedResolutionEngine,
    PlayerProfile,
    SkillCategory,
)
from types import SimpleNamespace
import random


def create_test_players():
    """Create test players."""

    # Elite running back
    elite_rb = PlayerProfile(
        name="Elite RB",
        position="RB",
        overall_rating=87,
        skills={
            SkillCategory.STRENGTH: 88,
            SkillCategory.AGILITY: 85,
            SkillCategory.SPEED: 84,
        },
        traits=["secure_hands"],
    )

    # Average blockers
    elite_lg = PlayerProfile(
        name="Elite LG",
        position="LG",
        overall_rating=86,
        skills={SkillCategory.STRENGTH: 89, SkillCategory.RUN_BLOCKING: 90},
        traits=[],
    )

    # Elite defenders
    elite_dt = PlayerProfile(
        name="Elite DT",
        position="DT",
        overall_rating=87,
        skills={
            SkillCategory.STRENGTH: 94,
            SkillCategory.RUN_DEFENSE: 92,
            SkillCategory.TACKLE: 89,
        },
        traits=["run_stuffer"],
    )

    return elite_rb, elite_lg, elite_dt


def main():
    """Test enhanced resolution directly."""
    engine = EnhancedResolutionEngine()
    runner, blocker, defender = create_test_players()

    print("🏈 ENHANCED RESOLUTION ENGINE TEST")
    print("=" * 50)
    print(f"Runner: {runner.name} (Rating: {runner.overall_rating})")
    print(f"Blocker: {blocker.name} (Rating: {blocker.overall_rating})")
    print(f"Defender: {defender.name} (Rating: {defender.overall_rating})")

    # Test different base results
    base_yards_tests = [2, 5, 8, 12, 15]

    for base_yards in base_yards_tests:
        print(f"\n📊 BASE YARDS: {base_yards}")
        print("-" * 30)

        # Run 5 simulations for each base yards
        for i in range(5):
            base_result = SimpleNamespace(
                outcome=SimpleNamespace(name="SUCCESS"),
                yards_gained=base_yards,
                dice_roll=random.randint(8, 15),
                total_modifier=random.randint(-1, 3),
                final_total=random.randint(10, 18),
            )

            situation = {"contact_level": "normal"}

            result = engine.resolve_run_play(
                runner, [blocker], [defender], base_result, situation
            )

            print(
                f"  Run {i + 1}: {result.outcome:12s} | {result.yards_gained:2d} yards | YAC: {getattr(result, 'yards_after_contact', 0)}"
            )

    print("\n✅ Direct test complete")


if __name__ == "__main__":
    main()
