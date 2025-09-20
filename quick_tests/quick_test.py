#!/usr/bin/env python3
"""
Quick test of the simulation system with single play execution.
"""

from football_simulator import FootballSimulator  # Adjust the import path if needed


# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
# sys.path.append(os.path.dirname(__file__))


def main():
    """Quick test of simulation system."""
    simulator = FootballSimulator()

    print("🏈 SINGLE PLAY TEST")
    print("=" * 40)

    # Load configurations
    elite_offense = simulator.load_team_config(
        "/Users/jasonmcinerney/repos/football/data/configs/elite_offense_trap.yaml"
    )
    elite_defense = simulator.load_team_config(
        "/Users/jasonmcinerney/repos/football/data/configs/elite_defense_cover3.yaml"
    )

    print(f"Offense: {elite_offense.label}")
    print(f"Defense: {elite_defense.label}")

    # Show player ratings
    print("\n📊 ELITE OFFENSE KEY PLAYERS:")
    print(
        f"   RB: {elite_offense.players['RB1'].name} (Overall: {elite_offense.players['RB1'].overall_rating})"
    )
    print(
        f"   LG: {elite_offense.players['LG'].name} (Overall: {elite_offense.players['LG'].overall_rating})"
    )
    print(
        f"   RG: {elite_offense.players['RG'].name} (Overall: {elite_offense.players['RG'].overall_rating})"
    )

    print("\n🛡️  ELITE DEFENSE KEY PLAYERS:")
    print(
        f"   DT1: {elite_defense.players['DT1'].name} (Overall: {elite_defense.players['DT1'].overall_rating})"
    )
    print(
        f"   DT2: {elite_defense.players['DT2'].name} (Overall: {elite_defense.players['DT2'].overall_rating})"
    )
    print(
        f"   MLB: {elite_defense.players['MLB'].name} (Overall: {elite_defense.players['MLB'].overall_rating})"
    )

    # Run 10 individual plays to see variation
    print("\n🎮 RUNNING 10 INDIVIDUAL PLAYS (with debug info):")
    print("-" * 60)

    for i in range(10):
        # Add debug info to understand what's happening
        situation = {
            "down": 1,
            "distance": 10,
            "field_position": 35,
            "time_remaining": 600,
            "score_differential": 0,
            "pass_rush_pressure": False,
        }

        # Manually check dice roll and modifiers
        base_dice_roll = simulator.rng.randint(2, 12)
        tactical_analysis = simulator._analyze_tactical_matchup(
            elite_offense, elite_defense
        )
        net_modifier = tactical_analysis["net_advantage"]
        final_total = base_dice_roll + net_modifier

        print(
            f"Play {i + 1:2d}: Dice={base_dice_roll:2d} + Mod={net_modifier:+.1f} = Total={final_total:.1f}"
        )

        result = simulator.simulate_single_play(elite_offense, elite_defense, situation)
        print(
            f"        Result: {result.outcome:12s} | {result.yards_gained:2d} yards | {', '.join(result.key_players)}"
        )
        if result.tactical_advantages:
            print(f"        Advantages: {', '.join(result.tactical_advantages)}")

    print("\n✅ Test complete - showing individual play variation")


if __name__ == "__main__":
    main()
