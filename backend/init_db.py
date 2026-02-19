import psycopg
from pathlib import Path


# TODO: glboal constants file
POSTGRESQL_OPTIONS = {
    "host": "localhost",
    "port": 5432,
    "dbname": "ricebikesdb",
    "user": "ricebikes",
    "password": "ricebikes",
}


def init_db() -> None:
    with psycopg.connect(**POSTGRESQL_OPTIONS) as conn:
        with conn.cursor() as cur:
            schema_contents = Path("schema.sql").read_text()
            cur.execute(schema_contents)
            conn.commit()


if __name__ == "__main__":
    init_db()
