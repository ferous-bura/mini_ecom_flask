def test_register(client):
    response = client.post('/auth/register', json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "test123"
    })
    assert response.status_code == 201
    assert "token" in response.json