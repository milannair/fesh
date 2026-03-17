"""
Integration tests for the Simulation API endpoints.
Tests request validation and error handling using Flask's test client.
"""


def test_list_simulations(client):
    """GET /api/simulation/list returns 200 with a list."""
    response = client.get('/api/simulation/list')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)


def test_get_simulation_not_found(client):
    """GET /api/simulation/<nonexistent-id> returns 404."""
    response = client.get('/api/simulation/nonexistent-id')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'not found' in data['error'].lower()
