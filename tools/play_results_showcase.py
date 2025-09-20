#!/usr/bin/env python3
"""
Actual Play Results Showcase
Shows detailed play-by-play results with tactical analysis and narratives.
"""

import sys
import os


from football.play_resolution import (
    PlayResolutionEngine,
    create_realistic_config,
)
from football.play_analyzer import PlayAnalysis, PlayMatchupFactor
from football.plays import FootballPlay

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def create_game_plays():
    """Create realistic game situation plays."""
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
            label="Outside Zone Left",
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
        "play_action": FootballPlay(
            name="play_action",
            label="Play Action Deep",
            play_type="pass",
            base_formation="I-formation",
            personnel=["21 Personnel"],
            assignments=[],
        ),
    }


def create_defensive_plays():
    """Create defensive plays."""
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
            label="MLB Blitz",
            play_type="defense",
            base_formation="4-3",
            personnel=["Base"],
            assignments=[],
        ),
        "nickel_coverage": FootballPlay(
            name="nickel_coverage",
            label="Nickel Cover-2",
            play_type="defense",
            base_formation="Nickel",
            personnel=["Nickel"],
            assignments=[],
        ),
    }


def _trap_right_analysis(def_name):
    if def_name == "base_43":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor(
                    "TRAP_CONCEPT", +1, "LG pulls, RG invites DT penetration"
                ),
                PlayMatchupFactor(
                    "MISDIRECTION", +1, "Backfield fake sells power right"
                ),
            ],
            disadvantages=[],
            net_impact=2,
            key_matchups=["LG vs LOLB", "RG vs NT"],
            scheme_analysis={
                "concept": "gap_scheme_misdirection",
                "blocking": "invite_and_trap",
            },
            confidence=0.80,
        )
    elif def_name == "run_blitz":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("BLITZ_BEATER", +2, "MLB blitzes into trap block")
            ],
            disadvantages=[
                PlayMatchupFactor("FAST_PURSUIT", -1, "OLBs flow hard to ball")
            ],
            net_impact=1,
            key_matchups=["Blitzing MLB vs Trap", "RB vs flowing OLBs"],
            scheme_analysis={
                "concept": "trap_vs_blitz",
                "advantage": "scheme_beats_aggression",
            },
            confidence=0.75,
        )
    return None


def _power_right_analysis(def_name):
    if def_name == "base_43":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("DOUBLE_TEAM", +1, "RG+RT vs 3-technique DT"),
                PlayMatchupFactor("LEAD_BLOCKER", +1, "FB leads through B-gap"),
            ],
            disadvantages=[],
            net_impact=2,
            key_matchups=["Double team vs DT", "FB vs MLB"],
            scheme_analysis={
                "concept": "gap_control",
                "blocking": "displacement_physics",
            },
            confidence=0.85,
        )
    elif def_name == "run_blitz":
        return PlayAnalysis(
            advantages=[PlayMatchupFactor("LEAD_BLOCKER", +1, "FB picks up blitzer")],
            disadvantages=[
                PlayMatchupFactor("EXTRA_HAT", -1, "Blitzer adds run defender")
            ],
            net_impact=0,
            key_matchups=["FB vs Blitzing MLB", "RB vs pursuit"],
            scheme_analysis={"concept": "power_vs_blitz", "result": "even_matchup"},
            confidence=0.70,
        )
    return None


def _outside_zone_analysis(def_name):
    if def_name == "nickel_coverage":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("LIGHT_BOX", +2, "Only 6 defenders in box"),
                PlayMatchupFactor(
                    "STRETCH_CONCEPT", +1, "Horizontal stretch creates gaps"
                ),
            ],
            disadvantages=[],
            net_impact=3,
            key_matchups=["OL vs DL", "RB vs Safety"],
            scheme_analysis={
                "concept": "zone_stretch",
                "advantage": "numbers_game",
            },
            confidence=0.85,
        )
    elif def_name == "run_blitz":
        return PlayAnalysis(
            advantages=[],
            disadvantages=[
                PlayMatchupFactor(
                    "BLITZ_DISRUPTION", -2, "MLB blitz disrupts zone timing"
                ),
                PlayMatchupFactor("HARD_PURSUIT", -1, "Defense flows fast outside"),
            ],
            net_impact=-3,
            key_matchups=["OL vs DL + Blitzer", "RB vs fast pursuit"],
            scheme_analysis={
                "concept": "zone_vs_blitz",
                "disadvantage": "timing_disrupted",
            },
            confidence=0.80,
        )
    return None


def _quick_slant_analysis(def_name):
    if def_name == "run_blitz":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("HOT_ROUTE", +2, "Quick release beats blitz timing"),
                PlayMatchupFactor(
                    "VACATED_COVERAGE", +1, "Blitzer leaves hole in coverage"
                ),
            ],
            disadvantages=[],
            net_impact=3,
            key_matchups=["WR vs CB", "QB vs pass rush"],
            scheme_analysis={
                "concept": "timing_vs_pressure",
                "advantage": "chess_match_won",
            },
            confidence=0.90,
        )
    elif def_name == "nickel_coverage":
        return PlayAnalysis(
            advantages=[],
            disadvantages=[
                PlayMatchupFactor("TIGHT_COVERAGE", -1, "Nickel DB in press coverage")
            ],
            net_impact=-1,
            key_matchups=["WR vs Nickel DB", "Route vs Coverage"],
            scheme_analysis={
                "concept": "quick_vs_coverage",
                "result": "defensive_advantage",
            },
            confidence=0.70,
        )
    return None


def _play_action_analysis(def_name):
    if def_name == "base_43":
        return PlayAnalysis(
            advantages=[
                PlayMatchupFactor("PLAY_ACTION", +2, "LBs bite on run fake"),
                PlayMatchupFactor(
                    "DEEP_CONCEPT", +1, "Route combinations stress coverage"
                ),
            ],
            disadvantages=[
                PlayMatchupFactor("SLOW_DEVELOP", -1, "Takes time to develop")
            ],
            net_impact=2,
            key_matchups=["Play fake vs LBs", "Deep routes vs Safeties"],
            scheme_analysis={
                "concept": "misdirection_pass",
                "advantage": "sells_run_well",
            },
            confidence=0.75,
        )
    return None


def create_realistic_analysis(
    off_name: str, def_name: str, situation: dict
) -> PlayAnalysis:
    """Create realistic tactical analysis based on game situation."""

    analysis_map = {
        "trap_right": _trap_right_analysis,
        "power_right": _power_right_analysis,
        "outside_zone": _outside_zone_analysis,
        "quick_slant": _quick_slant_analysis,
        "play_action": _play_action_analysis,
    }

    func = analysis_map.get(off_name)
    if func:
        result = func(def_name)
        if result:
            return result

    # Default neutral
    return PlayAnalysis(
        advantages=[],
        disadvantages=[],
        net_impact=0,
        key_matchups=["Even matchup"],
        scheme_analysis={"concept": "neutral"},
        confidence=0.50,
    )


def _run_play_narrative(offense, result):
    narrative = ""
    if "trap" in offense.name:
        narrative += "   QB hands off to RB on apparent power right...\n"
        narrative += "   But LG pulls behind the line while RG invites penetration!\n"
        if result.yards_gained > 3:
            narrative += "   RB cuts behind the trap block and finds daylight!\n"
        elif result.yards_gained > 0:
            narrative += "   RB follows the pulling guard for a solid gain.\n"
        else:
            narrative += "   Defense doesn't bite on the fake - minimal gain.\n"

    elif "power" in offense.name:
        narrative += "   FB leads through the B-gap as RG and RT double-team!\n"
        if result.yards_gained > 3:
            narrative += "   The double team creates movement, RB bursts through!\n"
        elif result.yards_gained > 0:
            narrative += (
                "   Physical blocking creates enough space for a decent gain.\n"
            )
        else:
            narrative += "   Defense holds strong at the point of attack.\n"

    elif "zone" in offense.name:
        narrative += "   OL zone blocks left as RB reads the defense...\n"
        if result.yards_gained > 3:
            narrative += "   A hole opens up and RB cuts through for good yardage!\n"
        elif result.yards_gained > 0:
            narrative += "   RB finds the crease and gets what's available.\n"
        else:
            narrative += "   Defense strings the play out to the sideline.\n"
    return narrative


def _pass_play_narrative(offense, result):
    narrative = ""
    if "slant" in offense.name:
        narrative += "   Quick 3-step drop, slant route at the sticks...\n"
        if result.yards_gained > 5:
            narrative += "   WR catches in stride and picks up extra yards!\n"
        elif result.yards_gained > 0:
            narrative += "   Quick completion, WR secured the catch.\n"
        else:
            narrative += "   Tight coverage, no room for the receiver.\n"

    elif "action" in offense.name:
        narrative += "   Play action fake freezes the linebackers...\n"
        if result.yards_gained > 8:
            narrative += "   WR breaks free downfield - big completion!\n"
        elif result.yards_gained > 0:
            narrative += "   QB finds his target for a nice gain.\n"
        else:
            narrative += "   Pass rush gets home before routes develop.\n"
    return narrative


def generate_play_narrative(
    offense: FootballPlay,
    defense: FootballPlay,
    result,
    analysis: PlayAnalysis,
    situation: dict,
) -> str:
    """Generate detailed play-by-play narrative."""

    suffix = ["st", "nd", "rd", "th"][min(situation["down"] - 1, 3)]
    down_desc = f"{situation['down']}{suffix} and {situation['distance']}"
    field_desc = f"at the {situation['field_position']}-yard line"

    # Formation setup
    narrative = f"\n{'=' * 60}\n"
    narrative += f"📍 {down_desc}, {field_desc}\n"
    narrative += f"🔥 Offense: {offense.label} ({offense.base_formation})\n"
    narrative += f"🛡️  Defense: {defense.label} ({defense.base_formation})\n"
    narrative += f"⚡ Tactical Advantage: {analysis.net_impact:+d} (Offense)\n\n"

    # Pre-snap analysis
    if analysis.advantages:
        narrative += "🎯 **Pre-Snap Read:**\n"
        for adv in analysis.advantages[:2]:
            narrative += f"   • {adv.description}\n"

    if analysis.disadvantages:
        narrative += "⚠️  **Defensive Strengths:**\n"
        for dis in analysis.disadvantages[:2]:
            narrative += f"   • {dis.description}\n"

    narrative += "\n🏈 **Play Execution:**\n"

    # Generate realistic play narrative based on play type and result
    if offense.play_type == "run":
        narrative += _run_play_narrative(offense, result)
    else:
        narrative += _pass_play_narrative(offense, result)

    # Result summary
    outcome_emoji = {
        "EXPLOSIVE_SUCCESS": "💥",
        "BIG_SUCCESS": "🎯",
        "SUCCESS": "✅",
        "MODERATE_GAIN": "👍",
        "NO_GAIN": "😐",
        "LOSS": "❌",
        "BIG_LOSS": "💀",
        "TURNOVER": "🚨",
    }

    narrative += f"\n{outcome_emoji.get(result.outcome.name, '📊')} **Result:** "

    if result.yards_gained > 0:
        narrative += f"Gain of {result.yards_gained} yards ({result.outcome.name})\n"
    elif result.yards_gained == 0:
        narrative += f"No gain ({result.outcome.name})\n"
    else:
        narrative += (
            f"Loss of {abs(result.yards_gained)} yards ({result.outcome.name})\n"
        )

    # Technical details
    narrative += "\n📊 **Technical:** "
    narrative += f"Dice: {result.dice_roll}, Modifiers: {result.total_modifier:+d}, "
    narrative += f"Final: {result.final_total}\n"

    return narrative


def run_play_results_showcase():
    """Run detailed play results showcase."""

    config = create_realistic_config()
    engine = PlayResolutionEngine(config)

    offensive_plays = create_game_plays()
    defensive_plays = create_defensive_plays()

    # Create realistic game scenarios
    game_scenarios = [
        {
            "description": "Opening Drive - Establishing the Run",
            "plays": [
                (
                    "trap_right",
                    "base_43",
                    {"down": 1, "distance": 10, "field_position": 35},
                ),
                (
                    "power_right",
                    "base_43",
                    {"down": 2, "distance": 7, "field_position": 37},
                ),
                (
                    "outside_zone",
                    "run_blitz",
                    {"down": 3, "distance": 4, "field_position": 40},
                ),
            ],
        },
        {
            "description": "Red Zone Pressure - Short Yardage",
            "plays": [
                (
                    "power_right",
                    "base_43",
                    {"down": 1, "distance": 10, "field_position": 18},
                ),
                (
                    "trap_right",
                    "run_blitz",
                    {"down": 2, "distance": 7, "field_position": 21},
                ),
                (
                    "quick_slant",
                    "nickel_coverage",
                    {"down": 3, "distance": 4, "field_position": 24},
                ),
            ],
        },
        {
            "description": "Two-Minute Drill - Passing Game",
            "plays": [
                (
                    "quick_slant",
                    "run_blitz",
                    {"down": 1, "distance": 10, "field_position": 45},
                ),
                (
                    "play_action",
                    "base_43",
                    {"down": 2, "distance": 6, "field_position": 49},
                ),
                (
                    "outside_zone",
                    "nickel_coverage",
                    {"down": 3, "distance": 3, "field_position": 52},
                ),
            ],
        },
    ]

    print("🏈 ACTUAL PLAY RESULTS SHOWCASE")
    print("=" * 70)
    print("Detailed play-by-play results with tactical analysis")

    for scenario in game_scenarios:
        print(f"\n🎬 **{scenario['description']}**")
        print("=" * 50)

        for play_data in scenario["plays"]:
            off_name, def_name, situation = play_data
            offense = offensive_plays[off_name]
            defense = defensive_plays[def_name]

            # Create tactical analysis
            analysis = create_realistic_analysis(off_name, def_name, situation)

            # Inject analysis into engine
            original_analyze = engine.play_analyzer.analyze_play_matchup
            engine.play_analyzer.analyze_play_matchup = (
                lambda offensive_play, defensive_play: analysis
            )

            # Execute the play
            result = engine.resolve_play(
                offensive_play=offense, defensive_play=defense, situation=situation
            )

            # Restore original analyzer
            engine.play_analyzer.analyze_play_matchup = original_analyze

            # Generate and display narrative
            narrative = generate_play_narrative(
                offense, defense, result, analysis, situation
            )
            print(narrative)

        print("\n" + "🏁" * 25 + " End of Drive Sequence " + "🏁" * 25)


if __name__ == "__main__":
    run_play_results_showcase()
