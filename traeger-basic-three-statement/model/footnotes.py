from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from dateutil.relativedelta import relativedelta
from orcaset import Node, yield_and_return
from orcaset.financial import (
    YF,
    Accrual,
    AccrualSeries,
    AccrualSeriesBase,
    Balance,
    Payment,
    PaymentSeries,
    PaymentSeriesBase,
    Period,
)

if TYPE_CHECKING:
    from .model import Traeger


@dataclass
class Footnotes[P: Traeger = Traeger](Node[P]):
    depreciation: "Depreciation[Footnotes]"
    capital_expenditures: "CapitalExpenditures[Footnotes]"
    cash_flow_before_revolver: "CashFlowBeforeRevolver[Footnotes]"
    net_revolver_draws: "NetRevolverDraws[Footnotes]"


@dataclass
class Depreciation[P: Footnotes = Footnotes](AccrualSeriesBase[P]):
    """Depreciation expense in opex and cost of revenue."""

    historical: "AccrualSeries[list[Accrual], Depreciation]"
    growth_rate: float

    def _accruals(self) -> Iterable[Accrual]:
        acc = yield from yield_and_return(self.historical)

        while True:
            period = Period(acc.period.end, acc.period.end + relativedelta(months=3, day=31))
            acc = Accrual(
                period=period,
                value=acc.value / acc.yf(*acc.period) * acc.yf(*period) * (1 + self.growth_rate * acc.yf(*period)),
                yf=acc.yf,
            )
            yield acc


@dataclass
class CapitalExpenditures[P: Footnotes = Footnotes](PaymentSeriesBase[P]):
    historical: "PaymentSeries[CapitalExpenditures]"
    growth_rate: float

    def _payments(self) -> Iterable[Payment]:
        pmt = yield from yield_and_return(self.historical)

        while True:
            dt1, dt2 = pmt.date, pmt.date + relativedelta(months=3, day=31)
            pmt = Payment(
                dt2,
                pmt.value * (1 + self.growth_rate * YF.cmonthly(dt1, dt2)),
            )
            yield pmt


@dataclass
class CashFlowBeforeRevolver[P: Footnotes = Footnotes](PaymentSeriesBase[P]):
    """Cash flow before any revolver draws or repayments."""

    def _payments(self) -> Iterable[Payment]:
        yield from (
            self.parent.parent.cash_flow.operating
            + self.parent.parent.cash_flow.investing
            + self.parent.parent.cash_flow.financing.long_term_debt
        )


@dataclass
class NetRevolverDraws[P: Footnotes = Footnotes](PaymentSeriesBase[P]):
    last_cash_balance: Balance
    min_cash: float

    def _payments(self) -> Iterable[Payment]:
        for pmt in self.parent.cash_flow_before_revolver.after(self.last_cash_balance.date):

            def make_bal(p: Payment):
                def inner():
                    prior_bal = self.parent.parent.balance_sheet.assets.cash.at(p.date - relativedelta(days=1))
                    ret_val = -min(p.value + (prior_bal - self.min_cash), (prior_bal - self.min_cash))
                    return ret_val

                return inner

            yield Payment(pmt.date, make_bal(pmt))


if __name__ == "__main__":
    from orcaset import NodeDescriptor

    print(NodeDescriptor.describe(Footnotes).pretty(2))
