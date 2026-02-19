import psycopg
import os
from pathlib import Path


def init_db() -> None:
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            schema_contents = Path("schema.sql").read_text()
            cur.execute(schema_contents)
            conn.commit()


if __name__ == "__main__":
    init_db()
