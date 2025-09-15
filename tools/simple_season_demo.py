"""
Simple Season Rating Demo
Shows core functionality of the season-based player rating system.
"""

import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent.parent / "src" / "football2" / "football"
sys.path.insert(0, str(src_path))

from season_ratings import SeasonRatingEngine, PlayerGameStats, StatCategory
from enhanced_resolution import PlayerProfile, SkillCategory


def create_test_players():
    """Create some test players for the demo."""
    
    # Elite QB
    mahomes = PlayerProfile(
        name="Patrick Mahomes",
        position="QB",
        overall_rating=96,
        skills={
            SkillCategory.AWARENESS: 97,
            SkillCategory.HANDS: 92,
            SkillCategory.SPEED: 76,
            SkillCategory.AGILITY: 83
        }
    )
    
    # Elite WR
    jefferson = PlayerProfile(
        name="Justin Jefferson",
        position="WR",
        overall_rating=94,
        skills={
            SkillCategory.HANDS: 94,
            SkillCategory.ROUTE_RUNNING: 96,
            SkillCategory.SPEED: 90,
            SkillCategory.AGILITY: 92
        }
    )
    
    return [mahomes, jefferson]


def simulate_game_performance(engine, player_id, position, week):
    """Simulate one game's performance for a player."""
    
    if position == "QB":
        # Good QB performance
        game_stats = PlayerGameStats(
            game_id=f"Week_{week}",
            week=week,
            opponent=f"Team_{week}",
            stats={
                StatCategory.PASS_ATTEMPTS: 35,
                StatCategory.PASS_COMPLETIONS: 28,
                StatCategory.PASS_YARDS: 320,
                StatCategory.PASS_TDS: 3 if week % 3 == 0 else 2,
                StatCategory.INTERCEPTIONS: 1 if week % 5 == 0 else 0
            },
            grade=85.0 + (week % 10)  # Varying performance
        )
    
    elif position == "WR":
        # Good WR performance  
        game_stats = PlayerGameStats(
            game_id=f"Week_{week}",
            week=week,
            opponent=f"Team_{week}",
            stats={
                StatCategory.TARGETS: 10,
                StatCategory.RECEPTIONS: 8 if week % 3 != 0 else 6,  # Some variation
                StatCategory.RECEIVING_YARDS: 120 if week % 3 != 0 else 80,
                StatCategory.RECEIVING_TDS: 1 if week % 4 == 0 else 0,
                StatCategory.DROPS: 2 if week % 7 == 0 else 0  # Occasional drops
            },
            grade=80.0 + (week % 15)
        )
    
    engine.record_game_stats(player_id, game_stats)
    return game_stats


def main():
    print("🏈 Season-Based Player Rating System Demo")
    print("=" * 50)
    
    # Create season engine
    engine = SeasonRatingEngine(2024)
    
    # Add test players
    players = create_test_players()
    
    mahomes_id = engine.add_player(players[0], "KC").player_profile.name.replace(" ", "_") + "_KC"
    jefferson_id = engine.add_player(players[1], "MIN").player_profile.name.replace(" ", "_") + "_MIN"
    
    print(f"\n📊 Initial Ratings:")
    print(f"Patrick Mahomes (QB): {players[0].overall_rating}")
    print(f"Justin Jefferson (WR): {players[1].overall_rating}")
    
    # Simulate 8 weeks of games
    print(f"\n🏈 Simulating 8-week season...")
    
    for week in range(1, 9):
        # Simulate games
        mahomes_game = simulate_game_performance(engine, mahomes_id, "QB", week)
        jefferson_game = simulate_game_performance(engine, jefferson_id, "WR", week)
        
        if week % 2 == 0:  # Show every other week
            print(f"\nWeek {week} Results:")
            print(f"  Mahomes: {mahomes_game.stats[StatCategory.PASS_COMPLETIONS]:.0f}/"
                  f"{mahomes_game.stats[StatCategory.PASS_ATTEMPTS]:.0f}, "
                  f"{mahomes_game.stats[StatCategory.PASS_YARDS]:.0f} yds, "
                  f"{mahomes_game.stats[StatCategory.PASS_TDS]:.0f} TD")
            
            print(f"  Jefferson: {jefferson_game.stats[StatCategory.RECEPTIONS]:.0f}/"
                  f"{jefferson_game.stats[StatCategory.TARGETS]:.0f}, "
                  f"{jefferson_game.stats[StatCategory.RECEIVING_YARDS]:.0f} yds, "
                  f"{jefferson_game.stats[StatCategory.RECEIVING_TDS]:.0f} TD")
    
    # Show final results
    print(f"\n📈 Final Season Summary:")
    print("=" * 30)
    
    # Get player summaries
    mahomes_summary = engine.get_player_rating_summary(mahomes_id)
    jefferson_summary = engine.get_player_rating_summary(jefferson_id)
    
    print(f"\n🎯 Patrick Mahomes:")
    print(f"  Games: {mahomes_summary['games_played']}")
    print(f"  Overall Change: {mahomes_summary['overall_rating_change']:+d}")
    print(f"  Season Grade: {mahomes_summary['season_grade']:.1f}")
    print(f"  Key Skills:")
    for skill, data in mahomes_summary['rating_changes'].items():
        if abs(data['change']) >= 1:
            print(f"    {skill}: {data['original']} → {data['current']} ({data['change']:+d})")
    
    print(f"\n🙌 Justin Jefferson:")
    print(f"  Games: {jefferson_summary['games_played']}")
    print(f"  Overall Change: {jefferson_summary['overall_rating_change']:+d}")
    print(f"  Season Grade: {jefferson_summary['season_grade']:.1f}")
    print(f"  Key Skills:")
    for skill, data in jefferson_summary['rating_changes'].items():
        if abs(data['change']) >= 1:
            print(f"    {skill}: {data['original']} → {data['current']} ({data['change']:+d})")
    
    # Show league leaders
    print(f"\n🏆 League Leaders:")
    passing_leaders = engine.get_league_leaders(StatCategory.PASS_YARDS)
    receiving_leaders = engine.get_league_leaders(StatCategory.RECEIVING_YARDS)
    
    if passing_leaders:
        print(f"  Passing: {passing_leaders[0][0]} - {passing_leaders[0][1]:.0f} yards")
    if receiving_leaders:
        print(f"  Receiving: {receiving_leaders[0][0]} - {receiving_leaders[0][1]:.0f} yards")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"   - Player ratings adjusted based on performance")
    print(f"   - Season statistics tracked automatically") 
    print(f"   - League leaders calculated dynamically")


if __name__ == "__main__":
    main()
