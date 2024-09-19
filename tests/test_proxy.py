import pytest
from fastapi.testclient import TestClient
import httpx
from app.main import app


client = TestClient(app)


@pytest.mark.asyncio
async def test_change_version():
    response = client.get("/version")
    assert response.json() == {}
    response = client.put("/version/client123", json={"version": "2.0"})
    assert response.status_code == 200
    assert response.json() == {'message': 'Client client123 version updated', 'client_version': '2.0'}
    response = client.get("/version")
    assert response.json() == {'client123': '2.0'}


@pytest.mark.asyncio
async def test_proxy_post_with_header(mocker, caplog):

    mock_response = httpx.Response(
        status_code=200,
        json={"type": "user_message",
              "id": "403918316",
              "created_at": 1719492969,
              "body": "heyy",
              "message_type": "inapp",
              "conversation_id": "476"},
        request=httpx.Request(method='get', url='/conversations/12')

    )
    mocker.patch("httpx.AsyncClient.request", return_value=mock_response)

    response = client.post("/conversations/12", headers={"Client-API-Version": "2.0"})
    assert "'Intercom-Version': '2.0'" in caplog.text
    assert response.status_code == 200
    assert "body" in response.json()


@pytest.mark.asyncio
async def test_proxy_get(mocker, caplog):
    mock_response = httpx.Response(
        status_code=200,
        json={"data": "mocked response"},
        request=httpx.Request(method='get', url='/contacts/12')
    )
    mocker.patch("httpx.AsyncClient.request", return_value=mock_response)

    response = client.get("/contacts/12", headers={"Client-ID": "client_1"})
    assert "'Intercom-Version': '1.0'" in caplog.text
    assert response.status_code == 200
    assert response.json() == {"data": "mocked response"}


@pytest.mark.asyncio
async def test_wrong_url():
    response = client.get('/test')
    assert response.status_code == 403
    assert response.text == 'Access denied'


@pytest.mark.asyncio
async def test_wrong_rate_limit(mocker):
    mock_response = httpx.Response(
        status_code=429,
        json={"error": "rate limit"},
        request=httpx.Request(method='get', url='/contacts/12')
    )
    mocker.patch("httpx.AsyncClient.request", return_value=mock_response)

    response = client.get("/contacts/12", headers={"Client-ID": "123"})
    assert response.text == 'Rate limit exceeded for client 123'