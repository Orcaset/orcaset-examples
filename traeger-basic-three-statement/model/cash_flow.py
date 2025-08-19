from dataclasses import dataclass
from itertools import pairwise
from typing import TYPE_CHECKING, Iterable

from orcaset.financial import Payment, PaymentSeriesBase

if TYPE_CHECKING:
    from .model import Traeger


@dataclass
class CashFlow[P: Traeger = Traeger](PaymentSeriesBase[P]):
    operating: "OperatingActivities[CashFlow]"
    investing: "InvestingActivities[CashFlow]"
    financing: "FinancingActivities[CashFlow]"

    def _payments(self) -> Iterable[Payment]:
        yield from self.operating + self.investing + self.financing


@dataclass
class OperatingActivities[P: CashFlow = CashFlow](PaymentSeriesBase[P]):
    net_income: "NetIncome[OperatingActivities]"
    depreciation: "Depreciation[OperatingActivities]"
    intangible_amortization: "IntangibleAmortization[OperatingActivities]"
    changes_in_working_capital: "ChangesInWorkingCapital[OperatingActivities]"

    def _payments(self) -> Iterable[Payment]:
        yield from (
            self.net_income
            + self.depreciation
            + self.intangible_amortization
            + self.changes_in_working_capital
        )


@dataclass
class NetIncome[P: OperatingActivities = OperatingActivities](PaymentSeriesBase[P]):
    def _payments(self) -> Iterable[Payment]:
        yield from (Payment(acc.period.end, acc.value) for acc in self.parent.parent.parent.income)


@dataclass
class Depreciation[P: OperatingActivities = OperatingActivities](PaymentSeriesBase[P]):
    def _payments(self) -> Iterable[Payment]:
        yield from (
            Payment(acc.period.end, -acc.value)
            for acc in self.parent.parent.parent.footnotes.depreciation
        )


@dataclass
class IntangibleAmortization[P: OperatingActivities = OperatingActivities](PaymentSeriesBase[P]):
    def _payments(self) -> Iterable[Payment]:
        yield from (
            Payment(acc.period.end, acc.value)
            for acc in self.parent.parent.parent.income.pretax_income.operating_income.operating_expenses.amort_of_intangibles
        )


@dataclass
class ChangesInWorkingCapital[P: OperatingActivities = OperatingActivities](PaymentSeriesBase[P]):
    def _payments(self) -> Iterable[Payment]:
        assets = self.parent.parent.parent.balance_sheet.assets
        liabilities = self.parent.parent.parent.balance_sheet.liabilities
        working_capital = (
            liabilities.accounts_payable
            + liabilities.accrued_expenses
            + liabilities.other_current_liabilities
            + -(assets.receivables + assets.inventory + assets.other_current_assets)
        )

        for bal1, bal2 in pairwise(working_capital):
            yield Payment(bal2.date, bal2.value - bal1.value)


@dataclass
class InvestingActivities[P: CashFlow = CashFlow](PaymentSeriesBase[P]):
    capital_expenditures: "CapitalExpenditures[InvestingActivities]"

    def _payments(self) -> Iterable[Payment]:
        yield from self.capital_expenditures


@dataclass
class CapitalExpenditures[P: InvestingActivities = InvestingActivities](PaymentSeriesBase[P]):
    def _payments(self) -> Iterable[Payment]:
        yield from self.parent.parent.parent.footnotes.capital_expenditures


@dataclass
class FinancingActivities[P: CashFlow = CashFlow](PaymentSeriesBase[P]):
    long_term_debt: "LongTermDebt[FinancingActivities]"
    revolver: "Revolver[FinancingActivities]"

    def _payments(self) -> Iterable[Payment]:
        yield from self.long_term_debt + self.revolver


@dataclass
class LongTermDebt[P: FinancingActivities = FinancingActivities](PaymentSeriesBase[P]):
    def _payments(self) -> Iterable[Payment]:
        for bal1, bal2 in pairwise(
            self.parent.parent.parent.balance_sheet.liabilities.long_term_debt
        ):
            yield Payment(bal2.date, bal2.value - bal1.value)


@dataclass
class Revolver[P: FinancingActivities = FinancingActivities](PaymentSeriesBase[P]):

    def _payments(self) -> Iterable[Payment]:
        for bal1, bal2 in pairwise(self.parent.parent.parent.balance_sheet.liabilities.revolver):
            yield Payment(bal2.date, bal2.value - bal1.value)


print("NOTE: Historical cash flows estimated from historical income and balance sheet.")


if __name__ == "__main__":
    from orcaset import NodeDescriptor

    print(NodeDescriptor.describe(CashFlow).pretty(2))
