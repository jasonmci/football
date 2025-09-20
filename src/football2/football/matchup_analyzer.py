"""
Football formation matchup analysis system.

Analyzes strategic advantages and disadvantages when offensive formations
face defensive formations, inspired by board game mechanics from games
like Techno Bowl and Statis Pro Football.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class MatchupAdvantage(Enum):
    """Strategic advantage levels in formation matchups."""

    MAJOR_ADVANTAGE = 3
    MINOR_ADVANTAGE = 1
    NEUTRAL = 0
    MINOR_DISADVANTAGE = -1
    MAJOR_DISADVANTAGE = -3


class PlayType(Enum):
    """Types of plays that formations excel at."""

    RUN_INSIDE = "run_inside"
    RUN_OUTSIDE = "run_outside"
    PASS_SHORT = "pass_short"
    PASS_DEEP = "pass_deep"
    PLAY_ACTION = "play_action"
    SCREEN = "screen"


@dataclass
class FormationStrengths:
    """Defines what a formation is good at."""

    formation_name: str
    run_blocking: int  # 1-5 scale
    pass_protection: int  # 1-5 scale
    route_diversity: int  # 1-5 scale
    misdirection: int  # 1-5 scale
    optimal_play_types: List[PlayType]


@dataclass
class DefenseStrengths:
    """Defines what a defensive formation excels at stopping."""

    formation_name: str
    run_defense: int  # 1-5 scale
    pass_rush: int  # 1-5 scale
    pass_coverage: int  # 1-5 scale
    gap_control: int  # 1-5 scale
    counters_play_types: List[PlayType]


@dataclass
class MatchupResult:
    """Result of analyzing an offensive vs defensive formation matchup."""

    offense_formation: str
    defense_formation: str
    run_advantage: MatchupAdvantage
    pass_advantage: MatchupAdvantage
    overall_advantage: MatchupAdvantage
    key_factors: List[str]
    recommended_plays: List[PlayType]


class FormationMatchupAnalyzer:
    """Analyzes strategic matchups between offensive and defensive formations."""

    def __init__(self):
        self._offensive_strengths = self._initialize_offensive_strengths()
        self._defensive_strengths = self._initialize_defensive_strengths()

    def _initialize_offensive_strengths(self) -> Dict[str, FormationStrengths]:
        """Initialize offensive formation strength profiles."""
        return {
            "empty_backfield": FormationStrengths(
                formation_name="empty_backfield",
                run_blocking=1,
                pass_protection=2,
                route_diversity=5,
                misdirection=3,
                optimal_play_types=[
                    PlayType.PASS_SHORT,
                    PlayType.PASS_DEEP,
                    PlayType.SCREEN,
                ],
            ),
            "spread_10": FormationStrengths(
                formation_name="spread_10",
                run_blocking=3,
                pass_protection=3,
                route_diversity=4,
                misdirection=4,
                optimal_play_types=[
                    PlayType.RUN_OUTSIDE,
                    PlayType.PASS_SHORT,
                    PlayType.SCREEN,
                ],
            ),
            "i_form": FormationStrengths(
                formation_name="i_form",
                run_blocking=5,
                pass_protection=4,
                route_diversity=2,
                misdirection=3,
                optimal_play_types=[PlayType.RUN_INSIDE, PlayType.PLAY_ACTION],
            ),
            "strong_i": FormationStrengths(
                formation_name="strong_i",
                run_blocking=5,
                pass_protection=5,
                route_diversity=1,
                misdirection=2,
                optimal_play_types=[PlayType.RUN_INSIDE, PlayType.RUN_OUTSIDE],
            ),
            "pistol_11": FormationStrengths(
                formation_name="pistol_11",
                run_blocking=4,
                pass_protection=3,
                route_diversity=3,
                misdirection=4,
                optimal_play_types=[
                    PlayType.RUN_INSIDE,
                    PlayType.RUN_OUTSIDE,
                    PlayType.PLAY_ACTION,
                ],
            ),
            "shotgun_11": FormationStrengths(
                formation_name="shotgun_11",
                run_blocking=2,
                pass_protection=4,
                route_diversity=4,
                misdirection=3,
                optimal_play_types=[
                    PlayType.PASS_SHORT,
                    PlayType.PASS_DEEP,
                    PlayType.SCREEN,
                ],
            ),
            "singleback_11": FormationStrengths(
                formation_name="singleback_11",
                run_blocking=4,
                pass_protection=4,
                route_diversity=3,
                misdirection=3,
                optimal_play_types=[
                    PlayType.RUN_INSIDE,
                    PlayType.PASS_SHORT,
                    PlayType.PLAY_ACTION,
                ],
            ),
        }

    def _initialize_defensive_strengths(self) -> Dict[str, DefenseStrengths]:
        """Initialize defensive formation strength profiles."""
        return {
            "34_defense": DefenseStrengths(
                formation_name="34_defense",
                run_defense=4,
                pass_rush=3,
                pass_coverage=3,
                gap_control=4,
                counters_play_types=[PlayType.RUN_INSIDE, PlayType.PLAY_ACTION],
            ),
            "dime": DefenseStrengths(
                formation_name="dime",
                run_defense=2,
                pass_rush=4,
                pass_coverage=5,
                gap_control=2,
                counters_play_types=[PlayType.PASS_SHORT, PlayType.PASS_DEEP],
            ),
            "prevent_defense": DefenseStrengths(
                formation_name="prevent_defense",
                run_defense=1,
                pass_rush=2,
                pass_coverage=5,
                gap_control=1,
                counters_play_types=[PlayType.PASS_DEEP],
            ),
            "goalline_defense": DefenseStrengths(
                formation_name="goalline_defense",
                run_defense=5,
                pass_rush=5,
                pass_coverage=1,
                gap_control=5,
                counters_play_types=[PlayType.RUN_INSIDE],
            ),
            "base43": DefenseStrengths(
                formation_name="base43",
                run_defense=4,
                pass_rush=4,
                pass_coverage=3,
                gap_control=4,
                counters_play_types=[
                    PlayType.RUN_INSIDE,
                    PlayType.RUN_OUTSIDE,
                    PlayType.PASS_SHORT,
                ],
            ),
            "nickel": DefenseStrengths(
                formation_name="nickel",
                run_defense=3,
                pass_rush=4,
                pass_coverage=4,
                gap_control=3,
                counters_play_types=[PlayType.PASS_SHORT, PlayType.SCREEN],
            ),
            "bear46": DefenseStrengths(
                formation_name="bear46",
                run_defense=5,
                pass_rush=5,
                pass_coverage=2,
                gap_control=5,
                counters_play_types=[PlayType.RUN_INSIDE, PlayType.RUN_OUTSIDE],
            ),
        }

    def analyze_matchup(self, offense_name: str, defense_name: str) -> MatchupResult:
        """
        Analyze the strategic matchup between an offensive and defensive formation.

        Args:
            offense_name: Name of the offensive formation
            defense_name: Name of the defensive formation

        Returns:
            MatchupResult with detailed analysis
        """
        offense = self._offensive_strengths.get(offense_name)
        defense = self._defensive_strengths.get(defense_name)

        if not offense or not defense:
            raise ValueError(f"Unknown formation: {offense_name} vs {defense_name}")

        # Calculate run advantage
        run_differential = offense.run_blocking - defense.run_defense
        run_advantage = self._calculate_advantage(run_differential)

        # Calculate pass advantage
        pass_differential = (offense.pass_protection + offense.route_diversity) / 2 - (
            defense.pass_rush + defense.pass_coverage
        ) / 2
        pass_advantage = self._calculate_advantage(pass_differential)

        # Overall advantage considers both aspects
        overall_differential = (run_differential + pass_differential) / 2
        overall_advantage = self._calculate_advantage(overall_differential)

        # Determine key factors
        key_factors = self._identify_key_factors(
            offense, defense, run_differential, pass_differential
        )

        # Recommend plays based on advantages
        recommended_plays = self._recommend_plays(
            offense, defense, run_advantage, pass_advantage
        )

        return MatchupResult(
            offense_formation=offense_name,
            defense_formation=defense_name,
            run_advantage=run_advantage,
            pass_advantage=pass_advantage,
            overall_advantage=overall_advantage,
            key_factors=key_factors,
            recommended_plays=recommended_plays,
        )

    def _calculate_advantage(self, differential: float) -> MatchupAdvantage:
        """Convert numerical differential to advantage enum."""
        if differential >= 2.0:
            return MatchupAdvantage.MAJOR_ADVANTAGE
        elif differential >= 0.5:
            return MatchupAdvantage.MINOR_ADVANTAGE
        elif differential <= -2.0:
            return MatchupAdvantage.MAJOR_DISADVANTAGE
        elif differential <= -0.5:
            return MatchupAdvantage.MINOR_DISADVANTAGE
        else:
            return MatchupAdvantage.NEUTRAL

    def _identify_key_factors(
        self,
        offense: FormationStrengths,
        defense: DefenseStrengths,
        run_diff: float,
        pass_diff: float,
    ) -> List[str]:
        """Identify the key strategic factors in this matchup."""
        factors = []

        if run_diff >= 1.0:
            factors.append(
                (
                    f"Offense has strong run blocking advantage "
                    f"({offense.run_blocking} vs {defense.run_defense})"
                )
            )
        elif run_diff <= -1.0:
            factors.append(
                (
                    f"Defense dominates run game "
                    f"({defense.run_defense} vs {offense.run_blocking})"
                )
            )

        if pass_diff >= 1.0:
            factors.append("Offense has passing game advantage")
        elif pass_diff <= -1.0:
            factors.append("Defense controls passing game")

        if offense.misdirection >= 4:
            factors.append(f"High misdirection potential with {offense.formation_name}")

        if defense.gap_control >= 4:
            factors.append(f"Excellent gap control from {defense.formation_name}")

        return factors

    def _recommend_plays(
        self,
        offense: FormationStrengths,
        defense: DefenseStrengths,
        run_advantage: MatchupAdvantage,
        pass_advantage: MatchupAdvantage,
    ) -> List[PlayType]:
        """Recommend optimal play types for this matchup."""
        recommendations = []

        # Favor plays where offense has advantage
        if run_advantage in [
            MatchupAdvantage.MAJOR_ADVANTAGE,
            MatchupAdvantage.MINOR_ADVANTAGE,
        ]:
            recommendations.extend([PlayType.RUN_INSIDE, PlayType.RUN_OUTSIDE])

        if pass_advantage in [
            MatchupAdvantage.MAJOR_ADVANTAGE,
            MatchupAdvantage.MINOR_ADVANTAGE,
        ]:
            recommendations.extend([PlayType.PASS_SHORT, PlayType.PASS_DEEP])

        # Always consider plays the offense excels at
        for play_type in offense.optimal_play_types:
            if (
                play_type not in recommendations
                and play_type not in defense.counters_play_types
            ):
                recommendations.append(play_type)

        # Avoid plays the defense specifically counters unless we have major advantage
        if run_advantage != MatchupAdvantage.MAJOR_ADVANTAGE:
            recommendations = [
                p
                for p in recommendations
                if p not in defense.counters_play_types
                or p in [PlayType.RUN_INSIDE, PlayType.RUN_OUTSIDE]
            ]

        if pass_advantage != MatchupAdvantage.MAJOR_ADVANTAGE:
            recommendations = [
                p
                for p in recommendations
                if p not in defense.counters_play_types
                or p in [PlayType.PASS_SHORT, PlayType.PASS_DEEP]
            ]

        return recommendations[:4]  # Limit to top 4 recommendations

    def get_formation_summary(
        self, formation_name: str, is_offense: bool = True
    ) -> Optional[Dict]:
        """Get a summary of a formation's strengths and characteristics."""
        if is_offense:
            formation = self._offensive_strengths.get(formation_name)
            if formation:
                return {
                    "name": formation.formation_name,
                    "run_blocking": formation.run_blocking,
                    "pass_protection": formation.pass_protection,
                    "route_diversity": formation.route_diversity,
                    "misdirection": formation.misdirection,
                    "optimal_plays": [
                        play.value for play in formation.optimal_play_types
                    ],
                }
        else:
            formation = self._defensive_strengths.get(formation_name)
            if formation:
                return {
                    "name": formation.formation_name,
                    "run_defense": formation.run_defense,
                    "pass_rush": formation.pass_rush,
                    "pass_coverage": formation.pass_coverage,
                    "gap_control": formation.gap_control,
                    "counters": [play.value for play in formation.counters_play_types],
                }
        return None
