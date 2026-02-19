import psycopg
import os
from models.transactions import Transaction, Bike, Customer


DATE_FORMAT = "%Y-%m-%d"


def get_transactions() -> list[dict]:
    """
    Returns the list of transactions in the database as a serialized dictionary.
    """
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
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


def add_bike(bike: Bike) -> int:
    """
    Add a bike to the database and return its id.
    """
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor(row_factory=psycopg.rows.scalar_row) as cur:
            bike_id = cur.execute(
                "INSERT INTO bikes (make, model) VALUES (%s, %s) RETURNING bike_id;",
                (bike.make, bike.model),
            ).fetchone()
            assert bike_id is not None
            conn.commit()
            return bike_id


def add_or_update_customer(customer: Customer) -> int:
    """
    Add a customer to the database and return its id.

    If a customer in the database with the same email as provided is found, the customer's data
    old data will be overridden. IMPORTANT: this function is not idempotent due to this behavior.
    """
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor(row_factory=psycopg.rows.scalar_row) as cur:
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
                    customer.first_name,
                    customer.last_name,
                    customer.email,
                    customer.phone_number,
                ),
            ).fetchone()
            assert customer_id is not None
            conn.commit()
            return customer_id


def add_transaction(transaction: Transaction) -> int:
    """
    Add a transaction to the database and return its id.
    """
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor(row_factory=psycopg.rows.scalar_row) as cur:
            transaction_id = cur.execute(
                """
                INSERT INTO repair_transactions (bike_id, customer_id, total_cost, transaction_date)
                VALUES (%s, %s, %s, %s)
                RETURNING transaction_id;
                """,
                (
                    transaction.bike_id,
                    transaction.customer_id,
                    transaction.total_cost,
                    transaction.date,
                ),
            ).fetchone()
            assert transaction_id is not None
            conn.commit()
            return transaction_id


def delete_transaction(id: int) -> bool:
    """
    Delete a transaction from the database with the given id. Returns a boolean indicating if
    the operation was successful.

    If a value of `False` is returned, it means that the transaction with the given id did not
    exist in the database.
    """
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor(row_factory=psycopg.rows.scalar_row) as cur:
            deleted = cur.execute(
                "DELETE FROM repair_transactions WHERE transaction_id = %s RETURNING transaction_id;",
                (id,),
            ).fetchall()
            conn.commit()
            return len(deleted) == 1
