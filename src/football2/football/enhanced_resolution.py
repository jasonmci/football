"""
Enhanced Play Resolution with Player Ratings
Adds player ratings, yards after catch, missed tackles, and incompletions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List, Tuple, Any
import random


class PlayerRating(Enum):
    """Player rating categories."""
    ELITE = "elite"        # 90+ overall
    GOOD = "good"          # 80-89 overall  
    AVERAGE = "average"    # 70-79 overall
    BELOW_AVERAGE = "below_average"  # 60-69 overall
    POOR = "poor"          # <60 overall


class SkillCategory(Enum):
    """Specific skill categories for players."""
    # Offensive skills
    SPEED = "speed"                    # Breakaway ability
    ACCELERATION = "acceleration"      # First step quickness
    AGILITY = "agility"               # Cutting, juking
    STRENGTH = "strength"             # Breaking tackles
    HANDS = "hands"                   # Catching ability
    ROUTE_RUNNING = "route_running"   # Route precision
    AWARENESS = "awareness"           # Football IQ
    
    # Blocking skills
    PASS_BLOCKING = "pass_blocking"   # Pass protection
    RUN_BLOCKING = "run_blocking"     # Run blocking
    
    # Defensive skills
    TACKLE = "tackle"                 # Tackling ability
    COVERAGE = "coverage"             # Pass coverage
    PASS_RUSH = "pass_rush"          # Getting to QB
    RUN_DEFENSE = "run_defense"      # Stopping runs


@dataclass
class PlayerProfile:
    """Individual player ratings and attributes."""
    name: str
    position: str
    overall_rating: int  # 0-99 scale
    
    # Specific skill ratings (0-99 scale)
    skills: Dict[SkillCategory, int] = field(default_factory=dict)
    
    # Physical attributes
    speed: int = 70        # 0-99 scale
    strength: int = 70     # 0-99 scale
    agility: int = 70      # 0-99 scale
    
    # Position-specific traits
    traits: List[str] = field(default_factory=list)  # "clutch", "fumble_prone", etc.
    
    @property
    def rating_tier(self) -> PlayerRating:
        """Get the overall rating tier."""
        if self.overall_rating >= 90:
            return PlayerRating.ELITE
        elif self.overall_rating >= 80:
            return PlayerRating.GOOD
        elif self.overall_rating >= 70:
            return PlayerRating.AVERAGE
        elif self.overall_rating >= 60:
            return PlayerRating.BELOW_AVERAGE
        else:
            return PlayerRating.POOR
    
    def get_skill(self, skill: SkillCategory) -> int:
        """Get a specific skill rating, defaulting to overall if not specified."""
        return self.skills.get(skill, self.overall_rating)


@dataclass 
class PlayExecutionResult:
    """Enhanced result including catch/completion details."""
    # Basic result
    outcome: str  # PlayOutcome
    yards_gained: int
    
    # Execution details
    completed: bool = True              # Was pass completed?
    initial_gain: int = 0              # Yards at catch/handoff
    yards_after_contact: int = 0       # YAC/YAH
    missed_tackles: int = 0            # Broken tackles
    
    # Player involvement
    key_players: List[str] = field(default_factory=list)  # Players who made key plays
    
    # Technical details
    dice_roll: int = 0
    total_modifier: int = 0
    final_total: int = 0
    
    @property
    def description(self) -> str:
        """Generate detailed play description."""
        if not self.completed:
            return f"Incomplete pass - {self.outcome}"
        
        desc = f"{self.yards_gained} yard gain"
        if self.missed_tackles > 0:
            desc += f" ({self.missed_tackles} missed tackle{'s' if self.missed_tackles > 1 else ''})"
        if self.yards_after_contact > 0:
            desc += f" with {self.yards_after_contact} YAC"
        return desc


class EnhancedResolutionEngine:
    """Enhanced resolution engine with player ratings."""
    
    def __init__(self, config=None, seed: Optional[int] = None):
        self.config = config  # Use existing ResolutionConfig
        self.rng = random.Random(seed)
        
        # Rating-based modifiers
        self.rating_modifiers = {
            PlayerRating.ELITE: +2,
            PlayerRating.GOOD: +1, 
            PlayerRating.AVERAGE: 0,
            PlayerRating.BELOW_AVERAGE: -1,
            PlayerRating.POOR: -2
        }
    
    def resolve_pass_play(
        self,
        qb: PlayerProfile,
        receiver: PlayerProfile,
        defender: PlayerProfile,
        base_result: Any,  # Original PlayResult
        situation: Dict[str, Any]
    ) -> PlayExecutionResult:
        """Resolve pass play with player ratings."""
        
        # 1. Determine completion probability
        completion_chance = self._calculate_completion_chance(
            qb, receiver, defender, base_result, situation
        )
        
        # 2. Roll for completion
        completion_roll = self.rng.randint(1, 100)
        completed = completion_roll <= completion_chance
        
        if not completed:
            # Check for interception on incomplete passes
            interception_risk = self._calculate_interception_risk(
                qb, receiver, defender, base_result, situation
            )
            if self.rng.randint(1, 100) <= interception_risk:
                return PlayExecutionResult(
                    outcome="INTERCEPTION",
                    yards_gained=0,
                    completed=False,
                    key_players=[defender.name, qb.name],
                    dice_roll=base_result.dice_roll,
                    total_modifier=base_result.total_modifier,
                    final_total=base_result.final_total
                )
            
            return PlayExecutionResult(
                outcome="INCOMPLETE",
                yards_gained=0,
                completed=False,
                key_players=[defender.name],
                dice_roll=base_result.dice_roll,
                total_modifier=base_result.total_modifier,
                final_total=base_result.final_total
            )
        
        # 3. Calculate initial catch point
        initial_gain = max(0, base_result.yards_gained)
        
        # Check for interception on completed passes (tipped balls, etc.)
        completed_int_risk = self._calculate_completed_pass_interception_risk(
            qb, receiver, defender, initial_gain, situation
        )
        if self.rng.randint(1, 100) <= completed_int_risk:
            return PlayExecutionResult(
                outcome="INTERCEPTION",
                yards_gained=0,
                completed=False,
                key_players=[defender.name, receiver.name],
                dice_roll=base_result.dice_roll,
                total_modifier=base_result.total_modifier,
                final_total=base_result.final_total
            )
        
        # 4. Calculate yards after catch
        yac = self._calculate_yards_after_catch(
            receiver, defender, initial_gain, situation
        )
        
        # 5. Calculate missed tackles
        missed_tackles = self._calculate_missed_tackles(
            receiver, defender, yac
        )
        
        total_yards = initial_gain + yac
        
        return PlayExecutionResult(
            outcome=base_result.outcome.name,
            yards_gained=total_yards,
            completed=True,
            initial_gain=initial_gain,
            yards_after_contact=yac,
            missed_tackles=missed_tackles,
            key_players=[qb.name, receiver.name],
            dice_roll=base_result.dice_roll,
            total_modifier=base_result.total_modifier,
            final_total=base_result.final_total
        )
    
    def resolve_run_play(
        self,
        runner: PlayerProfile,
        blockers: List[PlayerProfile],
        defenders: List[PlayerProfile],
        base_result: Any,  # Original PlayResult
        situation: Dict[str, Any]
    ) -> PlayExecutionResult:
        """Resolve run play with player ratings."""
        
        # 1. Calculate initial yards at handoff/first contact
        initial_gain = max(0, base_result.yards_gained // 2)  # Half comes from scheme
        
        # 2. Calculate yards after contact based on runner vs defenders
        yac = self._calculate_run_after_contact(
            runner, defenders, base_result.yards_gained - initial_gain
        )
        
        # 3. Calculate broken tackles
        missed_tackles = self._calculate_run_missed_tackles(
            runner, defenders, yac
        )
        
        total_yards = initial_gain + yac
        
        # 4. Handle fumbles for powerful runners
        fumble_risk = self._calculate_fumble_risk(runner, defenders, total_yards)
        if self.rng.randint(1, 100) <= fumble_risk:
            return PlayExecutionResult(
                outcome="FUMBLE",
                yards_gained=0,
                completed=False,
                key_players=[runner.name] + [d.name for d in defenders[:1]],
                dice_roll=base_result.dice_roll,
                total_modifier=base_result.total_modifier,
                final_total=base_result.final_total
            )
        
        return PlayExecutionResult(
            outcome=base_result.outcome.name,
            yards_gained=total_yards,
            completed=True,
            initial_gain=initial_gain,
            yards_after_contact=yac,
            missed_tackles=missed_tackles,
            key_players=[runner.name],
            dice_roll=base_result.dice_roll,
            total_modifier=base_result.total_modifier,
            final_total=base_result.final_total
        )
    
    def _calculate_completion_chance(
        self,
        qb: PlayerProfile,
        receiver: PlayerProfile,
        defender: PlayerProfile,
        base_result: Any,
        situation: Dict[str, Any]
    ) -> int:
        """Calculate completion percentage (0-100)."""
        
        # Base completion rate by route type/distance
        base_completion = 65  # Average NFL completion rate
        
        if base_result.yards_gained <= 5:  # Short routes
            base_completion = 80
        elif base_result.yards_gained <= 15:  # Medium routes
            base_completion = 65
        else:  # Deep routes
            base_completion = 45
        
        # Adjust for QB accuracy
        qb_modifier = (qb.overall_rating - 75) // 2  # -10 to +12 range
        
        # Adjust for receiver hands/route running
        wr_hands = receiver.get_skill(SkillCategory.HANDS)
        wr_routes = receiver.get_skill(SkillCategory.ROUTE_RUNNING)
        wr_modifier = ((wr_hands + wr_routes) // 2 - 75) // 2
        
        # Adjust for defender coverage
        def_coverage = defender.get_skill(SkillCategory.COVERAGE)
        def_modifier = -(def_coverage - 75) // 2  # Better coverage = lower completion
        
        # Situation adjustments
        pressure_modifier = 0
        if situation.get("pass_rush_pressure", False):
            pressure_modifier = -15
        
        # Calculate final completion chance
        completion_chance = (
            base_completion + 
            qb_modifier + 
            wr_modifier + 
            def_modifier + 
            pressure_modifier
        )
        
        return max(5, min(95, completion_chance))  # Cap between 5-95%
    
    def _calculate_yards_after_catch(
        self,
        receiver: PlayerProfile,
        defender: PlayerProfile,
        initial_gain: int,
        situation: Dict[str, Any]
    ) -> int:
        """Calculate yards after catch."""
        
        # YAC potential based on route type
        if initial_gain <= 5:  # Short routes have high YAC potential
            base_yac = 3
        elif initial_gain <= 15:  # Medium routes
            base_yac = 2
        else:  # Deep routes typically have less YAC
            base_yac = 1
        
        # Receiver speed/agility impact
        wr_speed = receiver.get_skill(SkillCategory.SPEED)
        wr_agility = receiver.get_skill(SkillCategory.AGILITY)
        wr_factor = ((wr_speed + wr_agility) // 2 - 70) // 10  # -3 to +3
        
        # Defender tackle ability
        def_tackle = defender.get_skill(SkillCategory.TACKLE)
        def_factor = -(def_tackle - 70) // 10  # Better tackle = less YAC
        
        # Roll for YAC
        yac_roll = self.rng.randint(0, base_yac + 2)
        yac = max(0, yac_roll + wr_factor + def_factor)
        
        return yac
    
    def _calculate_missed_tackles(
        self,
        ball_carrier: PlayerProfile,
        defender: PlayerProfile,
        yards_after: int
    ) -> int:
        """Calculate how many tackles were missed."""
        
        if yards_after <= 1:
            return 0
        
        # More YAC generally means more missed tackles
        base_chance = min(yards_after * 10, 40)  # Up to 40% chance
        
        # Ball carrier elusiveness
        bc_agility = ball_carrier.get_skill(SkillCategory.AGILITY)
        bc_factor = (bc_agility - 70) // 10
        
        # Defender tackling
        def_tackle = defender.get_skill(SkillCategory.TACKLE)
        def_factor = -(def_tackle - 70) // 10
        
        missed_chance = base_chance + (bc_factor * 5) + (def_factor * 5)
        
        # Roll for each potential missed tackle
        missed_tackles = 0
        for _ in range(min(3, yards_after // 2)):  # Max 3 missed tackles
            if self.rng.randint(1, 100) <= missed_chance:
                missed_tackles += 1
                missed_chance -= 15  # Each miss makes next one less likely
        
        return missed_tackles
    
    def _calculate_run_after_contact(
        self,
        runner: PlayerProfile,
        defenders: List[PlayerProfile],
        base_yac: int
    ) -> int:
        """Calculate yards after contact for runs."""
        
        if not defenders:
            return max(0, base_yac)
        
        # Runner power/strength
        runner_strength = runner.get_skill(SkillCategory.STRENGTH)
        runner_agility = runner.get_skill(SkillCategory.AGILITY)
        
        # Average defender ability
        avg_tackle = sum(d.get_skill(SkillCategory.TACKLE) for d in defenders) / len(defenders)
        
        # Power vs agility approach
        power_factor = int((runner_strength - avg_tackle) // 10)
        agility_factor = int((runner_agility - avg_tackle) // 10)
        
        # Use better approach
        best_factor = max(power_factor, agility_factor)
        
        return max(0, base_yac + best_factor)
    
    def _calculate_run_missed_tackles(
        self,
        runner: PlayerProfile,
        defenders: List[PlayerProfile],
        yac: int
    ) -> int:
        """Calculate missed tackles on runs."""
        
        if yac <= 0 or not defenders:
            return 0
        
        # Similar to pass YAC missed tackles
        missed_tackles = 0
        for defender in defenders[:2]:  # Max 2 defenders for simplicity
            miss_chance = min(yac * 8, 30)  # Base chance
            
            runner_elusiveness = (runner.get_skill(SkillCategory.AGILITY) - 70) // 10
            def_tackle = (defender.get_skill(SkillCategory.TACKLE) - 70) // 10
            
            miss_chance += (runner_elusiveness * 5) - (def_tackle * 5)
            
            if self.rng.randint(1, 100) <= miss_chance:
                missed_tackles += 1
        
        return missed_tackles
    
    def _calculate_fumble_risk(
        self,
        runner: PlayerProfile,
        defenders: List[PlayerProfile],
        total_yards: int
    ) -> int:
        """Calculate fumble risk percentage."""
        
        base_risk = 1  # 1% base fumble rate
        
        # More yards = slightly more risk (fatigue, more contact)
        if total_yards > 10:
            base_risk += 1
        
        # Runner ball security
        if "secure_hands" in runner.traits:
            base_risk -= 1
        elif "fumble_prone" in runner.traits:
            base_risk += 2
        
        # Defender hit power
        if defenders:
            avg_strength = sum(d.strength for d in defenders) / len(defenders)
            if avg_strength > 85:  # High strength defenders
                base_risk += 1
        
        return max(0, base_risk)

    def _calculate_interception_risk(
        self,
        qb: PlayerProfile,
        receiver: PlayerProfile,
        defender: PlayerProfile,
        base_result: Any,
        situation: Dict[str, Any]
    ) -> int:
        """Calculate interception risk percentage on incomplete passes."""
        
        # Base interception rate for incomplete passes
        base_risk = 8  # 8% of incompletions become interceptions
        
        # QB decision making and accuracy impact
        qb_awareness = qb.get_skill(SkillCategory.AWARENESS)
        if qb_awareness >= 90:  # Elite decision making
            base_risk -= 3
        elif qb_awareness >= 80:  # Good decision making
            base_risk -= 1
        elif qb_awareness < 70:  # Poor decision making
            base_risk += 2
        
        # QB traits
        if "interception_prone" in qb.traits:
            base_risk += 3
        elif "clutch" in qb.traits:
            base_risk -= 1
        
        # Defender ball skills
        def_coverage = defender.get_skill(SkillCategory.COVERAGE)
        def_hands = defender.get_skill(SkillCategory.HANDS)
        avg_def_skill = (def_coverage + def_hands) // 2
        
        if avg_def_skill >= 85:  # Elite ball skills
            base_risk += 2
        elif avg_def_skill >= 75:  # Good ball skills
            base_risk += 1
        elif avg_def_skill < 65:  # Poor ball skills
            base_risk -= 2
        
        # Pressure increases bad decisions
        if situation.get("pass_rush_pressure", False):
            base_risk += 3
        
        # Route difficulty - tighter windows = more interceptions
        if base_result.yards_gained > 15:  # Deep routes
            base_risk += 2
        elif base_result.yards_gained <= 5:  # Short, quick routes
            base_risk -= 1
        
        return max(0, min(25, base_risk))  # Cap at 25% for incomplete passes

    def _calculate_completed_pass_interception_risk(
        self,
        qb: PlayerProfile,
        receiver: PlayerProfile,
        defender: PlayerProfile,
        initial_gain: int,
        situation: Dict[str, Any]
    ) -> int:
        """Calculate interception risk on completed passes (tipped balls, etc.)."""
        
        # Much lower base rate for completed passes
        base_risk = 1  # 1% of completions can become interceptions
        
        # Receiver hands impact (fumbling into INT)
        wr_hands = receiver.get_skill(SkillCategory.HANDS)
        if wr_hands < 70:  # Poor hands can tip passes
            base_risk += 1
        
        # High pressure can cause receiver tips
        if situation.get("pass_rush_pressure", False):
            base_risk += 1
        
        # Defender positioning for tips/deflections
        def_coverage = defender.get_skill(SkillCategory.COVERAGE)
        if def_coverage >= 85:  # Elite coverage can create tips
            base_risk += 1
        
        # Short passes in traffic more likely to be tipped
        if initial_gain <= 5 and len(situation.get("defenders_nearby", [])) > 1:
            base_risk += 1
        
        return max(0, min(5, base_risk))  # Cap at 5% for completed passes


# Example usage and testing functions
def create_sample_players():
    """Create sample players for testing."""
    
    elite_qb = PlayerProfile(
        name="Elite QB",
        position="QB", 
        overall_rating=92,
        skills={
            SkillCategory.AWARENESS: 95,
            SkillCategory.HANDS: 90  # For handoffs
        }
    )
    
    elite_wr = PlayerProfile(
        name="Elite WR",
        position="WR",
        overall_rating=90,
        skills={
            SkillCategory.HANDS: 92,
            SkillCategory.ROUTE_RUNNING: 91,
            SkillCategory.SPEED: 94,
            SkillCategory.AGILITY: 88
        }
    )
    
    average_cb = PlayerProfile(
        name="Average CB", 
        position="CB",
        overall_rating=75,
        skills={
            SkillCategory.COVERAGE: 76,
            SkillCategory.TACKLE: 72
        }
    )
    
    power_rb = PlayerProfile(
        name="Power RB",
        position="RB",
        overall_rating=85,
        skills={
            SkillCategory.STRENGTH: 90,
            SkillCategory.AGILITY: 78,
            SkillCategory.SPEED: 82
        },
        traits=["secure_hands"]
    )
    
    return elite_qb, elite_wr, average_cb, power_rb


if __name__ == "__main__":
    # Example usage
    engine = EnhancedResolutionEngine()
    qb, wr, cb, rb = create_sample_players()
    
    print("🏈 Enhanced Resolution Engine Demo")
    print("=" * 50)
    
    # Mock a base result for testing
    from types import SimpleNamespace
    
    base_result = SimpleNamespace(
        outcome=SimpleNamespace(name="SUCCESS"),
        yards_gained=8,
        dice_roll=12,
        total_modifier=3,
        final_total=15
    )
    
    # Test pass play
    print("\n📡 Pass Play Result:")
    pass_result = engine.resolve_pass_play(
        qb, wr, cb, base_result, {"pass_rush_pressure": False}
    )
    print(f"   {pass_result.description}")
    print(f"   Completed: {pass_result.completed}")
    if pass_result.completed:
        print(f"   Initial gain: {pass_result.initial_gain}")
        print(f"   YAC: {pass_result.yards_after_contact}")
        print(f"   Missed tackles: {pass_result.missed_tackles}")
    
    # Test run play  
    print("\n🏃 Run Play Result:")
    run_result = engine.resolve_run_play(
        rb, [], [cb], base_result, {}
    )
    print(f"   {run_result.description}")
    print(f"   Initial gain: {run_result.initial_gain}")
    print(f"   YAC: {run_result.yards_after_contact}")
    print(f"   Missed tackles: {run_result.missed_tackles}")
