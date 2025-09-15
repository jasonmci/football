"""
Football Play Resolution Engine

Resolves play execution using dice rolls, formation advantages, and configurable outcomes.
Integrates with the existing dice engine to provide realistic football gameplay.
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import sys
import os

# Add our football system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from football.dice_engine import roll_core
from football2.football.plays import FootballPlay
from football2.football.matchup_analyzer import FormationMatchupAnalyzer, MatchupResult, MatchupAdvantage
from football2.football.play_analyzer import PlayAnalyzer, PlayAnalysis, PlayMatchupFactor


class PlayOutcome(Enum):
    """Possible outcomes for play execution."""
    # Positive outcomes
    EXPLOSIVE_SUCCESS = "explosive_success"  # 15+ yard gain, TD potential
    BIG_SUCCESS = "big_success"             # 8-14 yard gain  
    SUCCESS = "success"                     # 4-7 yard gain, conversion
    MODERATE_GAIN = "moderate_gain"         # 1-3 yard gain
    
    # Neutral/negative outcomes  
    NO_GAIN = "no_gain"                     # 0 yards
    LOSS = "loss"                           # -1 to -3 yards
    BIG_LOSS = "big_loss"                   # -4+ yards, sack
    
    # Special outcomes
    TURNOVER = "turnover"                   # Fumble, interception
    PENALTY = "penalty"                     # Flag thrown
    TOUCHDOWN = "touchdown"                 # Score!
    SAFETY = "safety"                       # Defense scores 2


class PlayType(Enum):
    """Categories of plays for resolution."""
    RUN = "run"
    PASS = "pass"
    SPECIAL = "special"


@dataclass
class ResolutionConfig:
    """Configuration for play resolution outcomes."""
    
    # Base dice expressions by play type
    base_dice: Dict[PlayType, str] = field(default_factory=lambda: {
        PlayType.RUN: "2d6",
        PlayType.PASS: "2d8", 
        PlayType.SPECIAL: "1d12"
    })
    
    # Outcome thresholds (dice total needed for each outcome) - REALISTIC FOOTBALL
    thresholds: Dict[PlayOutcome, int] = field(default_factory=lambda: {
        PlayOutcome.EXPLOSIVE_SUCCESS: 20,  # Increased from 18 (harder to achieve)
        PlayOutcome.BIG_SUCCESS: 16,        # Increased from 15
        PlayOutcome.SUCCESS: 13,            # Increased from 12  
        PlayOutcome.MODERATE_GAIN: 10,      # Increased from 9
        PlayOutcome.NO_GAIN: 7,             # Increased from 6
        PlayOutcome.LOSS: 4,                # Same
        PlayOutcome.BIG_LOSS: 2,            # Same
        PlayOutcome.TURNOVER: 1,            # Natural 1s can cause turnovers
    })
    
    # Formation advantage modifiers (added to dice roll) - TONED DOWN
    formation_bonuses: Dict[int, int] = field(default_factory=lambda: {
        3: +3,   # Reduced from +4 - Major advantage  
        1: +1,   # Reduced from +2 - Minor advantage
        0: 0,    # Neutral
        -1: -1,  # Reduced from -2 - Minor disadvantage
        -3: -3   # Reduced from -4 - Major disadvantage
    })
    
    # Situational modifiers
    down_distance_modifiers: Dict[str, int] = field(default_factory=lambda: {
        "1st_and_10": 0,
        "2nd_short": +1,    # 2nd and 1-3
        "2nd_medium": 0,    # 2nd and 4-7
        "2nd_long": -1,     # 2nd and 8+
        "3rd_short": +2,    # 3rd and 1-3
        "3rd_medium": 0,    # 3rd and 4-7  
        "3rd_long": -2,     # 3rd and 8+
        "4th_down": -3,     # Any 4th down
        "goal_line": +2,    # Inside 5-yard line
        "red_zone": +1,     # Inside 20-yard line
    })
    
    # Yardage results by outcome (random ranges) - REALISTIC FOOTBALL
    yardage_ranges: Dict[PlayOutcome, Tuple[int, int]] = field(default_factory=lambda: {
        PlayOutcome.EXPLOSIVE_SUCCESS: (12, 25),  # Reduced from (15, 40)
        PlayOutcome.BIG_SUCCESS: (6, 11),         # Reduced from (8, 14)  
        PlayOutcome.SUCCESS: (3, 5),              # Reduced from (4, 7)
        PlayOutcome.MODERATE_GAIN: (1, 2),        # Reduced from (1, 3)
        PlayOutcome.NO_GAIN: (0, 0),
        PlayOutcome.LOSS: (-2, -1),               # Less punitive 
        PlayOutcome.BIG_LOSS: (-5, -3),           # Reduced from (-8, -4)
        PlayOutcome.TURNOVER: (0, 0),  # Possession change, no yards
    })


# Create a realistic configuration preset
def create_realistic_config() -> ResolutionConfig:
    """Create a realistic football configuration with conservative outcomes."""
    return ResolutionConfig()


# Create an arcade configuration for comparison
def create_arcade_config() -> ResolutionConfig:
    """Create an arcade-style configuration with bigger plays."""
    config = ResolutionConfig()
    # Make explosive plays easier and bigger
    config.thresholds[PlayOutcome.EXPLOSIVE_SUCCESS] = 17
    config.thresholds[PlayOutcome.BIG_SUCCESS] = 14
    config.yardage_ranges[PlayOutcome.EXPLOSIVE_SUCCESS] = (18, 35)
    config.yardage_ranges[PlayOutcome.BIG_SUCCESS] = (10, 17)
    return config


@dataclass 
class PlayResult:
    """Result of executing a play."""
    outcome: PlayOutcome
    yards_gained: int
    dice_roll: int
    total_modifier: int
    final_total: int
    description: str
    details: Dict[str, Any] = field(default_factory=dict)


class PlayResolutionEngine:
    """Resolves football plays using dice and formation analysis."""
    
    def __init__(self, config: Optional[ResolutionConfig] = None, seed: Optional[int] = None):
        self.config = config or ResolutionConfig()
        self.rng = random.Random(seed)
        self.matchup_analyzer = FormationMatchupAnalyzer()
        self.play_analyzer = PlayAnalyzer()  # Add the new play analyzer
    
    def resolve_play(
        self,
        offensive_play: FootballPlay,
        defensive_play: FootballPlay,
        situation: Optional[Dict[str, Any]] = None
    ) -> PlayResult:
        """
        Resolve a play matchup using dice and configuration.
        
        Args:
            offensive_play: The offensive play being run
            defensive_play: The defensive play being run  
            situation: Game situation (down, distance, field position, etc.)
            
        Returns:
            PlayResult with outcome, yardage, and details
        """
        situation = situation or {}
        
        # Analyze formation matchup
        try:
            matchup = self.matchup_analyzer.analyze_matchup(
                offensive_play.base_formation,
                defensive_play.base_formation
            )
        except ValueError:
            # If formations aren't in matchup analyzer, create neutral matchup
            matchup = MatchupResult(
                offense_formation=offensive_play.base_formation,
                defense_formation=defensive_play.base_formation,
                run_advantage=MatchupAdvantage.NEUTRAL,
                pass_advantage=MatchupAdvantage.NEUTRAL, 
                overall_advantage=MatchupAdvantage.NEUTRAL,
                key_factors=[],
                recommended_plays=[]
            )
        
        # NEW: Analyze specific play assignments and techniques
        play_analysis = self.play_analyzer.analyze_play_matchup(offensive_play, defensive_play)
        
        # Determine play type
        play_type = PlayType.RUN if offensive_play.play_type == "run" else PlayType.PASS
        
        # Calculate modifiers (now includes play-specific analysis)
        modifiers = self._calculate_modifiers(offensive_play, defensive_play, matchup, situation, play_analysis)
        
        # Get base dice expression
        dice_expr = self.config.base_dice[play_type]
        
        # Calculate advantage/disadvantage for dice rolling (now includes play analysis)
        advantage, disadvantage = self._calculate_dice_advantage(modifiers, matchup, play_type, play_analysis)
        
        # Roll dice!
        dice_roll = roll_core(dice_expr, self.rng, advantage, disadvantage)
        
        # Apply modifiers
        total_modifier = sum(modifiers.values())
        final_total = dice_roll + total_modifier
        
        # Determine outcome
        outcome = self._determine_outcome(final_total)
        
        # Calculate yardage
        yards_gained = self._calculate_yardage(outcome, play_type)
        
        # Create description (now includes play analysis details)
        description = self._create_description(
            offensive_play, defensive_play, outcome, yards_gained, matchup, play_analysis
        )
        
        return PlayResult(
            outcome=outcome,
            yards_gained=yards_gained,
            dice_roll=dice_roll,
            total_modifier=total_modifier,
            final_total=final_total,
            description=description,
            details={
                "modifiers": modifiers,
                "advantage": advantage,
                "disadvantage": disadvantage,
                "matchup": matchup,
                "play_analysis": play_analysis,  # Include detailed play analysis
                "play_type": play_type.value
            }
        )
    
    def _calculate_modifiers(
        self,
        offense: FootballPlay,
        defense: FootballPlay, 
        matchup: MatchupResult,
        situation: Dict[str, Any],
        play_analysis: PlayAnalysis
    ) -> Dict[str, int]:
        """Calculate all modifiers that apply to the dice roll."""
        modifiers = {}
        
        # Formation advantage modifier
        if offense.play_type == "run":
            advantage = matchup.run_advantage.value
        else:
            advantage = matchup.pass_advantage.value
            
        modifiers["formation"] = self.config.formation_bonuses.get(advantage, 0)
        
        # Down and distance modifier
        down = situation.get("down", 1)
        distance = situation.get("distance", 10)
        field_pos = situation.get("field_position", 50)
        
        situation_key = self._get_situation_key(down, distance, field_pos)
        modifiers["situation"] = self.config.down_distance_modifiers.get(situation_key, 0)
        
        # Pre-snap complexity modifier (motion, shifts create confusion)
        complexity = 0
        if offense.motion:
            complexity += 1
        if len(offense.pre_snap_shifts) > 0:
            complexity += len(offense.pre_snap_shifts)
        if len(defense.pre_snap_shifts) > 1:  # Defense reacting
            complexity -= 1
            
        modifiers["complexity"] = complexity
        
        # NEW: Play-specific modifiers from detailed analysis (CAPPED for realism)
        play_impact = min(3, max(-3, play_analysis.net_impact))  # Cap at +/-3
        modifiers["play_advantages"] = play_impact
        
        # Add individual factor modifiers for transparency (but don't double-count)
        # Just for debugging - these are already included in net_impact
        for i, advantage_factor in enumerate(play_analysis.advantages[:2]):  # Limit to 2
            modifiers[f"adv_{i+1}"] = 0  # For display only, don't affect total
            
        for i, disadvantage_factor in enumerate(play_analysis.disadvantages[:2]):  # Limit to 2  
            modifiers[f"dis_{i+1}"] = 0  # For display only, don't affect total
        
        return modifiers
    
    def _calculate_dice_advantage(
        self,
        modifiers: Dict[str, int],
        matchup: MatchupResult, 
        play_type: PlayType,
        play_analysis: PlayAnalysis
    ) -> Tuple[int, int]:
        """Calculate advantage/disadvantage dice for the roll."""
        advantage = 0
        disadvantage = 0
        
        # Formation-based advantage
        if play_type == PlayType.RUN:
            adv_val = matchup.run_advantage.value
        else:
            adv_val = matchup.pass_advantage.value
            
        if adv_val > 0:
            advantage += 1
        elif adv_val < 0:
            disadvantage += 1
            
        # Major advantages get extra dice
        if abs(adv_val) >= 3:
            if adv_val > 0:
                advantage += 1
            else:
                disadvantage += 1
        
        # NEW: Play-specific advantages affect dice
        net_impact = play_analysis.net_impact
        if net_impact >= 3:
            advantage += 1
        elif net_impact >= 6:
            advantage += 2  # Major play advantage
        elif net_impact <= -3:
            disadvantage += 1
        elif net_impact <= -6:
            disadvantage += 2  # Major play disadvantage
        
        # Specific high-impact factors get bonus dice
        for factor in play_analysis.advantages:
            if factor.impact >= 3:  # Major advantages like free rusher protection
                advantage += 1
                break  # Only one bonus die per category
                
        for factor in play_analysis.disadvantages:
            if factor.impact <= -3:  # Major disadvantages like free rusher
                disadvantage += 1
                break
        
        return advantage, disadvantage
    
    def _determine_outcome(self, final_total: int) -> PlayOutcome:
        """Determine play outcome based on final dice total."""
        # Check thresholds in descending order
        for outcome in [
            PlayOutcome.EXPLOSIVE_SUCCESS,
            PlayOutcome.BIG_SUCCESS, 
            PlayOutcome.SUCCESS,
            PlayOutcome.MODERATE_GAIN,
            PlayOutcome.NO_GAIN,
            PlayOutcome.LOSS,
            PlayOutcome.BIG_LOSS,
            PlayOutcome.TURNOVER
        ]:
            threshold = self.config.thresholds[outcome]
            if final_total >= threshold:
                return outcome
                
        return PlayOutcome.TURNOVER  # Fallback for very low rolls
    
    def _calculate_yardage(self, outcome: PlayOutcome, play_type: PlayType) -> int:
        """Calculate yards gained based on outcome."""
        min_yards, max_yards = self.config.yardage_ranges[outcome]
        
        if min_yards == max_yards:
            return min_yards
            
        # Add some randomness within the range
        return self.rng.randint(min_yards, max_yards)
    
    def _get_situation_key(self, down: int, distance: int, field_pos: int) -> str:
        """Convert game situation to modifier key."""
        if field_pos <= 5:
            return "goal_line"
        elif field_pos <= 20:
            return "red_zone"
        elif down == 4:
            return "4th_down"
        elif down == 1:
            return "1st_and_10"
        elif down == 2:
            if distance <= 3:
                return "2nd_short"
            elif distance <= 7:
                return "2nd_medium"
            else:
                return "2nd_long"
        elif down == 3:
            if distance <= 3:
                return "3rd_short"
            elif distance <= 7:
                return "3rd_medium"
            else:
                return "3rd_long"
        else:
            return "1st_and_10"  # Default
    
    def _create_description(
        self,
        offense: FootballPlay,
        defense: FootballPlay,
        outcome: PlayOutcome,
        yards: int,
        matchup: MatchupResult,
        play_analysis: PlayAnalysis
    ) -> str:
        """Create a narrative description of the play result."""
        
        base_descriptions = {
            PlayOutcome.EXPLOSIVE_SUCCESS: f"🚀 EXPLOSIVE PLAY! {offense.label} breaks through for {yards} yards!",
            PlayOutcome.BIG_SUCCESS: f"💪 Big gain! {offense.label} powers for {yards} yards.",
            PlayOutcome.SUCCESS: f"✅ Successful execution. {offense.label} gains {yards} yards.",
            PlayOutcome.MODERATE_GAIN: f"➡️ Modest gain. {offense.label} picks up {yards} yards.",
            PlayOutcome.NO_GAIN: f"🛑 No gain. {defense.label} holds the line.",
            PlayOutcome.LOSS: f"📉 Loss of {abs(yards)} yards. {defense.label} wins the battle.",
            PlayOutcome.BIG_LOSS: f"💥 BIG LOSS! {defense.label} forces {abs(yards)} yard loss!",
            PlayOutcome.TURNOVER: f"🔄 TURNOVER! {defense.label} forces a turnover!",
        }
        
        description = base_descriptions.get(outcome, f"Play result: {yards} yards")
        
        # NEW: Add play-specific context from analysis
        key_factors = []
        
        # Add the most impactful advantage/disadvantage
        if play_analysis.advantages:
            top_advantage = max(play_analysis.advantages, key=lambda x: x.impact)
            if top_advantage.impact >= 2:
                key_factors.append(top_advantage.description)
        
        if play_analysis.disadvantages:
            top_disadvantage = min(play_analysis.disadvantages, key=lambda x: x.impact)
            if top_disadvantage.impact <= -2:
                key_factors.append(top_disadvantage.description)
        
        # Add formation context for interesting matchups
        if matchup.key_factors:
            factor = matchup.key_factors[0]  # Use first key factor
            key_factors.append(factor)
        
        # Combine into final description
        if key_factors:
            description += f" ({'; '.join(key_factors[:2])})"  # Limit to 2 factors
            
        return description
