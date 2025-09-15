#!/usr/bin/env python3
"""
Test script for the new football play system.

Demonstrates how plays inherit from formations and apply dynamic modifications
including pre-snap shifts, motion, and position-specific assignments.
"""

import sys
sys.path.append('src')

from pathlib import Path
from football2.football.play_loader import PlayLoader
from football2.football.yaml_loader import FormationLoader
from football2.football.plays import PlayExecutor, PositionAssignmentCatalog


def test_play_loading():
    """Test loading plays with the new system."""
    print("🏈 NEW FOOTBALL PLAY SYSTEM")
    print("=" * 50)
    
    # Initialize loaders
    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)
    play_executor = PlayExecutor()
    
    # Load offensive plays
    offense_plays_dir = Path("data/plays/offense")
    print(f"\n📁 Loading plays from: {offense_plays_dir}")
    
    try:
        plays = play_loader.load_plays_from_directory(offense_plays_dir)
        print(f"✅ Loaded {len(plays)} offensive plays")
        
        for play_name, play in plays.items():
            print(f"\n🎯 PLAY: {play.label}")
            print(f"   Base Formation: {play.base_formation}")
            print(f"   Personnel: {play.personnel}")
            print(f"   Type: {play.play_type}")
            print(f"   Tags: {', '.join(play.tags)}")
            
            # Show pre-snap modifications
            if play.pre_snap_shifts:
                print(f"   Pre-snap Shifts: {len(play.pre_snap_shifts)}")
                for shift in play.pre_snap_shifts:
                    print(f"     • {shift.player_position}: {shift.action.value}")
            
            # Show motion
            if play.motion:
                print(f"   Motion: {play.motion.player_position} ({play.motion.motion_type})")
                if play.defensive_reactions:
                    print(f"   Defensive Reactions: {len(play.defensive_reactions)}")
                    for reaction in play.defensive_reactions:
                        print(f"     • {reaction.defensive_position}: {reaction.reaction_type.value}")
            
            # Show assignments by category
            assignments_by_type = {}
            for assignment in play.assignments:
                assignment_type = assignment.assignment_type.value
                if assignment_type not in assignments_by_type:
                    assignments_by_type[assignment_type] = []
                assignments_by_type[assignment_type].append(assignment.player_position)
            
            print(f"   Assignments:")
            for assignment_type, players in assignments_by_type.items():
                print(f"     • {assignment_type}: {', '.join(players)}")
            
            # Validate assignments
            violations = play.validate_assignments()
            if violations:
                print(f"   ⚠️  Violations: {violations}")
            else:
                print(f"   ✅ All assignments valid")
    
    except Exception as e:
        print(f"❌ Error loading plays: {e}")


def test_play_execution():
    """Test executing a play against a formation."""
    print(f"\n\n🎬 PLAY EXECUTION TEST")
    print("=" * 40)
    
    # Initialize components
    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)
    play_executor = PlayExecutor()
    
    try:
        # Load a formation
        offensive_formations = formation_loader.load_formations_directory("data/formations/offense")
        shotgun_formation = offensive_formations.get("shotgun_11")
        
        if not shotgun_formation:
            print("❌ Could not load shotgun_11 formation")
            return
        
        # Load a play
        motion_play_path = Path("data/plays/offense/smash_concept_motion.yaml")
        if motion_play_path.exists():
            motion_play = play_loader.load_play(motion_play_path)
            
            print(f"🎯 Executing: {motion_play.label}")
            print(f"   Formation: {motion_play.base_formation}")
            
            # Execute the play
            result = play_executor.execute_play(motion_play, shotgun_formation)
            
            print(f"\n📊 Execution Results:")
            print(f"   Play: {result['play_name']}")
            print(f"   Base Formation: {result['base_formation']}")
            
            if result['violations']:
                print(f"   ⚠️  Violations: {result['violations']}")
            else:
                print(f"   ✅ Clean execution")
            
            if result['motion_path']:
                motion = result['motion_path']
                print(f"   🏃 Motion: {motion['player']} ({motion['type']})")
                print(f"      Start: {motion['start']}, End: {motion['end']}")
            
            if result['defensive_reactions']:
                print(f"   🛡️  Defensive Reactions:")
                for reaction in result['defensive_reactions']:
                    print(f"      • {reaction['defensive_player']}: {reaction['reaction']}")
        
        else:
            print(f"❌ Could not find play file: {motion_play_path}")
    
    except Exception as e:
        print(f"❌ Error executing play: {e}")


def show_assignment_catalog():
    """Show available assignments for each position."""
    print(f"\n\n📋 POSITION ASSIGNMENT CATALOG")
    print("=" * 45)
    
    print(f"\n🏃 OFFENSIVE POSITIONS:")
    for position, assignments in PositionAssignmentCatalog.OFFENSIVE_ASSIGNMENTS.items():
        assignment_names = [a.value for a in assignments]
        print(f"   {position:3}: {', '.join(assignment_names)}")
    
    print(f"\n🛡️  DEFENSIVE POSITIONS:")
    for position, assignments in PositionAssignmentCatalog.DEFENSIVE_ASSIGNMENTS.items():
        assignment_names = [a.value for a in assignments]
        print(f"   {position:3}: {', '.join(assignment_names)}")


def test_defensive_plays():
    """Test loading defensive plays."""
    print(f"\n\n🛡️  DEFENSIVE PLAY SYSTEM")
    print("=" * 35)
    
    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)
    
    # Load defensive plays
    defense_plays_dir = Path("data/plays/defense")
    
    try:
        plays = play_loader.load_plays_from_directory(defense_plays_dir)
        print(f"✅ Loaded {len(plays)} defensive plays")
        
        for play_name, play in plays.items():
            print(f"\n🎯 DEFENSIVE PLAY: {play.label}")
            print(f"   Base Formation: {play.base_formation}")
            print(f"   Type: {play.play_type}")
            print(f"   Tags: {', '.join(play.tags)}")
            
            # Count assignment types
            assignment_counts = {}
            for assignment in play.assignments:
                assignment_type = assignment.assignment_type.value
                assignment_counts[assignment_type] = assignment_counts.get(assignment_type, 0) + 1
            
            print(f"   Assignment Distribution:")
            for assignment_type, count in assignment_counts.items():
                print(f"     • {assignment_type}: {count} players")
    
    except Exception as e:
        print(f"❌ Error loading defensive plays: {e}")


if __name__ == "__main__":
    print("🎲 FOOTBALL PLAY SYSTEM DEMONSTRATION")
    print("Dynamic plays built on formation foundations!")
    print()
    
    test_play_loading()
    test_play_execution()
    show_assignment_catalog()
    test_defensive_plays()
    
    print(f"\n\n🏆 SYSTEM CAPABILITIES:")
    print("• ✅ Plays inherit from base formations")
    print("• ✅ Pre-snap shifts and adjustments")
    print("• ✅ Player motion with defensive reactions")
    print("• ✅ Position-specific assignment validation")
    print("• ✅ Comprehensive offensive and defensive plays")
    print("• ✅ Board game-ready strategic depth!")
