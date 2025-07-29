from dataclasses import dataclass
from datetime import date

@dataclass
class Lease:
    start: date
    end: date
    monthly_rent: float
    vacant: bool
