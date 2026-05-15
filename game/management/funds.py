"""Small corporate funds ledger for management-phase spending.

The ledger is intentionally narrow: it tracks the cash the corporation can
spend right now, aggregate income/expenses, and the short transaction history
that gives those numbers a story trail.
"""

from __future__ import annotations

from dataclasses import dataclass, field

MISSION_FUND_CATEGORIES = (
    "agent_pay_morale",
    "research",
    "equipment",
    "robot_power_armor_maintenance",
    "corporate_reserves",
)

DEFAULT_MISSION_FUND_SPLIT = {
    "agent_pay_morale": 25,
    "research": 25,
    "equipment": 20,
    "robot_power_armor_maintenance": 15,
    "corporate_reserves": 15,
}


@dataclass(frozen=True)
class FundsTransaction:
    """One income or spending entry in the corporate ledger."""

    kind: str
    amount: int
    source: str
    note: str = ""
    balance_after: int = 0

    def to_dict(self) -> dict:
        """Serialize the transaction for save files."""
        return {
            "kind": self.kind,
            "amount": self.amount,
            "source": self.source,
            "note": self.note,
            "balance_after": self.balance_after,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FundsTransaction":
        """Restore a transaction from save data."""
        return cls(
            kind=str(data.get("kind", "income")),
            amount=int(data.get("amount", 0)),
            source=str(data.get("source", "legacy")),
            note=str(data.get("note", "")),
            balance_after=int(data.get("balance_after", 0)),
        )


@dataclass
class CorporateFunds:
    """Track available corporate cash and its transaction history."""

    current_funds: int = 0
    income: int = 0
    expenses: int = 0
    transaction_history: list[FundsTransaction] = field(default_factory=list)

    @property
    def available_funds(self) -> int:
        """Return the cash available for immediate management decisions."""
        return self.current_funds

    def can_afford(self, amount: int) -> bool:
        """Return whether an amount can be spent without overdrafting."""
        return amount >= 0 and self.current_funds >= amount

    def add_funds(self, amount: int, source: str, note: str = "") -> bool:
        """Record income from a named source."""
        if amount <= 0:
            return False
        self.current_funds += amount
        self.income += amount
        self.transaction_history.append(
            FundsTransaction("income", amount, source, note, self.current_funds)
        )
        return True

    def spend_funds(self, amount: int, sink: str, note: str = "") -> bool:
        """Spend funds atomically when the ledger can afford the amount."""
        if amount <= 0 or not self.can_afford(amount):
            return False
        self.current_funds -= amount
        self.expenses += amount
        self.transaction_history.append(
            FundsTransaction("expense", amount, sink, note, self.current_funds)
        )
        return True

    def to_dict(self) -> dict:
        """Serialize the ledger for save files."""
        return {
            "current_funds": self.current_funds,
            "income": self.income,
            "expenses": self.expenses,
            "transaction_history": [
                transaction.to_dict() for transaction in self.transaction_history
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CorporateFunds":
        """Restore a ledger from save data."""
        return cls(
            current_funds=int(data.get("current_funds", 0)),
            income=int(data.get("income", 0)),
            expenses=int(data.get("expenses", 0)),
            transaction_history=[
                FundsTransaction.from_dict(transaction)
                for transaction in data.get("transaction_history", [])
            ],
        )


def calculate_mission_fund_reward(mission: object | None, victory: bool) -> int:
    """Return the cash payout for a resolved mission."""
    if not victory or mission is None:
        return 0
    return max(0, int(getattr(mission, "fund_reward", 0)))


def default_mission_fund_distribution(amount: int) -> dict[str, int]:
    """Split a payout across small post-mission allocation categories."""
    amount = max(0, int(amount))
    distribution = {key: 0 for key in MISSION_FUND_CATEGORIES}
    if amount <= 0:
        return distribution

    allocated = 0
    for key in MISSION_FUND_CATEGORIES:
        if key == "corporate_reserves":
            continue
        share = amount * DEFAULT_MISSION_FUND_SPLIT[key] // 100
        distribution[key] = share
        allocated += share
    distribution["corporate_reserves"] = amount - allocated
    return distribution


FundsLedger = CorporateFunds
