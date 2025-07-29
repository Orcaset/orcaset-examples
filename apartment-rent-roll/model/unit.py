from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Generator, List, Literal

from orcaset import Node, cached_generator

from .lease import Lease

if TYPE_CHECKING:
    from .model import ApartmentModel


@dataclass
class Units[P: ApartmentModel](Node[P]):
    units: list[Unit]

    def __post_init__(self):
        for unit in self.units:
            unit.parent = self

    def __iter__(self):
        yield from iter(self.units)

    def __len__(self):
        return len(self.units)


@dataclass
class Unit[P: Units](Node[P]):
    """
    Class that is iterable over `Lease` objects for a specific unit.

    Attributes:
        unit: Unique identifier for the unit.
        unit_type: Type of the unit (e.g., "studio", "1br", "2br").
        initial_lease: The initial lease for the unit.
        get_next_lease: A callable that generates the next lease based on the current unit ID
                      and the list of previous leases.
    """

    unit: str
    unit_type: Literal["studio", "1br", "2br"]
    initial_lease: Lease
    get_next_lease: Callable[[Unit, List[Lease]], Lease]

    @cached_generator
    def __iter__(self) -> Generator[Lease, None, None]:
        leases = [self.initial_lease]
        yield self.initial_lease

        while True:
            next_lease = self.get_next_lease(self, leases)
            leases.append(next_lease)
            yield next_lease
