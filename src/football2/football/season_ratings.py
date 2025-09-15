"""
Season-Based Player Rating System
Tracks player performance throughout a season and dynamically adjusts ratings.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import statistics
from datetime import datetime
from pathlib import Path

from enhanced_resolution import PlayerProfile, SkillCategory, PlayerRating


class StatCategory(Enum):
    """Statistical categories tracked for players."""
    # Passing stats
    PASS_ATTEMPTS = "pass_attempts"
    PASS_COMPLETIONS = "pass_completions"
    PASS_YARDS = "pass_yards"
    PASS_TDS = "pass_touchdowns"
    INTERCEPTIONS = "interceptions"
    SACKS_TAKEN = "sacks_taken"
    QBR = "quarterback_rating"
    
    # Rushing stats
    RUSH_ATTEMPTS = "rush_attempts"
    RUSH_YARDS = "rush_yards"
    RUSH_TDS = "rush_touchdowns"
    FUMBLES = "fumbles"
    BROKEN_TACKLES = "broken_tackles"
    YARDS_AFTER_CONTACT = "yards_after_contact"
    
    # Receiving stats
    TARGETS = "targets"
    RECEPTIONS = "receptions"
    RECEIVING_YARDS = "receiving_yards"
    RECEIVING_TDS = "receiving_touchdowns"
    DROPS = "drops"
    YARDS_AFTER_CATCH = "yards_after_catch"
    
    # Defensive stats
    TACKLES = "tackles"
    TACKLES_FOR_LOSS = "tackles_for_loss"
    SACKS = "sacks"
    PASS_BREAKUPS = "pass_breakups"
    INTERCEPTIONS_DEF = "interceptions_defense"
    FORCED_FUMBLES = "forced_fumbles"
    
    # Special categories
    CLUTCH_PLAYS = "clutch_plays"
    PENALTIES = "penalties"
    MISSED_TACKLES = "missed_tackles"
    

@dataclass
class PlayerGameStats:
    """Statistics for a single game."""
    game_id: str
    week: int
    opponent: str
    stats: Dict[StatCategory, float] = field(default_factory=dict)
    grade: float = 0.0  # 0-100 game grade
    key_plays: List[str] = field(default_factory=list)
    
    def get_stat(self, category: StatCategory) -> float:
        """Get a specific stat, defaulting to 0."""
        return self.stats.get(category, 0.0)


@dataclass 
class SeasonStats:
    """Aggregated season statistics."""
    season: int
    games_played: int = 0
    total_stats: Dict[StatCategory, float] = field(default_factory=dict)
    per_game_averages: Dict[StatCategory, float] = field(default_factory=dict)
    season_grade: float = 0.0
    
    def calculate_averages(self):
        """Calculate per-game averages."""
        if self.games_played > 0:
            for stat, total in self.total_stats.items():
                self.per_game_averages[stat] = total / self.games_played


@dataclass
class PlayerSeasonProfile:
    """Complete player profile for a season including performance tracking."""
    # Base profile
    player_profile: PlayerProfile
    season: int
    team: str
    
    # Performance tracking
    games: List[PlayerGameStats] = field(default_factory=list)
    season_stats: Optional[SeasonStats] = None
    
    # Dynamic ratings (change throughout season)
    current_ratings: Dict[SkillCategory, int] = field(default_factory=dict)
    peak_ratings: Dict[SkillCategory, int] = field(default_factory=dict)
    lowest_ratings: Dict[SkillCategory, int] = field(default_factory=dict)
    
    # Trending information
    recent_form: float = 0.0  # Last 4 games performance trend
    confidence: float = 50.0  # Player confidence level
    injury_risk: float = 0.0  # Injury probability
    
    # Contract/roster info
    salary: int = 0
    contract_years: int = 1
    rookie_year: bool = False
    
    def __post_init__(self):
        """Initialize current ratings from base profile."""
        if not self.current_ratings:
            self.current_ratings = self.player_profile.skills.copy()
            self.peak_ratings = self.current_ratings.copy()
            self.lowest_ratings = self.current_ratings.copy()


class SeasonRatingEngine:
    """Engine for managing player ratings throughout a season."""
    
    def __init__(self, season: int):
        self.season = season
        self.players: Dict[str, PlayerSeasonProfile] = {}
        self.week = 0
        
    def add_player(self, profile: PlayerProfile, team: str, **kwargs) -> PlayerSeasonProfile:
        """Add a player to the season rating system."""
        player_id = f"{profile.name}_{team}".replace(" ", "_")
        
        season_profile = PlayerSeasonProfile(
            player_profile=profile,
            season=self.season,
            team=team,
            **kwargs
        )
        
        self.players[player_id] = season_profile
        return season_profile
    
    def record_game_stats(self, player_id: str, game_stats: PlayerGameStats):
        """Record statistics for a player's game."""
        if player_id not in self.players:
            raise ValueError(f"Player {player_id} not found")
        
        player = self.players[player_id]
        player.games.append(game_stats)
        
        # Update season totals
        self._update_season_stats(player)
        
        # Adjust ratings based on performance
        self._adjust_ratings_from_performance(player, game_stats)
        
        # Update trends
        self._update_player_trends(player)
    
    def _update_season_stats(self, player: PlayerSeasonProfile):
        """Update aggregated season statistics."""
        if not player.season_stats:
            player.season_stats = SeasonStats(season=self.season)
        
        # Reset totals
        player.season_stats.total_stats.clear()
        player.season_stats.games_played = len(player.games)
        
        # Sum all game stats
        for game in player.games:
            for stat_type, value in game.stats.items():
                current = player.season_stats.total_stats.get(stat_type, 0.0)
                player.season_stats.total_stats[stat_type] = current + value
        
        # Calculate averages and season grade
        player.season_stats.calculate_averages()
        player.season_stats.season_grade = statistics.mean([g.grade for g in player.games]) if player.games else 0.0
    
    def _adjust_ratings_from_performance(self, player: PlayerSeasonProfile, game_stats: PlayerGameStats):
        """Adjust player ratings based on recent performance."""
        # Get position-specific performance indicators
        performance_factors = self._calculate_performance_factors(player, game_stats)
        
        # Adjust ratings based on performance
        for skill, factor in performance_factors.items():
            current_rating = player.current_ratings.get(skill, player.player_profile.get_skill(skill))
            
            # Calculate adjustment (max ±3 points per game)
            adjustment = max(-3, min(3, int(factor * 3)))
            
            # Apply adjustment with boundaries
            new_rating = max(30, min(99, current_rating + adjustment))
            player.current_ratings[skill] = new_rating
            
            # Track peaks and lows
            player.peak_ratings[skill] = max(player.peak_ratings.get(skill, new_rating), new_rating)
            player.lowest_ratings[skill] = min(player.lowest_ratings.get(skill, new_rating), new_rating)
    
    def _calculate_performance_factors(self, player: PlayerSeasonProfile, game_stats: PlayerGameStats) -> Dict[SkillCategory, float]:
        """Calculate performance factors for rating adjustments."""
        factors = {}
        position = player.player_profile.position
        
        # Quarterback performance factors
        if position == "QB":
            # Completion percentage affects hands/awareness
            attempts = game_stats.get_stat(StatCategory.PASS_ATTEMPTS)
            completions = game_stats.get_stat(StatCategory.PASS_COMPLETIONS)
            
            if attempts > 0:
                completion_pct = completions / attempts
                if completion_pct > 0.70:
                    factors[SkillCategory.HANDS] = 0.5
                    factors[SkillCategory.AWARENESS] = 0.3
                elif completion_pct < 0.50:
                    factors[SkillCategory.HANDS] = -0.4
                    factors[SkillCategory.AWARENESS] = -0.2
            
            # Interceptions hurt awareness
            interceptions = game_stats.get_stat(StatCategory.INTERCEPTIONS)
            if interceptions > 2:
                factors[SkillCategory.AWARENESS] = factors.get(SkillCategory.AWARENESS, 0) - 0.6
        
        # Running back performance factors
        elif position == "RB":
            attempts = game_stats.get_stat(StatCategory.RUSH_ATTEMPTS)
            yards = game_stats.get_stat(StatCategory.RUSH_YARDS)
            broken_tackles = game_stats.get_stat(StatCategory.BROKEN_TACKLES)
            
            if attempts > 0:
                ypc = yards / attempts
                if ypc > 5.0:
                    factors[SkillCategory.AGILITY] = 0.4
                    factors[SkillCategory.SPEED] = 0.3
                elif ypc < 3.0:
                    factors[SkillCategory.AGILITY] = -0.3
                    factors[SkillCategory.SPEED] = -0.2
            
            # Broken tackles affect strength/agility
            if broken_tackles > 3:
                factors[SkillCategory.STRENGTH] = 0.4
                factors[SkillCategory.AGILITY] = 0.3
        
        # Wide receiver performance factors
        elif position == "WR":
            targets = game_stats.get_stat(StatCategory.TARGETS)
            receptions = game_stats.get_stat(StatCategory.RECEPTIONS)
            drops = game_stats.get_stat(StatCategory.DROPS)
            
            if targets > 0:
                catch_rate = receptions / targets
                if catch_rate > 0.75:
                    factors[SkillCategory.HANDS] = 0.5
                    factors[SkillCategory.ROUTE_RUNNING] = 0.2
                elif catch_rate < 0.50:
                    factors[SkillCategory.HANDS] = -0.4
            
            if drops > 2:
                factors[SkillCategory.HANDS] = factors.get(SkillCategory.HANDS, 0) - 0.8
        
        # Defensive player factors
        elif position in ["CB", "S", "LB"]:
            tackles = game_stats.get_stat(StatCategory.TACKLES)
            missed_tackles = game_stats.get_stat(StatCategory.MISSED_TACKLES)
            
            if tackles > 8:
                factors[SkillCategory.TACKLE] = 0.4
            elif tackles < 3:
                factors[SkillCategory.TACKLE] = -0.2
            
            if missed_tackles > 3:
                factors[SkillCategory.TACKLE] = factors.get(SkillCategory.TACKLE, 0) - 0.6
        
        return factors
    
    def _update_player_trends(self, player: PlayerSeasonProfile):
        """Update player trending metrics."""
        if len(player.games) < 2:
            return
        
        # Calculate recent form (last 4 games)
        recent_games = player.games[-4:]
        recent_grades = [game.grade for game in recent_games]
        player.recent_form = statistics.mean(recent_grades)
        
        # Update confidence based on recent performance
        if player.recent_form > 75:
            player.confidence = min(100, player.confidence + 5)
        elif player.recent_form < 50:
            player.confidence = max(0, player.confidence - 3)
    
    def get_player_rating_summary(self, player_id: str) -> Dict[str, Any]:
        """Get comprehensive rating summary for a player."""
        if player_id not in self.players:
            return {}
        
        player = self.players[player_id]
        
        # Calculate rating changes
        rating_changes = {}
        for skill in SkillCategory:
            original = player.player_profile.get_skill(skill)
            current = player.current_ratings.get(skill, original)
            rating_changes[skill.value] = {
                'original': original,
                'current': current,
                'change': current - original,
                'peak': player.peak_ratings.get(skill, current),
                'lowest': player.lowest_ratings.get(skill, current)
            }
        
        return {
            'player_name': player.player_profile.name,
            'position': player.player_profile.position,
            'team': player.team,
            'overall_rating_change': self._calculate_overall_change(player),
            'rating_changes': rating_changes,
            'season_stats': player.season_stats.__dict__ if player.season_stats else {},
            'recent_form': player.recent_form,
            'confidence': player.confidence,
            'games_played': len(player.games),
            'season_grade': player.season_stats.season_grade if player.season_stats else 0.0
        }
    
    def _calculate_overall_change(self, player: PlayerSeasonProfile) -> int:
        """Calculate overall rating change from season start."""
        original_overall = player.player_profile.overall_rating
        
        # Weight skill changes by importance for position
        skill_weights = self._get_position_skill_weights(player.player_profile.position)
        
        weighted_change = 0
        total_weight = 0
        
        for skill, weight in skill_weights.items():
            original = player.player_profile.get_skill(skill)
            current = player.current_ratings.get(skill, original)
            weighted_change += (current - original) * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_change = weighted_change / total_weight
            return max(-10, min(10, int(avg_change)))  # Cap at ±10
        
        return 0
    
    def _get_position_skill_weights(self, position: str) -> Dict[SkillCategory, float]:
        """Get skill importance weights by position."""
        weights = {
            "QB": {
                SkillCategory.HANDS: 0.3,
                SkillCategory.AWARENESS: 0.4,
                SkillCategory.SPEED: 0.1,
                SkillCategory.AGILITY: 0.2
            },
            "RB": {
                SkillCategory.SPEED: 0.3,
                SkillCategory.AGILITY: 0.3,
                SkillCategory.STRENGTH: 0.3,
                SkillCategory.HANDS: 0.1
            },
            "WR": {
                SkillCategory.HANDS: 0.4,
                SkillCategory.ROUTE_RUNNING: 0.3,
                SkillCategory.SPEED: 0.2,
                SkillCategory.AGILITY: 0.1
            },
            "CB": {
                SkillCategory.COVERAGE: 0.4,
                SkillCategory.SPEED: 0.3,
                SkillCategory.AGILITY: 0.2,
                SkillCategory.TACKLE: 0.1
            },
            "LB": {
                SkillCategory.TACKLE: 0.4,
                SkillCategory.COVERAGE: 0.2,
                SkillCategory.RUN_DEFENSE: 0.3,
                SkillCategory.STRENGTH: 0.1
            }
        }
        
        return weights.get(position, {
            SkillCategory.SPEED: 0.25,
            SkillCategory.STRENGTH: 0.25,
            SkillCategory.AGILITY: 0.25,
            SkillCategory.AWARENESS: 0.25
        })
    
    def get_league_leaders(self, stat_category: StatCategory, min_games: int = 8) -> List[Tuple[str, float]]:
        """Get league leaders in a specific statistical category."""
        leaders = []
        
        for player_id, player in self.players.items():
            if not player.season_stats or len(player.games) < min_games:
                continue
            
            stat_value = player.season_stats.total_stats.get(stat_category, 0.0)
            leaders.append((player.player_profile.name, stat_value))
        
        return sorted(leaders, key=lambda x: x[1], reverse=True)[:10]
    
    def export_season_data(self, filepath: str):
        """Export season data to JSON file."""
        export_data = {
            'season': self.season,
            'week': self.week,
            'players': {}
        }
        
        for player_id, player in self.players.items():
            export_data['players'][player_id] = {
                'profile': {
                    'name': player.player_profile.name,
                    'position': player.player_profile.position,
                    'overall_rating': player.player_profile.overall_rating,
                    'skills': {skill.value: rating for skill, rating in player.player_profile.skills.items()}
                },
                'current_ratings': {skill.value: rating for skill, rating in player.current_ratings.items()},
                'season_stats': {
                    **player.season_stats.__dict__,
                    'total_stats': {stat.value: value for stat, value in player.season_stats.total_stats.items()},
                    'per_game_averages': {stat.value: value for stat, value in player.season_stats.per_game_averages.items()}
                } if player.season_stats else None,
                'games': [{
                    **game.__dict__,
                    'stats': {stat.value: value for stat, value in game.stats.items()}
                } for game in player.games],
                'team': player.team
            }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def import_season_data(self, filepath: str):
        """Import season data from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.season = data['season']
        self.week = data['week']
        
        for player_id, player_data in data['players'].items():
            # Reconstruct PlayerProfile
            profile_data = player_data['profile']
            skills = {SkillCategory(skill): rating for skill, rating in profile_data['skills'].items()}
            
            profile = PlayerProfile(
                name=profile_data['name'],
                position=profile_data['position'],
                overall_rating=profile_data['overall_rating'],
                skills=skills
            )
            
            # Create season profile
            season_profile = PlayerSeasonProfile(
                player_profile=profile,
                season=self.season,
                team=player_data['team']
            )
            
            # Restore current ratings
            season_profile.current_ratings = {
                SkillCategory(skill): rating for skill, rating in player_data['current_ratings'].items()
            }
            
            # Restore games and stats
            if player_data['season_stats']:
                season_profile.season_stats = SeasonStats(**player_data['season_stats'])
            
            self.players[player_id] = season_profile


def create_sample_season_data():
    """Create sample season data for testing."""
    engine = SeasonRatingEngine(2024)
    
    # Create some sample players
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
    
    hill = PlayerProfile(
        name="Tyreek Hill",
        position="WR", 
        overall_rating=93,
        skills={
            SkillCategory.HANDS: 88,
            SkillCategory.ROUTE_RUNNING: 90,
            SkillCategory.SPEED: 99,
            SkillCategory.AGILITY: 95
        }
    )
    
    henry = PlayerProfile(
        name="Derrick Henry",
        position="RB",
        overall_rating=91,
        skills={
            SkillCategory.STRENGTH: 95,
            SkillCategory.SPEED: 88,
            SkillCategory.AGILITY: 78,
            SkillCategory.HANDS: 75
        }
    )
    
    # Add players to season
    engine.add_player(mahomes, "KC")
    engine.add_player(hill, "MIA")
    engine.add_player(henry, "TEN")
    
    return engine


if __name__ == "__main__":
    # Demo the season rating system
    print("🏈 Season-Based Player Rating System Demo")
    print("=" * 50)
    
    engine = create_sample_season_data()
    
    # Simulate some game stats
    mahomes_game1 = PlayerGameStats(
        game_id="KC_vs_LV_W1",
        week=1,
        opponent="LV",
        stats={
            StatCategory.PASS_ATTEMPTS: 35,
            StatCategory.PASS_COMPLETIONS: 28,
            StatCategory.PASS_YARDS: 335,
            StatCategory.PASS_TDS: 3,
            StatCategory.INTERCEPTIONS: 0
        },
        grade=89.5
    )
    
    engine.record_game_stats("Patrick_Mahomes_KC", mahomes_game1)
    
    # Show updated ratings
    summary = engine.get_player_rating_summary("Patrick_Mahomes_KC")
    print(f"\n📊 {summary['player_name']} Rating Summary:")
    print(f"Overall Change: {summary['overall_rating_change']:+d}")
    print(f"Recent Form: {summary['recent_form']:.1f}")
    print(f"Season Grade: {summary['season_grade']:.1f}")
    
    print("\n🎯 Skill Changes:")
    for skill, data in summary['rating_changes'].items():
        if data['change'] != 0:
            print(f"  {skill}: {data['original']} → {data['current']} ({data['change']:+d})")
