import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Orcaset - Basic Model Example

    This notebook demonstrates basic usage and capabilities of [Orcaset](https://github.com/Orcaset/orcaset).

    1. **Model construction** - Create the model by construction classes for each line item
    2. **Run model scenarios** - Instantiate the model with base case assumptions
    3. **Third-party data integration** - Fetch interpolated Treasury rates via web API
    4. **Interactive sensitivity** - Use [marimo's](https://marimo.io) reactive UI components to create interactive charts

    This notebook creates a simple model with the following structure.

    ```
        ┌── Revenue
        ├── Operating Expense
    ┌── Operating Income
    ├── Interest Expense
    Net Income
    ```

    Interest expense is calculated by adding a spread to the most recent end-of-day 5-year US Treasury rate fetched over the web. Since the rate is updated at the end of every business day, the interest expense line item will change depending on the date this notebook is run.

    The demo analysis is short. Model definitions, data retrieval, scenario instantiation, and chart presentation are all delivered in less than 100 lines of code.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Results

    The chart and table below represent model outputs. The sliders sensitize key model assumptions. Changing the value of any assumption will immediately update the chart and table below.
    """
    )
    return


@app.cell
def _(date, mo):
    start_date = date(2020, 12, 31)
    revenue_growth_rate = mo.ui.slider(start=-1, stop=1, step=0.01, value=0.15, label="Revenue growth rate")
    opex_pct_revenue = mo.ui.slider(start=-1, stop=0, step=0.01, value=-0.65, label="Operating expenses (% revenue)")
    coupon_spread = mo.ui.slider(start=0, stop=0.2, step=0.01, value=0.03, label="Coupon spread")
    mo.vstack([revenue_growth_rate, opex_pct_revenue, coupon_spread])
    return coupon_spread, opex_pct_revenue, revenue_growth_rate, start_date


@app.cell
def _(alt, df, mo):
    chart_df = df.T.stack().reset_index().rename(columns={'level_0': 'Date', 'level_1': 'Item', 0:'Value'})
    mo.ui.altair_chart(alt.Chart(chart_df).mark_line()
        .encode(x=alt.X('Date:T', axis=alt.Axis(grid=False, format='%Y-%m-%d')), y='Value', color='Item'))
    return


@app.cell
def _(df, mo):
    display_df = df.apply(func=lambda row: [f'({v:,.0f})' if v < 0 else f'{v:,.0f}' for v in row])
    mo.ui.table(display_df, label="Quarterly Financial Summary")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""The rest of this notebook defines the model, fetches the Treasury rate, and creates a model scenario (note that marimo cells run in order of dependency, not in order of appearance).""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Constructing the Model

    This section defines the model classes each class represents a line item in the model. See the [`orcaset` homepage](https://github.com/Orcaset/orcaset) for an in-depth guide to the using Orcaset. Note that all imports are in the last cell of this notebook.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Income and Operating Income

    Orcaset models define financial line items with custom classes that yield series of values. Relationships to sub-line items are defined as regular attributes, and links to parent line items are declared with type variables.

    In this income model, we will define models that yield consecutive `Accrual` objects that have a start date, end date, and accrual value. We can quickly define accrual line items by inheriting from `AccrualSeriesBase` and overriding the `_accruals` method.

    `NetIncome` is simply the sum of operating income and interest expense. `OperatingIncome` is the sum of revenue and operating expenses.
    """
    )
    return


@app.cell
def _(Accrual, AccrualSeriesBase, Iterable, P, dataclass):
    @dataclass
    class NetIncome[P](AccrualSeriesBase[P]):
        operating_income: "OperatingIncome[NetIncome]"
        interest_expense: "InterestExpense[NetIncome]"

        def _accruals(self) -> Iterable[Accrual]:
            yield from self.operating_income + self.interest_expense
    return (NetIncome,)


@app.cell
def _(Accrual, AccrualSeriesBase, Iterable, NetIncome, P, dataclass):
    @dataclass
    class OperatingIncome[P: NetIncome](AccrualSeriesBase[P]):
        revenue: "Revenue[OperatingIncome]"
        operating_expense: "OperatingExpense[OperatingIncome]"

        def _accruals(self) -> Iterable[Accrual]:
            yield from self.revenue + self.operating_expense
    return (OperatingIncome,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Revenue and Operating Expenses

    Revenue takes initial starting values and grows at a constant annual rate. Operating expenses are determined as a percent of revenue.
    """
    )
    return


@app.cell
def _(
    Accrual,
    AccrualSeriesBase,
    Iterable,
    OperatingIncome,
    P,
    Period,
    YF,
    dataclass,
    date,
    relativedelta,
):
    @dataclass
    class Revenue[P: OperatingIncome](AccrualSeriesBase[P]):
        start_date: date
        freq: relativedelta
        initial_amount: float
        growth_rate: float

        def _accruals(self) -> Iterable[Accrual]:
            value = self.initial_amount
            for period in Period.series(start=self.start_date, freq=self.freq):
                yield Accrual.cmonthly(period, value)
                value *= (1 + self.growth_rate * YF.cmonthly(*period))


    @dataclass
    class OperatingExpense[P: OperatingIncome](AccrualSeriesBase[P]):
        pct_revenue: float

        def _accruals(self) -> Iterable[Accrual]:
            yield from self.parent.revenue * self.pct_revenue
    return OperatingExpense, Revenue


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Interest Expense

    Interest is based on a constant oustanding principal balance and a coupon assumption. When the model is instantiated with assumptions, we'll fetch the latest end-of-day Treasury rate to determine the coupon.
    """
    )
    return


@app.cell
def _(
    Accrual,
    AccrualSeriesBase,
    Iterable,
    NetIncome,
    P,
    Period,
    YF,
    dataclass,
    date,
    relativedelta,
):
    @dataclass
    class InterestExpense[P: NetIncome](AccrualSeriesBase[P]):
        start_date: date
        principal: float
        coupon: float

        def _accruals(self) -> Iterable[Accrual]:
            for period in Period.series(start=self.start_date, freq=relativedelta(months=6, day=31)):
                yield Accrual(period, self.principal * -self.coupon * YF.thirty360(*period), YF.thirty360)
    return (InterestExpense,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Running Model Scenarios

    Now that the model is defined, we can populate it with our assumptions and query the projections. The first assumption we need is the current Treasury rate.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Fetching Data Over the Web

    Since the model runs in a normal Python environment, we can use any Python client to request the rates data. We'll use [`httpx`](https://www.python-httpx.org) for this demo.

    The Treasury publishes constant maturity Treasury yields on a nightly basis. They are freely available through the online [portal](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2025) or [API](https://fiscaldata.treasury.gov/api-documentation/). The Treasury's API returns data in XML format that requires additional parsing overhead, so instead we will pull rates from an endpoint maintained by Orcaset that returns interpolated rates in a simple JSON response.

    ```json
    {
        "years": Float,
        "rate": Float
    }
    ```

    To get the interpolated base rate, we'll send a request to `https://treasury-rates.azurewebsites.net/interpolate` with a single query parameter `tenor` equal to the desired tenor in years.
    """
    )
    return


@app.cell
def _(httpx):
    response = httpx.get(f'https://treasury-rates.azurewebsites.net/interpolate?tenor={5}', timeout=10)
    t_rate = response.json()['rate']
    print("Current EOD 5-year Treasury rate: ", "{:.2%}".format(t_rate))
    return (t_rate,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Now that we've fetched the Treasury rate for the coupon, we can create and instance of the model with our base assumptions.""")
    return


@app.cell
def _(
    InterestExpense,
    NetIncome,
    OperatingExpense,
    OperatingIncome,
    Revenue,
    coupon_spread,
    opex_pct_revenue,
    relativedelta,
    revenue_growth_rate,
    start_date,
    t_rate,
):
    net_income = NetIncome[None](
        operating_income=OperatingIncome[NetIncome](
            revenue=Revenue[OperatingIncome](
                start_date=start_date,
                freq=relativedelta(months=3, day=31),
                initial_amount=1000,
                growth_rate=revenue_growth_rate.value
            ),
            operating_expense=OperatingExpense[OperatingIncome](
                pct_revenue=opex_pct_revenue.value
            )
        ),
        interest_expense=InterestExpense[NetIncome](
            start_date=start_date,
            principal=1_500,
            coupon=t_rate + coupon_spread.value
        )
    )
    return (net_income,)


@app.cell
def _(Period, net_income, pd, relativedelta, start_date):
    quarters = list(Period.series(start=start_date, freq=relativedelta(months=3, day=31), end_offset=relativedelta(years=3)))

    with net_income as ni:
        revenue = [ni.operating_income.revenue.accrue(*q) for q in quarters]
        opex = [ni.operating_income.operating_expense.accrue(*q) for q in quarters]
        opinc = [ni.operating_income.accrue(*q) for q in quarters]
        intexp = [ni.interest_expense.accrue(*q) for q in quarters]
        nis = [ni.accrue(*q) for q in quarters]

    df = pd.DataFrame.from_records(
        data=[revenue, opex, opinc, intexp, nis], 
        index=['Revenue', 'Operating expense', 'Operating income', 'Interest expense', 'Net Income'], 
        columns=[end.isoformat() for _, end in quarters])
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Summary

    This notebook shows basic model construction and usage. It leverages other tools in the Python ecosystem to create a rich, interactive model.

    - **Model construction:** Define classes representing financial statement line items.
    - **Query results:** Create a model instance under prevailing assumptions and call `.accrue(...)` to calculate accrued values. Update model assumptions to reflect sensitivity analysis.
    - **Fetch data:** Retrieve Treasury yield data over the web from a third-party API.
    - **Interactive sensitivities:** Use marimo to create interactive sensitivity charts and tables.
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pyodide_http
    pyodide_http.patch_all()  # Enable httpx requests from WASM export

    from dataclasses import dataclass
    from typing import Iterable
    from datetime import date
    import altair as alt
    from dateutil.relativedelta import relativedelta
    import httpx
    import pandas as pd
    from orcaset import NodeDescriptor
    from orcaset.financial import AccrualSeriesBase, Period, Accrual, YF
    return (
        Accrual,
        AccrualSeriesBase,
        Iterable,
        Period,
        YF,
        alt,
        dataclass,
        date,
        httpx,
        pd,
        relativedelta,
    )


if __name__ == "__main__":
    app.run()
