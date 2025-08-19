from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Iterable

from dateutil.relativedelta import relativedelta
from orcaset import yield_and_return
from orcaset.financial import Balance, BalanceSeries, BalanceSeriesBase, Period

if TYPE_CHECKING:
    from .model import Traeger


@dataclass
class BalanceSheet[P: Traeger = Traeger](BalanceSeriesBase[P]):
    assets: "Assets[BalanceSheet]"
    liabilities: "Liabilities[BalanceSheet]"
    equity: "Equity[BalanceSheet]"

    def _balances(self) -> Iterable[Balance]:
        yield from self.assets + -(self.liabilities + self.equity)


# ASSETS
@dataclass
class Assets[P: BalanceSheet = BalanceSheet](BalanceSeriesBase[P]):
    cash: "Cash[Assets]"
    receivables: "Receivables[Assets]"
    inventory: "Inventory[Assets]"
    other_current_assets: "OtherCurrentAssets[Assets]"
    ppe: "PropertyPlantEquipment[Assets]"
    intangible_assets: "IntangibleAssets[Assets]"
    other_non_current_assets: "OtherNonCurrentAssets[Assets]"

    def _balances(self) -> Iterable[Balance]:
        yield from (
            self.cash
            + self.receivables
            + self.inventory
            + self.other_current_assets
            + self.ppe
            + self.intangible_assets
            + self.other_non_current_assets
        )


@dataclass
class Cash[P: Assets = Assets](BalanceSeriesBase[P]):
    historical: "BalanceSeries[Cash]"

    def _balances(self) -> Iterable[Balance]:
        bal = yield from yield_and_return(self.historical)

        for pmt in (
            self.parent.parent.parent.footnotes.cash_flow_before_revolver
            + self.parent.parent.parent.footnotes.net_revolver_draws
        ).after(bal.date):
            bal = Balance(pmt.date, lambda b=bal, p=pmt: b.value + p.value)
            yield bal


@dataclass
class Receivables[P: Assets = Assets](BalanceSeriesBase[P]):
    historical: "BalanceSeries[Receivables]"
    pct_revenue: float

    def _balances(self) -> Iterable[Balance]:
        last_bal = yield from yield_and_return(self.historical)

        for revenue in self.parent.parent.parent.income.pretax_income.operating_income.gross_profit.revenue.after(
            last_bal.date
        ):
            yield Balance(revenue.period.end, revenue.value * self.pct_revenue)


@dataclass
class Inventory[P: Assets = Assets](BalanceSeriesBase[P]):
    historical: "BalanceSeries[Inventory]"
    pct_cost_of_revenue: float

    def _balances(self) -> Iterable[Balance]:
        last_bal = yield from yield_and_return(self.historical)

        for cost in self.parent.parent.parent.income.pretax_income.operating_income.gross_profit.cost_of_revenue.after(
            last_bal.date
        ):
            yield Balance(cost.period.end, cost.value * self.pct_cost_of_revenue)


@dataclass
class OtherCurrentAssets[P: Assets = Assets](BalanceSeriesBase[P]):
    historical: "BalanceSeries[OtherCurrentAssets]"
    pct_inventory: float

    def _balances(self) -> Iterable[Balance]:
        last_bal = yield from yield_and_return(self.historical)

        for inventory_bal in self.parent.inventory.after(last_bal.date):
            yield Balance(inventory_bal.date, inventory_bal.value * self.pct_inventory)


@dataclass
class PropertyPlantEquipment[P: Assets = Assets](BalanceSeriesBase[P]):
    historical: "BalanceSeries[PropertyPlantEquipment]"

    def _balances(self) -> Iterable[Balance]:
        bal = yield from yield_and_return(self.historical)

        for period in Period.series(bal.date, relativedelta(months=3, day=31)):
            bal = Balance(
                period.end,
                lambda b=bal, p=period: (
                    b.value
                    + self.parent.parent.parent.footnotes.depreciation.accrue(*p)
                    - self.parent.parent.parent.footnotes.capital_expenditures.over(*p)
                ),
            )
            yield bal


@dataclass
class IntangibleAssets[P: Assets = Assets](BalanceSeriesBase[P]):
    total_cost: "TotalCost[IntangibleAssets]"
    accumulated_amortization: "AccumulatedAmortization[IntangibleAssets]"

    def _balances(self) -> Iterable[Balance]:
        yield from self.total_cost + self.accumulated_amortization


@dataclass
class TotalCost[P: IntangibleAssets = IntangibleAssets](BalanceSeriesBase[P]):
    """
    Total unamortized cost of intangible assets. Assumes no future acquisitions or
    other events that would increase total costs (zero future increases).
    """

    historical: "BalanceSeries[TotalCost]"

    def _balances(self) -> Iterable[Balance]:
        yield from yield_and_return(self.historical)


@dataclass
class AccumulatedAmortization[P: IntangibleAssets = IntangibleAssets](BalanceSeriesBase[P]):
    historical: "BalanceSeries[AccumulatedAmortization]"

    def _balances(self) -> Iterable[Balance]:
        bal = Balance(date.min, 0)
        for bal in self.historical:
            yield bal * 0

        for acc in self.parent.parent.parent.parent.income.pretax_income.operating_income.operating_expenses.amort_of_intangibles.after(
            bal.date
        ):
            yield Balance(acc.period.end, bal.value + acc.value)


@dataclass
class OtherNonCurrentAssets[P: Assets = Assets](BalanceSeriesBase[P]):
    historical: "BalanceSeries[OtherNonCurrentAssets]"

    def _balances(self) -> Iterable[Balance]:
        last_bal = yield from yield_and_return(self.historical)

        for period in Period.series(last_bal.date, relativedelta(months=3, day=31)):
            yield Balance(period.end, last_bal.value)


# LIABILITIES
@dataclass
class Liabilities[P: BalanceSheet = BalanceSheet](BalanceSeriesBase[P]):
    accounts_payable: "AccountsPayable[Liabilities]"
    accrued_expenses: "AccruedExpenses[Liabilities]"
    other_current_liabilities: "OtherCurrentLiabilities[Liabilities]"
    revolver: "Revolver[Liabilities]"
    long_term_debt: "LongTermDebt[Liabilities]"
    other_non_current_liabilities: "OtherNonCurrentLiabilities[Liabilities]"

    def _balances(self) -> Iterable[Balance]:
        yield from (
            self.accounts_payable
            + self.accrued_expenses
            + self.other_current_liabilities
            + self.revolver
            + self.long_term_debt
            + self.other_non_current_liabilities
        )


@dataclass
class AccountsPayable[P: Liabilities = Liabilities](BalanceSeriesBase[P]):
    historical: "BalanceSeries[AccountsPayable]"
    pct_cost_of_revenue: float

    def _balances(self) -> Iterable[Balance]:
        last_bal = yield from yield_and_return(self.historical)

        for cost in self.parent.parent.parent.income.pretax_income.operating_income.gross_profit.cost_of_revenue.after(
            last_bal.date
        ):
            yield Balance(cost.period.end, cost.value * self.pct_cost_of_revenue)


@dataclass
class AccruedExpenses[P: Liabilities = Liabilities](BalanceSeriesBase[P]):
    historical: "BalanceSeries[AccruedExpenses]"
    pct_cost_of_revenue: float

    def _balances(self) -> Iterable[Balance]:
        last_bal = yield from yield_and_return(self.historical)

        for cost in self.parent.parent.parent.income.pretax_income.operating_income.gross_profit.cost_of_revenue.after(
            last_bal.date
        ):
            yield Balance(cost.period.end, cost.value * self.pct_cost_of_revenue)


@dataclass
class OtherCurrentLiabilities[P: Liabilities = Liabilities](BalanceSeriesBase[P]):
    historical: "BalanceSeries[OtherCurrentLiabilities]"
    pct_opex: float

    def _balances(self) -> Iterable[Balance]:
        last_bal = yield from yield_and_return(self.historical)

        for opex in self.parent.parent.parent.income.pretax_income.operating_income.operating_expenses.after(
            last_bal.date
        ):
            yield Balance(opex.period.end, opex.value * -self.pct_opex)


@dataclass
class Revolver[P: Liabilities = Liabilities](BalanceSeriesBase[P]):
    historical: "BalanceSeries[Revolver]"

    def _balances(self) -> Iterable[Balance]:
        bal = yield from yield_and_return(self.historical)

        for pmt in self.parent.parent.parent.footnotes.net_revolver_draws.after(bal.date):
            bal = Balance(pmt.date, lambda b=bal, p=pmt: b.value + p.value)
            yield bal


@dataclass
class LongTermDebt[P: Liabilities = Liabilities](BalanceSeriesBase[P]):
    historical: "BalanceSeriesBase[LongTermDebt]"

    def _balances(self) -> Iterable[Balance]:
        bal = yield from yield_and_return(self.historical)
        while True:
            bal = Balance(bal.date + relativedelta(years=1, day=31), bal.value)
            yield bal


@dataclass
class OtherNonCurrentLiabilities[P: Liabilities = Liabilities](BalanceSeriesBase[P]):
    historical: "BalanceSeries[OtherNonCurrentLiabilities]"

    def _balances(self) -> Iterable[Balance]:
        bal = yield from yield_and_return(self.historical)

        for period in Period.series(bal.date, relativedelta(months=3, day=31)):
            bal = Balance(period.end, bal.value)
            yield bal


# EQUITY
@dataclass
class Equity[P: BalanceSheet = BalanceSheet](BalanceSeriesBase[P]):
    common_stock: "CommonStock[Equity]"

    def _balances(self) -> Iterable[Balance]:
        yield from self.common_stock


@dataclass
class CommonStock[P: Equity = Equity](BalanceSeriesBase[P]):
    historical: "BalanceSeries[CommonStock]"

    def _balances(self) -> Iterable[Balance]:
        bal = yield from yield_and_return(self.historical)

        for acc in self.parent.parent.parent.income.after(bal.date):
            bal = Balance(acc.period.end, lambda b=bal: acc.value + b.value)
            yield bal


if __name__ == "__main__":
    from orcaset import NodeDescriptor

    print(NodeDescriptor.describe(BalanceSheet).pretty(2))
