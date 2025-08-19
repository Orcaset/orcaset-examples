from datetime import date

from dateutil.relativedelta import relativedelta
from orcaset.financial import Accrual, Payment, Period

hist_periods = list(
    Period.series(
        date(2022, 3, 31),
        relativedelta(months=3, day=31),
        relativedelta(year=2025, months=3, day=31),
    )
)

depreciation = [
    Accrual.cmonthly(per, val)
    for per, val in zip(
        hist_periods, [-3564, -3898, -3742, -3807, -3619, -3260, -3260, -3731, -3749]
    )
]

capital_expenditures = [
    Payment(dt, val)
    for dt, val in zip(
        (end for _, end in hist_periods),
        [-2082, -6772, -8906, -11040, -5683, -2051, -7983, -4013, -1826],
    )
]
