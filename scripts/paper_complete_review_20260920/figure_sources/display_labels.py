"""Reader-facing labels for the paper figures.

The dictionaries deliberately keep the frozen data keys out of plotted text.  Figure
builders may continue to use the keys for lookup, but every label that reaches a
PNG/PDF should come from this module or be written in full at the call site.
"""

CONSTRUCTION_LABELS = {
    "A1": "Dual-encoder baseline",
    "DUP": "Duplicate-branch control",
    "TRI": "Equal-weight replacement",
    "BAL": "Balanced replacement",
}

ENCODER_LABELS = {
    "B": "DINOv2-B/14",
    "C": "AnomalyCLIP visual",
    "S": "DINOv2-S/14",
    "D": "WideResNet50-2",
    "E1": "DINO ViT-S/8",
    "E2": "ConvNeXt-Tiny",
    "E3": "Swin-Tiny",
}

MATCHING_RULE_LABELS = {
    "J": "Joint matching",
    "L": "Independent matching",
}

INTERACTION_LABELS = {
    "I_TRI": "Equal-weight replacement interaction",
    "I_BAL": "Balanced replacement interaction",
}

# These are intentionally two-line labels.  "Baseline" is a reader-facing name;
# the nearby legend/caption expands it to Dual-encoder baseline.
BASELINE_RULE_LABELS = {
    "J": "Baseline\nJoint matching",
    "L": "Baseline\nIndependent matching",
}

FIG7_METHOD_LABELS = {
    "controlled_A1_J": BASELINE_RULE_LABELS["J"],
    "controlled_A1_L": BASELINE_RULE_LABELS["L"],
    "anomalydino_canvas": "AnomalyDINO\ncanvas",
    "anomalydino_canvas_rotation": "AnomalyDINO\ncanvas + rotation",
    "PatchCore_native_local128": "PatchCore\nnative 128",
    "PatchCore_native_official224": "PatchCore\nofficial 224",
}


def formula_subscript(construction: str, rule: str) -> str:
    """Return a descriptive upright subscript for E/I formulas."""
    construction_word = {
        "TRI": "Equal",
        "BAL": "Balanced",
    }[construction]
    # J/L remain mathematical rule indices; reader-facing prose uses the full
    # Joint matching / Independent matching names elsewhere.
    rule_word = {"J": "J", "L": "L"}[rule]
    return f"{construction_word},{rule_word}"
