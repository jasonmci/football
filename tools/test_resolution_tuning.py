#!/usr/bin/env python3
"""
Simple test to verify our realistic tuning is working.
Tests the resolution engine directly with trap/power advantages.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from football2.football.play_resolution import PlayResolutionEngine, create_realistic_config, create_arcade_config
from football2.football.play_analyzer import PlayAnalysis, PlayMatchupFactor
from football2.football.plays import FootballPlay
import statistics

def create_test_plays():
    """Create simple test plays."""
    
    # Simple trap play
    trap_play = FootballPlay(
        name="trap_right",
        label="Trap Right",
        play_type="run",
        base_formation="I-formation",
        personnel=["I-formation"],
        assignments=[]
    )
    
    # Simple power play  
    power_play = FootballPlay(
        name="power_right",
        label="Power Right", 
        play_type="run",
        base_formation="I-formation",
        personnel=["I-formation"],
        assignments=[]
    )
    
    # Simple defense
    defense = FootballPlay(
        name="base_defense",
        label="Base Defense",
        play_type="defense", 
        base_formation="4-3",
        personnel=["Base"],
        assignments=[]
    )
    
    return trap_play, power_play, defense

def create_test_analysis(play_name: str) -> PlayAnalysis:
    """Create tactical analysis similar to what our analyzer would produce."""
    
    if "trap" in play_name:
        # Trap play advantages
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("TRAP_BLOCK", +1, "Trap blocking scheme creates gap"),
                PlayMatchupFactor("TRAP_CONCEPT", +1, "Misdirection confuses defense"),
                PlayMatchupFactor("PULLING_GUARD", +1, "Guard pulls to create angle")
            ],
            disadvantages=[],
            net_impact=3,  # Capped at +3 by our tuning
            key_matchups=["LG vs DT", "RG vs DT"],
            scheme_analysis={"blocking_scheme": "trap", "concept": "misdirection"},
            confidence=0.85
        )
    elif "power" in play_name:
        # Power play advantages  
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("POWER_CONCEPT", +1, "Power concept creates leverage"),
                PlayMatchupFactor("DOUBLE_TEAM", +1, "Double team creates displacement"),
                PlayMatchupFactor("EXTRA_BLOCKER", +1, "Additional blocker at point of attack")
            ],
            disadvantages=[],
            net_impact=3,  # Capped at +3 by our tuning
            key_matchups=["RG+RT vs DT", "FB vs LB"],
            scheme_analysis={"blocking_scheme": "power", "concept": "gap_control"},
            confidence=0.80
        )
    else:
        # Basic play
        return PlayAnalysis(
            advantages=[],
            disadvantages=[],
            net_impact=0,
            key_matchups=[],
            scheme_analysis={"blocking_scheme": "base"},
            confidence=0.50
        )

def test_resolution_configs():
    """Test both realistic and arcade configurations."""
    
    trap_play, power_play, defense = create_test_plays()
    
    configs = [
        ("Realistic", create_realistic_config()),
        ("Arcade", create_arcade_config())
    ]
    
    test_plays = [
        ("Trap Right", trap_play),
        ("Power Right", power_play)
    ]
    
    situations = [
        {"down": 1, "distance": 10, "field_position": 25},
        {"down": 3, "distance": 2, "field_position": 45}
    ]
    
    print("🏈 Resolution Engine Tuning Test")
    print("=" * 60)
    
    for config_name, config in configs:
        print(f"\n🎮 {config_name} Configuration")
        print("-" * 40)
        
        engine = PlayResolutionEngine(config)
        
        for play_name, play in test_plays:
            for situation in situations:
                situation_desc = f"{situation['down']} & {situation['distance']}"
                print(f"\n📋 {play_name} - {situation_desc}")
                
                # Create tactical analysis
                analysis = create_test_analysis(play.name)
                
                results = []
                outcomes = []
                
                # Run 15 simulations
                for i in range(15):
                    try:
                        # Create tactical analysis for this play
                        analysis = create_test_analysis(play.name)
                        
                        # Simulate the analyzer being called in the engine
                        # We'll inject our analysis via monkey patching for this test
                        original_analyze = engine.play_analyzer.analyze_play_matchup
                        engine.play_analyzer.analyze_play_matchup = lambda offensive_play, defensive_play: analysis
                        
                        result = engine.resolve_play(
                            offensive_play=play,
                            defensive_play=defense,
                            situation=situation
                        )
                        
                        # Restore original method
                        engine.play_analyzer.analyze_play_matchup = original_analyze
                        
                        results.append(result.yards_gained)
                        outcomes.append(result.outcome.name)
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                        continue
                
                if results:
                    avg_yards = statistics.mean(results)
                    max_yards = max(results)
                    min_yards = min(results)
                    
                    print(f"   📊 Avg: {avg_yards:.1f} yds | Range: {min_yards} to {max_yards} yds")
                    
                    # Count explosive plays (>15 yards)
                    explosive_count = sum(1 for y in results if y > 15)
                    explosive_pct = (explosive_count / len(results)) * 100
                    
                    print(f"   💥 Explosive plays (>15 yds): {explosive_count}/{len(results)} ({explosive_pct:.0f}%)")
                    
                    # Realism assessment
                    if config_name == "Realistic":
                        if avg_yards > 8:
                            print(f"   ⚠️  Still too high for realistic football")
                        elif avg_yards > 5:
                            print(f"   ✅ Good realistic average")
                        else:
                            print(f"   ✅ Conservative realistic average")
                            
                        if max_yards > 25:
                            print(f"   ⚠️  Max still too explosive")
                        else:
                            print(f"   ✅ Reasonable max yards")

if __name__ == '__main__':
    test_resolution_configs()
