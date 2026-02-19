import pytest
from app import create_app
from init_db import init_db


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    init_db()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_create_transactions(client):
    response = client.get("/api/transactions")
    assert response.status_code == 200
    assert response.json == [
        {
            "bike": {"id": 5, "make": "Santa Cruz", "model": "Hightower"},
            "customer": {
                "email": "sophie.kim@email.com",
                "first_name": "Sophie",
                "id": 4,
                "last_name": "Kim",
                "phone_number": "7135550104",
            },
            "total_cost": 55.0,
            "transaction_date": "2026-01-28",
            "transaction_id": 10,
        },
        {
            "bike": {"id": 4, "make": "Cannondale", "model": "Synapse"},
            "customer": {
                "email": "daniel.reed@email.com",
                "first_name": "Daniel",
                "id": 5,
                "last_name": "Reed",
                "phone_number": "7135550105",
            },
            "total_cost": 180.0,
            "transaction_date": "2026-01-25",
            "transaction_id": 9,
        },
        {
            "bike": {"id": 3, "make": "Giant", "model": "Defy"},
            "customer": {
                "email": "maria.lopez@email.com",
                "first_name": "Maria",
                "id": 2,
                "last_name": "Lopez",
                "phone_number": "7135550102",
            },
            "total_cost": 95.75,
            "transaction_date": "2026-01-22",
            "transaction_id": 8,
        },
        {
            "bike": {"id": 2, "make": "Specialized", "model": "Allez"},
            "customer": {
                "email": "james.carter@email.com",
                "first_name": "James",
                "id": 3,
                "last_name": "Carter",
                "phone_number": "7135550103",
            },
            "total_cost": 60.0,
            "transaction_date": "2026-01-20",
            "transaction_id": 7,
        },
        {
            "bike": {"id": 1, "make": "Trek", "model": "Domane"},
            "customer": {
                "email": "alex.nguyen@email.com",
                "first_name": "Alex",
                "id": 1,
                "last_name": "Nguyen",
                "phone_number": "7135550101",
            },
            "total_cost": 150.0,
            "transaction_date": "2026-01-18",
            "transaction_id": 6,
        },
        {
            "bike": {"id": 5, "make": "Santa Cruz", "model": "Hightower"},
            "customer": {
                "email": "daniel.reed@email.com",
                "first_name": "Daniel",
                "id": 5,
                "last_name": "Reed",
                "phone_number": "7135550105",
            },
            "total_cost": 75.25,
            "transaction_date": "2026-01-15",
            "transaction_id": 5,
        },
        {
            "bike": {"id": 4, "make": "Cannondale", "model": "Synapse"},
            "customer": {
                "email": "sophie.kim@email.com",
                "first_name": "Sophie",
                "id": 4,
                "last_name": "Kim",
                "phone_number": "7135550104",
            },
            "total_cost": 200.0,
            "transaction_date": "2026-01-12",
            "transaction_id": 4,
        },
        {
            "bike": {"id": 3, "make": "Giant", "model": "Defy"},
            "customer": {
                "email": "james.carter@email.com",
                "first_name": "James",
                "id": 3,
                "last_name": "Carter",
                "phone_number": "7135550103",
            },
            "total_cost": 45.5,
            "transaction_date": "2026-01-10",
            "transaction_id": 3,
        },
        {
            "bike": {"id": 2, "make": "Specialized", "model": "Allez"},
            "customer": {
                "email": "maria.lopez@email.com",
                "first_name": "Maria",
                "id": 2,
                "last_name": "Lopez",
                "phone_number": "7135550102",
            },
            "total_cost": 120.0,
            "transaction_date": "2026-01-08",
            "transaction_id": 2,
        },
        {
            "bike": {"id": 1, "make": "Trek", "model": "Domane"},
            "customer": {
                "email": "alex.nguyen@email.com",
                "first_name": "Alex",
                "id": 1,
                "last_name": "Nguyen",
                "phone_number": "7135550101",
            },
            "total_cost": 89.99,
            "transaction_date": "2026-01-05",
            "transaction_id": 1,
        },
    ]


def test_create_transaction(client):
    create_response = client.post(
        "/api/transactions/create",
        json={
            "date": "2025-02-17",
            "total_cost": 20.20,
            "customer": {
                "first_name": "Diego",
                "last_name": "Frias",
                "email": "mail@dzfrias.dev",
            },
            "bike": {"make": "Domane", "model": "Trek"},
        },
    )
    assert create_response.status_code == 201
    assert create_response.json == {"id": 11}
    get_response = client.get("/api/transactions")
    assert get_response.status_code == 200
    assert get_response.json[-1]["transaction_id"] == 11


def test_delete_transaction(client):
    delete_response = client.delete("/api/transactions/delete/1")
    assert delete_response.status_code == 204
    get_response = client.get("/api/transactions")
    assert get_response.status_code == 200
    assert all(transaction["transaction_id"] != 1 for transaction in get_response.json)


def test_double_delete_transaction(client):
    delete_response = client.delete("/api/transactions/delete/1")
    assert delete_response.status_code == 204
    delete_response2 = client.delete("/api/transactions/delete/1")
    assert delete_response2.status_code == 404
