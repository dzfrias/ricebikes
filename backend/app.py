import json
import psycopg
import jsonschema
from datetime import datetime
from flask import Flask, request
from pathlib import Path


# Options for connnecting to the PostgreSQL server. Note that this would change depending on if a
# production build was deployed.
POSTGRESQL_OPTIONS = {
    "host": "localhost",
    "port": 5432,
    "dbname": "ricebikesdb",
    "user": "ricebikes",
    "password": "ricebikes",
}
DATE_FORMAT = "%Y-%m-%d"


# Execute schema
with psycopg.connect(**POSTGRESQL_OPTIONS) as conn:
    with conn.cursor() as cur:
        # TODO: embed this into a python module
        schema_contents = Path("schema.sql").read_text()
        cur.execute(schema_contents)
        conn.commit()


app = Flask(__name__)


@app.route("/")
def index():
    return "Hello world"


# TODO: redesign to be separated :(
@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    with psycopg.connect(**POSTGRESQL_OPTIONS) as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            raw_transactions = cur.execute(
                """
                SELECT
                    rt.transaction_id,
                    rt.total_cost,
                    rt.transaction_date,
                    b.bike_id,
                    b.make,
                    b.model,
                    c.customer_id,
                    c.first_name,
                    c.last_name,
                    c.email,
                    c.phone_number
                FROM repair_transactions AS rt
                JOIN bikes AS b
                    ON b.bike_id = rt.bike_id
                JOIN customers AS c
                    ON c.customer_id = rt.customer_id;
                """,
            )
            # Convert to nested structure; as far as I know this is one of the cleaner ways to
            # to do this using pyscopg without defining a custom row factory that relies on some
            # naming convention to determine the object structure. This approach would be rather
            # hacky. The general incongruity is that SQL returns things as tuples, not nested a
            # nested structure. Some SQL wrappers try to abstract this away, but I don't think
            # that makes for is a very accurate abstraction.
            transactions = [
                {
                    "transaction_id": raw["transaction_id"],
                    "transaction_date": raw["transaction_date"].strftime(DATE_FORMAT),
                    # NOTE: it is safe here to call `float`. Although certain numbers are not
                    # represented with total accuracy in the floating point format, we actually
                    # don't need to do any arithmetic with `total_cost`, and thus, our precision
                    # does not matter. Floating point stringify-ers will write floating points in
                    # their shortest round-trippable form.
                    "total_cost": float(raw["total_cost"]),
                    "customer": {
                        "id": raw["customer_id"],
                        "first_name": raw["first_name"],
                        "last_name": raw["last_name"],
                        "email": raw["email"],
                        # NOTE: in the database, phone numbers are stored as optinally NULL text.
                        # However, the specification document I was given says to return a number
                        # in the JSON response to represent the phone number. I don't think that
                        # is a very good approach (for example, what happens when we need to
                        # represent different country codes?), so I'm returning it as a string.
                        "phone_number": raw["phone_number"],
                    },
                    "bike": {
                        "id": raw["bike_id"],
                        "make": raw["make"],
                        "model": raw["model"],
                    },
                }
                # Sort by date
                for raw in sorted(
                    raw_transactions, key=lambda x: x["transaction_date"], reverse=True
                )
            ]
            return transactions


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


@app.route("/api/transactions/create", methods=["POST"])
def add_transaction():
    data = json.loads(request.data)
    try:
        jsonschema.validate(
            instance=data,
            schema=CREATE_TRANSACTION_SCHEMA,
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as e:
        return f"Bad JSON payload: {e.message}", 400
    try:
        mdy = datetime.strptime(data["date"], DATE_FORMAT).date()
    except ValueError:
        return (
            "Bad date format for `date` field in request. Expected YYYY-MM-DD.",
            400,
        )
    total_cost = data["total_cost"]
    customer = data["customer"]
    bike = data["bike"]
    with psycopg.connect(**POSTGRESQL_OPTIONS) as conn:
        with conn.cursor(row_factory=psycopg.rows.scalar_row) as cur:
            bike_id = cur.execute(
                "INSERT INTO bikes (make, model) VALUES (%s, %s) RETURNING bike_id;",
                (bike["make"], bike["model"]),
            ).fetchone()
            customer_id = cur.execute(
                """
                INSERT INTO customers (first_name, last_name, email, phone_number)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email)
                DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    phone_number = EXCLUDED.phone_number
                RETURNING customer_id;
                """,
                (
                    customer["first_name"],
                    customer["last_name"],
                    customer["email"],
                    # `phone_number` is an optional field
                    customer.get("phone_number"),
                ),
            ).fetchone()
            transaction_id = cur.execute(
                """
                INSERT INTO repair_transactions (bike_id, customer_id, total_cost, transaction_date)
                VALUES (%s, %s, %s, %s)
                RETURNING transaction_id;
                """,
                (bike_id, customer_id, total_cost, mdy),
            ).fetchone()
            conn.commit()
            return {"id": transaction_id}, 201


@app.route("/api/transactions/update/<int:id>", methods=["PUT"])
def update_transaction(id: int):
    pass


@app.route("/api/transactions/delete/<int:id>", methods=["DELETE"])
def delete_transaction(id: int):
    with psycopg.connect(**POSTGRESQL_OPTIONS) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM repair_transactions WHERE transaction_id = %s;", (id,)
            )
            conn.commit()
    return "", 204


if __name__ == "__main__":
    app.run()
