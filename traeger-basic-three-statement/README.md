# Traeger - Three statement model

This is a three statement model for [Traeger](https://www.traeger.com), a popular grill and smoker company. It is a simplified model meant to demonstrate `orcaset` usage rather than a detailed representation of the company's future financial projections. The base case assumptions are generally based off historical averages (see the [base case assumptions](base_case.py) for detail).

The top-level model has four components:
- Income Statement
- Balance Sheet
- Cash Flow Statement
- Footnotes - Additional detail that doesn't neatly fit into a core statement

The model classes are located in the [model](./model) folder. Running any of the model files directly will print a summary of the model line items. For example, `uv run -m model.cash_flow` will print the tree below where the initial tag is the attribute name and the parenthetical is the class type.

```
      net_income (NetIncome)
      depreciation (Depreciation)
      intangible_amortization (IntangibleAmortization)
      changes_in_working_capital (ChangesInWorkingCapital)
    operating (OperatingActivities)
      capital_expenditures (CapitalExpenditures)
    investing (InvestingActivities)
      long_term_debt (LongTermDebt)
      revolver (Revolver)
    financing (FinancingActivities)
  None (CashFlow)
```

Try changing assumptions in and re-running the projections file to see how outputs change.
