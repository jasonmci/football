#!/usr/bin/env python3
"""
Test script for intelligent play calling system.

Demonstrates how the AI coach makes strategic decisions based on
game situation, field position, and opponent formations.
"""

import sys
sys.path.append('src')

from football2.football.play_caller import (
    IntelligentPlayCaller, GameContext, GameSituation, 
    FieldPosition, determine_game_situation
)


def test_game_scenarios():
    """Test the play caller in various realistic game scenarios."""
    play_caller = IntelligentPlayCaller()
    
    print("🧠 INTELLIGENT PLAY CALLING SYSTEM")
    print("=" * 50)
    print("AI Coach recommendations for strategic situations")
    print()
    
    # Scenario 1: Opening drive
    print("📖 SCENARIO 1: Opening Drive")
    print("-" * 30)
    context = GameContext(
        down=1,
        yards_to_go=10,
        field_position=FieldPosition.OWN_TERRITORY,
        time_remaining=3600,  # Full game
        score_differential=0,
        situation=GameSituation.FIRST_DOWN
    )
    
    recommendation = play_caller.get_full_recommendation(context, "base43")
    print(f"Situation: 1st & 10 at own 25, vs Base 4-3")
    print(f"Top Formation: {recommendation['top_recommendation']['formation']}")
    print(f"Play Call: {recommendation['top_recommendation']['play_type']}")
    print(f"Confidence: {recommendation['top_recommendation']['confidence']:.1%}")
    print(f"Risk Level: {recommendation['top_recommendation']['risk_level']}")
    print("Reasoning:")
    for reason in recommendation['top_recommendation']['reasoning']:
        print(f"  • {reason}")
    
    # Scenario 2: Third and long
    print("\n\n⚡ SCENARIO 2: Third and Long")
    print("-" * 35)
    context = GameContext(
        down=3,
        yards_to_go=12,
        field_position=FieldPosition.MIDFIELD,
        time_remaining=1800,
        score_differential=0,
        situation=GameSituation.LONG_YARDAGE
    )
    
    recommendation = play_caller.get_full_recommendation(context, "nickel")
    print(f"Situation: 3rd & 12 at midfield, vs Nickel")
    print(f"Top Formation: {recommendation['top_recommendation']['formation']}")
    print(f"Play Call: {recommendation['top_recommendation']['play_type']}")
    print(f"Confidence: {recommendation['top_recommendation']['confidence']:.1%}")
    print(f"Risk Level: {recommendation['top_recommendation']['risk_level']}")
    print("Reasoning:")
    for reason in recommendation['top_recommendation']['reasoning']:
        print(f"  • {reason}")
    
    # Scenario 3: Goal line
    print("\n\n🥅 SCENARIO 3: Goal Line Stand")
    print("-" * 35)
    context = GameContext(
        down=2,
        yards_to_go=2,
        field_position=FieldPosition.GOAL_LINE,
        time_remaining=600,
        score_differential=-3,  # Trailing by 3
        situation=GameSituation.GOAL_LINE
    )
    
    recommendation = play_caller.get_full_recommendation(context, "goalline_defense")
    print(f"Situation: 2nd & Goal at 2-yard line, vs Goal Line Defense")
    print(f"Top Formation: {recommendation['top_recommendation']['formation']}")
    print(f"Play Call: {recommendation['top_recommendation']['play_type']}")
    print(f"Confidence: {recommendation['top_recommendation']['confidence']:.1%}")
    print(f"Risk Level: {recommendation['top_recommendation']['risk_level']}")
    print("Reasoning:")
    for reason in recommendation['top_recommendation']['reasoning']:
        print(f"  • {reason}")
    
    # Scenario 4: Two-minute drill
    print("\n\n⏰ SCENARIO 4: Two-Minute Drill")
    print("-" * 35)
    context = GameContext(
        down=1,
        yards_to_go=10,
        field_position=FieldPosition.OPPONENT_TERRITORY,
        time_remaining=90,  # 1:30 left
        score_differential=-7,  # Trailing by 7
        situation=GameSituation.TWO_MINUTE_DRILL
    )
    
    recommendation = play_caller.get_full_recommendation(context, "prevent_defense")
    print(f"Situation: 1st & 10 at opp 35, 1:30 left, down 7, vs Prevent")
    print(f"Top Formation: {recommendation['top_recommendation']['formation']}")
    print(f"Play Call: {recommendation['top_recommendation']['play_type']}")
    print(f"Confidence: {recommendation['top_recommendation']['confidence']:.1%}")
    print(f"Risk Level: {recommendation['top_recommendation']['risk_level']}")
    print("Reasoning:")
    for reason in recommendation['top_recommendation']['reasoning']:
        print(f"  • {reason}")


def show_all_formation_options():
    """Show formation recommendations for different scenarios."""
    play_caller = IntelligentPlayCaller()
    
    print("\n\n📊 FORMATION PREFERENCES BY SITUATION")
    print("=" * 50)
    
    scenarios = [
        ("1st Down", GameSituation.FIRST_DOWN),
        ("Short Yardage", GameSituation.SHORT_YARDAGE),
        ("Medium Yardage", GameSituation.MEDIUM_YARDAGE),
        ("Long Yardage", GameSituation.LONG_YARDAGE),
        ("Goal Line", GameSituation.GOAL_LINE),
        ("Red Zone", GameSituation.RED_ZONE),
        ("Two-Minute", GameSituation.TWO_MINUTE_DRILL)
    ]
    
    for name, situation in scenarios:
        context = GameContext(
            down=1,
            yards_to_go=10,
            field_position=FieldPosition.MIDFIELD,
            time_remaining=1800,
            score_differential=0,
            situation=situation
        )
        
        formations = play_caller.suggest_formation(context)
        print(f"{name:15} → {', '.join(formations)}")


def test_matchup_awareness():
    """Test how the play caller adapts to different defensive formations."""
    play_caller = IntelligentPlayCaller()
    
    print("\n\n🎯 MATCHUP-AWARE PLAY CALLING")
    print("=" * 40)
    print("How recommendations change vs different defenses")
    print()
    
    # Standard 3rd and medium scenario
    context = GameContext(
        down=3,
        yards_to_go=6,
        field_position=FieldPosition.MIDFIELD,
        time_remaining=1800,
        score_differential=0,
        situation=GameSituation.MEDIUM_YARDAGE
    )
    
    defenses = ["base43", "nickel", "dime", "bear46"]
    
    for defense in defenses:
        recommendation = play_caller.get_full_recommendation(context, defense)
        top_rec = recommendation['top_recommendation']
        
        print(f"vs {defense.upper().replace('_', ' ')}:")
        print(f"  Formation: {top_rec['formation']}")
        print(f"  Play: {top_rec['play_type']}")
        print(f"  Confidence: {top_rec['confidence']:.1%}")
        print()


if __name__ == "__main__":
    print("🎮 FOOTBALL AI COACH")
    print("Strategic play calling for board game football!")
    print()
    
    test_game_scenarios()
    show_all_formation_options()
    test_matchup_awareness()
    
    print("\n🏆 AI COACH INSIGHTS:")
    print("• Adapts formation choice based on down & distance")
    print("• Considers opponent defensive alignment")
    print("• Balances risk/reward based on game situation")
    print("• Provides confidence levels for decision support")
    print("• Perfect for strategic board game mechanics!")
