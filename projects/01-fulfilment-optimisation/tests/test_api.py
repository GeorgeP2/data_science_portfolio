import copy
import json

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from fulfilment_optimisation.api.app import create_app
from fulfilment_optimisation.api.schemas import _EXAMPLE_REQUEST, _EXAMPLE_RESPONSE

from portfolio import ProjectPaths, load_config

CFG = load_config(ProjectPaths.from_file(__file__).config)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app(CFG))


def request(**changes):
    body = copy.deepcopy(_EXAMPLE_REQUEST)
    body.update(changes)
    return body


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_example_request_returns_documented_response(client):
    response = client.post("/batch", json=_EXAMPLE_REQUEST)
    assert response.status_code == 200
    body = response.json()
    assert body["solve_time_ms"] >= 0
    assert body == {**_EXAMPLE_RESPONSE, "solve_time_ms": body["solve_time_ms"]}


@pytest.mark.parametrize("router", ["s_shape", "largest_gap"])
def test_batches_cover_every_order_within_capacity(client, router):
    body = client.post("/batch", json=request(router=router, capacity=3)).json()
    ids = [i for batch in body["batches"] for i in batch["order_ids"]]
    assert sorted(ids) == [1, 2, 3, 4]
    assert all(batch["items"] <= 3 for batch in body["batches"])
    lengths = sum(batch["route"]["length"] for batch in body["batches"])
    assert body["total_distance"] == pytest.approx(lengths)


def test_custom_layout(client):
    layout = {
        "n_aisles": 2,
        "n_positions": 5,
        "location_length": 1.0,
        "aisle_spacing": 3.0,
        "end_offset": 1.0,
        "depot_offset": 0.0,
    }
    orders = [{"id": 7, "locations": [{"aisle": 1, "position": 4}]}]
    body = client.post("/batch", json=request(layout=layout, orders=orders)).json()
    # In and back to the last position of aisle 1: 2 * (3 across + 5 deep).
    assert body["total_distance"] == 16


def test_too_many_orders_is_413(client):
    orders = [
        {"id": i, "locations": [{"aisle": 0, "position": 0}]} for i in range(CFG.api.max_orders + 1)
    ]
    response = client.post("/batch", json=request(orders=orders))
    assert response.status_code == 413
    assert f"limit is {CFG.api.max_orders}" in response.json()["detail"]


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"capacity": 1}, "order 1 exceeds capacity 1"),
        (
            {"orders": [{"id": 1, "locations": [{"aisle": 10, "position": 0}]}]},
            "outside the layout",
        ),
        ({"layout": "nowhere"}, "unknown layout 'nowhere'"),
        ({"budget_ms": 60_000}, "over the limit"),
    ],
)
def test_unsolvable_requests_are_422(client, changes, message):
    response = client.post("/batch", json=request(**changes))
    assert response.status_code == 422
    assert message in response.json()["detail"]


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"solver": "magic"}, "unknown solver 'magic'"),
        ({"router": "teleport"}, "unknown router 'teleport'"),
        (
            {"orders": [{"id": 1, "locations": [{"aisle": 0, "position": 0}]}] * 2},
            "repeated: [1]",
        ),
        ({"orders": []}, "at least 1 item"),
        ({"capacity": 0}, "greater than or equal to 1"),
    ],
)
def test_invalid_fields_are_422(client, changes, message):
    response = client.post("/batch", json=request(**changes))
    assert response.status_code == 422
    assert any(message in error["msg"] for error in response.json()["detail"])


def test_openapi_has_examples(client):
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert schemas["BatchRequest"]["examples"] == [_EXAMPLE_REQUEST]
    assert schemas["BatchResponse"]["examples"] == [_EXAMPLE_RESPONSE]


def test_example_file_matches_documented_request():
    path = ProjectPaths.from_file(__file__).root / "examples" / "batch_request.json"
    assert json.loads(path.read_text()) == _EXAMPLE_REQUEST
