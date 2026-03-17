"""
Integration tests for the Graph API endpoints.
Tests request validation and error handling using Flask's test client.
"""

import io


def test_health_check(client):
    """GET /health returns 200 with status ok."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'


def test_generate_ontology_no_files(client):
    """POST /api/graph/ontology/generate without files returns 400."""
    response = client.post(
        '/api/graph/ontology/generate',
        data={'simulation_requirement': 'test requirement'},
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data


def test_generate_ontology_no_requirement(client):
    """POST /api/graph/ontology/generate with file but no simulation_requirement returns 400."""
    fake_file = (io.BytesIO(b'Some document content'), 'test.txt')
    response = client.post(
        '/api/graph/ontology/generate',
        data={'files': fake_file},
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'simulation_requirement' in data['error'].lower() or 'requirement' in data['error'].lower()


def test_list_projects(client):
    """GET /api/graph/project/list returns 200 with a list."""
    response = client.get('/api/graph/project/list')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)


def test_get_project_not_found(client):
    """GET /api/graph/project/<nonexistent-id> returns 404."""
    response = client.get('/api/graph/project/nonexistent-id')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'not found' in data['error'].lower()
