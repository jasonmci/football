PLAY_O = ["inside_run", "outside_run", "short_pass", "deep_pass", "screen"]
PLAY_D = ["base", "run_commit", "blitz", "short_shell", "deep_shell"]

BASE = {
    ("inside_run", "base"): 0,
    ("inside_run", "run_commit"): -2,
    ("inside_run", "blitz"): -1,
    ("inside_run", "short_shell"): +1,
    ("inside_run", "deep_shell"): +2,
    ("outside_run", "base"): 0,
    ("outside_run", "run_commit"): -2,
    ("outside_run", "blitz"): -1,
    ("outside_run", "short_shell"): +1,
    ("outside_run", "deep_shell"): +2,
    ("short_pass", "base"): 0,
    ("short_pass", "run_commit"): +2,
    ("short_pass", "blitz"): -2,  # pressure hurts short game here
    ("short_pass", "short_shell"): -1,
    ("short_pass", "deep_shell"): +1,
    ("deep_pass", "base"): +1,
    ("deep_pass", "run_commit"): +2,
    ("deep_pass", "blitz"): -1,  # risk/reward vs blitz
    ("deep_pass", "short_shell"): +1,
    ("deep_pass", "deep_shell"): -2,
    ("screen", "base"): +1,
    ("screen", "run_commit"): 0,
    ("screen", "blitz"): +3,  # classic screen vs blitz win
    ("screen", "short_shell"): -1,
    ("screen", "deep_shell"): 0,
}
