"""
Integration tests for the Report API endpoints.
Tests request validation and error handling using Flask's test client.
"""


def test_get_report_not_found(client):
    """GET /api/report/<nonexistent-id> returns 404."""
    response = client.get('/api/report/nonexistent-id')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'not found' in data['error'].lower()


def test_generate_report_missing_params(client):
    """POST /api/report/generate without simulation_id returns 400."""
    response = client.post(
        '/api/report/generate',
        json={},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'simulation_id' in data['error'].lower()
