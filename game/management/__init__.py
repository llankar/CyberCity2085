"""Management-phase domain modules."""

from .corporation import CorporationFinance
from .equipment import AgentLoadout, Armor, EquipmentItem, Weapon
from .funds import (
    CorporateFunds,
    FundsLedger,
    FundsTransaction,
    calculate_mission_fund_reward,
    default_mission_fund_distribution,
)

__all__ = [
    "CorporationFinance",
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
