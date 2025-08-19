from datetime import date

from orcaset.financial import (
    Accrual,
    AccrualSeries,
    BalanceSeries,
    PaymentSeries,
    Period,
)

import model.balance_sheet as bs
import model.cash_flow as cf
import model.footnotes as fn
import model.income as inc
from historicals import balance_sheet as hist_bs
from historicals import footnotes as hist_fn
from historicals import income as hist_inc
from model.model import Traeger


class Assumptions:
    # INCOME ASSUMPTIONS
    revenue_growth_rates = AccrualSeries(
        [
            Accrual.cmonthly(Period(date(2025, 3, 31), date(2025, 12, 31)), 0.05),
            Accrual.cmonthly(Period(date(2025, 12, 31), date(2026, 12, 31)), 0.15),
            Accrual.cmonthly(Period(date(2026, 12, 31), date(2027, 12, 31)), 0.1),
            Accrual.cmonthly(Period(date(2027, 12, 31), date(2030, 12, 31)), 0.05),
            Accrual.cmonthly(Period(date(2030, 12, 31), date.max), 0.03),
        ]
    )
    cost_of_revenue_pct_revenue = -0.6
    sales_and_marketing_pct_revenue = sum(acc.value for acc in hist_inc.sales_and_marketing) / sum(
        acc.value for acc in hist_inc.revenue
    )
    general_and_admin_growth_rates = AccrualSeries(
        [
            Accrual.cmonthly(Period(date(2025, 3, 31), date(2030, 12, 31)), 0.05),
            Accrual.cmonthly(Period(date(2030, 12, 31), date.max), 0.03),
        ]
    )
    amort_of_intangibles_growth_rate = 0.0
    interest_rate = 0.08
    annual_other_income = sum(acc.value for acc in hist_inc.other_income) / len(hist_inc.other_income) * 4
    tax_rate = 0.21

    # BALANCE SHEET ASSUMPTIONS
    min_cash = 10_000
    receivables_pct_revenue = sum(
        bal.value / rev.value for rev, bal in zip(hist_inc.revenue, hist_bs.receivables[1:])
    ) / len(hist_inc.revenue)
    inventory_pct_cost_of_revenue = sum(
        bal.value / cost.value for cost, bal in zip(hist_inc.cost_of_revenue, hist_bs.inventory[1:])
    ) / len(hist_inc.cost_of_revenue)
    other_current_assets_pct_inventory = sum(
        oca_bal.value / inv_bal.value for oca_bal, inv_bal in zip(hist_bs.other_current_assets, hist_bs.inventory)
    ) / len(hist_bs.other_current_assets[1:])
    accounts_payable_pct_cost_of_revenue = sum(
        bal.value / cost.value for cost, bal in zip(hist_inc.cost_of_revenue, hist_bs.accounts_payable[1:])
    ) / len(hist_inc.cost_of_revenue)
    accrued_expenses_pct_cost_of_revenue = sum(
        bal.value / cost.value for cost, bal in zip(hist_inc.cost_of_revenue, hist_bs.accrued_expenses[1:])
    ) / len(hist_inc.cost_of_revenue)
    other_current_liabilities_pct_opex = 0.1

    # FOOTNOTE ASSUMPTIONS
    depreciation_growth_rate = 0.05
    capital_expenditures_growth_rate = 0.05
    start_date = date(2025, 3, 31)


income = inc.NetIncome(
    pretax_income=inc.PretaxIncome(
        operating_income=inc.OperatingIncome(
            gross_profit=inc.GrossProfit(
                revenue=inc.Revenue(
                    historical=AccrualSeries(hist_inc.revenue),
                    growth_rates=Assumptions.revenue_growth_rates,
                ),
                cost_of_revenue=inc.CostOfRevenue(
                    historical=AccrualSeries(hist_inc.cost_of_revenue),
                    pct_revenue=Assumptions.cost_of_revenue_pct_revenue,
                ),
            ),
            operating_expenses=inc.OperatingExpenses(
                sales_and_marketing=inc.SalesAndMarketing(
                    historical=AccrualSeries(hist_inc.sales_and_marketing),
                    pct_revenue=Assumptions.sales_and_marketing_pct_revenue,
                ),
                general_and_admin=inc.GeneralAndAdmin(
                    historical=AccrualSeries(hist_inc.general_and_administrative),
                    growth_rates=Assumptions.general_and_admin_growth_rates,
                ),
                amort_of_intangibles=inc.AmortOfIntangibles(
                    historical=AccrualSeries(hist_inc.amort_of_intangibles),
                    growth_rate=Assumptions.amort_of_intangibles_growth_rate,
                ),
            ),
        ),
        interest_expense=inc.InterestExpense(
            historical=AccrualSeries(hist_inc.interest_expense),
            interest_rate=Assumptions.interest_rate,
        ),
        other_income=inc.OtherIncome(
            historical=AccrualSeries(hist_inc.other_income),
            projected_amt=Assumptions.annual_other_income,
        ),
    ),
    tax_expense=inc.TaxExpense(historical=AccrualSeries(hist_inc.tax_expense), tax_rate=Assumptions.tax_rate),
)


balance_sheet = bs.BalanceSheet(
    assets=bs.Assets(
        cash=bs.Cash(historical=BalanceSeries(hist_bs.cash)),
        receivables=bs.Receivables(
            historical=BalanceSeries(hist_bs.receivables),
            pct_revenue=Assumptions.receivables_pct_revenue,
        ),
        inventory=bs.Inventory(
            historical=BalanceSeries(hist_bs.inventory),
            pct_cost_of_revenue=Assumptions.inventory_pct_cost_of_revenue,
        ),
        other_current_assets=bs.OtherCurrentAssets(
            historical=BalanceSeries(hist_bs.other_current_assets),
            pct_inventory=Assumptions.other_current_assets_pct_inventory,
        ),
        ppe=bs.PropertyPlantEquipment(
            historical=BalanceSeries(hist_bs.ppe),
        ),
        intangible_assets=bs.IntangibleAssets(
            total_cost=bs.TotalCost(
                historical=BalanceSeries(hist_bs.intangible_assets),
            ),
            accumulated_amortization=bs.AccumulatedAmortization(
                historical=BalanceSeries(hist_bs.intangible_assets),
            ),
        ),
        other_non_current_assets=bs.OtherNonCurrentAssets(
            historical=BalanceSeries(hist_bs.other_non_current_assets),
        ),
    ),
    liabilities=bs.Liabilities(
        accounts_payable=bs.AccountsPayable(
            historical=BalanceSeries(hist_bs.accounts_payable),
            pct_cost_of_revenue=Assumptions.accounts_payable_pct_cost_of_revenue,
        ),
        accrued_expenses=bs.AccruedExpenses(
            historical=BalanceSeries(hist_bs.accrued_expenses),
            pct_cost_of_revenue=Assumptions.accrued_expenses_pct_cost_of_revenue,
        ),
        other_current_liabilities=bs.OtherCurrentLiabilities(
            historical=BalanceSeries(hist_bs.other_current_liabilities),
            pct_opex=Assumptions.other_current_liabilities_pct_opex,
        ),
        revolver=bs.Revolver(historical=BalanceSeries(hist_bs.revolver)),
        long_term_debt=bs.LongTermDebt(
            historical=BalanceSeries(hist_bs.long_term_debt),
        ),
        other_non_current_liabilities=bs.OtherNonCurrentLiabilities(
            historical=BalanceSeries(hist_bs.other_non_current_liabilities),
        ),
    ),
    equity=bs.Equity(
        common_stock=bs.CommonStock(historical=BalanceSeries(hist_bs.common_stock)),
    ),
)

footnotes = fn.Footnotes(
    depreciation=fn.Depreciation(
        historical=AccrualSeries(hist_fn.depreciation),
        growth_rate=Assumptions.depreciation_growth_rate,
    ),
    capital_expenditures=fn.CapitalExpenditures(
        historical=PaymentSeries(hist_fn.capital_expenditures),
        growth_rate=Assumptions.capital_expenditures_growth_rate,
    ),
    cash_flow_before_revolver=fn.CashFlowBeforeRevolver(),
    net_revolver_draws=fn.NetRevolverDraws(
        last_cash_balance=hist_bs.cash[-1],
        min_cash=Assumptions.min_cash,
    ),
)

cash_flow = cf.CashFlow(
    operating=cf.OperatingActivities(
        net_income=cf.NetIncome(),
        depreciation=cf.Depreciation(),
        intangible_amortization=cf.IntangibleAmortization(),
        changes_in_working_capital=cf.ChangesInWorkingCapital(),
    ),
    investing=cf.InvestingActivities(capital_expenditures=cf.CapitalExpenditures()),
    financing=cf.FinancingActivities(long_term_debt=cf.LongTermDebt(), revolver=cf.Revolver()),
)

traeger = Traeger(income=income, balance_sheet=balance_sheet, cash_flow=cash_flow, footnotes=footnotes)
