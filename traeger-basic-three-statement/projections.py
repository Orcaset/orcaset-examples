from datetime import date

from dateutil.relativedelta import relativedelta
from orcaset import NodeDescriptor
from orcaset.financial import Period, BalanceSeriesBase

from base_case import Traeger, traeger


# Prints the model structure
print(NodeDescriptor.describe(Traeger).pretty(indent=2))


# Print historical and projected summary financials
periods = list(Period.series(date(2023, 12, 31), relativedelta(months=3, day=31), relativedelta(years=3)))
dates = list(set(sum(periods, ())))
dates.sort()


with traeger as trg:
    rev = [trg.income.pretax_income.operating_income.gross_profit.revenue.accrue(*per) for per in periods]
    gp = [trg.income.pretax_income.operating_income.gross_profit.accrue(*per) for per in periods]
    opex = [trg.income.pretax_income.operating_income.operating_expenses.accrue(*per) for per in periods]
    opinc = [trg.income.pretax_income.operating_income.accrue(*per) for per in periods]
    interest_exp = [trg.income.pretax_income.interest_expense.accrue(*per) for per in periods]
    net_income = [trg.income.accrue(*per) for per in periods]

# Income Statement Table
print("\n## Income Statement")
print()
header = ["Line Item"] + [end.isoformat() for _, end in periods]
print("| " + " | ".join(header) + " |")
print("| " + " | ".join(["---"] * len(header)) + " |")
print(f"| Revenue | " + " | ".join(f"{r:,.0f}" for r in rev) + " |")
print(f"| Gross Profit | " + " | ".join(f"{g:,.0f}" for g in gp) + " |")
print(f"| Operating Expenses | " + " | ".join(f"{o:,.0f}" for o in opex) + " |")
print(f"| Operating Income | " + " | ".join(f"{oi:,.0f}" for oi in opinc) + " |")
print(f"| Interest Expense | " + " | ".join(f"{ie:,.0f}" for ie in interest_exp) + " |")
print(f"| Net Income | " + " | ".join(f"{ni:,.0f}" for ni in net_income) + " |")


cf_periods = [per for per in periods if per.start >= date(2025, 3, 31)]

with traeger as trg:
    op_cf = [trg.cash_flow.operating.over(*per) for per in cf_periods]
    inv_cf = [trg.cash_flow.investing.over(*per) for per in cf_periods]
    fin_cf = [trg.cash_flow.financing.over(*per) for per in cf_periods]
    tot_cf = [trg.cash_flow.over(*per) for per in cf_periods]
    capex = [trg.footnotes.capital_expenditures.over(*per) for per in cf_periods]
    net_rev = [trg.footnotes.net_revolver_draws.over(*per) for per in cf_periods]

# Cash Flow Statement Table
print("\n## Cash Flow Statement")
print()
header = ["Line Item"] + [end.isoformat() for _, end in cf_periods]
print("| " + " | ".join(header) + " |")
print("| " + " | ".join(["---"] * len(header)) + " |")
print(f"| Operating CF | " + " | ".join(f"{c:,.0f}" for c in op_cf) + " |")
print(f"| Investing CF | " + " | ".join(f"{c:,.0f}" for c in inv_cf) + " |")
print(f"| Financing CF | " + " | ".join(f"{c:,.0f}" for c in fin_cf) + " |")
print(f"| Total CF | " + " | ".join(f"{c:,.0f}" for c in tot_cf) + " |")

print("\n## Additional Metrics")
print()
print("| " + " | ".join(header) + " |")
print("| " + " | ".join(["---"] * len(header)) + " |")
print(f"| Net Revolver | " + " | ".join(f"{c:,.0f}" for c in net_rev) + " |")
print(f"| CapEx | " + " | ".join(f"{c:,.0f}" for c in capex) + " |")


with traeger as trg:
    assets = [trg.balance_sheet.assets.at(dt) for dt in dates]
    liabilities = [trg.balance_sheet.liabilities.at(dt) for dt in dates]
    equity = [trg.balance_sheet.equity.at(dt) for dt in dates]
    bs = [trg.balance_sheet.at(dt) for dt in dates]

# Balance Sheet Table
print("\n## Balance Sheet")
print()
header = ["Line Item"] + [dt.isoformat() for dt in dates]
print("| " + " | ".join(header) + " |")
print("| " + " | ".join(["---"] * len(header)) + " |")
print(f"| Assets | " + " | ".join(f"{a:,.0f}" for a in assets) + " |")
print(f"| Liabilities | " + " | ".join(f"{li:,.0f}" for li in liabilities) + " |")
print(f"| Equity | " + " | ".join(f"{e:,.0f}" for e in equity) + " |")
print(f"| Balance Sheet | " + " | ".join(f"{b:,.0f}" for b in bs) + " |")

print("\n## Balance Sheet Detail")
print()
print("| " + " | ".join(header) + " |")
print("| " + " | ".join(["---"] * len(header)) + " |")
with traeger as trg:
    for node in (
        [*trg.balance_sheet.assets.child_nodes]
        + [*trg.balance_sheet.liabilities.child_nodes]
        + [*trg.balance_sheet.equity.child_nodes]
    ):
        vals = [node.at(dt) for dt in dates if isinstance(node, BalanceSeriesBase)]
        print(f"| {type(node).__name__} | " + " | ".join(f"{v:,.0f}" for v in vals) + " |")
