#!/usr/bin/env python3
import sys
import os
import statistics
from football2.football.play_resolution import (
    PlayResolutionEngine,
    create_realistic_config,
)
from football2.football.play_analyzer import PlayAnalysis, PlayMatchupFactor
from football2.football.plays import FootballPlay

"""
Offensive vs Defensive Play Matchup Showcase
Demonstrates how different offensive and defensive strategies clash.
"""


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def create_offensive_plays():
    """Create a variety of offensive plays."""
    return {
        "trap_right": FootballPlay(
            name="trap_right",
            label="Trap Right",
            play_type="run",
            base_formation="I-formation",
            personnel=["I-formation"],
            assignments=[],
        ),
        "power_right": FootballPlay(
            name="power_right",
            label="Power Right",
            play_type="run",
            base_formation="I-formation",
            personnel=["I-formation"],
            assignments=[],
        ),
        "outside_zone": FootballPlay(
            name="outside_zone",
            label="Outside Zone",
            play_type="run",
            base_formation="Shotgun",
            personnel=["11 Personnel"],
            assignments=[],
        ),
        "counter": FootballPlay(
            name="counter",
            label="Counter",
            play_type="run",
            base_formation="Shotgun",
            personnel=["11 Personnel"],
            assignments=[],
        ),
        "quick_slant": FootballPlay(
            name="quick_slant",
            label="Quick Slant",
            play_type="pass",
            base_formation="Shotgun",
            personnel=["11 Personnel"],
            assignments=[],
        ),
        "deep_post": FootballPlay(
            name="deep_post",
            label="Deep Post",
            play_type="pass",
            base_formation="Shotgun",
            personnel=["11 Personnel"],
            assignments=[],
        ),
    }


def create_defensive_plays():
    """Create a variety of defensive plays."""
    return {
        "base_43": FootballPlay(
            name="base_43",
            label="Base 4-3",
            play_type="defense",
            base_formation="4-3",
            personnel=["Base"],
            assignments=[],
        ),
        "run_blitz": FootballPlay(
            name="run_blitz",
            label="Run Blitz",
            play_type="defense",
            base_formation="4-3",
            personnel=["Base"],
            assignments=[],
        ),
        "nickel_coverage": FootballPlay(
            name="nickel_coverage",
            label="Nickel Coverage",
            play_type="defense",
            base_formation="Nickel",
            personnel=["Nickel"],
            assignments=[],
        ),
        "pass_rush": FootballPlay(
            name="pass_rush",
            label="Pass Rush",
            play_type="defense",
            base_formation="4-3",
            personnel=["Base"],
            assignments=[],
        ),
        "goal_line": FootballPlay(
            name="goal_line",
            label="Goal Line Defense",
            play_type="defense",
            base_formation="6-1",
            personnel=["Goal Line"],
            assignments=[],
        ),
    }


def _trap_right_analysis(defense_name: str) -> PlayAnalysis:
    if defense_name == "base_43":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("TRAP_CONCEPT", +1, "Misdirection vs base front"),
                PlayMatchupFactor("PULLING_GUARD", +1, "Guard pulls to create angle"),
            ],
            disadvantages=[],
            net_impact=2,
            key_matchups=["LG vs DT", "RG vs NT"],
            scheme_analysis={"type": "gap_scheme", "advantage": "misdirection"},
            confidence=0.80,
        )
    elif defense_name == "run_blitz":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("TRAP_CONCEPT", +2, "Blitzer runs into trap")
            ],
            disadvantages=[
                PlayMatchupFactor("EXTRA_RUSHER", -1, "Blitzer adds pressure")
            ],
            net_impact=1,
            key_matchups=["Blitzing LB vs Trap"],
            scheme_analysis={"type": "blitz_beater", "advantage": "scheme"},
            confidence=0.75,
        )
    return PlayAnalysis(
        advantages=[],
        disadvantages=[],
        net_impact=0,
        key_matchups=["Balanced matchup"],
        scheme_analysis={"type": "neutral"},
        confidence=0.50,
    )


def _power_right_analysis(defense_name: str) -> PlayAnalysis:
    if defense_name == "base_43":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("POWER_CONCEPT", +1, "Physical advantage at point"),
                PlayMatchupFactor("DOUBLE_TEAM", +1, "Double team displacement"),
            ],
            disadvantages=[],
            net_impact=2,
            key_matchups=["RG+RT vs DT", "FB vs MIKE"],
            scheme_analysis={"type": "power_gap", "advantage": "physicality"},
            confidence=0.85,
        )
    elif defense_name == "goal_line":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("POWER_CONCEPT", +1, "Power vs heavy defense")
            ],
            disadvantages=[
                PlayMatchupFactor("CROWDED_BOX", -2, "Extra defenders in box")
            ],
            net_impact=-1,
            key_matchups=["FB vs Stack"],
            scheme_analysis={"type": "goal_line", "advantage": "defense"},
            confidence=0.70,
        )
    return PlayAnalysis(
        advantages=[],
        disadvantages=[],
        net_impact=0,
        key_matchups=["Balanced matchup"],
        scheme_analysis={"type": "neutral"},
        confidence=0.50,
    )


def _outside_zone_analysis(defense_name: str) -> PlayAnalysis:
    if defense_name == "nickel_coverage":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("ZONE_CONCEPT", +1, "Stretch defense horizontally"),
                PlayMatchupFactor("LIGHTER_BOX", +1, "Nickel = fewer run defenders"),
            ],
            disadvantages=[],
            net_impact=2,
            key_matchups=["OL vs DL", "RB vs Safety"],
            scheme_analysis={"type": "zone_stretch", "advantage": "numbers"},
            confidence=0.80,
        )
    elif defense_name == "run_blitz":
        return PlayAnalysis(
            advantages=[],
            disadvantages=[
                PlayMatchupFactor("EXTRA_RUSHER", -2, "Blitzer disrupts timing"),
                PlayMatchupFactor("FAST_FLOW", -1, "Hard to cut vs aggressive flow"),
            ],
            net_impact=-3,
            key_matchups=["Blitzer vs Cutback"],
            scheme_analysis={"type": "blitz_vs_zone", "advantage": "defense"},
            confidence=0.85,
        )
    return PlayAnalysis(
        advantages=[],
        disadvantages=[],
        net_impact=0,
        key_matchups=["Balanced matchup"],
        scheme_analysis={"type": "neutral"},
        confidence=0.50,
    )


def _quick_slant_analysis(defense_name: str) -> PlayAnalysis:
    if defense_name == "run_blitz":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("QUICK_RELEASE", +2, "Ball out before rush arrives"),
                PlayMatchupFactor("BLITZ_BEATER", +1, "Designed to beat pressure"),
            ],
            disadvantages=[],
            net_impact=3,
            key_matchups=["WR vs Blitzing LB"],
            scheme_analysis={"type": "hot_route", "advantage": "timing"},
            confidence=0.90,
        )
    elif defense_name == "nickel_coverage":
        return PlayAnalysis(
            advantages=[],
            disadvantages=[
                PlayMatchupFactor("TIGHT_COVERAGE", -1, "Nickel DB in tight coverage")
            ],
            net_impact=-1,
            key_matchups=["WR vs Nickel DB"],
            scheme_analysis={
                "type": "coverage_vs_quick",
                "advantage": "slight_defense",
            },
            confidence=0.70,
        )
    return PlayAnalysis(
        advantages=[],
        disadvantages=[],
        net_impact=0,
        key_matchups=["Balanced matchup"],
        scheme_analysis={"type": "neutral"},
        confidence=0.50,
    )


def _deep_post_analysis(defense_name: str) -> PlayAnalysis:
    if defense_name == "nickel_coverage":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("DEEP_ROUTE", +1, "Attacking deep coverage"),
                PlayMatchupFactor("ROUTE_CONCEPT", +1, "Post breaks coverage"),
            ],
            disadvantages=[
                PlayMatchupFactor("COVERAGE_HELP", -1, "Safety help over top")
            ],
            net_impact=1,
            key_matchups=["WR vs CB+Safety"],
            scheme_analysis={"type": "deep_ball", "advantage": "slight_offense"},
            confidence=0.60,
        )
    elif defense_name == "pass_rush":
        return PlayAnalysis(
            advantages=[],
            disadvantages=[
                PlayMatchupFactor("HEAVY_RUSH", -2, "Pass rush disrupts timing"),
                PlayMatchupFactor("DEEP_ROUTE", -1, "Route takes time to develop"),
            ],
            net_impact=-3,
            key_matchups=["OL vs DL", "QB vs Pocket"],
            scheme_analysis={"type": "rush_vs_deep", "advantage": "defense"},
            confidence=0.85,
        )
    return PlayAnalysis(
        advantages=[],
        disadvantages=[],
        net_impact=0,
        key_matchups=["Balanced matchup"],
        scheme_analysis={"type": "neutral"},
        confidence=0.50,
    )


def create_matchup_analysis(offense_name: str, defense_name: str) -> PlayAnalysis:
    """Create realistic tactical analysis for specific matchups."""
    analysis = None
    if offense_name == "trap_right":
        analysis = _trap_right_analysis(defense_name)
    elif offense_name == "power_right":
        analysis = _power_right_analysis(defense_name)
    elif offense_name == "outside_zone":
        analysis = _outside_zone_analysis(defense_name)
    elif offense_name == "quick_slant":
        analysis = _quick_slant_analysis(defense_name)
    elif offense_name == "deep_post":
        analysis = _deep_post_analysis(defense_name)

    if analysis is not None:
        return analysis

    # Default neutral matchup
    return PlayAnalysis(
        advantages=[],
        disadvantages=[],
        net_impact=0,
        key_matchups=["Balanced matchup"],
        scheme_analysis={"type": "neutral"},
        confidence=0.50,
    )


def simulate_and_report_matchup(
    engine,
    offense,
    defense,
    off_name,
    def_name,
    matchup_desc,
    situation,
):
    print(f"\n⚔️  {matchup_desc}")
    print(f"    🔥 {offense.label} vs 🛡️  {defense.label}")

    # Create tactical analysis for this specific matchup
    analysis = create_matchup_analysis(off_name, def_name)

    # Inject analysis into engine
    original_analyze = engine.play_analyzer.analyze_play_matchup
    engine.play_analyzer.analyze_play_matchup = (
        lambda offensive_play, defensive_play: analysis
    )

    results = []
    outcomes = []

    # Run simulations
    for i in range(10):
        try:
            result = engine.resolve_play(
                offensive_play=offense,
                defensive_play=defense,
                situation=situation,
            )
            results.append(result.yards_gained)
            outcomes.append(result.outcome.name)
        except Exception:
            continue

    # Restore original analyzer
    engine.play_analyzer.analyze_play_matchup = original_analyze

    if results:
        avg_yards = statistics.mean(results)
        best_yards = max(results)
        worst_yards = min(results)

        # Count successful outcomes (gain of 1+ yards)
        successful = sum(1 for y in results if y > 0)
        success_rate = (successful / len(results)) * 100

        print(
            f"    📊 Results: {avg_yards:.1f} avg yds ({worst_yards} to {best_yards})"
        )
        print(
            f"    ✅ Success Rate: {success_rate:.0f}% | "
            f"Net Impact: {analysis.net_impact:+d}"
        )

        # Show key tactical factors
        if analysis.advantages:
            advantages_str = ", ".join([f.factor_type for f in analysis.advantages[:2]])
            print(f"    ⚡ Advantages: {advantages_str}")
        if analysis.disadvantages:
            disadvantages_str = ", ".join(
                [f.factor_type for f in analysis.disadvantages[:2]]
            )
            print(f"    ⚠️  Disadvantages: {disadvantages_str}")

        # Strategic assessment
        if analysis.net_impact >= 2:
            print("    🎯 Tactical Assessment: Strong offensive advantage")
        elif analysis.net_impact <= -2:
            print("    🛡️  Tactical Assessment: Strong defensive advantage")
        else:
            print("    ⚖️  Tactical Assessment: Balanced matchup")

    print()  # Extra spacing between matchups


def run_matchup_showcase():
    """Run comprehensive matchup showcase."""

    config = create_realistic_config()
    engine = PlayResolutionEngine(config)

    offensive_plays = create_offensive_plays()
    defensive_plays = create_defensive_plays()

    # Define interesting matchup scenarios
    scenarios = [
        ("1st & 10 - Midfield", {"down": 1, "distance": 10, "field_position": 50}),
        ("3rd & 2 - Red Zone", {"down": 3, "distance": 2, "field_position": 15}),
        ("2nd & 8 - Own 20", {"down": 2, "distance": 8, "field_position": 20}),
    ]

    # Key matchups to highlight
    key_matchups = [
        ("trap_right", "base_43", "Classic trap vs base defense"),
        ("trap_right", "run_blitz", "Trap vs aggressive run defense"),
        ("power_right", "base_43", "Power vs balanced front"),
        ("power_right", "goal_line", "Power vs goal line stack"),
        ("outside_zone", "nickel_coverage", "Zone vs spread defense"),
        ("outside_zone", "run_blitz", "Zone vs run blitz"),
        ("quick_slant", "run_blitz", "Hot route vs blitz"),
        ("quick_slant", "nickel_coverage", "Quick pass vs coverage"),
        ("deep_post", "nickel_coverage", "Deep ball vs coverage"),
        ("deep_post", "pass_rush", "Deep route vs pass rush"),
    ]

    print("🏈 OFFENSIVE vs DEFENSIVE PLAY MATCHUPS")
    print("=" * 70)

    for scenario_name, situation in scenarios:
        print(f"\n🏟️  {scenario_name}")
        print("=" * 50)

        for off_name, def_name, matchup_desc in key_matchups:
            offense = offensive_plays[off_name]
            defense = defensive_plays[def_name]
            simulate_and_report_matchup(
                engine,
                offense,
                defense,
                off_name,
                def_name,
                matchup_desc,
                situation,
            )


if __name__ == "__main__":
    run_matchup_showcase()
