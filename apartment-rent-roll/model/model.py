from dataclasses import dataclass
from orcaset import Node
from typing import Self

from .unit import Unit
from .income import EffectiveGrossIncome


@dataclass
class ApartmentModel(Node[None]):
    market: str
    units: "list[Unit]"
    egi: "EffectiveGrossIncome[Self]"


if __name__ == "__main__":
    from orcaset import NodeDescriptor

    print(NodeDescriptor.describe(ApartmentModel).pretty(indent=2))
