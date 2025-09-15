"""
Intelligent play calling system for formation-based football strategy.

Suggests optimal formations and plays based on game situation, down/distance,
field position, and opponent tendencies. Designed for board game mechanics
where strategic decision-making is key.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
from .matchup_analyzer import FormationMatchupAnalyzer, PlayType


class GameSituation(Enum):
    """Different game situations that affect play calling."""
    FIRST_DOWN = "first_down"
    SHORT_YARDAGE = "short_yardage"  # 2-3 yards to go
    MEDIUM_YARDAGE = "medium_yardage"  # 4-7 yards to go
    LONG_YARDAGE = "long_yardage"  # 8+ yards to go
    GOAL_LINE = "goal_line"  # Inside 5 yard line
    RED_ZONE = "red_zone"  # Inside 20 yard line
    TWO_MINUTE_DRILL = "two_minute_drill"
    HAIL_MARY = "hail_mary"  # 20+ yards, minimal time


class FieldPosition(Enum):
    """Field position zones affecting strategy."""
    OWN_GOAL_LINE = "own_goal_line"  # Own 1-10
    OWN_TERRITORY = "own_territory"  # Own 11-40
    MIDFIELD = "midfield"  # Own 41 - Opp 40
    OPPONENT_TERRITORY = "opponent_territory"  # Opp 41-20
    RED_ZONE = "red_zone"  # Opp 20-5
    GOAL_LINE = "goal_line"  # Opp 5-1


@dataclass
class GameContext:
    """Current game context for play calling decisions."""
    down: int  # 1-4
    yards_to_go: int
    field_position: FieldPosition
    time_remaining: int  # seconds
    score_differential: int  # positive if leading
    situation: GameSituation


@dataclass
class PlayRecommendation:
    """A specific play call recommendation."""
    formation: str
    play_type: PlayType
    confidence: float  # 0.0 - 1.0
    reasoning: List[str]
    risk_level: str  # "LOW", "MEDIUM", "HIGH"


class IntelligentPlayCaller:
    """AI-driven play calling system for strategic football."""
    
    def __init__(self):
        self.analyzer = FormationMatchupAnalyzer()
        self._situation_preferences = self._initialize_situation_preferences()
    
    def _initialize_situation_preferences(self) -> Dict[GameSituation, Dict]:
        """Define formation and play preferences for each game situation."""
        return {
            GameSituation.FIRST_DOWN: {
                "formations": ["singleback_11", "pistol_11", "shotgun_11"],
                "play_types": [PlayType.RUN_INSIDE, PlayType.PASS_SHORT, PlayType.PLAY_ACTION],
                "risk_tolerance": "MEDIUM"
            },
            GameSituation.SHORT_YARDAGE: {
                "formations": ["i_form", "strong_i", "pistol_11"],
                "play_types": [PlayType.RUN_INSIDE, PlayType.RUN_OUTSIDE],
                "risk_tolerance": "LOW"
            },
            GameSituation.MEDIUM_YARDAGE: {
                "formations": ["shotgun_11", "singleback_11", "spread_10"],
                "play_types": [PlayType.PASS_SHORT, PlayType.RUN_OUTSIDE, PlayType.SCREEN],
                "risk_tolerance": "MEDIUM"
            },
            GameSituation.LONG_YARDAGE: {
                "formations": ["shotgun_11", "empty_backfield", "spread_10"],
                "play_types": [PlayType.PASS_SHORT, PlayType.PASS_DEEP, PlayType.SCREEN],
                "risk_tolerance": "HIGH"
            },
            GameSituation.GOAL_LINE: {
                "formations": ["strong_i", "i_form", "pistol_11"],
                "play_types": [PlayType.RUN_INSIDE, PlayType.PLAY_ACTION],
                "risk_tolerance": "LOW"
            },
            GameSituation.RED_ZONE: {
                "formations": ["singleback_11", "pistol_11", "strong_i"],
                "play_types": [PlayType.RUN_INSIDE, PlayType.PASS_SHORT, PlayType.PLAY_ACTION],
                "risk_tolerance": "MEDIUM"
            },
            GameSituation.TWO_MINUTE_DRILL: {
                "formations": ["shotgun_11", "empty_backfield", "spread_10"],
                "play_types": [PlayType.PASS_SHORT, PlayType.PASS_DEEP, PlayType.SCREEN],
                "risk_tolerance": "HIGH"
            },
            GameSituation.HAIL_MARY: {
                "formations": ["empty_backfield"],
                "play_types": [PlayType.PASS_DEEP],
                "risk_tolerance": "HIGH"
            }
        }
    
    def suggest_formation(self, context: GameContext, 
                         opponent_formation: Optional[str] = None) -> List[str]:
        """
        Suggest optimal formations for the given game context.
        
        Args:
            context: Current game situation
            opponent_formation: Known or predicted opponent formation
            
        Returns:
            List of formation names in priority order
        """
        preferences = self._situation_preferences.get(context.situation, {})
        base_formations = preferences.get("formations", [])
        
        # Adjust based on down and distance
        if context.down == 1:
            # First down - more options
            additional = ["singleback_11", "pistol_11"]
            base_formations.extend([f for f in additional if f not in base_formations])
        elif context.down == 3 and context.yards_to_go >= 8:
            # Third and long - passing focus
            base_formations = ["shotgun_11", "empty_backfield", "spread_10"]
        elif context.down == 4:
            # Fourth down - depends on distance
            if context.yards_to_go <= 2:
                base_formations = ["strong_i", "i_form"]
            else:
                base_formations = ["shotgun_11", "empty_backfield"]
        
        # Factor in opponent formation matchups if known
        if opponent_formation:
            ranked_formations = []
            for formation in base_formations:
                try:
                    matchup = self.analyzer.analyze_matchup(formation, opponent_formation)
                    score = matchup.overall_advantage.value
                    ranked_formations.append((formation, score))
                except ValueError:
                    # Unknown formation, keep it but with neutral score
                    ranked_formations.append((formation, 0))
            
            # Sort by matchup advantage
            ranked_formations.sort(key=lambda x: x[1], reverse=True)
            return [formation for formation, _ in ranked_formations]
        
        return base_formations[:3]
    
    def suggest_play(self, context: GameContext, formation: str,
                    opponent_formation: Optional[str] = None) -> PlayRecommendation:
        """
        Suggest the optimal play type for given formation and context.
        
        Args:
            context: Current game situation
            formation: Chosen offensive formation
            opponent_formation: Known or predicted defensive formation
            
        Returns:
            PlayRecommendation with detailed analysis
        """
        preferences = self._situation_preferences.get(context.situation, {})
        preferred_plays = preferences.get("play_types", [])
        risk_tolerance = preferences.get("risk_tolerance", "MEDIUM")
        
        # Get formation strengths
        formation_profile = self.analyzer.get_formation_summary(formation, is_offense=True)
        
        reasoning = []
        confidence = 0.5
        
        # Analyze matchup if opponent formation is known
        if opponent_formation:
            try:
                matchup = self.analyzer.analyze_matchup(formation, opponent_formation)
                preferred_plays = matchup.recommended_plays
                reasoning.extend(matchup.key_factors)
                
                # Adjust confidence based on matchup advantage
                if matchup.overall_advantage.value >= 1:
                    confidence += 0.3
                elif matchup.overall_advantage.value <= -1:
                    confidence -= 0.2
                    
                reasoning.append(f"Matchup analysis vs {opponent_formation}")
            except ValueError:
                reasoning.append(f"Unknown opponent formation: {opponent_formation}")
        
        # Select best play from preferences
        if preferred_plays:
            best_play = preferred_plays[0]
            
            # Add situational reasoning
            if context.situation == GameSituation.SHORT_YARDAGE:
                reasoning.append("Short yardage situation favors power running")
                confidence += 0.2
            elif context.situation == GameSituation.LONG_YARDAGE:
                reasoning.append("Long yardage requires passing attack")
                confidence += 0.2
            elif context.situation == GameSituation.GOAL_LINE:
                reasoning.append("Goal line demands high-percentage plays")
                confidence += 0.1
            
            # Factor in formation strengths
            if formation_profile:
                if best_play in [PlayType.RUN_INSIDE, PlayType.RUN_OUTSIDE]:
                    if formation_profile["run_blocking"] >= 4:
                        reasoning.append(f"Excellent run blocking in {formation}")
                        confidence += 0.1
                elif best_play in [PlayType.PASS_SHORT, PlayType.PASS_DEEP]:
                    if formation_profile["route_diversity"] >= 4:
                        reasoning.append(f"Great route options in {formation}")
                        confidence += 0.1
        else:
            # Fallback to formation's optimal plays
            if formation_profile and formation_profile["optimal_plays"]:
                best_play = PlayType(formation_profile["optimal_plays"][0])
                reasoning.append(f"Using {formation}'s optimal play type")
            else:
                best_play = PlayType.RUN_INSIDE  # Conservative fallback
                reasoning.append("Conservative play call - limited information")
                confidence = 0.3
        
        # Determine risk level
        high_risk_plays = [PlayType.PASS_DEEP, PlayType.PLAY_ACTION]
        if best_play in high_risk_plays:
            risk_level = "HIGH"
        elif best_play in [PlayType.SCREEN]:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Adjust for game situation
        if context.down >= 3 and context.yards_to_go > 5:
            risk_level = "HIGH"  # Must take risks
        elif context.situation == GameSituation.GOAL_LINE:
            risk_level = "LOW"   # Minimize turnovers
        
        confidence = min(1.0, max(0.0, confidence))  # Clamp to valid range
        
        return PlayRecommendation(
            formation=formation,
            play_type=best_play,
            confidence=confidence,
            reasoning=reasoning,
            risk_level=risk_level
        )
    
    def get_full_recommendation(self, context: GameContext,
                              opponent_formation: Optional[str] = None) -> Dict:
        """
        Get complete play call recommendation including formation and play.
        
        Args:
            context: Current game situation
            opponent_formation: Known or predicted defensive formation
            
        Returns:
            Dictionary with formation options and play recommendations
        """
        # Get formation suggestions
        formations = self.suggest_formation(context, opponent_formation)
        
        # Get play recommendations for each formation
        play_options = []
        for formation in formations[:3]:  # Top 3 formations
            play_rec = self.suggest_play(context, formation, opponent_formation)
            play_options.append({
                "formation": formation,
                "play_type": play_rec.play_type.value,
                "confidence": play_rec.confidence,
                "risk_level": play_rec.risk_level,
                "reasoning": play_rec.reasoning
            })
        
        return {
            "situation": context.situation.value,
            "recommended_formations": formations,
            "play_options": play_options,
            "top_recommendation": play_options[0] if play_options else None
        }


def determine_game_situation(down: int, yards_to_go: int, 
                           field_position: FieldPosition) -> GameSituation:
    """Helper function to determine game situation from basic parameters."""
    if field_position == FieldPosition.GOAL_LINE:
        return GameSituation.GOAL_LINE
    elif field_position == FieldPosition.RED_ZONE:
        return GameSituation.RED_ZONE
    elif down == 1:
        return GameSituation.FIRST_DOWN
    elif yards_to_go <= 3:
        return GameSituation.SHORT_YARDAGE
    elif yards_to_go <= 7:
        return GameSituation.MEDIUM_YARDAGE
    else:
        return GameSituation.LONG_YARDAGE
