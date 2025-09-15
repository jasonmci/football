"""
Comprehensive Season Rating System Demo
Shows how player ratings evolve throughout a season based on performance.
"""

import random
from typing import Dict, List
import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent.parent / "src" / "football2" / "football"
sys.path.insert(0, str(src_path))

from season_ratings import (
    SeasonRatingEngine, PlayerGameStats, StatCategory, 
    create_sample_season_data
)
from roster_management import RosterManager, create_sample_roster_data
from enhanced_resolution import PlayerProfile, SkillCategory


def simulate_quarterback_season(engine: SeasonRatingEngine, player_id: str, weeks: int = 17):
    """Simulate a quarterback's season with varying performance."""
    print(f"\n🏈 Simulating {weeks}-week season for {player_id}")
    print("=" * 60)
    
    # Get initial ratings
    player = engine.players[player_id]
    initial_overall = player.player_profile.overall_rating
    print(f"Starting Overall Rating: {initial_overall}")
    
    # Simulate each week
    for week in range(1, weeks + 1):
        # Generate realistic QB stats with some variance
        base_attempts = 32 + random.randint(-8, 8)
        completion_rate = 0.65 + random.gauss(0, 0.08)  # Normal distribution around 65%
        completion_rate = max(0.45, min(0.85, completion_rate))  # Clamp to realistic range
        
        completions = int(base_attempts * completion_rate)
        yards = completions * (7.5 + random.gauss(0, 1.5))  # YAC variance
        touchdowns = max(0, int(completions * 0.08 + random.gauss(0, 0.5)))
        interceptions = max(0, int(base_attempts * 0.025 + random.gauss(0, 0.4)))
        
        # Create game stats
        game_stats = PlayerGameStats(
            game_id=f"Week_{week}",
            week=week,
            opponent=f"OPP{week}",
            stats={
                StatCategory.PASS_ATTEMPTS: base_attempts,
                StatCategory.PASS_COMPLETIONS: completions,
                StatCategory.PASS_YARDS: yards,
                StatCategory.PASS_TDS: touchdowns,
                StatCategory.INTERCEPTIONS: interceptions,
                StatCategory.SACKS_TAKEN: random.randint(1, 4)
            },
            grade=60 + (completion_rate - 0.55) * 100  # Grade based on performance
        )
        
        # Record the game
        engine.record_game_stats(player_id, game_stats)
        
        # Show key weeks
        if week % 4 == 0 or week == weeks:
            player = engine.players[player_id]
            current_overall = engine._calculate_overall_change(player) + initial_overall
            print(f"Week {week:2d}: {completions:2d}/{base_attempts:2d} ({completion_rate:.1%}), "
                  f"{yards:3.0f} yds, {touchdowns} TD, {interceptions} INT "
                  f"| Overall: {current_overall:2d} ({current_overall-initial_overall:+d})")
    
    return engine.get_player_rating_summary(player_id)


def simulate_running_back_season(engine: SeasonRatingEngine, player_id: str, weeks: int = 17):
    """Simulate a running back's season."""
    print(f"\n🏃 Simulating {weeks}-week season for {player_id}")
    print("=" * 60)
    
    player = engine.players[player_id]
    initial_overall = player.player_profile.overall_rating
    print(f"Starting Overall Rating: {initial_overall}")
    
    for week in range(1, weeks + 1):
        # RB stats with variance
        attempts = 18 + random.randint(-6, 8)
        yards_per_carry = 4.2 + random.gauss(0, 0.8)
        yards_per_carry = max(2.0, min(7.0, yards_per_carry))
        
        yards = attempts * yards_per_carry
        touchdowns = max(0, int(attempts * 0.08 + random.gauss(0, 0.3)))
        fumbles = 1 if random.random() < 0.1 else 0  # 10% chance per game
        broken_tackles = max(0, int(attempts * 0.15 + random.gauss(0, 1)))
        
        game_stats = PlayerGameStats(
            game_id=f"Week_{week}",
            week=week,
            opponent=f"OPP{week}",
            stats={
                StatCategory.RUSH_ATTEMPTS: attempts,
                StatCategory.RUSH_YARDS: yards,
                StatCategory.RUSH_TDS: touchdowns,
                StatCategory.FUMBLES: fumbles,
                StatCategory.BROKEN_TACKLES: broken_tackles,
                StatCategory.YARDS_AFTER_CONTACT: yards * 0.6  # 60% of yards after contact
            },
            grade=50 + (yards_per_carry - 3.5) * 15  # Grade based on YPC
        )
        
        engine.record_game_stats(player_id, game_stats)
        
        if week % 4 == 0 or week == weeks:
            player = engine.players[player_id]
            current_overall = engine._calculate_overall_change(player) + initial_overall
            print(f"Week {week:2d}: {attempts:2d} att, {yards:3.0f} yds ({yards_per_carry:.1f} YPC), "
                  f"{touchdowns} TD, {broken_tackles} BT "
                  f"| Overall: {current_overall:2d} ({current_overall-initial_overall:+d})")
    
    return engine.get_player_rating_summary(player_id)


def simulate_receiver_season(engine: SeasonRatingEngine, player_id: str, weeks: int = 17):
    """Simulate a wide receiver's season."""
    print(f"\n🙌 Simulating {weeks}-week season for {player_id}")
    print("=" * 60)
    
    player = engine.players[player_id]
    initial_overall = player.player_profile.overall_rating
    print(f"Starting Overall Rating: {initial_overall}")
    
    for week in range(1, weeks + 1):
        # WR stats
        targets = 8 + random.randint(-3, 5)
        catch_rate = 0.68 + random.gauss(0, 0.1)
        catch_rate = max(0.4, min(0.9, catch_rate))
        
        receptions = int(targets * catch_rate)
        yards_per_catch = 12 + random.gauss(0, 3)
        yards = receptions * yards_per_catch
        touchdowns = max(0, int(receptions * 0.12 + random.gauss(0, 0.3)))
        drops = max(0, targets - receptions - random.randint(0, 2))
        
        game_stats = PlayerGameStats(
            game_id=f"Week_{week}",
            week=week,
            opponent=f"OPP{week}",
            stats={
                StatCategory.TARGETS: targets,
                StatCategory.RECEPTIONS: receptions,
                StatCategory.RECEIVING_YARDS: yards,
                StatCategory.RECEIVING_TDS: touchdowns,
                StatCategory.DROPS: drops,
                StatCategory.YARDS_AFTER_CATCH: yards * 0.4  # 40% YAC
            },
            grade=55 + (catch_rate - 0.6) * 50  # Grade based on catch rate
        )
        
        engine.record_game_stats(player_id, game_stats)
        
        if week % 4 == 0 or week == weeks:
            player = engine.players[player_id]
            current_overall = engine._calculate_overall_change(player) + initial_overall
            print(f"Week {week:2d}: {receptions:2d}/{targets:2d} ({catch_rate:.1%}), "
                  f"{yards:3.0f} yds, {touchdowns} TD, {drops} drops "
                  f"| Overall: {current_overall:2d} ({current_overall-initial_overall:+d})")
    
    return engine.get_player_rating_summary(player_id)


def display_season_summary(engine: SeasonRatingEngine):
    """Display comprehensive season summary."""
    print("\n" + "=" * 80)
    print("🏆 SEASON SUMMARY")
    print("=" * 80)
    
    # League leaders in key stats
    print("\n📊 League Leaders:")
    
    passing_leaders = engine.get_league_leaders(StatCategory.PASS_YARDS, min_games=12)
    if passing_leaders:
        print("\n🎯 Passing Yards:")
        for i, (name, yards) in enumerate(passing_leaders[:5], 1):
            print(f"  {i}. {name}: {yards:,.0f} yards")
    
    rushing_leaders = engine.get_league_leaders(StatCategory.RUSH_YARDS, min_games=12)
    if rushing_leaders:
        print("\n🏃 Rushing Yards:")
        for i, (name, yards) in enumerate(rushing_leaders[:5], 1):
            print(f"  {i}. {name}: {yards:,.0f} yards")
    
    receiving_leaders = engine.get_league_leaders(StatCategory.RECEIVING_YARDS, min_games=12)
    if receiving_leaders:
        print("\n🙌 Receiving Yards:")
        for i, (name, yards) in enumerate(receiving_leaders[:5], 1):
            print(f"  {i}. {name}: {yards:,.0f} yards")
    
    # Rating changes
    print("\n📈 Biggest Rating Changes:")
    rating_changes = []
    
    for player_id, player in engine.players.items():
        if len(player.games) >= 12:  # Minimum games played
            original = player.player_profile.overall_rating
            current = engine._calculate_overall_change(player) + original
            change = current - original
            rating_changes.append((player.player_profile.name, original, current, change))
    
    # Sort by biggest changes
    rating_changes.sort(key=lambda x: abs(x[3]), reverse=True)
    
    print("\n⬆️ Biggest Improvements:")
    improvements = [p for p in rating_changes if p[3] > 0][:5]
    for name, original, current, change in improvements:
        print(f"  {name}: {original} → {current} ({change:+d})")
    
    print("\n⬇️ Biggest Declines:")
    declines = [p for p in rating_changes if p[3] < 0][:5]
    for name, original, current, change in declines:
        print(f"  {name}: {original} → {current} ({change:+d})")


def demo_roster_integration(engine: SeasonRatingEngine):
    """Demonstrate integration with roster management."""
    print("\n" + "=" * 80)
    print("🏟️ ROSTER INTEGRATION DEMO")
    print("=" * 80)
    
    # Create roster manager and get analysis
    roster_manager = create_sample_roster_data()
    
    # Analyze KC roster with updated ratings
    kc_analysis = roster_manager.get_roster_analysis("KC", engine)
    
    print(f"\n📊 {kc_analysis['team']} Analysis:")
    print(f"Roster Size: {kc_analysis['roster_size']}/53")
    
    salary_info = kc_analysis['salary_cap']
    print(f"Salary Cap: ${salary_info['used']:,} / ${salary_info['total_cap']:,} "
          f"({salary_info['percentage_used']:.1f}%)")
    print(f"Available: ${salary_info['available']:,}")
    
    print("\n🌟 Top Players:")
    for i, player in enumerate(kc_analysis['top_players'], 1):
        print(f"  {i}. {player['name']}: {player['current_rating']} "
              f"(was {player['overall_rating']})")


def create_enhanced_sample_data():
    """Create more comprehensive sample data for testing."""
    engine = create_sample_season_data()
    
    # Add more realistic NFL players
    additional_players = [
        PlayerProfile(
            name="Josh Allen",
            position="QB",
            overall_rating=89,
            skills={
                SkillCategory.AWARENESS: 85,
                SkillCategory.HANDS: 88,
                SkillCategory.SPEED: 82,
                SkillCategory.AGILITY: 79,
                SkillCategory.STRENGTH: 92
            }
        ),
        PlayerProfile(
            name="Aaron Donald",
            position="DT",
            overall_rating=95,
            skills={
                SkillCategory.STRENGTH: 96,
                SkillCategory.AGILITY: 88,
                SkillCategory.TACKLE: 94,
                SkillCategory.RUN_DEFENSE: 92,
                SkillCategory.AWARENESS: 89
            }
        ),
        PlayerProfile(
            name="Cooper Kupp",
            position="WR",
            overall_rating=87,
            skills={
                SkillCategory.HANDS: 92,
                SkillCategory.ROUTE_RUNNING: 95,
                SkillCategory.SPEED: 78,
                SkillCategory.AGILITY: 85,
                SkillCategory.AWARENESS: 88
            }
        )
    ]
    
    # Add players to teams
    engine.add_player(additional_players[0], "BUF")  # Josh Allen
    engine.add_player(additional_players[1], "LAR")  # Aaron Donald
    engine.add_player(additional_players[2], "LAR")  # Cooper Kupp
    
    return engine


if __name__ == "__main__":
    print("🏈 COMPREHENSIVE SEASON RATING SYSTEM DEMO")
    print("=" * 80)
    print("Simulating a full NFL season with dynamic player ratings...")
    
    # Create enhanced sample data
    engine = create_enhanced_sample_data()
    
    # Simulate seasons for different position players
    qb_summary = simulate_quarterback_season(engine, "Patrick_Mahomes_KC", 17)
    rb_summary = simulate_running_back_season(engine, "Derrick_Henry_TEN", 17)
    wr_summary = simulate_receiver_season(engine, "Tyreek_Hill_MIA", 17)
    
    # Also simulate the additional players (shortened seasons for demo)
    simulate_quarterback_season(engine, "Josh_Allen_BUF", 12)
    simulate_receiver_season(engine, "Cooper_Kupp_LAR", 12)
    
    # Display comprehensive season summary
    display_season_summary(engine)
    
    # Show detailed player summaries
    print("\n" + "=" * 80)
    print("🔍 DETAILED PLAYER ANALYSIS")
    print("=" * 80)
    
    for player_name, summary in [
        ("Patrick Mahomes", qb_summary),
        ("Derrick Henry", rb_summary), 
        ("Tyreek Hill", wr_summary)
    ]:
        print(f"\n📊 {player_name} Season Analysis:")
        print(f"Games Played: {summary['games_played']}")
        print(f"Overall Rating Change: {summary['overall_rating_change']:+d}")
        print(f"Season Grade: {summary['season_grade']:.1f}")
        print(f"Recent Form: {summary['recent_form']:.1f}")
        print(f"Confidence: {summary['confidence']:.1f}%")
        
        print("Key Skill Changes:")
        for skill, data in summary['rating_changes'].items():
            if abs(data['change']) >= 2:  # Only show significant changes
                print(f"  {skill}: {data['original']} → {data['current']} "
                      f"({data['change']:+d}) [Peak: {data['peak']}]")
    
    # Demonstrate roster integration
    demo_roster_integration(engine)
    
    # Export season data
    export_path = "/tmp/season_2024_demo.json"
    engine.export_season_data(export_path)
    print(f"\n💾 Season data exported to: {export_path}")
    
    print("\n🎉 Demo completed! The season rating system successfully:")
    print("  ✅ Tracked player performance across 17 weeks")
    print("  ✅ Dynamically adjusted ratings based on stats")
    print("  ✅ Calculated league leaders and trends")
    print("  ✅ Integrated with roster management")
    print("  ✅ Exported comprehensive season data")
