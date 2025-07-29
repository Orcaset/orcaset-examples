from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from orcaset.financial import YF, Accrual, AccrualSeries, AccrualSeriesBase, Period

if TYPE_CHECKING:
    from .model import ApartmentModel


@dataclass
class EffectiveGrossIncome[P: ApartmentModel](AccrualSeriesBase[P]):
    gross_rent: "GrossRent[EffectiveGrossIncome]"
    vacancy: "Vacancy[EffectiveGrossIncome]"
    credit_loss: "CreditLoss[EffectiveGrossIncome]"
    other_income: "OtherIncome[EffectiveGrossIncome]"

    def _accruals(self) -> Iterable[Accrual]:
        yield from self.gross_rent + self.vacancy + self.credit_loss + self.other_income


@dataclass
class GrossRent[P: EffectiveGrossIncome[ApartmentModel]](AccrualSeriesBase[P]):
    """
    Total gross rental revenue equal to the sum of in-place leases and market rent on vacant units.
    Ignores loss to lease.
    """

    def _accruals(self) -> Iterable[Accrual]:
        unit_gross_rent = []  # Collect AccrualSeries of gross rent for each unit
        for unit in self.parent.parent.units:
            # Create a generator that calculates gross rent for each lease period
            gross_rent_accruals = (
                Accrual.cmonthly(
                    Period(lease.start, lease.end),
                    lease.monthly_rent * YF.cmonthly(lease.start, lease.end) * 12,
                )
                for lease in unit
            )

            unit_gross_rent.append(AccrualSeries(gross_rent_accruals))

        yield from sum(unit_gross_rent, start=AccrualSeries([]))


@dataclass
class Vacancy[P: EffectiveGrossIncome[ApartmentModel]](AccrualSeriesBase[P]):
    """Vacancy equal to the sum of market rent on vacant units plus the vacancy rate times occupied rent."""

    vacancy_rate: float

    def _accruals(self) -> Iterable[Accrual]:
        unit_vacancy = []
        for unit in self.parent.parent.units:
            # Create a generator that calculates vacancy for each lease period
            vacancy_accruals = (
                Accrual.cmonthly(
                    Period(lease.start, lease.end),
                    lease.monthly_rent * YF.cmonthly(lease.start, lease.end) * (-12 if lease.vacant else -self.vacancy_rate * 12),
                )
                for lease in unit
            )

            unit_vacancy.append(AccrualSeries(vacancy_accruals))

        yield from sum(unit_vacancy, start=AccrualSeries([]))


@dataclass
class CreditLoss[P: EffectiveGrossIncome[ApartmentModel]](AccrualSeriesBase[P]):
    """Allowance for collections on non-vacant units."""

    pct_rent: float

    def _accruals(self) -> Iterable[Accrual]:
        yield from (self.parent.gross_rent + self.parent.vacancy) * -self.pct_rent


@dataclass
class OtherIncome[P: EffectiveGrossIncome[ApartmentModel]](AccrualSeriesBase[P]):
    """
    Other income not related to leases, e.g., parking fees, laundry income
    calculated as a percent of rent net of vacancy and collection losses.
    """

    pct_net_rent: float

    def _accruals(self) -> Iterable[Accrual]:
        yield from (self.parent.gross_rent + self.parent.vacancy + self.parent.credit_loss) * self.pct_net_rent
