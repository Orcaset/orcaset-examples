from datetime import date

from dateutil.relativedelta import relativedelta
from orcaset import date_series
from orcaset.financial import Balance


hist_dates = list(
    date_series(
        date(2022, 12, 31),
        relativedelta(months=3, day=31),
        relativedelta(year=2025, months=3, day=31),
    )
)


# Includes restricted cash
cash = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [51555, 27732, 14496, 11280, 29921, 23620, 18025, 16872, 14981, 12034]
    )
]

receivables = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [42050, 99591, 83290, 50996, 59938, 79049, 89230, 70786, 85331, 94958]
    )
]

inventory = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [153471, 132381, 97803, 101891, 96175, 99902, 91035, 105058, 107367, 127236]
    )
]

# Prepaid expenses and other current assets
other_current_assets = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [27162, 28034, 29842, 35051, 30346, 27971, 26340, 24348, 35444, 18349]
    )
]

ppe = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [55510, 49775, 52274, 55232, 42591, 40725, 39807, 38241, 36949, 35616]
    )
]


intangible_assets = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [512858, 502290, 491700, 481155, 470546, 460069, 449471, 438922, 428536, 418129]
    )
]

# Includes goodwill and lease ROU assets
other_non_current_assets = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [104109, 98194, 100240, 101115, 131242, 130750, 128498, 123849, 122069, 119278]
    )
]

accounts_payable = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [29841, 26244, 18563, 26028, 33280, 25890, 33661, 30575, 27701, 19073]
    )
]
accrued_expenses = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [52295, 56286, 49094, 40682, 52941, 46144, 48070, 56630, 82143, 64989]
    )
]


other_current_liabilities = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [18812, 17694, 19362, 16308, 19103, 19592, 4476, 4242, 7147, 5207]
    )
]

other_non_current_liabilities = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [30831, 30289, 18129, 19670, 38137, 37364, 37290, 36394, 33561, 32799]
    )
]

revolver = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [11709, 40909, 40000, 25000, 28400, 40635, 23500, 12000, 5000, 25000]
    )
]

long_term_debt = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [468358, 439186, 396972, 397259, 397550, 397836, 398123, 398409, 398695, 398982]
    )
]

common_stock = [
    Balance(dt, val)
    for dt, val in zip(
        hist_dates, [334869, 327389, 327525, 311773, 291348, 294625, 297286, 279826, 276430, 279550]
    )
]
