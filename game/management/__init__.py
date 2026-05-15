"""Management-phase domain modules."""

from .equipment import AgentLoadout, Armor, EquipmentItem, Weapon
from .funds import (
    CorporateFunds,
    FundsLedger,
    FundsTransaction,
    calculate_mission_fund_reward,
    default_mission_fund_distribution,
)

__all__ = [
    "AgentLoadout",
    "Armor",
    "EquipmentItem",
    "Weapon",
    "CorporateFunds",
    "FundsLedger",
    "FundsTransaction",
    "calculate_mission_fund_reward",
    "default_mission_fund_distribution",
]
