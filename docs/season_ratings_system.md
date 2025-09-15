# Season-Based Player Rating System

A comprehensive system for tracking and adjusting NFL player ratings throughout a season based on performance statistics and game outcomes.

## Features

### 🎯 Dynamic Rating Adjustments
- **Performance-Based Changes**: Player ratings adjust dynamically based on game statistics
- **Position-Specific Factors**: Different positions have different performance indicators
- **Realistic Boundaries**: Rating changes are capped to prevent unrealistic swings
- **Peak/Low Tracking**: Tracks highest and lowest ratings achieved during the season

### 📊 Comprehensive Statistics Tracking
- **27 Statistical Categories**: From passing yards to broken tackles to missed tackles
- **Game-by-Game Records**: Complete statistical history for every game
- **Season Aggregation**: Automatic calculation of totals and per-game averages
- **Performance Grades**: 0-100 game grades with season averages

### 🏆 League Leadership & Analysis
- **League Leaders**: Dynamic tracking of statistical leaders across categories
- **Rating Changes**: Biggest improvements and declines throughout the season
- **Trending Metrics**: Recent form, confidence levels, and injury risk
- **Contract Integration**: Full salary cap and roster management

## Core Components

### PlayerSeasonProfile
```python
@dataclass
class PlayerSeasonProfile:
    player_profile: PlayerProfile      # Base ratings and info
    season: int                       # Season year
    team: str                        # Current team
    games: List[PlayerGameStats]     # Game-by-game statistics
    current_ratings: Dict[SkillCategory, int]  # Dynamic ratings
    recent_form: float               # Last 4 games performance
    confidence: float                # Player confidence (0-100)
```

### Statistical Categories
```python
# Passing Stats
PASS_ATTEMPTS, PASS_COMPLETIONS, PASS_YARDS, PASS_TDS, INTERCEPTIONS

# Rushing Stats  
RUSH_ATTEMPTS, RUSH_YARDS, RUSH_TDS, BROKEN_TACKLES, YARDS_AFTER_CONTACT

# Receiving Stats
TARGETS, RECEPTIONS, RECEIVING_YARDS, RECEIVING_TDS, DROPS, YARDS_AFTER_CATCH

# Defensive Stats
TACKLES, TACKLES_FOR_LOSS, SACKS, PASS_BREAKUPS, FORCED_FUMBLES

# Special Categories
CLUTCH_PLAYS, PENALTIES, MISSED_TACKLES
```

## How Rating Adjustments Work

### Position-Specific Performance Factors

**Quarterbacks**
- Completion percentage affects `HANDS` and `AWARENESS`
- Multiple interceptions hurt `AWARENESS` significantly
- High completion rate (>70%) provides positive adjustment
- Poor completion rate (<50%) provides negative adjustment

**Running Backs**
- Yards per carry affects `AGILITY` and `SPEED`
- Broken tackles boost `STRENGTH` and `AGILITY`
- Excellent YPC (>5.0) provides positive adjustments
- Poor YPC (<3.0) provides negative adjustments

**Wide Receivers**
- Catch rate affects `HANDS` and `ROUTE_RUNNING`
- Drops significantly hurt `HANDS` rating
- High catch rate (>75%) provides positive adjustments
- Multiple drops (>2) provide large negative adjustments

**Defensive Players**
- Tackle count affects `TACKLE` rating
- Missed tackles hurt `TACKLE` rating significantly
- High tackle games (>8) provide positive adjustments

### Rating Change Mechanics
- **Maximum Change**: ±3 points per game per skill
- **Overall Impact**: Weighted average based on position importance
- **Boundaries**: Ratings capped between 30-99
- **Peak Tracking**: System remembers highest/lowest ratings achieved

## Usage Examples

### Basic Season Simulation
```python
from season_ratings import SeasonRatingEngine, PlayerGameStats, StatCategory

# Create season engine
engine = SeasonRatingEngine(2024)

# Add player
mahomes = PlayerProfile(name="Patrick Mahomes", position="QB", overall_rating=96)
player_profile = engine.add_player(mahomes, "KC")

# Record game performance
game_stats = PlayerGameStats(
    game_id="Week_1",
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

engine.record_game_stats("Patrick_Mahomes_KC", game_stats)

# Get updated summary
summary = engine.get_player_rating_summary("Patrick_Mahomes_KC")
print(f"Overall Change: {summary['overall_rating_change']:+d}")
```

### League Leaders Analysis
```python
# Get passing yards leaders
leaders = engine.get_league_leaders(StatCategory.PASS_YARDS, min_games=8)
for rank, (name, yards) in enumerate(leaders[:5], 1):
    print(f"{rank}. {name}: {yards:,.0f} yards")
```

### Roster Integration
```python
from roster_management import RosterManager

# Create roster manager
manager = RosterManager(2024)

# Get comprehensive team analysis with updated ratings
analysis = manager.get_roster_analysis("KC", engine)
print(f"Top Players: {analysis['top_players']}")
print(f"Salary Cap Usage: {analysis['salary_cap']['percentage_used']:.1f}%")
```

## Sample Output

```
🏈 Season-Based Player Rating System Demo
==================================================

📊 Initial Ratings:
Patrick Mahomes (QB): 96
Justin Jefferson (WR): 94

🏈 Simulating 8-week season...

Week 2 Results:
  Mahomes: 28/35, 320 yds, 2 TD
  Jefferson: 8/10, 120 yds, 0 TD

📈 Final Season Summary:
==============================

🎯 Patrick Mahomes:
  Games: 8
  Overall Change: +2
  Season Grade: 89.5
  Key Skills:
    hands: 92 → 99 (+7)

🙌 Justin Jefferson:
  Games: 8
  Overall Change: +2
  Season Grade: 84.5
  Key Skills:
    hands: 94 → 99 (+5)

🏆 League Leaders:
  Passing: Patrick Mahomes - 2560 yards
  Receiving: Justin Jefferson - 880 yards
```

## Advanced Features

### Roster Management
- **Salary Cap Tracking**: Full NFL salary cap management with realistic contracts
- **Depth Charts**: Position-specific depth chart management
- **Trade System**: Player trades with contract and cap considerations
- **Free Agency**: Sign/release players with cap impact calculations

### Contract System
```python
@dataclass
class PlayerContract:
    total_value: int           # Total contract value
    years: int                # Contract length  
    guaranteed_money: int     # Guaranteed money
    cap_hit: int             # Current year cap hit
    contract_type: ContractType  # Rookie, veteran, franchise tag, etc.
```

### Data Export/Import
```python
# Export season data
engine.export_season_data("season_2024.json")

# Import for analysis
engine.import_season_data("season_2024.json")
```

## Files Structure

```
src/football2/football/
├── season_ratings.py       # Core season rating engine
├── roster_management.py    # NFL roster and contract management
└── enhanced_resolution.py  # Base player profiles and ratings

tools/
├── simple_season_demo.py   # Basic demo showing core functionality
└── season_rating_demo.py   # Comprehensive demo with full features
```

## Technical Architecture

### Rating Calculation Flow
1. **Game Stats Input** → Statistical performance recorded
2. **Performance Analysis** → Position-specific factor calculation  
3. **Rating Adjustment** → Apply bounded changes to skill ratings
4. **Overall Recalculation** → Weighted skill average for overall rating
5. **Trend Updates** → Update recent form, confidence, and other metrics

### Position Skill Weights
Different positions weight skills differently for overall rating:

- **QB**: Awareness (40%), Hands (30%), Speed (10%), Agility (20%)
- **RB**: Speed (30%), Agility (30%), Strength (30%), Hands (10%)  
- **WR**: Hands (40%), Route Running (30%), Speed (20%), Agility (10%)
- **CB**: Coverage (40%), Speed (30%), Agility (20%), Tackle (10%)

## Integration with Football Engine

The season rating system integrates seamlessly with:
- **Dice Resolution Engine**: Uses current ratings for play outcomes
- **RPO System**: Player ratings affect RPO success rates
- **Zone Blitz Defense**: Defensive ratings impact blitz effectiveness
- **Play Resolution**: Dynamic ratings provide realistic game simulation

This creates a complete ecosystem where player performance affects ratings, which in turn affects future performance, creating realistic season-long narrative arcs.
