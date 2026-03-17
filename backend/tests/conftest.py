import pytest
import os
import sys
from unittest.mock import MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Pre-mock heavy third-party modules so unit tests can import app.services.*
# without requiring zep_cloud, camel, etc. to be installed
for mod_name in [
    'zep_cloud', 'zep_cloud.client', 'zep_cloud.types',
    'camel', 'camel.models', 'camel.types',
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

@pytest.fixture
def app():
    """Create Flask test app"""
    # Set required env vars for testing
    os.environ.setdefault('LLM_API_KEY', 'test-api-key')
    os.environ.setdefault('ZEP_API_KEY', 'test-zep-key')
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()

@pytest.fixture
def tmp_text_file(tmp_path):
    """Create a temporary text file"""
    f = tmp_path / "test.txt"
    f.write_text("Hello world. This is a test document.")
    return str(f)

@pytest.fixture
def tmp_md_file(tmp_path):
    """Create a temporary markdown file"""
    f = tmp_path / "test.md"
    f.write_text("# Test\n\nThis is a markdown test document.")
    return str(f)
