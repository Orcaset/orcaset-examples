from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from dateutil.relativedelta import relativedelta
from orcaset import yield_and_return
from orcaset.financial import Accrual, AccrualSeries, AccrualSeriesBase, Period

if TYPE_CHECKING:
    from .model import Traeger


@dataclass
class NetIncome[P: Traeger = Traeger](AccrualSeriesBase[P]):
    pretax_income: "PretaxIncome[NetIncome]"
    tax_expense: "TaxExpense[NetIncome]"

    def _accruals(self) -> Iterable[Accrual]:
        yield from self.pretax_income + self.tax_expense


@dataclass
class TaxExpense[P: NetIncome = NetIncome](AccrualSeriesBase[P]):
    historical: "AccrualSeries[list[Accrual], TaxExpense]"
    tax_rate: float

    def _accruals(self) -> Iterable[Accrual]:
        last_acc = yield from yield_and_return(self.historical)

        for pretax in self.parent.pretax_income.after(last_acc.period.end):
            yield Accrual(
                period=pretax.period,
                value=pretax.value * self.tax_rate,
                yf=last_acc.yf,
            )


@dataclass
class PretaxIncome[P: NetIncome = NetIncome](AccrualSeriesBase[P]):
    operating_income: "OperatingIncome[PretaxIncome]"
    interest_expense: "InterestExpense[PretaxIncome]"
    other_income: "OtherIncome[PretaxIncome]"

    def _accruals(self) -> Iterable[Accrual]:
        yield from self.operating_income + self.interest_expense + self.other_income


@dataclass
class InterestExpense[P: PretaxIncome = PretaxIncome](AccrualSeriesBase[P]):
    historical: "AccrualSeries[list[Accrual], InterestExpense]"
    interest_rate: float

    def _accruals(self) -> Iterable[Accrual]:
        last_acc = yield from yield_and_return(self.historical)

        liabilities = self.parent.parent.parent.balance_sheet.liabilities
        total_debt = liabilities.revolver + liabilities.long_term_debt

        for period in Period.series(last_acc.period.end, relativedelta(months=3, day=31)):
            yield Accrual(
                period=period,
                value=lambda td=total_debt: td.at(period.start) * -self.interest_rate * last_acc.yf(*period),
                yf=last_acc.yf,
            )


@dataclass
class OtherIncome[P: PretaxIncome = PretaxIncome](AccrualSeriesBase[P]):
    """Projected as a constant annual amount."""

    historical: "AccrualSeries[list[Accrual], OtherIncome]"
    projected_amt: float

    def _accruals(self) -> Iterable[Accrual]:
        last_acc = yield from yield_and_return(self.historical)

        while True:
            period = Period(last_acc.period.end, last_acc.period.end + relativedelta(years=1, day=31))
            last_acc = Accrual(period=period, value=self.projected_amt, yf=last_acc.yf)
            yield last_acc


@dataclass
class OperatingIncome[P: PretaxIncome = PretaxIncome](AccrualSeriesBase[P]):
    gross_profit: "GrossProfit[OperatingIncome]"
    operating_expenses: "OperatingExpenses[OperatingIncome]"

    def _accruals(self) -> Iterable[Accrual]:
        yield from self.gross_profit + self.operating_expenses


@dataclass
class OperatingExpenses[P: OperatingIncome = OperatingIncome](AccrualSeriesBase[P]):
    sales_and_marketing: "SalesAndMarketing[OperatingExpenses]"
    general_and_admin: "GeneralAndAdmin[OperatingExpenses]"
    amort_of_intangibles: "AmortOfIntangibles[OperatingExpenses]"

    def _accruals(self) -> Iterable[Accrual]:
        yield from (self.sales_and_marketing + self.general_and_admin + self.amort_of_intangibles)


@dataclass
class GrossProfit[P: OperatingIncome = OperatingIncome](AccrualSeriesBase[P]):
    revenue: "Revenue[GrossProfit]"
    cost_of_revenue: "CostOfRevenue[GrossProfit]"

    def _accruals(self) -> Iterable[Accrual]:
        yield from self.revenue + self.cost_of_revenue


@dataclass
class Revenue[P: GrossProfit = GrossProfit](AccrualSeriesBase[P]):
    historical: "AccrualSeries[list[Accrual], Revenue]"
    growth_rates: "AccrualSeries[list[Accrual], Revenue]"

    def _accruals(self) -> Iterable[Accrual]:
        acc = yield from yield_and_return(self.historical)

        while True:
            period = Period(acc.period.end, acc.period.end + relativedelta(months=3, day=31))
            acc = Accrual(
                period=period,
                value=acc.value
                / acc.yf(*acc.period)
                * acc.yf(*period)
                * (1 + self.growth_rates.w_avg(*period)),
                yf=acc.yf,
            )
            yield acc


@dataclass
class CostOfRevenue[P: GrossProfit = GrossProfit](AccrualSeriesBase[P]):
    historical: "AccrualSeries[list[Accrual], CostOfRevenue]"
    pct_revenue: float

    def _accruals(self) -> Iterable[Accrual]:
        last_acc = yield from yield_and_return(self.historical)

        for rev in self.parent.revenue.after(last_acc.period.end):
            yield rev * self.pct_revenue


@dataclass
class SalesAndMarketing[P: OperatingExpenses = OperatingExpenses](AccrualSeriesBase[P]):
    historical: "AccrualSeries[list[Accrual], SalesAndMarketing]"
    pct_revenue: float

    def _accruals(self) -> Iterable[Accrual]:
        last_acc = yield from yield_and_return(self.historical)

        for rev in self.parent.parent.gross_profit.revenue.after(last_acc.period.end):
            yield rev * self.pct_revenue


@dataclass
class GeneralAndAdmin[P: OperatingExpenses = OperatingExpenses](AccrualSeriesBase[P]):
    historical: "AccrualSeries[list[Accrual], GeneralAndAdmin]"
    growth_rates: "AccrualSeries[list[Accrual], GeneralAndAdmin]"

    def _accruals(self) -> Iterable[Accrual]:
        acc = yield from yield_and_return(self.historical)

        while True:
            period = Period(
                acc.period.end,
                acc.period.end + relativedelta(years=1, day=31),
            )
            acc = Accrual(
                period=period,
                value=acc.value
                / acc.yf(*acc.period)
                * acc.yf(*period)
                * (1 + self.growth_rates.w_avg(*period)),
                yf=acc.yf,
            )
            yield acc


@dataclass
class AmortOfIntangibles[P: OperatingExpenses = OperatingExpenses](AccrualSeriesBase[P]):
    historical: "AccrualSeries[list[Accrual], AmortOfIntangibles]"
    growth_rate: float

    def _accruals(self) -> Iterable[Accrual]:
        acc = yield from yield_and_return(self.historical)

        while True:
            period = Period(acc.period.end, acc.period.end + relativedelta(years=1, day=31))
            acc = Accrual(
                period=period,
                value=acc.value
                / acc.yf(*acc.period)
                * acc.yf(*period)
                * (1 + self.growth_rate * acc.yf(*period)),
                yf=acc.yf,
            )
            yield acc


if __name__ == "__main__":
    from orcaset import NodeDescriptor

    print(NodeDescriptor.describe(NetIncome).pretty(2))
