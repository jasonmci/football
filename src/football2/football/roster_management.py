"""
NFL Roster Management System
Manages team rosters and player contracts with season ratings integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json
from pathlib import Path

from season_ratings import PlayerSeasonProfile, SeasonRatingEngine, StatCategory
from enhanced_resolution import PlayerProfile, SkillCategory


class ContractType(Enum):
    """Contract types for players."""
    ROOKIE = "rookie"
    VETERAN = "veteran"
    FRANCHISE_TAG = "franchise_tag"
    TRANSITION_TAG = "transition_tag"
    PRACTICE_SQUAD = "practice_squad"


@dataclass
class PlayerContract:
    """Player contract details."""
    total_value: int  # Total contract value
    years: int  # Contract length
    guaranteed_money: int  # Guaranteed money
    signing_bonus: int  # Signing bonus
    cap_hit: int  # Current year cap hit
    contract_type: ContractType
    can_be_cut: bool = True
    no_trade_clause: bool = False


@dataclass
class TeamRoster:
    """Complete team roster with salary cap management."""
    team_code: str  # e.g., "KC", "TB", "GB"
    team_name: str  # e.g., "Kansas City Chiefs"
    
    # Roster management
    active_roster: List[str] = field(default_factory=list)  # Player IDs
    practice_squad: List[str] = field(default_factory=list)
    injured_reserve: List[str] = field(default_factory=list)
    
    # Financial
    salary_cap: int = 224_800_000  # 2024 salary cap
    total_cap_used: int = 0
    available_cap: int = 0
    
    # Contracts
    player_contracts: Dict[str, PlayerContract] = field(default_factory=dict)
    
    # Depth charts
    depth_charts: Dict[str, List[str]] = field(default_factory=dict)  # Position -> Player IDs
    
    def __post_init__(self):
        """Calculate available cap space."""
        self.calculate_cap_space()
    
    def calculate_cap_space(self):
        """Calculate total cap usage and available space."""
        self.total_cap_used = sum(
            contract.cap_hit for contract in self.player_contracts.values()
        )
        self.available_cap = self.salary_cap - self.total_cap_used
    
    def add_player(self, player_id: str, contract: PlayerContract, roster_type: str = "active"):
        """Add a player to the roster."""
        if roster_type == "active":
            if len(self.active_roster) >= 53:
                raise ValueError("Active roster is full (53 players)")
            self.active_roster.append(player_id)
        elif roster_type == "practice_squad":
            if len(self.practice_squad) >= 16:
                raise ValueError("Practice squad is full (16 players)")
            self.practice_squad.append(player_id)
        elif roster_type == "ir":
            self.injured_reserve.append(player_id)
        
        self.player_contracts[player_id] = contract
        self.calculate_cap_space()
    
    def release_player(self, player_id: str) -> Optional[PlayerContract]:
        """Release a player from the roster."""
        contract = self.player_contracts.pop(player_id, None)
        
        # Remove from all roster lists
        for roster_list in [self.active_roster, self.practice_squad, self.injured_reserve]:
            if player_id in roster_list:
                roster_list.remove(player_id)
        
        # Remove from depth charts
        for position, players in self.depth_charts.items():
            if player_id in players:
                players.remove(player_id)
        
        self.calculate_cap_space()
        return contract
    
    def set_depth_chart(self, position: str, player_ids: List[str]):
        """Set the depth chart for a position."""
        # Validate all players are on active roster
        for player_id in player_ids:
            if player_id not in self.active_roster:
                raise ValueError(f"Player {player_id} not on active roster")
        
        self.depth_charts[position] = player_ids.copy()
    
    def get_starters(self) -> Dict[str, Optional[str]]:
        """Get starting lineup (first player at each position)."""
        return {
            position: players[0] if players else None
            for position, players in self.depth_charts.items()
        }


class RosterManager:
    """Manages rosters for all NFL teams."""
    
    def __init__(self, season: int):
        self.season = season
        self.teams: Dict[str, TeamRoster] = {}
        self.free_agents: List[str] = []  # Player IDs not on any roster
        
        # NFL team data
        self.nfl_teams = {
            "KC": "Kansas City Chiefs",
            "TB": "Tampa Bay Buccaneers", 
            "GB": "Green Bay Packers",
            "BUF": "Buffalo Bills",
            "MIA": "Miami Dolphins",
            "CIN": "Cincinnati Bengals",
            "BAL": "Baltimore Ravens",
            "TEN": "Tennessee Titans",
            "LAC": "Los Angeles Chargers",
            "LV": "Las Vegas Raiders",
            "DEN": "Denver Broncos",
            "IND": "Indianapolis Colts",
            "CLE": "Cleveland Browns",
            "PIT": "Pittsburgh Steelers",
            "HOU": "Houston Texans",
            "JAX": "Jacksonville Jaguars",
            "DAL": "Dallas Cowboys",
            "PHI": "Philadelphia Eagles",
            "NYG": "New York Giants",
            "WAS": "Washington Commanders",
            "MIN": "Minnesota Vikings",
            "DET": "Detroit Lions",
            "CHI": "Chicago Bears",
            "SF": "San Francisco 49ers",
            "LAR": "Los Angeles Rams",
            "SEA": "Seattle Seahawks",
            "ARI": "Arizona Cardinals",
            "ATL": "Atlanta Falcons",
            "CAR": "Carolina Panthers",
            "NO": "New Orleans Saints",
            "NYJ": "New York Jets",
            "NE": "New England Patriots"
        }
        
        # Initialize all team rosters
        for team_code, team_name in self.nfl_teams.items():
            self.teams[team_code] = TeamRoster(team_code, team_name)
    
    def get_team_roster(self, team_code: str) -> Optional[TeamRoster]:
        """Get roster for a specific team."""
        return self.teams.get(team_code.upper())
    
    def trade_player(self, player_id: str, from_team: str, to_team: str, compensation: Optional[Dict[str, Any]] = None):
        """Execute a trade between teams."""
        from_roster = self.get_team_roster(from_team)
        to_roster = self.get_team_roster(to_team)
        
        if not from_roster or not to_roster:
            raise ValueError("Invalid team codes")
        
        # Get player contract
        contract = from_roster.player_contracts.get(player_id)
        if not contract:
            raise ValueError(f"Player {player_id} not found on {from_team} roster")
        
        if contract.no_trade_clause:
            raise ValueError(f"Player {player_id} has no-trade clause")
        
        # Check cap space
        if to_roster.available_cap < contract.cap_hit:
            raise ValueError(f"Insufficient cap space for {to_team}")
        
        # Execute trade
        from_roster.release_player(player_id)
        to_roster.add_player(player_id, contract)
        
        print(f"🔄 Trade completed: {player_id} from {from_team} to {to_team}")
        if compensation:
            print(f"   Compensation: {compensation}")
    
    def sign_free_agent(self, player_id: str, team_code: str, contract: PlayerContract):
        """Sign a free agent to a team."""
        if player_id not in self.free_agents:
            raise ValueError(f"Player {player_id} is not a free agent")
        
        roster = self.get_team_roster(team_code)
        if not roster:
            raise ValueError("Invalid team code")
        
        if roster.available_cap < contract.cap_hit:
            raise ValueError("Insufficient cap space")
        
        roster.add_player(player_id, contract)
        self.free_agents.remove(player_id)
        
        print(f"✍️ Free agent signed: {player_id} to {team_code}")
    
    def release_to_free_agency(self, player_id: str, team_code: str):
        """Release a player to free agency."""
        roster = self.get_team_roster(team_code)
        if not roster:
            raise ValueError("Invalid team code")
        
        contract = roster.release_player(player_id)
        if contract:
            self.free_agents.append(player_id)
            print(f"🚪 Player released: {player_id} from {team_code}")
    
    def get_roster_analysis(self, team_code: str, season_engine: SeasonRatingEngine) -> Dict[str, Any]:
        """Get comprehensive roster analysis including ratings."""
        roster = self.get_team_roster(team_code)
        if not roster:
            return {}
        
        analysis = {
            "team": f"{roster.team_name} ({team_code})",
            "roster_size": len(roster.active_roster),
            "salary_cap": {
                "total_cap": roster.salary_cap,
                "used": roster.total_cap_used,
                "available": roster.available_cap,
                "percentage_used": (roster.total_cap_used / roster.salary_cap) * 100
            },
            "position_groups": {},
            "top_players": [],
            "contract_analysis": {},
            "depth_chart_strength": {}
        }
        
        # Analyze by position
        position_groups = {}
        for player_id in roster.active_roster:
            if player_id in season_engine.players:
                player = season_engine.players[player_id]
                position = player.player_profile.position
                
                if position not in position_groups:
                    position_groups[position] = []
                
                position_groups[position].append({
                    "player_id": player_id,
                    "name": player.player_profile.name,
                    "overall_rating": player.player_profile.overall_rating,
                    "current_rating": self._calculate_current_overall(player),
                    "contract": roster.player_contracts.get(player_id)
                })
        
        # Sort players by rating within each position
        for position, players in position_groups.items():
            players.sort(key=lambda x: x["current_rating"], reverse=True)
            analysis["position_groups"][position] = players
        
        # Find top 5 players overall
        all_players = []
        for players in position_groups.values():
            all_players.extend(players)
        
        analysis["top_players"] = sorted(all_players, key=lambda x: x["current_rating"], reverse=True)[:5]
        
        # Contract analysis
        contract_types = {}
        total_guaranteed = 0
        
        for contract in roster.player_contracts.values():
            contract_type = contract.contract_type.value
            if contract_type not in contract_types:
                contract_types[contract_type] = {"count": 0, "total_value": 0}
            
            contract_types[contract_type]["count"] += 1
            contract_types[contract_type]["total_value"] += contract.cap_hit
            total_guaranteed += contract.guaranteed_money
        
        analysis["contract_analysis"] = {
            "by_type": contract_types,
            "total_guaranteed": total_guaranteed
        }
        
        return analysis
    
    def _calculate_current_overall(self, player: PlayerSeasonProfile) -> int:
        """Calculate current overall rating based on skill changes."""
        base_rating = player.player_profile.overall_rating
        
        # Calculate weighted average of skill changes
        skill_weights = {
            SkillCategory.AWARENESS: 0.15,
            SkillCategory.HANDS: 0.15,
            SkillCategory.SPEED: 0.2,
            SkillCategory.AGILITY: 0.15,
            SkillCategory.STRENGTH: 0.15,
            SkillCategory.COVERAGE: 0.1,
            SkillCategory.TACKLE: 0.1
        }
        
        total_change = 0
        total_weight = 0
        
        for skill, weight in skill_weights.items():
            original = player.player_profile.get_skill(skill)
            current = player.current_ratings.get(skill, original)
            change = current - original
            total_change += change * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_change = total_change / total_weight
            return max(40, min(99, int(base_rating + avg_change)))
        
        return base_rating
    
    def simulate_draft(self, draft_picks: List[Dict[str, Any]], rookie_profiles: List[PlayerProfile]):
        """Simulate a draft with rookie contracts."""
        for i, pick_info in enumerate(draft_picks):
            if i >= len(rookie_profiles):
                break
            
            team_code = pick_info["team"]
            pick_number = pick_info["pick"]
            rookie = rookie_profiles[i]
            
            # Calculate rookie contract based on draft position
            contract_value = self._calculate_rookie_contract(pick_number)
            
            contract = PlayerContract(
                total_value=contract_value["total"],
                years=4,
                guaranteed_money=contract_value["guaranteed"],
                signing_bonus=contract_value["signing_bonus"],
                cap_hit=contract_value["year1_cap"],
                contract_type=ContractType.ROOKIE,
                can_be_cut=False
            )
            
            # Add rookie to team
            player_id = f"{rookie.name}_{team_code}".replace(" ", "_")
            roster = self.get_team_roster(team_code)
            if roster and roster.available_cap >= contract.cap_hit:
                roster.add_player(player_id, contract)
                print(f"🏈 Draft Pick #{pick_number}: {rookie.name} to {team_code}")
    
    def _calculate_rookie_contract(self, pick_number: int) -> Dict[str, int]:
        """Calculate rookie contract values based on draft position."""
        # Simplified rookie contract calculation
        if pick_number == 1:
            return {
                "total": 37_000_000,
                "guaranteed": 24_000_000,
                "signing_bonus": 24_000_000,
                "year1_cap": 9_250_000
            }
        elif pick_number <= 10:
            base = 30_000_000 - (pick_number - 1) * 2_000_000
            return {
                "total": base,
                "guaranteed": int(base * 0.65),
                "signing_bonus": int(base * 0.65),
                "year1_cap": int(base / 4)
            }
        elif pick_number <= 32:
            base = 15_000_000 - (pick_number - 11) * 500_000
            return {
                "total": base,
                "guaranteed": int(base * 0.5),
                "signing_bonus": int(base * 0.5),
                "year1_cap": int(base / 4)
            }
        else:
            base = max(4_000_000, 8_000_000 - (pick_number - 33) * 50_000)
            return {
                "total": base,
                "guaranteed": int(base * 0.3),
                "signing_bonus": int(base * 0.2),
                "year1_cap": int(base / 4)
            }
    
    def export_roster_data(self, filepath: str):
        """Export all roster data to JSON."""
        export_data = {
            "season": self.season,
            "teams": {},
            "free_agents": self.free_agents
        }
        
        for team_code, roster in self.teams.items():
            export_data["teams"][team_code] = {
                "team_name": roster.team_name,
                "active_roster": roster.active_roster,
                "practice_squad": roster.practice_squad,
                "injured_reserve": roster.injured_reserve,
                "salary_cap": roster.salary_cap,
                "total_cap_used": roster.total_cap_used,
                "contracts": {
                    player_id: {
                        "total_value": contract.total_value,
                        "years": contract.years,
                        "guaranteed_money": contract.guaranteed_money,
                        "signing_bonus": contract.signing_bonus,
                        "cap_hit": contract.cap_hit,
                        "contract_type": contract.contract_type.value,
                        "can_be_cut": contract.can_be_cut,
                        "no_trade_clause": contract.no_trade_clause
                    }
                    for player_id, contract in roster.player_contracts.items()
                },
                "depth_charts": roster.depth_charts
            }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)


def create_sample_roster_data():
    """Create sample roster data for testing."""
    manager = RosterManager(2024)
    
    # Sample contracts for key players
    mahomes_contract = PlayerContract(
        total_value=503_000_000,
        years=10,
        guaranteed_money=141_482_000,
        signing_bonus=10_000_000,
        cap_hit=46_800_000,
        contract_type=ContractType.VETERAN,
        no_trade_clause=True
    )
    
    hill_contract = PlayerContract(
        total_value=120_000_000,
        years=4,
        guaranteed_money=72_200_000,
        signing_bonus=22_200_000,
        cap_hit=27_240_000,
        contract_type=ContractType.VETERAN
    )
    
    # Add players to rosters
    kc_roster = manager.get_team_roster("KC")
    mia_roster = manager.get_team_roster("MIA")
    
    if kc_roster:
        kc_roster.add_player("Patrick_Mahomes_KC", mahomes_contract)
        kc_roster.set_depth_chart("QB", ["Patrick_Mahomes_KC"])
    
    if mia_roster:
        mia_roster.add_player("Tyreek_Hill_MIA", hill_contract)
        mia_roster.set_depth_chart("WR", ["Tyreek_Hill_MIA"])
    
    return manager


if __name__ == "__main__":
    print("🏈 NFL Roster Management System Demo")
    print("=" * 50)
    
    manager = create_sample_roster_data()
    
    # Show KC roster summary
    kc_roster = manager.get_team_roster("KC")
    if kc_roster:
        print(f"\n📊 {kc_roster.team_name} Roster:")
        print(f"Active Players: {len(kc_roster.active_roster)}/53")
        print(f"Salary Cap: ${kc_roster.total_cap_used:,} / ${kc_roster.salary_cap:,}")
        print(f"Available: ${kc_roster.available_cap:,}")
        print(f"Cap Usage: {(kc_roster.total_cap_used/kc_roster.salary_cap)*100:.1f}%")
        
        print("\n🏆 Starters:")
        starters = kc_roster.get_starters()
        for position, player_id in starters.items():
            if player_id:
                print(f"  {position}: {player_id}")
