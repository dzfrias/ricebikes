import services.transactions as transactions
import jsonschema
import json
from datetime import datetime
from decimal import Decimal
from flask import Blueprint, request
from models.transactions import Transaction, Bike, Customer


DATE_FORMAT = "%Y-%m-%d"


bp = Blueprint("transactions", __name__)


@bp.get("/api/transactions")
def get_all():
    return transactions.get_transactions()


# This is the JSON schema for the /api/transactions/create endpoint. All inputs should be against
# this.
CREATE_TRANSACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "date": {"type": "string", "format": "date"},
        "total_cost": {"type": "number"},
        "customer": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "phone_number": {"type": ["string", "null"]},
            },
            "additionalProperties": False,
            "required": ["first_name", "last_name", "email"],
        },
        "bike": {
            "type": "object",
            "properties": {
                "make": {"type": "string"},
                "model": {"type": "string"},
            },
            "additionalProperties": False,
            "required": ["make", "model"],
        },
    },
    "required": ["date", "total_cost", "customer", "bike"],
    "additionalProperties": False,
}


@bp.post("/api/transactions/create")
def create():
    data = json.loads(request.data, parse_float=Decimal)
    try:
        jsonschema.validate(
            instance=data,
            schema=CREATE_TRANSACTION_SCHEMA,
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as e:
        return f"Bad JSON payload: {e.message}", 400
    try:
        date = datetime.strptime(data["date"], DATE_FORMAT).date()
    except ValueError:
        return (
            "Bad date format for `date` field in request. Expected YYYY-MM-DD.",
            400,
        )
    bike = Bike(make=data["bike"]["make"], model=data["bike"]["model"])
    bike_id = transactions.add_bike(bike)
    customer = Customer(
        first_name=data["customer"]["first_name"],
        last_name=data["customer"]["last_name"],
        email=data["customer"]["email"],
        phone_number=data["customer"].get("phone_number"),
    )
    customer_id = transactions.add_or_update_customer(customer)
    transaction = Transaction(
        bike_id=bike_id,
        customer_id=customer_id,
        date=date,
        total_cost=data["total_cost"],
    )
    transaction_id = transactions.add_transaction(transaction)

    return {"id": transaction_id}, 201


@bp.delete("/api/transactions/delete/<int:id>")
def delete(id: int):
    did_delete = transactions.delete_transaction(id)
    return "", 204 if did_delete else 404
