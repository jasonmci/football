#!/usr/bin/env python3
"""
Complete Play Analysis with Defensive Schemes and Player Ratings
Shows how specific defensive play calls interact with player ratings.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from football.enhanced_resolution import (
    EnhancedResolutionEngine,
    PlayerProfile,
    SkillCategory,
)
from football.play_analyzer import PlayAnalysis, PlayMatchupFactor
from football.plays import FootballPlay
from types import SimpleNamespace


def create_offensive_plays():
    """Create offensive plays with player assignments."""
    return {
        "quick_slant": {
            "play": FootballPlay(
                name="quick_slant",
                label="Quick Slant",
                play_type="pass",
                base_formation="Shotgun",
                personnel=["11 Personnel"],
                assignments=[],
            ),
            "key_players": ["QB", "WR1"],
            "route_depth": 5,
        },
        "deep_post": {
            "play": FootballPlay(
                name="deep_post",
                label="Deep Post",
                play_type="pass",
                base_formation="Shotgun",
                personnel=["11 Personnel"],
                assignments=[],
            ),
            "key_players": ["QB", "WR1"],
            "route_depth": 18,
        },
        "power_run": {
            "play": FootballPlay(
                name="power_right",
                label="Power Right",
                play_type="run",
                base_formation="I-formation",
                personnel=["21 Personnel"],
                assignments=[],
            ),
            "key_players": ["RB", "FB"],
            "route_depth": 0,
        },
        "outside_zone": {
            "play": FootballPlay(
                name="outside_zone",
                label="Outside Zone",
                play_type="run",
                base_formation="Shotgun",
                personnel=["11 Personnel"],
                assignments=[],
            ),
            "key_players": ["RB"],
            "route_depth": 0,
        },
    }


def create_defensive_schemes():
    """Create specific defensive schemes with player assignments."""
    return {
        "cover_2": {
            "play": FootballPlay(
                name="cover_2",
                label="Cover-2 Man",
                play_type="defense",
                base_formation="4-3",
                personnel=["Base"],
                assignments=[],
            ),
            "coverage": "Cover-2 with man underneath",
            "pressure": "4-man rush",
            "strength": "Strong vs deep passes",
            "weakness": "Vulnerable to intermediate routes",
            "key_defenders": ["CB1", "FS", "SS"],
        },
        "cover_3": {
            "play": FootballPlay(
                name="cover_3",
                label="Cover-3 Zone",
                play_type="defense",
                base_formation="4-3",
                personnel=["Base"],
                assignments=[],
            ),
            "coverage": "3-deep zone with 4 underneath",
            "pressure": "4-man rush",
            "strength": "Strong vs deep passes and runs",
            "weakness": "Soft underneath coverage",
            "key_defenders": ["CB1", "CB2", "FS"],
        },
        "nickel_blitz": {
            "play": FootballPlay(
                name="nickel_blitz",
                label="Nickel A-Gap Blitz",
                play_type="defense",
                base_formation="Nickel",
                personnel=["Nickel"],
                assignments=[],
            ),
            "coverage": "Cover-1 man with blitzing safety",
            "pressure": "6-man rush (SS blitz)",
            "strength": "Creates pressure and coverage",
            "weakness": "Vulnerable to quick passes",
            "key_defenders": ["CB1", "SS", "MLB"],
        },
        "goal_line": {
            "play": FootballPlay(
                name="goal_line_stack",
                label="Goal Line 6-1",
                play_type="defense",
                base_formation="6-1",
                personnel=["Goal Line"],
                assignments=[],
            ),
            "coverage": "Man coverage with run support",
            "pressure": "6-man front",
            "strength": "Dominant vs power runs",
            "weakness": "Vulnerable to quick passes",
            "key_defenders": ["MLB", "NT", "DE"],
        },
        "prevent": {
            "play": FootballPlay(
                name="prevent",
                label="Prevent Defense",
                play_type="defense",
                base_formation="Dime",
                personnel=["Dime"],
                assignments=[],
            ),
            "coverage": "Cover-4 with deep help",
            "pressure": "3-man rush",
            "strength": "Prevents big plays",
            "weakness": "Gives up underneath",
            "key_defenders": ["CB1", "CB2", "FS", "SS"],
        },
    }


def create_realistic_players():
    """Create realistic NFL-caliber players."""
    return {
        # Elite tier
        "mahomes": PlayerProfile(
            "Patrick Mahomes",
            "QB",
            96,
            {SkillCategory.AWARENESS: 97, SkillCategory.HANDS: 92},
        ),
        "hill": PlayerProfile(
            "Tyreek Hill",
            "WR",
            93,
            {
                SkillCategory.HANDS: 88,
                SkillCategory.ROUTE_RUNNING: 90,
                SkillCategory.SPEED: 99,
                SkillCategory.AGILITY: 95,
            },
        ),
        "henry": PlayerProfile(
            "Derrick Henry",
            "RB",
            91,
            {
                SkillCategory.STRENGTH: 95,
                SkillCategory.SPEED: 88,
                SkillCategory.AGILITY: 78,
            },
        ),
        "ramsey": PlayerProfile(
            "Jalen Ramsey",
            "CB",
            94,
            {SkillCategory.COVERAGE: 96, SkillCategory.TACKLE: 87},
        ),
        "watt": PlayerProfile(
            "T.J. Watt",
            "LB",
            95,
            {SkillCategory.PASS_RUSH: 97, SkillCategory.TACKLE: 88},
        ),
        # Good tier
        "cousins": PlayerProfile(
            "Kirk Cousins",
            "QB",
            83,
            {SkillCategory.AWARENESS: 85, SkillCategory.HANDS: 82},
        ),
        "robinson": PlayerProfile(
            "Allen Robinson",
            "WR",
            82,
            {
                SkillCategory.HANDS: 87,
                SkillCategory.ROUTE_RUNNING: 85,
                SkillCategory.SPEED: 78,
                SkillCategory.AGILITY: 80,
            },
        ),
        "cook": PlayerProfile(
            "Dalvin Cook",
            "RB",
            87,
            {
                SkillCategory.STRENGTH: 79,
                SkillCategory.SPEED: 91,
                SkillCategory.AGILITY: 93,
            },
        ),
        "alexander": PlayerProfile(
            "Jaire Alexander",
            "CB",
            88,
            {SkillCategory.COVERAGE: 90, SkillCategory.TACKLE: 82},
        ),
        # Average tier
        "backup_qb": PlayerProfile(
            "Backup QB",
            "QB",
            74,
            {SkillCategory.AWARENESS: 75, SkillCategory.HANDS: 74},
        ),
        "depth_wr": PlayerProfile(
            "Depth WR",
            "WR",
            71,
            {
                SkillCategory.HANDS: 73,
                SkillCategory.ROUTE_RUNNING: 69,
                SkillCategory.SPEED: 76,
                SkillCategory.AGILITY: 72,
            },
        ),
        "avg_cb": PlayerProfile(
            "Average CB",
            "CB",
            75,
            {SkillCategory.COVERAGE: 76, SkillCategory.TACKLE: 74},
        ),
    }


def analyze_matchup_with_scheme(off_play, def_scheme, players, situation):
    """Analyze how offensive play works against specific defensive scheme."""

    # Create tactical analysis based on scheme matchup
    advantages = []
    disadvantages = []

    if off_play["play"].play_type == "pass":
        route_depth = off_play["route_depth"]

        # Quick passes vs different coverages
        if route_depth <= 6:  # Quick routes
            if "blitz" in def_scheme["play"].name:
                advantages.append(
                    PlayMatchupFactor(
                        "QUICK_RELEASE", +2, "Ball out before blitz arrives"
                    )
                )
            elif "cover_3" in def_scheme["play"].name:
                advantages.append(
                    PlayMatchupFactor("UNDERNEATH_SOFT", +1, "Soft underneath coverage")
                )
            elif "prevent" in def_scheme["play"].name:
                advantages.append(
                    PlayMatchupFactor(
                        "PREVENT_WEAKNESS", +2, "Prevent gives up underneath"
                    )
                )

        # Deep passes vs coverages
        elif route_depth >= 15:  # Deep routes
            if "cover_2" in def_scheme["play"].name:
                disadvantages.append(
                    PlayMatchupFactor("DEEP_COVERAGE", -1, "Cover-2 has deep help")
                )
            elif "prevent" in def_scheme["play"].name:
                disadvantages.append(
                    PlayMatchupFactor("DEEP_HELP", -3, "Prevent designed to stop deep")
                )
            elif "blitz" in def_scheme["play"].name:
                disadvantages.append(
                    PlayMatchupFactor(
                        "PRESSURE_VS_DEEP", -2, "Blitz disrupts deep timing"
                    )
                )

    else:  # Run plays
        if "power" in off_play["play"].name:
            if "goal_line" in def_scheme["play"].name:
                disadvantages.append(
                    PlayMatchupFactor("HEAVY_BOX", -2, "6-man front stops power")
                )
            elif "nickel" in def_scheme["play"].name:
                advantages.append(
                    PlayMatchupFactor("LIGHT_BOX", +2, "Nickel = fewer run defenders")
                )

        elif "zone" in off_play["play"].name:
            if "blitz" in def_scheme["play"].name:
                disadvantages.append(
                    PlayMatchupFactor(
                        "BLITZ_DISRUPTION", -2, "Blitz disrupts zone timing"
                    )
                )
            elif "prevent" in def_scheme["play"].name:
                advantages.append(
                    PlayMatchupFactor("PREVENT_RUN", +3, "Prevent can't stop runs")
                )

    # Calculate net impact
    net_impact = sum(adv.impact for adv in advantages) + sum(
        dis.impact for dis in disadvantages
    )
    net_impact = max(-3, min(3, net_impact))  # Cap at +/-3

    return PlayAnalysis(
        advantages=advantages,
        disadvantages=disadvantages,
        net_impact=net_impact,
        key_matchups=[f"{off_play['play'].label} vs {def_scheme['play'].label}"],
        scheme_analysis={
            "offensive_concept": off_play["play"].name,
            "defensive_concept": def_scheme["play"].name,
            "coverage": def_scheme["coverage"],
            "pressure": def_scheme["pressure"],
        },
        confidence=0.85,
    )


def run_complete_analysis():
    """Run complete analysis showing defensive schemes and player ratings."""

    engine = EnhancedResolutionEngine(seed=42)

    offensive_plays = create_offensive_plays()
    defensive_schemes = create_defensive_schemes()
    players = create_realistic_players()

    print("🏈 COMPLETE DEFENSIVE SCHEME + PLAYER ANALYSIS")
    print("=" * 80)

    # Test key matchups
    test_scenarios = [
        {
            "offense": "quick_slant",
            "player_combo": ("mahomes", "hill"),
            "defenses": ["cover_3", "nickel_blitz", "prevent"],
            "situation": {"down": 3, "distance": 7, "pass_rush_pressure": False},
        },
        {
            "offense": "deep_post",
            "player_combo": ("cousins", "robinson"),
            "defenses": ["cover_2", "cover_3", "prevent"],
            "situation": {"down": 2, "distance": 8, "pass_rush_pressure": False},
        },
        {
            "offense": "power_run",
            "player_combo": ("henry",),
            "defenses": ["cover_3", "nickel_blitz", "goal_line"],
            "situation": {"down": 1, "distance": 10},
        },
    ]

    for scenario in test_scenarios:
        off_play = offensive_plays[scenario["offense"]]

        print(
            f"\n🎯 **{off_play['play'].label}** - {scenario['player_combo'][0].upper()}"
        )
        if len(scenario["player_combo"]) > 1:
            print(
                f"   👥 {players[scenario['player_combo'][0]].name} ➜ {players[scenario['player_combo'][1]].name}"
            )
        else:
            print(f"   👤 {players[scenario['player_combo'][0]].name}")

        print("=" * 60)

        for def_name in scenario["defenses"]:
            def_scheme = defensive_schemes[def_name]

            print(f"\n🛡️  **{def_scheme['play'].label}**")
            print(f"   📋 Coverage: {def_scheme['coverage']}")
            print(f"   🔥 Pressure: {def_scheme['pressure']}")
            print(f"   💪 Strength: {def_scheme['strength']}")
            print(f"   ⚠️  Weakness: {def_scheme['weakness']}")

            # Analyze the matchup
            analysis = analyze_matchup_with_scheme(
                off_play, def_scheme, players, scenario["situation"]
            )

            print(f"   ⚡ Net Advantage: {analysis.net_impact:+d}")

            if analysis.advantages:
                print("   ✅ Offensive Advantages:")
                for adv in analysis.advantages:
                    print(f"      • {adv.description}")

            if analysis.disadvantages:
                print("   ❌ Defensive Advantages:")
                for dis in analysis.disadvantages:
                    print(f"      • {dis.description}")

            # Simulate the play result
            base_result = SimpleNamespace(
                outcome=SimpleNamespace(name="SUCCESS"),
                yards_gained=max(
                    1, off_play.get("route_depth", 4) + analysis.net_impact
                ),
                dice_roll=11,
                total_modifier=analysis.net_impact,
                final_total=11 + analysis.net_impact,
            )

            # Run simulation
            completions = 0
            total_yards = 0
            total_yac = 0
            trials = 15

            for _ in range(trials):
                if off_play["play"].play_type == "pass":
                    qb = players[scenario["player_combo"][0]]
                    wr = players[scenario["player_combo"][1]]
                    cb = players["avg_cb"]  # Use average CB

                    pressure = "blitz" in def_name
                    sit = {"pass_rush_pressure": pressure}

                    result = engine.resolve_pass_play(qb, wr, cb, base_result, sit)

                    if result.completed:
                        completions += 1
                        total_yards += result.yards_gained
                        total_yac += result.yards_after_contact
                else:
                    rb = players[scenario["player_combo"][0]]
                    defenders = [players["avg_cb"]]  # Simplified

                    result = engine.resolve_run_play(rb, [], defenders, base_result, {})
                    completions += 1
                    total_yards += result.yards_gained
                    total_yac += result.yards_after_contact

            if off_play["play"].play_type == "pass":
                completion_rate = (completions / trials) * 100
                avg_yards = total_yards / max(1, completions) if completions > 0 else 0
                avg_yac = total_yac / max(1, completions) if completions > 0 else 0
                print(
                    f"   📊 Result: {completion_rate:.0f}% completion | {avg_yards:.1f} avg yds | {avg_yac:.1f} YAC"
                )
            else:
                avg_yards = total_yards / trials
                avg_yac = total_yac / trials
                print(f"   📊 Result: {avg_yards:.1f} avg yds | {avg_yac:.1f} YAC")

            # Strategic assessment
            if analysis.net_impact >= 2:
                print("   🎯 Assessment: **Strong offensive advantage**")
            elif analysis.net_impact <= -2:
                print("   🛡️  Assessment: **Strong defensive advantage**")
            else:
                print("   ⚖️  Assessment: **Balanced matchup**")


if __name__ == "__main__":
    run_complete_analysis()
