import pytest

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_health(api_client):
    response = await api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.parametrize("a,b,expected", [(10, 2, 5), (-6, 2, -3), (0, 2, 0)])
async def test_division(api_client, a, b, expected):
    response = await api_client.post("/divide", json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json() == {"result": expected}


async def test_zero_denominator(api_client):
    response = await api_client.post("/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert response.json() == {"detail": "denominator must not be zero"}


@pytest.mark.parametrize("body", [{"a": 10}, {"a": "invalid", "b": 2}])
async def test_invalid_body(api_client, body):
    response = await api_client.post("/divide", json=body)
    assert response.status_code == 422


async def test_missing_route(api_client):
    assert (await api_client.get("/unknown")).status_code == 404
