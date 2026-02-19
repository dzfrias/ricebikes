import datetime
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Bike:
    make: str
    model: str


@dataclass
class Customer:
    first_name: str
    last_name: str
    email: str
    phone_number: str | None


@dataclass
class Transaction:
    bike_id: int
    customer_id: int
    total_cost: Decimal
    date: datetime.date
