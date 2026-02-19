from dataclasses import dataclass
from datetime import date


@dataclass
class Bike:
    id: int
    make: str
    model: str


@dataclass
class Customer:
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str | None


@dataclass
class Transaction:
    id: int
    bike_id: int
    customer_id: int
    # TODO: maybe Decimal?
    total_cost: float
    mdy: date
