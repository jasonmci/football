#!/usr/bin/env python3
"""
Test the new motion and shift abstraction system.

Demonstrates how the system now uses lane/depth/alignment instead of x/y coordinates.
"""

import sys
sys.path.append('src')

from pathlib import Path
from football2.football.play_loader import PlayLoader
from football2.football.yaml_loader import FormationLoader


def test_motion_abstraction():
    """Test that motion uses football abstractions instead of coordinates."""
    print("🏈 TESTING MOTION & SHIFT ABSTRACTIONS")
    print("=" * 50)

    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)

    # Load plays with motion
    motion_plays = [
        "pa_slant_motion.yaml",
        "smash_concept_motion.yaml"
    ]

    for play_file in motion_plays:
        play_path = Path("data/plays/offense") / play_file
        if play_path.exists():
            play = play_loader.load_play(play_path)
            print(f"\n🎯 {play.label}")
            print("-" * 30)

            # Show pre-snap shifts
            if play.pre_snap_shifts:
                print("⚡ Pre-snap Shifts:")
                for shift in play.pre_snap_shifts:
                    shift_info = f"  {shift.player_position}: {shift.action.value}"
                    if shift.target_lane:
                        shift_info += f" → {shift.target_lane}"
                    if shift.target_depth:
                        shift_info += f"/{shift.target_depth}"
                    if shift.target_alignment:
                        shift_info += f"/{shift.target_alignment}"
                    print(shift_info)

            # Show motion
            if play.motion:
                print("🏃 Motion:")
                motion = play.motion
                start = f"{motion.start_lane or '?'}/{motion.start_depth or '?'}"
                end = f"{motion.end_lane or '?'}/{motion.end_depth or '?'}"
                if motion.end_alignment:
                    end += f"/{motion.end_alignment}"
                print(f"  {motion.player_position}: {motion.motion_type}")
                print(f"  Route: {start} → {end} ({motion.speed})")

            # Show formation modifications
            modifications = play.get_formation_modifications()
            if modifications:
                print("📍 Final Position Changes:")
                for player, mods in modifications.items():
                    mod_str = ", ".join([f"{k}={v}" for k, v in mods.items()])
                    print(f"  {player}: {mod_str}")


def test_clean_offensive_plays():
    """Test that offensive plays no longer have defensive_reactions."""
    print("\n\n🧹 TESTING CLEAN OFFENSIVE PLAYS")
    print("=" * 40)

    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)

    # Load all offensive plays
    offense_plays = play_loader.load_plays_from_directory(Path("data/plays/offense"))

    clean_count = 0
    for play_name, play in offense_plays.items():
        has_def_reactions = hasattr(play, 'defensive_reactions') and play.defensive_reactions
        if not has_def_reactions:
            clean_count += 1
        else:
            print(f"⚠️  {play_name} still has defensive reactions!")

    print(f"✅ {clean_count}/{len(offense_plays)} offensive plays are clean")
    print("   (No defensive_reactions on offensive plays)")


if __name__ == "__main__":
    test_motion_abstraction()
    test_clean_offensive_plays()

    print("\n\n🎯 ABSTRACTION BENEFITS:")
    print("• No need to calculate x/y coordinates manually")
    print("• Uses football terminology (lane/depth/alignment)")
    print("• Automatic translation to game board coordinates")
    print("• More intuitive for play designers")
    print("• Cleaner separation of offense/defense concerns")
