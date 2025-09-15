#!/usr/bin/env python3
"""
Interactive Play Selector - Choose offensive and defensive plays and see simulation results
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import random

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from football2.football.enhanced_resolution import (
    EnhancedResolutionEngine, PlayerProfile, SkillCategory
)


class InteractivePlaySelector:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.engine = EnhancedResolutionEngine()
        
        # Create average players for simulation
        self.average_players = self._create_average_players()
        
    def _create_average_players(self):
        """Create average players for all positions"""
        players = {}
        
        # Offensive positions
        offensive_positions = [
            "QB", "RB", "FB", "WR1", "WR2", "WR3", "WR4", "WR5", 
            "TE1", "TE2", "LT", "LG", "C", "RG", "RT"
        ]
        
        # Defensive positions
        defensive_positions = [
            "DE1", "DE2", "DT1", "DT2", "NT", "OLB1", "OLB2", "MLB1", "MLB2", 
            "CB1", "CB2", "CB3", "SS", "FS", "NB"  # NB = Nickel Back
        ]
        
        all_positions = offensive_positions + defensive_positions
        
        for position in all_positions:
            players[position] = PlayerProfile(
                name=f"Average {position}",
                position=position,
                overall_rating=75,
                skills={
                    SkillCategory.AWARENESS: 75,
                    SkillCategory.HANDS: 75,
                    SkillCategory.STRENGTH: 75,
                    SkillCategory.AGILITY: 75,
                    SkillCategory.SPEED: 75,
                    SkillCategory.PASS_BLOCKING: 75,
                    SkillCategory.RUN_BLOCKING: 75,
                    SkillCategory.PASS_RUSH: 75,
                    SkillCategory.RUN_DEFENSE: 75,
                    SkillCategory.COVERAGE: 75,
                    SkillCategory.TACKLE: 75,
                    SkillCategory.ROUTE_RUNNING: 75,
                },
                traits=["average"]
            )
        
        return players
    
    def list_plays(self, play_type):
        """List available plays of given type (offense/defense)"""
        plays_dir = self.repo_root / "data" / "plays" / play_type
        play_files = [f.stem for f in plays_dir.glob("*.yaml")]
        return sorted(play_files)
    
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
                if choice.lower() in ['q', 'quit', 'exit']:
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
    
    def load_play_data(self, play_name, play_type):
        """Load play data from YAML file"""
        try:
            play_file = self.repo_root / "data" / "plays" / play_type / f"{play_name}.yaml"
            with open(play_file, 'r') as f:
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
        
        if 'description' in play_data:
            print(f"Description: {play_data['description']}")
        
        if 'tactical_advantages' in play_data:
            print(f"Tactical Advantages: {', '.join(play_data['tactical_advantages'])}")
        
        if 'execution_notes' in play_data:
            print(f"Execution: {play_data['execution_notes']}")
    
    def simulate_play_matchup(self, offensive_play, defensive_play):
        """Simulate the selected plays and show results using basic logic"""
        try:
            offense_data = self.load_play_data(offensive_play, "offense")
            defense_data = self.load_play_data(defensive_play, "defense")
            
            if not offense_data or not defense_data:
                return None
            
            print(f"\n{'='*60}")
            print(f"SIMULATING: {offensive_play.replace('_', ' ').title()} vs {defensive_play.replace('_', ' ').title()}")
            print(f"{'='*60}")
            
            # Show play details
            self.show_play_details(offensive_play, "offense")
            self.show_play_details(defensive_play, "defense")
            
            print(f"\n{'SIMULATION RESULTS':^60}")
            print("-" * 60)
            
            # Simple simulation logic based on play characteristics
            results = []
            for i in range(10):
                result = self._simulate_single_play(offense_data, defense_data)
                results.append(result)
                outcome = result['outcome']
                yards = result['yards']
                print(f"Sim {i+1:2d}: {yards:+3d} yards - {outcome}")
            
            # Show summary statistics
            total_yards = sum(r['yards'] for r in results)
            avg_yards = total_yards / len(results)
            max_yards = max(r['yards'] for r in results)
            min_yards = min(r['yards'] for r in results)
            
            # Count outcomes
            outcomes = {}
            for result in results:
                outcomes[result['outcome']] = outcomes.get(result['outcome'], 0) + 1
            
            print("-" * 60)
            print(f"SUMMARY ({len(results)} simulations):")
            print(f"  Average: {avg_yards:+5.1f} yards")
            print(f"  Range: {min_yards:+3d} to {max_yards:+3d} yards")
            print(f"  Total: {total_yards:+4d} yards")
            
            print(f"\nOUTCOME BREAKDOWN:")
            for outcome, count in sorted(outcomes.items()):
                percentage = (count / len(results)) * 100
                print(f"  {outcome}: {count}/{len(results)} ({percentage:.0f}%)")
            
            return results
            
        except Exception as e:
            print(f"Error simulating play: {e}")
            return None
    
    def _simulate_single_play(self, offense_data, defense_data):
        """Simple simulation logic for a single play"""
        # Base success chance
        base_yards = 0
        outcome = "incomplete"
        
        # Determine play type from offense data
        play_type = self._determine_play_type(offense_data)
        
        # Get tactical advantages
        off_advantages = offense_data.get('tactical_advantages', [])
        def_advantages = defense_data.get('tactical_advantages', [])
        
        # Simple simulation based on play type and matchups
        if play_type == "run":
            base_yards = random.randint(-2, 8)
            outcomes = ["successful_run", "stuffed", "big_gain", "fumble"]
            weights = [60, 25, 13, 2]
            
            # Adjust for tactical matchups
            if "goal_line_power" in off_advantages and "goal_line_stop" in def_advantages:
                base_yards -= 1  # Even matchup
            elif "outside_speed" in off_advantages and "edge_discipline" not in def_advantages:
                base_yards += 2  # Advantage to offense
            elif "gap_control" in def_advantages and "power_running" in off_advantages:
                base_yards -= 1  # Advantage to defense
            
        elif play_type == "pass":
            base_yards = random.randint(-1, 12)
            outcomes = ["complete", "incomplete", "interception", "sack"]
            weights = [45, 40, 8, 7]
            
            # Adjust for tactical matchups
            if "deep_threat" in off_advantages and "deep_coverage" in def_advantages:
                base_yards += 1  # Even but slight edge to offense
            elif "quick_timing" in off_advantages and "pass_rush" in def_advantages:
                weights = [50, 35, 5, 10]  # More sacks
            elif "mismatch_creation" in off_advantages:
                base_yards += 3  # Good advantage
                
        else:  # Special plays
            base_yards = random.randint(-3, 15)
            outcomes = ["successful", "failed", "turnover", "big_play"]
            weights = [50, 35, 10, 5]
        
        # Select outcome based on weights
        outcome = random.choices(outcomes, weights=weights)[0]
        
        # Adjust yards based on outcome
        if outcome in ["stuffed", "failed", "sack"]:
            base_yards = min(base_yards, random.randint(-3, 1))
        elif outcome in ["big_gain", "big_play"]:
            base_yards = max(base_yards, random.randint(8, 25))
        elif outcome in ["fumble", "interception", "turnover"]:
            base_yards = random.randint(-5, 0)
        
        return {
            'yards': base_yards,
            'outcome': outcome
        }
    
    def _determine_play_type(self, offense_data):
        """Determine if play is run, pass, or special based on play data"""
        name = offense_data.get('name', '').lower()
        description = offense_data.get('description', '').lower()
        execution = offense_data.get('execution_notes', '').lower()
        
        # Check for run indicators
        run_keywords = ['run', 'zone', 'power', 'draw', 'sweep', 'dive', 'trap', 'counter']
        pass_keywords = ['pass', 'slant', 'route', 'throw', 'reception', 'vert', 'screen']
        
        text_to_check = f"{name} {description} {execution}"
        
        run_count = sum(1 for keyword in run_keywords if keyword in text_to_check)
        pass_count = sum(1 for keyword in pass_keywords if keyword in text_to_check)
        
        if run_count > pass_count:
            return "run"
        elif pass_count > run_count:
            return "pass"
        else:
            return "special"
    
    def run_interactive_session(self):
        """Main interactive loop"""
        print("=" * 60)
        print("FOOTBALL PLAY SIMULATOR - Interactive Mode")
        print("=" * 60)
        print("Choose offensive and defensive plays to simulate!")
        print("(All players have average ratings: 75 overall)")
        print("Type 'q' at any prompt to quit")
        
        while True:
            print("\n" + "="*60)
            
            # Get offensive play choice
            offensive_play = self.get_play_choice("offense")
            if offensive_play is None:
                break
            
            # Get defensive play choice  
            defensive_play = self.get_play_choice("defense")
            if defensive_play is None:
                break
            
            # Simulate the matchup
            results = self.simulate_play_matchup(offensive_play, defensive_play)
            
            # Ask if user wants to continue
            print("\n" + "-"*60)
            continue_choice = input("Run another simulation? (y/n): ").strip().lower()
            if continue_choice in ['n', 'no', 'q', 'quit']:
                break
        
        print("\nThanks for using the Football Play Simulator!")


if __name__ == "__main__":
    selector = InteractivePlaySelector()
    selector.run_interactive_session()
    
    def list_plays(self, play_type):
        """List available plays of given type (offense/defense)"""
        plays_dir = self.repo_root / "data" / "plays" / play_type
        play_files = [f.stem for f in plays_dir.glob("*.yaml")]
        return sorted(play_files)
    
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
                if choice.lower() in ['q', 'quit', 'exit']:
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
        try:
            play_file = self.repo_root / "data" / "plays" / play_type / f"{play_name}.yaml"
            with open(play_file, 'r') as f:
                play_data = yaml.safe_load(f)
            
            print(f"\n{play_type.upper()} PLAY DETAILS:")
            print("=" * 50)
            print(f"Name: {play_data.get('name', play_name)}")
            print(f"Formation: {play_data.get('formation', 'Unknown')}")
            print(f"Personnel: {play_data.get('personnel', 'Unknown')}")
            
            if 'description' in play_data:
                print(f"Description: {play_data['description']}")
            
            if 'tactical_advantages' in play_data:
                print(f"Tactical Advantages: {', '.join(play_data['tactical_advantages'])}")
            
            if 'execution_notes' in play_data:
                print(f"Execution: {play_data['execution_notes']}")
                
        except Exception as e:
            print(f"Could not load play details: {e}")
    
    def simulate_play(self, offensive_play, defensive_play):
        """Simulate the selected plays and show results"""
        try:
            # Load plays
            offense_play = self.play_repo.get_play("offense", offensive_play)
            defense_play = self.play_repo.get_play("defense", defensive_play)
            
            print(f"\n{'='*60}")
            print(f"SIMULATING: {offensive_play.replace('_', ' ').title()} vs {defensive_play.replace('_', ' ').title()}")
            print(f"{'='*60}")
            
            # Show play details
            self.show_play_details(offensive_play, "offense")
            self.show_play_details(defensive_play, "defense")
            
            print(f"\n{'SIMULATION RESULTS':^60}")
            print("-" * 60)
            
            # Run multiple simulations to show variance
            results = []
            for i in range(10):
                result = self.engine.resolve_play(
                    offense_play, 
                    defense_play, 
                    self.average_roster, 
                    self.average_roster
                )
                results.append(result)
                print(f"Sim {i+1:2d}: {result.yards_gained:+3d} yards - {result.outcome}")
            
            # Show summary statistics
            total_yards = sum(r.yards_gained for r in results)
            avg_yards = total_yards / len(results)
            max_yards = max(r.yards_gained for r in results)
            min_yards = min(r.yards_gained for r in results)
            
            # Count outcomes
            outcomes = {}
            for result in results:
                outcomes[result.outcome] = outcomes.get(result.outcome, 0) + 1
            
            print("-" * 60)
            print(f"SUMMARY ({len(results)} simulations):")
            print(f"  Average: {avg_yards:+5.1f} yards")
            print(f"  Range: {min_yards:+3d} to {max_yards:+3d} yards")
            print(f"  Total: {total_yards:+4d} yards")
            
            print(f"\nOUTCOME BREAKDOWN:")
            for outcome, count in sorted(outcomes.items()):
                percentage = (count / len(results)) * 100
                print(f"  {outcome}: {count}/{len(results)} ({percentage:.0f}%)")
            
            return results
            
        except Exception as e:
            print(f"Error simulating play: {e}")
            return None
    
    def run_interactive_session(self):
        """Main interactive loop"""
        print("=" * 60)
        print("FOOTBALL PLAY SIMULATOR - Interactive Mode")
        print("=" * 60)
        print("Choose offensive and defensive plays to simulate!")
        print("(All players have average ratings: 75 overall)")
        print("Type 'q' at any prompt to quit")
        
        while True:
            print("\n" + "="*60)
            
            # Get offensive play choice
            offensive_play = self.get_play_choice("offense")
            if offensive_play is None:
                break
            
            # Get defensive play choice  
            defensive_play = self.get_play_choice("defense")
            if defensive_play is None:
                break
            
            # Simulate the matchup
            results = self.simulate_play(offensive_play, defensive_play)
            
            # Ask if user wants to continue
            print("\n" + "-"*60)
            continue_choice = input("Run another simulation? (y/n): ").strip().lower()
            if continue_choice in ['n', 'no', 'q', 'quit']:
                break
        
        print("\nThanks for using the Football Play Simulator!")


if __name__ == "__main__":
    selector = InteractivePlaySelector()
    selector.run_interactive_session()
