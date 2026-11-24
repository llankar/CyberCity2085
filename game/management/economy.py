"""Canonical strategic-economy scale for CyberCity 2085.

One ordinary successful mission is the reference unit (roughly 1,500 funds).
Systems import these values so prices do not drift back into incompatible
single-, double- and five-digit economies.
"""

MISSION_BASE_REWARD = 1_200
MISSION_RISK_REWARD = 100

NEODOLLAR_SYMBOL = "₦"
NEW_CAMPAIGN_FUNDS = 1_500
NEW_CAMPAIGN_FREE_RECRUITS = 4


def format_neodollars(amount: int, *, signed: bool = False) -> str:
    """Return the canonical double-barred Neodollar display."""
    spec = "+," if signed else ","
    return f"{NEODOLLAR_SYMBOL}{int(amount):{spec}}"

RECRUIT_PRICE_MULTIPLIER = 50
RECRUIT_PRICE_ROUNDING = 50

WEEKLY_DIRECTIVE_COSTS = {
    "civil_defense": 700,
    "crew_recovery": 500,
    "black_intel": 600,
}

ASSET_ACQUIRE_COSTS = {
    "cat_robot_k9": 5_500,
    "cat_robot_phantom": 4_500,
    "cat_robot_titan_bot": 9_000,
    "cat_armor_mantis": 5_000,
    "cat_armor_aegis": 7_500,
    "cat_armor_titan": 10_000,
}

# Per mission; powerful assets should be a choice, not a negligible surcharge.
ASSET_DEPLOY_COSTS = {
    "light": 150,
    "recon": 120,
    "medium": 250,
    "heavy": 400,
}

