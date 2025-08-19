from dataclasses import dataclass

from orcaset import Node

from .balance_sheet import BalanceSheet
from .cash_flow import CashFlow
from .footnotes import Footnotes
from .income import NetIncome


@dataclass
class Traeger[P = None](Node[P]):
    income: "NetIncome[Traeger]"
    balance_sheet: "BalanceSheet[Traeger]"
    cash_flow: "CashFlow[Traeger]"
    footnotes: "Footnotes[Traeger]"


if __name__ == "__main__":
    from orcaset import NodeDescriptor

    print(NodeDescriptor.describe(Traeger).pretty(2))
