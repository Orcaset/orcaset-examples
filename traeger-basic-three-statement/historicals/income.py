from orcaset.financial import Accrual, Period
from datetime import date
from dateutil.relativedelta import relativedelta

hist_dates = list(
    Period.series(
        date(2022, 12, 31),
        relativedelta(months=3, day=31),
        relativedelta(year=2025, months=3, day=31),
    )
)

revenue = [
    Accrual.cmonthly(per, val)
    for per, val in zip(
        hist_dates, [153161, 171512, 117730, 163479, 144914, 168471, 122050, 168637, 143283]
    )
]

cost_of_revenue = [
    Accrual.cmonthly(per, val)
    for per, val in zip(
        hist_dates, [-97738, -108181, -73064, -103342, -82351, -96143, -70362, -99747, -83824]
    )
]

sales_and_marketing = [
    Accrual.cmonthly(per, val)
    for per, val in zip(
        hist_dates, [-22075, -27915, -25913, -32824, -21679, -28224, -26162, -33591, -22210]
    )
]

# Includes all operating expenses other than sales and marketing and amortization of intangibles
general_and_administrative = [
    Accrual.cmonthly(per, val)
    for per, val in zip(
        hist_dates, [-27722, -54136, -22748, -30117, -32138, -30491, -24135, -26719, -25019]
    )
]

amort_of_intangibles = [
    Accrual.cmonthly(per, val)
    for per, val in zip(hist_dates, [-8889, -8888, -8889, -8888, -8819, -8818, -8819, -8818, -8818])
]


interest_expense = [
    Accrual.cmonthly(per, val)
    for per, val in zip(hist_dates, [-8081, -7810, -7517, -7867, -8096, -8678, -8534, -8192, -7893])
]

other_income = [
    Accrual.cmonthly(per, val)
    for per, val in zip(hist_dates, [578, 5450, 1992, -3715, 3676, 1281, -3964, -513, 2103])
]

tax_expense = [
    Accrual.cmonthly(per, val)
    for per, val in zip(hist_dates, [-164, -198, -852, -771, -190, 24, 137, 1985, 1600])
]
