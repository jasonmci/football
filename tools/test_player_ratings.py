#!/usr/bin/env python3
"""
Enhanced Resolution Testing - Player Ratings Impact
Shows how player ratings affect completions, YAC, missed tackles, etc.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from football2.football.enhanced_resolution import (
    EnhancedResolutionEngine, PlayerProfile, SkillCategory, PlayExecutionResult
)
from types import SimpleNamespace
import statistics

def create_player_archetypes():
    """Create different player archetypes for testing."""
    
    players = {}
    
    # Elite players
    players["elite_qb"] = PlayerProfile(
        name="Aaron Rodgers",
        position="QB",
        overall_rating=95,
        skills={
            SkillCategory.AWARENESS: 99,
            SkillCategory.HANDS: 90
        }
    )
    
    players["elite_wr"] = PlayerProfile(
        name="DeAndre Hopkins", 
        position="WR",
        overall_rating=94,
        skills={
            SkillCategory.HANDS: 96,
            SkillCategory.ROUTE_RUNNING: 95,
            SkillCategory.SPEED: 88,
            SkillCategory.AGILITY: 92
        }
    )
    
    players["speed_wr"] = PlayerProfile(
        name="Tyreek Hill",
        position="WR", 
        overall_rating=91,
        skills={
            SkillCategory.HANDS: 85,
            SkillCategory.ROUTE_RUNNING: 88,
            SkillCategory.SPEED: 99,
            SkillCategory.AGILITY: 94
        }
    )
    
    # Average players
    players["avg_qb"] = PlayerProfile(
        name="Average QB",
        position="QB",
        overall_rating=75,
        skills={
            SkillCategory.AWARENESS: 75,
            SkillCategory.HANDS: 75
        }
    )
    
    players["avg_wr"] = PlayerProfile(
        name="Average WR",
        position="WR",
        overall_rating=72,
        skills={
            SkillCategory.HANDS: 72,
            SkillCategory.ROUTE_RUNNING: 70,
            SkillCategory.SPEED: 75,
            SkillCategory.AGILITY: 73
        }
    )
    
    # Defensive players
    players["elite_cb"] = PlayerProfile(
        name="Jalen Ramsey",
        position="CB",
        overall_rating=93,
        skills={
            SkillCategory.COVERAGE: 95,
            SkillCategory.TACKLE: 88
        }
    )
    
    players["avg_cb"] = PlayerProfile(
        name="Average CB",
        position="CB", 
        overall_rating=75,
        skills={
            SkillCategory.COVERAGE: 75,
            SkillCategory.TACKLE: 73
        }
    )
    
    players["poor_cb"] = PlayerProfile(
        name="Weak CB",
        position="CB",
        overall_rating=65,
        skills={
            SkillCategory.COVERAGE: 62,
            SkillCategory.TACKLE: 68
        }
    )
    
    # Running backs
    players["power_rb"] = PlayerProfile(
        name="Derrick Henry",
        position="RB",
        overall_rating=92,
        skills={
            SkillCategory.STRENGTH: 96,
            SkillCategory.AGILITY: 78,
            SkillCategory.SPEED: 88
        },
        traits=["secure_hands"]
    )
    
    players["speed_rb"] = PlayerProfile(
        name="Chris Johnson",
        position="RB", 
        overall_rating=88,
        skills={
            SkillCategory.STRENGTH: 72,
            SkillCategory.AGILITY: 94,
            SkillCategory.SPEED: 99
        }
    )
    
    players["avg_rb"] = PlayerProfile(
        name="Average RB",
        position="RB",
        overall_rating=74,
        skills={
            SkillCategory.STRENGTH: 75,
            SkillCategory.AGILITY: 73,
            SkillCategory.SPEED: 76
        }
    )
    
    # Linebackers/Safeties
    players["elite_lb"] = PlayerProfile(
        name="Elite LB",
        position="LB",
        overall_rating=90,
        skills={
            SkillCategory.TACKLE: 93,
            SkillCategory.COVERAGE: 85
        }
    )
    
    players["avg_lb"] = PlayerProfile(
        name="Average LB", 
        position="LB",
        overall_rating=75,
        skills={
            SkillCategory.TACKLE: 76,
            SkillCategory.COVERAGE: 70
        }
    )
    
    return players

def create_test_scenarios():
    """Create different play scenarios."""
    return [
        {
            "name": "Quick Slant (5 yards)",
            "base_result": SimpleNamespace(
                outcome=SimpleNamespace(name="SUCCESS"),
                yards_gained=5,
                dice_roll=10,
                total_modifier=2,
                final_total=12
            ),
            "situation": {"pass_rush_pressure": False}
        },
        {
            "name": "Deep Post (18 yards)",
            "base_result": SimpleNamespace(
                outcome=SimpleNamespace(name="BIG_SUCCESS"),
                yards_gained=18,
                dice_roll=14,
                total_modifier=3,
                final_total=17
            ),
            "situation": {"pass_rush_pressure": False}
        },
        {
            "name": "Under Pressure (8 yards)",
            "base_result": SimpleNamespace(
                outcome=SimpleNamespace(name="SUCCESS"),
                yards_gained=8,
                dice_roll=11,
                total_modifier=1,
                final_total=12
            ),
            "situation": {"pass_rush_pressure": True}
        },
        {
            "name": "Power Run (4 yards)",
            "base_result": SimpleNamespace(
                outcome=SimpleNamespace(name="SUCCESS"),
                yards_gained=4,
                dice_roll=9,
                total_modifier=2,
                final_total=11
            ),
            "situation": {}
        },
        {
            "name": "Outside Run (7 yards)",
            "base_result": SimpleNamespace(
                outcome=SimpleNamespace(name="SUCCESS"),
                yards_gained=7,
                dice_roll=12,
                total_modifier=1,
                final_total=13
            ),
            "situation": {}
        }
    ]

def test_player_impact():
    """Test how different player ratings impact results."""
    
    engine = EnhancedResolutionEngine(seed=42)  # Fixed seed for consistency
    players = create_player_archetypes()
    scenarios = create_test_scenarios()
    
    print("🏈 PLAYER RATINGS IMPACT ANALYSIS")
    print("=" * 70)
    
    # Test pass play combinations
    pass_combos = [
        ("elite_qb", "elite_wr", "avg_cb", "🌟 Elite QB + Elite WR vs Average CB"),
        ("elite_qb", "speed_wr", "elite_cb", "⚡ Elite QB + Speed WR vs Elite CB"),
        ("avg_qb", "avg_wr", "avg_cb", "⚖️  Average vs Average"),
        ("avg_qb", "avg_wr", "elite_cb", "😤 Average vs Elite CB"),
        ("elite_qb", "avg_wr", "poor_cb", "🎯 Elite QB vs Weak CB"),
    ]
    
    for scenario in scenarios[:3]:  # Pass scenarios
        print(f"\n🎯 **{scenario['name']}**")
        print("-" * 50)
        
        for qb_key, wr_key, cb_key, description in pass_combos:
            qb = players[qb_key]
            wr = players[wr_key]  
            cb = players[cb_key]
            
            # Run multiple simulations
            completions = 0
            total_yards = 0
            total_yac = 0
            total_missed_tackles = 0
            trials = 20
            
            for _ in range(trials):
                result = engine.resolve_pass_play(
                    qb, wr, cb, scenario["base_result"], scenario["situation"]
                )
                
                if result.completed:
                    completions += 1
                    total_yards += result.yards_gained
                    total_yac += result.yards_after_contact
                    total_missed_tackles += result.missed_tackles
            
            completion_rate = (completions / trials) * 100
            avg_yards = total_yards / max(1, completions)
            avg_yac = total_yac / max(1, completions)
            avg_missed = total_missed_tackles / max(1, completions)
            
            print(f"   {description}")
            print(f"      📊 Completion: {completion_rate:.0f}% | Avg: {avg_yards:.1f} yds | YAC: {avg_yac:.1f} | Missed tackles: {avg_missed:.1f}")
    
    # Test run play combinations
    print(f"\n\n🏃 **RUN PLAY ANALYSIS**")
    print("=" * 50)
    
    run_combos = [
        ("power_rb", ["elite_lb"], "💪 Power RB vs Elite LB"),
        ("speed_rb", ["avg_lb"], "⚡ Speed RB vs Average LB"), 
        ("avg_rb", ["elite_lb"], "😤 Average RB vs Elite LB"),
        ("power_rb", ["avg_lb"], "🎯 Power RB vs Average LB"),
        ("speed_rb", ["elite_lb"], "🏃 Speed RB vs Elite LB"),
    ]
    
    for scenario in scenarios[3:]:  # Run scenarios
        print(f"\n🏃 **{scenario['name']}**")
        print("-" * 40)
        
        for rb_key, def_keys, description in run_combos:
            rb = players[rb_key]
            defenders = [players[key] for key in def_keys]
            
            # Run simulations
            total_yards = 0
            total_yac = 0
            total_missed_tackles = 0
            fumbles = 0
            trials = 20
            
            for _ in range(trials):
                result = engine.resolve_run_play(
                    rb, [], defenders, scenario["base_result"], scenario["situation"]
                )
                
                if result.outcome == "FUMBLE":
                    fumbles += 1
                else:
                    total_yards += result.yards_gained
                    total_yac += result.yards_after_contact
                    total_missed_tackles += result.missed_tackles
            
            successful_runs = trials - fumbles
            avg_yards = total_yards / max(1, successful_runs)
            avg_yac = total_yac / max(1, successful_runs) 
            avg_missed = total_missed_tackles / max(1, successful_runs)
            fumble_rate = (fumbles / trials) * 100
            
            print(f"   {description}")
            print(f"      📊 Avg: {avg_yards:.1f} yds | YAC: {avg_yac:.1f} | Missed tackles: {avg_missed:.1f} | Fumbles: {fumble_rate:.0f}%")

def test_situational_impact():
    """Test how situations affect outcomes."""
    
    engine = EnhancedResolutionEngine(seed=123)
    players = create_player_archetypes()
    
    print(f"\n\n🎬 **SITUATIONAL IMPACT ANALYSIS**")  
    print("=" * 50)
    
    # Test pressure vs no pressure
    qb = players["avg_qb"]
    wr = players["avg_wr"] 
    cb = players["avg_cb"]
    
    base_result = SimpleNamespace(
        outcome=SimpleNamespace(name="SUCCESS"),
        yards_gained=10,
        dice_roll=11,
        total_modifier=2,
        final_total=13
    )
    
    situations = [
        ({"pass_rush_pressure": False}, "🛡️  Clean Pocket"),
        ({"pass_rush_pressure": True}, "🔥 Under Pressure")
    ]
    
    print("\n📡 **Pass Play Under Different Pressure**")
    
    for situation, desc in situations:
        completions = 0
        total_yards = 0
        trials = 25
        
        for _ in range(trials):
            result = engine.resolve_pass_play(qb, wr, cb, base_result, situation)
            if result.completed:
                completions += 1
                total_yards += result.yards_gained
        
        completion_rate = (completions / trials) * 100
        avg_yards = total_yards / max(1, completions)
        
        print(f"   {desc}: {completion_rate:.0f}% completion | {avg_yards:.1f} avg yards")

if __name__ == "__main__":
    test_player_impact()
    test_situational_impact()
