#!/usr/bin/env python3
"""
Test the enhanced play resolution engine with specific play examples.

This demonstrates how pulling guards, blitzes, and other tactical elements
affect play outcomes in realistic ways.
"""


import sys

from pathlib import Path
from football2.football.play_loader import PlayLoader
from football2.football.yaml_loader import FormationLoader
from football2.football.play_resolution import PlayResolutionEngine
from football2.football.play_analyzer import PlayAnalyzer

sys.path.append("src")
print("🚀 Starting advanced resolution test...")
print("✅ All imports successful")


def test_matchup():
    """Test any available offensive vs defensive play matchup."""
    print("\n🏈 Testing Play Assignment Analysis")
    print("=" * 50)

    # Initialize loaders
    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)

    # Load plays
    offense_dir = Path("data/plays/offense")
    defense_dir = Path("data/plays/defense")

    print(f"Loading from {offense_dir} and {defense_dir}...")

    offensive_plays = play_loader.load_plays_from_directory(offense_dir)
    defensive_plays = play_loader.load_plays_from_directory(defense_dir)

    print(
        f"Loaded {len(offensive_plays)} offensive and {len(defensive_plays)} defensive plays"
    )

    if not offensive_plays or not defensive_plays:
        print("❌ No plays found")
        return

    # Get first available plays
    off_play = list(offensive_plays.values())[0]
    def_play = list(defensive_plays.values())[0]

    print(f"\nOffensive Play: {off_play.label}")
    print(f"Defensive Play: {def_play.label}")

    # Show assignments that create advantages/disadvantages
    print("\n📋 Key Offensive Assignments:")
    for assign in off_play.assignments[:5]:
        details = assign.details or {}
        extra_info = ""
        if details.get("scheme") == "pull":
            extra_info = " 🎯 (PULLING GUARD!)"
        elif details.get("technique") == "crack":
            extra_info = " 🎯 (CRACK BLOCK!)"
        elif assign.assignment_type.value == "lead_block":
            extra_info = " 🎯 (LEAD BLOCKER!)"

        print(f"  {assign.player_position}: {assign.assignment_type.value}{extra_info}")

    print("\n🛡️ Key Defensive Assignments:")
    for assign in def_play.assignments[:5]:
        details = assign.details or {}
        # Handle case where details might be a string
        if isinstance(details, str):
            details = {}
        extra_info = ""
        if assign.assignment_type.value == "blitz":
            extra_info = " 🎯 (BLITZING!)"
        elif details.get("technique") == "stunt":
            extra_info = " 🎯 (STUNTING!)"

        print(f"  {assign.player_position}: {assign.assignment_type.value}{extra_info}")

    # Analyze matchup
    print("\n🔍 Analyzing tactical matchup...")
    analyzer = PlayAnalyzer()
    analysis = analyzer.analyze_play_matchup(off_play, def_play)

    print("\n📊 Tactical Analysis:")
    print(f"Net Impact: {analysis.net_impact:+d}")
    print(f"Confidence: {analysis.confidence:.1%}")

    if analysis.advantages:
        print("\n✅ Tactical Advantages:")
        for adv in analysis.advantages:
            print(f"  • {adv.description} ({adv.impact:+d})")

    if analysis.disadvantages:
        print("\n❌ Tactical Disadvantages:")
        for dis in analysis.disadvantages:
            print(f"  • {dis.description} ({dis.impact:+d})")

    if not analysis.advantages and not analysis.disadvantages:
        print("\n⚖️ No significant tactical advantages detected")
        print("This could mean:")
        print("• Both schemes are well-matched")
        print("• The analyzer needs more specific assignment data")
        print("• The plays don't have distinctive tactical elements")

    # Show resolution with the enhanced engine
    print("\n🎲 Enhanced Resolution Examples:")
    engine = PlayResolutionEngine(seed=42)

    scenarios = [
        {
            "down": 1,
            "distance": 10,
            "field_position": 50,
            "desc": "1st & 10 at midfield",
        },
        {
            "down": 3,
            "distance": 3,
            "field_position": 15,
            "desc": "3rd & short in red zone",
        },
    ]

    for scenario in scenarios:
        result = engine.resolve_play(off_play, def_play, scenario)
        print(f"\n  {scenario['desc']}:")
        print(f"    Outcome: {result.outcome.value} ({result.yards_gained:+d} yards)")
        print(
            f"    Dice: {result.dice_roll} + Modifiers: {result.total_modifier} = {result.final_total}"
        )
        print(f"    Description: {result.description}")

        # Show key modifiers
        key_mods = [
            f"{k}: {v:+d}" for k, v in result.details["modifiers"].items() if v != 0
        ]
        if key_mods:
            print(f"    Key Modifiers: {', '.join(key_mods[:3])}")


def demonstrate_specific_advantages():
    """Show how specific play elements create advantages."""
    print("\n\n🎯 SPECIFIC TACTICAL EXAMPLES")
    print("=" * 50)

    print("How the enhanced engine analyzes real football tactics:")
    print("\n🔄 PULLING GUARDS:")
    print("  • Counter plays with pulling guards get +2 advantage")
    print("  • Creates extra gaps and outnumbers defense at point of attack")
    print("  • Especially effective vs 4-3 defenses")

    print("\n💨 BLITZES:")
    print("  • Corner/safety blitzes create pressure (-1 to -3 disadvantage)")
    print("  • But also create coverage holes (+1 to +2 advantage for quick passes)")
    print("  • Net effect depends on play type and protection scheme")

    print("\n🔨 CRACK BLOCKS:")
    print("  • WR crack blocks on linebackers get +1 advantage")
    print("  • Seals inside pursuit on outside runs")
    print("  • Creates confusion in linebacker fits")

    print("\n🌪️ DEFENSIVE STUNTS:")
    print("  • DL stunts vs basic pass protection get +2 advantage for defense")
    print("  • Confused blocking assignments lead to free rushers")
    print("  • Countered by slide protection or quick passes")

    print("\n💪 POWER CONCEPTS:")
    print("  • Extra blockers (FB, pulling guard) get +1 to +2 advantage")
    print("  • Physical advantage at point of attack")
    print("  • Especially effective on short yardage")


if __name__ == "__main__":
    print("🏈 ADVANCED FOOTBALL PLAY RESOLUTION TESTING")
    print("Demonstrating how specific play assignments affect outcomes")
    print("=" * 70)

    try:
        test_matchup()
        demonstrate_specific_advantages()

        print("\n\n🎮 SUMMARY: THE MISSING PIECE")
        print("=" * 50)
        print(
            "Your football engine now analyzes the actual TACTICS that create advantages:"
        )
        print("\n✅ What we've built:")
        print("• PlayAnalyzer examines every player assignment")
        print("• Identifies tactical advantages (pulling guards, blitzes, etc.)")
        print("• Converts tactics into gameplay modifiers")
        print("• Enhanced resolution engine uses tactical analysis")
        print("• Realistic descriptions include tactical context")
        print("\n🚀 This creates authentic football strategy where:")
        print("• Counter plays with pulling guards beat basic defenses")
        print("• Blitzes create pressure but holes in coverage")
        print("• Crack blocks and power concepts matter")
        print("• Specific play calls beat specific defensive schemes")
        print("\nNow you have a remarkably sophisticated football game! 🏆")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
