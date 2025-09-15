"""
Advanced Play Analysis Engine

Analyzes specific play assignments and techniques to determine tactical advantages.
This is where the real football strategy comes alive - pulling guards vs stunts,
blitz pickup vs coverage, etc.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set, Any
from .plays import FootballPlay, PlayerAssignment, AssignmentType


class TacticalAdvantage(Enum):
    """Specific tactical advantages that can be gained."""
    # Blocking advantages
    EXTRA_BLOCKER = "extra_blocker"
    PULLING_GUARD = "pulling_guard"
    DOUBLE_TEAM = "double_team"
    SEAL_BLOCK = "seal_block"
    CRACK_BLOCK = "crack_block"
    TRAP_BLOCK = "trap_block"  # NEW: Trap blocking scheme
    
    # Coverage advantages  
    OVERLOAD_BLITZ = "overload_blitz"
    COVERAGE_BUST = "coverage_bust"
    MISMATCH = "mismatch"
    PICK_PLAY = "pick_play"
    
    # Movement advantages
    MOTION_CONFUSION = "motion_confusion"
    SHIFT_ADVANTAGE = "shift_advantage"
    STACK_FORMATION = "stack_formation"
    
    # Timing advantages
    QUICK_SNAP = "quick_snap"
    HARD_COUNT = "hard_count"
    
    # Scheme advantages
    POWER_CONCEPT = "power_concept"
    COUNTER_ACTION = "counter_action"
    PLAY_ACTION = "play_action"
    RPO = "rpo"  # Run-pass option
    TRAP_CONCEPT = "trap_concept"  # NEW: Trap misdirection


class TacticalDisadvantage(Enum):
    """Specific tactical disadvantages."""
    # Blocking problems
    FREE_RUSHER = "free_rusher"
    STUNTS_VS_PROTECTION = "stunts_vs_protection"
    OUTNUMBERED = "outnumbered"
    BLOWN_ASSIGNMENT = "blown_assignment"
    
    # Coverage problems
    UNCOVERED_RECEIVER = "uncovered_receiver"
    WRONG_LEVERAGE = "wrong_leverage"
    SPEED_MISMATCH = "speed_mismatch"
    
    # Scheme problems
    PREDICTABLE_PLAY = "predictable_play"
    WRONG_PERSONNEL = "wrong_personnel"
    BAD_TIMING = "bad_timing"


@dataclass
class PlayMatchupFactor:
    """A specific factor affecting the play matchup."""
    factor_type: str  # TacticalAdvantage or TacticalDisadvantage name
    impact: int  # -3 to +3 impact on play success
    description: str
    confidence: float = 1.0  # 0.0 to 1.0, how certain we are
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlayAnalysis:
    """Complete analysis of a play matchup."""
    advantages: List[PlayMatchupFactor]
    disadvantages: List[PlayMatchupFactor]
    net_impact: int  # Sum of all factors
    key_matchups: List[str]  # Key player vs player matchups
    scheme_analysis: Dict[str, Any]  # Detailed scheme breakdown
    confidence: float  # Overall confidence in analysis


class PlayAnalyzer:
    """Analyzes play assignments to determine tactical advantages."""
    
    def __init__(self):
        self.blocking_schemes = self._init_blocking_schemes()
        self.coverage_schemes = self._init_coverage_schemes()
        self.rush_techniques = self._init_rush_techniques()
    
    def analyze_play_matchup(
        self, 
        offensive_play: FootballPlay, 
        defensive_play: FootballPlay
    ) -> PlayAnalysis:
        """
        Perform comprehensive analysis of offensive vs defensive play.
        
        This is where the magic happens - we analyze every assignment
        and technique to find advantages and disadvantages.
        """
        advantages = []
        disadvantages = []
        key_matchups = []
        
        # Analyze blocking vs pass rush
        blocking_analysis = self._analyze_blocking_scheme(offensive_play, defensive_play)
        advantages.extend(blocking_analysis["advantages"])
        disadvantages.extend(blocking_analysis["disadvantages"])
        key_matchups.extend(blocking_analysis["key_matchups"])
        
        # Analyze coverage vs routes
        coverage_analysis = self._analyze_coverage_scheme(offensive_play, defensive_play)
        advantages.extend(coverage_analysis["advantages"])
        disadvantages.extend(coverage_analysis["disadvantages"])
        key_matchups.extend(coverage_analysis["key_matchups"])
        
        # Analyze run fits vs blocking scheme
        if offensive_play.play_type == "run":
            run_analysis = self._analyze_run_scheme(offensive_play, defensive_play)
            advantages.extend(run_analysis["advantages"])
            disadvantages.extend(run_analysis["disadvantages"])
            key_matchups.extend(run_analysis["key_matchups"])
        
        # Analyze motion and pre-snap advantages
        motion_analysis = self._analyze_motion_advantages(offensive_play, defensive_play)
        advantages.extend(motion_analysis["advantages"])
        disadvantages.extend(motion_analysis["disadvantages"])
        
        # Calculate net impact
        net_impact = sum(adv.impact for adv in advantages) + sum(dis.impact for dis in disadvantages)
        
        # Overall confidence based on how many factors we identified
        total_factors = len(advantages) + len(disadvantages)
        confidence = min(1.0, total_factors * 0.2 + 0.4)  # 0.4-1.0 range
        
        scheme_analysis = {
            "offensive_scheme": self._identify_offensive_scheme(offensive_play),
            "defensive_scheme": self._identify_defensive_scheme(defensive_play),
            "blocking_vs_rush": blocking_analysis,
            "coverage_vs_routes": coverage_analysis
        }
        
        return PlayAnalysis(
            advantages=advantages,
            disadvantages=disadvantages,
            net_impact=net_impact,
            key_matchups=key_matchups,
            scheme_analysis=scheme_analysis,
            confidence=confidence
        )
    
    def _analyze_blocking_scheme(self, offense: FootballPlay, defense: FootballPlay) -> Dict[str, Any]:
        """Analyze blocking scheme vs pass rush/run fits."""
        advantages = []
        disadvantages = []
        key_matchups = []
        
        # Get assignments
        off_assignments = {assign.player_position: assign for assign in offense.assignments}
        def_assignments = {assign.player_position: assign for assign in defense.assignments}
        
        # Count rushers vs blockers
        rushers = self._count_rushers(defense)
        blockers = self._count_blockers(offense)
        
        # Basic numbers game
        if blockers > rushers:
            # Cap the advantage - even having extra blockers isn't a guarantee
            impact = min(1, blockers - rushers)  # Reduced from min(2, blockers - rushers)
            advantages.append(PlayMatchupFactor(
                factor_type=TacticalAdvantage.EXTRA_BLOCKER.value,
                impact=impact,
                description=f"Offense has {blockers - rushers} extra blocker(s)",
                details={"blocker_count": blockers, "rusher_count": rushers}
            ))
        elif rushers > blockers:
            # Free rushers are still dangerous but not game-breaking
            impact = max(-2, -(rushers - blockers))  # Reduced from max(-3, -(rushers - blockers))
            disadvantages.append(PlayMatchupFactor(
                factor_type=TacticalDisadvantage.FREE_RUSHER.value,
                impact=impact,
                description=f"Defense has {rushers - blockers} free rusher(s)",
                details={"blocker_count": blockers, "rusher_count": rushers}
            ))
        
        # Analyze specific techniques
        
        # Check for pulling guards (huge advantage on counters/powers)
        pulling_guards = self._find_pulling_guards(offense)
        if pulling_guards:
            impact = 1 if offense.play_type == "run" else 0  # Reduced from 2/1
            if impact > 0:
                advantages.append(PlayMatchupFactor(
                    factor_type=TacticalAdvantage.PULLING_GUARD.value,
                    impact=impact,
                    description=f"{', '.join(pulling_guards)} pulling to create extra gap",
                    details={"pulling_players": pulling_guards}
                ))
        
        # Check for defensive stunts vs protection scheme
        stunts = self._find_stunts(defense)
        if stunts and self._has_basic_protection(offense):
            disadvantages.append(PlayMatchupFactor(
                factor_type=TacticalDisadvantage.STUNTS_VS_PROTECTION.value,
                impact=-1,  # Reduced from -2
                description=f"Defensive stunts ({', '.join(stunts)}) vs basic protection",
                details={"stunts": stunts}
            ))
        
        # Check for trap blocks (guard lets DT through, then traps)
        trap_blocks = self._find_trap_blocks(offense)
        if trap_blocks:
            advantages.append(PlayMatchupFactor(
                factor_type=TacticalAdvantage.TRAP_BLOCK.value,
                impact=1,  # Reduced from 2
                description=f"Trap block by {', '.join(trap_blocks)} creates misdirection",
                details={"trap_blockers": trap_blocks}
            ))
        
        # Check for double teams (power concept indicator)
        double_teams = self._find_double_teams(offense)
        if double_teams:
            impact = 1 if len(double_teams) >= 2 else 0  # Reduced impact
            if impact > 0:
                advantages.append(PlayMatchupFactor(
                    factor_type=TacticalAdvantage.DOUBLE_TEAM.value,
                    impact=impact,
                    description=f"Double team blocks ({len(double_teams)}) create push at point of attack",
                    details={"double_teams": double_teams}
                ))
        
        # Check for crack blocks (WR blocking inside linebacker)
        crack_blocks = self._find_crack_blocks(offense)
        if crack_blocks:
            advantages.append(PlayMatchupFactor(
                factor_type=TacticalAdvantage.CRACK_BLOCK.value,
                impact=1,
                description=f"Crack block by {', '.join(crack_blocks)} on linebacker",
                details={"crack_blockers": crack_blocks}
            ))
        
        return {
            "advantages": advantages,
            "disadvantages": disadvantages,
            "key_matchups": key_matchups,
            "blockers": blockers,
            "rushers": rushers
        }
    
    def _analyze_coverage_scheme(self, offense: FootballPlay, defense: FootballPlay) -> Dict[str, Any]:
        """Analyze coverage vs receiving routes."""
        advantages = []
        disadvantages = []
        key_matchups = []
        
        # Only applicable for pass plays
        if offense.play_type != "pass":
            return {"advantages": [], "disadvantages": [], "key_matchups": []}
        
        # Count receivers vs coverage
        receivers = self._count_receivers(offense)
        coverage_players = self._count_coverage_players(defense)
        
        # Analyze blitzes vs coverage
        blitzers = self._count_blitzers(defense)
        if blitzers > 0:
            # More blitzers = less coverage
            if blitzers >= 2:
                advantages.append(PlayMatchupFactor(
                    factor_type=TacticalAdvantage.OVERLOAD_BLITZ.value,
                    impact=2,
                    description=f"Heavy blitz ({blitzers} rushers) creates coverage holes",
                    details={"blitzer_count": blitzers}
                ))
            
            # But also creates more pressure
            disadvantages.append(PlayMatchupFactor(
                factor_type=TacticalDisadvantage.FREE_RUSHER.value,
                impact=-1,
                description="Blitz creates additional pass rush pressure",
                details={"blitzer_count": blitzers}
            ))
        
        # Check for specific coverage mismatches
        coverage_mismatches = self._find_coverage_mismatches(offense, defense)
        for mismatch in coverage_mismatches:
            advantages.append(mismatch)
        
        return {
            "advantages": advantages,
            "disadvantages": disadvantages,
            "key_matchups": key_matchups
        }
    
    def _analyze_run_scheme(self, offense: FootballPlay, defense: FootballPlay) -> Dict[str, Any]:
        """Analyze run blocking vs run fits."""
        advantages = []
        disadvantages = []
        key_matchups = []
        
        # Analyze gap assignments vs run fits
        run_direction = self._get_run_direction(offense)
        run_fits = self._get_run_fits(defense)
        
        # Power concept analysis
        if self._is_power_concept(offense):
            # Power concept with extra blocker
            advantages.append(PlayMatchupFactor(
                factor_type=TacticalAdvantage.POWER_CONCEPT.value,
                impact=1,  # Reduced from 2
                description="Power running concept with lead blocker and double teams",
                details={"concept": "power"}
            ))
        
        # Trap concept analysis  
        if self._is_trap_concept(offense):
            advantages.append(PlayMatchupFactor(
                factor_type=TacticalAdvantage.TRAP_CONCEPT.value,
                impact=1,  # Reduced from 2
                description="Trap concept with misdirection and deception",
                details={"concept": "trap"}
            ))
        
        # Counter concept analysis  
        if self._is_counter_concept(offense):
            advantages.append(PlayMatchupFactor(
                factor_type=TacticalAdvantage.COUNTER_ACTION.value,
                impact=1,
                description="Counter action misdirects defense",
                details={"concept": "counter"}
            ))
        
        # Check if defense is overloaded to one side
        if run_direction and self._defense_overloaded_opposite(defense, run_direction):
            advantages.append(PlayMatchupFactor(
                factor_type=TacticalAdvantage.SEAL_BLOCK.value,
                impact=2,
                description=f"Defense overloaded away from {run_direction}",
                details={"run_direction": run_direction}
            ))
        
        return {
            "advantages": advantages,
            "disadvantages": disadvantages,
            "key_matchups": key_matchups
        }
    
    def _analyze_motion_advantages(self, offense: FootballPlay, defense: FootballPlay) -> Dict[str, Any]:
        """Analyze pre-snap motion and shifts."""
        advantages = []
        disadvantages = []
        
        # Offensive motion creates confusion
        if offense.motion:
            # Motion can create mismatches or confusion
            motion_type = offense.motion.motion_type
            if motion_type in ["jet", "orbit"]:
                advantages.append(PlayMatchupFactor(
                    factor_type=TacticalAdvantage.MOTION_CONFUSION.value,
                    impact=1,
                    description=f"{motion_type.title()} motion forces defensive adjustments",
                    details={"motion_type": motion_type}
                ))
        
        # Pre-snap shifts
        if offense.pre_snap_shifts:
            shift_count = len(offense.pre_snap_shifts)
            if shift_count >= 2:
                advantages.append(PlayMatchupFactor(
                    factor_type=TacticalAdvantage.SHIFT_ADVANTAGE.value,
                    impact=1,
                    description=f"Multiple pre-snap shifts ({shift_count}) create confusion",
                    details={"shift_count": shift_count}
                ))
        
        return {"advantages": advantages, "disadvantages": disadvantages}
    
    # Helper methods for analysis
    
    def _count_rushers(self, defense: FootballPlay) -> int:
        """Count defensive players assigned to rush."""
        return sum(1 for assign in defense.assignments 
                  if assign.assignment_type == AssignmentType.RUSH or 
                     assign.assignment_type == AssignmentType.BLITZ)
    
    def _count_blockers(self, offense: FootballPlay) -> int:
        """Count offensive players assigned to block."""
        return sum(1 for assign in offense.assignments 
                  if assign.assignment_type in [AssignmentType.RUN_BLOCK, AssignmentType.PASS_BLOCK])
    
    def _count_receivers(self, offense: FootballPlay) -> int:
        """Count offensive players running routes."""
        return sum(1 for assign in offense.assignments 
                  if assign.assignment_type == AssignmentType.ROUTE)
    
    def _count_coverage_players(self, defense: FootballPlay) -> int:
        """Count defensive players in coverage."""
        return sum(1 for assign in defense.assignments 
                  if assign.assignment_type == AssignmentType.COVERAGE)
    
    def _count_blitzers(self, defense: FootballPlay) -> int:
        """Count defensive players blitzing."""
        return sum(1 for assign in defense.assignments 
                  if assign.assignment_type == AssignmentType.BLITZ)
    
    def _find_pulling_guards(self, offense: FootballPlay) -> List[str]:
        """Find guards/tackles that are pulling."""
        pulling = []
        for assign in offense.assignments:
            if assign.assignment_type == AssignmentType.RUN_BLOCK:
                details = assign.details or {}
                # Handle case where details might be a string
                if isinstance(details, str):
                    details = {}
                if details.get("scheme") == "pull":
                    pulling.append(assign.player_position)
        return pulling
    
    def _find_stunts(self, defense: FootballPlay) -> List[str]:
        """Find defensive line stunts."""
        stunts = []
        for assign in defense.assignments:
            if assign.assignment_type == AssignmentType.RUSH:
                details = assign.details or {}
                # Handle case where details might be a string
                if isinstance(details, str):
                    details = {}
                if details.get("technique") == "stunt":
                    stunts.append(assign.player_position)
        return stunts
    
    def _find_crack_blocks(self, offense: FootballPlay) -> List[str]:
        """Find wide receivers assigned to crack block."""
        crack_blockers = []
        for assign in offense.assignments:
            if assign.assignment_type == AssignmentType.RUN_BLOCK:
                details = assign.details or {}
                # Handle case where details might be a string
                if isinstance(details, str):
                    details = {}
                if details.get("technique") == "crack" and assign.player_position.startswith("WR"):
                    crack_blockers.append(assign.player_position)
        return crack_blockers
    
    def _find_trap_blocks(self, offense: FootballPlay) -> List[str]:
        """Find trap blocking schemes."""
        trap_blockers = []
        for assign in offense.assignments:
            if assign.assignment_type == AssignmentType.RUN_BLOCK:
                details = assign.details or {}
                if isinstance(details, str):
                    details = {}
                # Look for trap-specific schemes
                if (details.get("scheme") == "pull" and details.get("technique") == "trap_block") or \
                   (details.get("scheme") == "trap_set" and details.get("technique") == "invite_penetration"):
                    trap_blockers.append(assign.player_position)
        return trap_blockers
    
    def _find_double_teams(self, offense: FootballPlay) -> List[str]:
        """Find double team blocking schemes."""
        double_teams = []
        for assign in offense.assignments:
            if assign.assignment_type == AssignmentType.RUN_BLOCK:
                details = assign.details or {}
                if isinstance(details, str):
                    details = {}
                if details.get("scheme") == "double_team":
                    partner = details.get("partner", "unknown")
                    double_teams.append(f"{assign.player_position}+{partner}")
        return double_teams
    
    def _has_basic_protection(self, offense: FootballPlay) -> bool:
        """Check if offense is using basic protection scheme."""
        # This is simplified - in reality you'd analyze the specific protection calls
        protection_schemes = []
        for assign in offense.assignments:
            if assign.assignment_type == AssignmentType.PASS_BLOCK:
                details = assign.details or {}
                scheme = details.get("scheme", "basic")
                protection_schemes.append(scheme)
        
        # If most blockers are using basic schemes, vulnerable to stunts
        basic_count = sum(1 for scheme in protection_schemes if scheme in ["basic", "big_on_big", "vertical_set"])
        return basic_count > len(protection_schemes) / 2
    
    def _find_coverage_mismatches(self, offense: FootballPlay, defense: FootballPlay) -> List[PlayMatchupFactor]:
        """Find coverage mismatches (speed, size, etc.)."""
        mismatches = []
        
        # This is simplified - in reality you'd analyze specific matchups
        # For now, just look for obvious mismatches like RB vs CB
        
        # Check if RB is running routes vs linebacker coverage
        rb_routes = [assign for assign in offense.assignments 
                    if assign.player_position.startswith("RB") and assign.assignment_type == AssignmentType.ROUTE]
        
        if rb_routes:
            # RB vs LB is generally favorable for offense
            mismatches.append(PlayMatchupFactor(
                factor_type=TacticalAdvantage.MISMATCH.value,
                impact=1,
                description="Running back matched up against linebacker in coverage",
                details={"matchup_type": "speed_mismatch"}
            ))
        
        return mismatches
    
    def _get_run_direction(self, offense: FootballPlay) -> Optional[str]:
        """Determine the primary run direction."""
        for assign in offense.assignments:
            if assign.assignment_type == AssignmentType.RUN_BLOCK and assign.player_position.startswith("RB"):
                return assign.direction
        return None
    
    def _get_run_fits(self, defense: FootballPlay) -> Dict[str, str]:
        """Get defensive run fit assignments."""
        fits = {}
        for assign in defense.assignments:
            if assign.assignment_type == AssignmentType.RUN_FIT:
                details = assign.details or {}
                gap = details.get("gap", "unknown")
                fits[assign.player_position] = gap
        return fits
    
    def _is_power_concept(self, offense: FootballPlay) -> bool:
        """Check if this is a power running concept."""
        # Look for lead blocker + double teams (enhanced for power concept)
        has_lead_blocker = any(assign.assignment_type == AssignmentType.LEAD_BLOCK 
                              for assign in offense.assignments)
        has_double_teams = len(self._find_double_teams(offense)) >= 2
        has_pulling_guard = len(self._find_pulling_guards(offense)) > 0
        return has_lead_blocker and (has_double_teams or has_pulling_guard)
    
    def _is_trap_concept(self, offense: FootballPlay) -> bool:
        """Check if this is a trap running concept."""
        # Look for trap-specific blocking schemes
        trap_indicators = 0
        for assign in offense.assignments:
            if assign.assignment_type == AssignmentType.RUN_BLOCK:
                details = assign.details or {}
                if isinstance(details, str):
                    details = {}
                # Check for trap schemes
                if details.get("technique") == "trap_block":
                    trap_indicators += 1
                elif details.get("technique") == "invite_penetration":
                    trap_indicators += 1
                elif details.get("scheme") == "trap_set":
                    trap_indicators += 1
        return trap_indicators >= 2  # Need both trap block and invite penetration
    
    def _is_counter_concept(self, offense: FootballPlay) -> bool:
        """Check if this is a counter running concept."""
        # Look for counter-specific indicators
        for assign in offense.assignments:
            if assign.assignment_type == AssignmentType.HANDOFF:
                details = assign.details or {}
                if isinstance(details, str):
                    details = {}
                if details.get("fake_direction") or details.get("technique") == "counter_step":
                    return True
        return False
    
    def _defense_overloaded_opposite(self, defense: FootballPlay, run_direction: str) -> bool:
        """Check if defense is overloaded away from run direction."""
        # This is simplified - would need detailed position analysis
        # For now, just return False
        return False
    
    def _identify_offensive_scheme(self, offense: FootballPlay) -> str:
        """Identify the offensive scheme being run."""
        if offense.play_type == "run":
            if self._is_trap_concept(offense):
                return "trap"
            elif self._is_power_concept(offense):
                return "power"
            elif self._is_counter_concept(offense):
                return "counter"
            else:
                return "base_run"
        else:
            # Analyze pass concepts
            return "pass_concept"
    
    def _identify_defensive_scheme(self, defense: FootballPlay) -> str:
        """Identify the defensive scheme being run."""
        blitz_count = self._count_blitzers(defense)
        if blitz_count >= 2:
            return "blitz"
        elif blitz_count == 1:
            return "pressure"
        else:
            return "base_coverage"
    
    def _init_blocking_schemes(self) -> Dict[str, Any]:
        """Initialize blocking scheme knowledge."""
        return {
            "zone": {"strengths": ["speed", "mobility"], "weaknesses": ["power", "stunts"]},
            "power": {"strengths": ["gaps", "physical"], "weaknesses": ["speed", "edges"]},
            "protection": {"strengths": ["time"], "weaknesses": ["blitz", "coverage"]}
        }
    
    def _init_coverage_schemes(self) -> Dict[str, Any]:
        """Initialize coverage scheme knowledge."""
        return {
            "man": {"strengths": ["individual_coverage"], "weaknesses": ["picks", "crossing"]},
            "zone": {"strengths": ["help", "robber"], "weaknesses": ["seams", "levels"]}
        }
    
    def _init_rush_techniques(self) -> Dict[str, Any]:
        """Initialize pass rush technique knowledge."""
        return {
            "speed": {"strengths": ["outside"], "weaknesses": ["power", "inside"]},
            "power": {"strengths": ["inside"], "weaknesses": ["speed", "outside"]},
            "stunt": {"strengths": ["confusion"], "weaknesses": ["time", "communication"]}
        }
