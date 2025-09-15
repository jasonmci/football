#!/usr/bin/env python3
"""
Test the Football Play Resolution Engine

Demonstrates how plays are resolved using dice rolling, formation advantages,
and configurable outcomes. Shows the full cycle from formation matchup to
final yardage result.
"""

import sys
sys.path.append('src')

from pathlib import Path
from football2.football.play_loader import PlayLoader
from football2.football.yaml_loader import FormationLoader
from football2.football.play_resolution import PlayResolutionEngine, ResolutionConfig


def test_play_resolution():
    """Test play resolution with different matchups."""
    print("🎲 FOOTBALL PLAY RESOLUTION ENGINE")
    print("=" * 60)
    
    # Load plays
    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)
    
    offense_plays = play_loader.load_plays_from_directory(Path("data/plays/offense"))
    defense_plays = play_loader.load_plays_from_directory(Path("data/plays/defense"))
    
    # Create resolution engine
    engine = PlayResolutionEngine(seed=42)  # Fixed seed for consistent testing
    
    # Test scenarios
    scenarios = [
        {
            "name": "POWER vs RUN DEFENSE",
            "offense": "power_left",
            "defense": "bear46_run_commit",
            "situation": {"down": 1, "distance": 2, "field_position": 3},
            "description": "Goal line stand - 1st and Goal from the 3"
        },
        {
            "name": "QUICK PASS vs BLITZ",
            "offense": "empty_slants", 
            "defense": "nickel_doubleA_cover2",
            "situation": {"down": 3, "distance": 8, "field_position": 45},
            "description": "3rd and 8 from midfield"
        },
        {
            "name": "DEEP SHOT vs PREVENT",
            "offense": "four_verts",
            "defense": "prevent_quarters", 
            "situation": {"down": 2, "distance": 15, "field_position": 25},
            "description": "2nd and 15 from the 25 - need big play"
        },
        {
            "name": "BALANCED vs BASE",
            "offense": "inside_zone_right",
            "defense": "43_cover3_base",
            "situation": {"down": 1, "distance": 10, "field_position": 50},
            "description": "1st and 10 from midfield"
        },
        {
            "name": "MOTION CONCEPT",
            "offense": "smash_concept_motion",
            "defense": "nickel_zone_blitz_showA",
            "situation": {"down": 2, "distance": 6, "field_position": 15},
            "description": "2nd and 6 in the red zone"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🏈 SCENARIO {i}: {scenario['name']}")
        print("-" * 50)
        print(f"📍 {scenario['description']}")
        
        off_play = offense_plays.get(scenario['offense'])
        def_play = defense_plays.get(scenario['defense'])
        
        if not off_play or not def_play:
            print(f"❌ Missing play: {scenario['offense']} or {scenario['defense']}")
            continue
        
        print(f"⚡ Offense: {off_play.label}")
        print(f"🛡️  Defense: {def_play.label}")
        
        # Resolve the play multiple times to show variability
        print(f"\n🎲 RESOLUTION RESULTS:")
        
        for attempt in range(3):
            result = engine.resolve_play(off_play, def_play, scenario['situation'])
            
            # Format the result display
            outcome_emoji = {
                "explosive_success": "🚀",
                "big_success": "💪", 
                "success": "✅",
                "moderate_gain": "➡️",
                "no_gain": "🛑",
                "loss": "📉",
                "big_loss": "💥",
                "turnover": "🔄"
            }
            
            emoji = outcome_emoji.get(result.outcome.value, "❓")
            
            print(f"  {emoji} Attempt {attempt + 1}: {result.description}")
            print(f"     Dice: {result.dice_roll} + {result.total_modifier} = {result.final_total}")
            
            # Show key modifiers
            mods = result.details["modifiers"]
            mod_details = []
            for mod_type, value in mods.items():
                if value != 0:
                    sign = "+" if value > 0 else ""
                    mod_details.append(f"{mod_type} {sign}{value}")
            
            if mod_details:
                print(f"     Modifiers: {', '.join(mod_details)}")
            
            # Show advantage/disadvantage dice
            adv = result.details["advantage"]
            dis = result.details["disadvantage"]
            if adv or dis:
                dice_info = []
                if adv: dice_info.append(f"advantage +{adv}")
                if dis: dice_info.append(f"disadvantage -{dis}")
                print(f"     Dice: {', '.join(dice_info)}")


def test_configurable_outcomes():
    """Test different resolution configurations."""
    print(f"\n\n⚙️  TESTING CONFIGURABLE OUTCOMES")
    print("=" * 45)
    
    # Create custom config for high-scoring games
    high_scoring_config = ResolutionConfig()
    high_scoring_config.formation_bonuses = {
        3: +6,   # Bigger bonuses
        1: +3,
        0: 0,
        -1: -3, 
        -3: -6
    }
    # Update specific thresholds for easier scoring
    from football2.football.play_resolution import PlayOutcome
    high_scoring_config.thresholds[PlayOutcome.EXPLOSIVE_SUCCESS] = 16  # Was 18
    high_scoring_config.thresholds[PlayOutcome.BIG_SUCCESS] = 13        # Was 15
    high_scoring_config.thresholds[PlayOutcome.SUCCESS] = 10            # Was 12
    
    # Create conservative config for defensive games
    defensive_config = ResolutionConfig()
    # Update specific thresholds for harder scoring
    defensive_config.thresholds[PlayOutcome.EXPLOSIVE_SUCCESS] = 20  # Was 18
    defensive_config.thresholds[PlayOutcome.BIG_SUCCESS] = 17        # Was 15
    defensive_config.thresholds[PlayOutcome.SUCCESS] = 14            # Was 12
    
    # Test the same play with different configs
    formation_loader = FormationLoader()
    play_loader = PlayLoader(formation_loader)
    
    offense_plays = play_loader.load_plays_from_directory(Path("data/plays/offense"))
    defense_plays = play_loader.load_plays_from_directory(Path("data/plays/defense"))
    
    off_play = offense_plays["power_left"]
    def_play = defense_plays["43_cover3_base"] 
    situation = {"down": 1, "distance": 10, "field_position": 50}
    
    configs = [
        ("Standard", PlayResolutionEngine(seed=123)),
        ("High-Scoring", PlayResolutionEngine(high_scoring_config, seed=123)),
        ("Defensive", PlayResolutionEngine(defensive_config, seed=123))
    ]
    
    print(f"\n🔄 Same matchup with different configurations:")
    print(f"   {off_play.label} vs {def_play.label}")
    
    for config_name, engine in configs:
        result = engine.resolve_play(off_play, def_play, situation)
        print(f"\n📊 {config_name} Config:")
        print(f"   {result.description}")
        print(f"   Roll: {result.dice_roll} + {result.total_modifier} = {result.final_total}")


if __name__ == "__main__":
    test_play_resolution()
    test_configurable_outcomes()
    
    print(f"\n\n🏆 RESOLUTION ENGINE FEATURES:")
    print("• Advanced dice mechanics with advantage/disadvantage")
    print("• Formation matchup analysis impacts dice modifiers")
    print("• Situational awareness (down, distance, field position)")
    print("• Configurable outcome thresholds and yardage ranges")
    print("• Detailed result tracking with modifier breakdown")
    print("• Narrative descriptions of play outcomes")
    print("• Multiple resolution configs for different game styles")
