"""
Pytest configuration and fixtures for testing
"""
import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir)


@pytest.fixture(autouse=True)
def mock_data_path(temp_data_dir, monkeypatch):
    """Mock the DATA_PATH for tests"""
    import learning_server

    # Ensure temp directory exists
    temp_data_dir.mkdir(parents=True, exist_ok=True)

    # Set environment variable before importing
    monkeypatch.setenv('DATA_PATH', str(temp_data_dir))

    # Update module-level variables
    monkeypatch.setattr(learning_server, 'DATA_PATH', temp_data_dir)
    monkeypatch.setattr(learning_server, 'CHALLENGES_FILE', temp_data_dir / 'challenges.json')
    monkeypatch.setattr(learning_server, 'PROGRESS_FILE', temp_data_dir / 'progress.json')
    monkeypatch.setattr(learning_server, 'REVIEWS_FILE', temp_data_dir / 'reviews.json')

    # Recreate data directory
    temp_data_dir.mkdir(parents=True, exist_ok=True)

    return temp_data_dir


@pytest.fixture
def sample_challenge_data():
    """Sample challenge data for testing"""
    return {
        "topic": "Docker Networking",
        "difficulty": "intermediate",
        "challenge_type": "practical",
        "description": "Test challenge description"
    }


@pytest.fixture
def sample_progress_data():
    """Sample progress data for testing"""
    return {
        "topic": "Docker Networking",
        "activity": "Completed tutorial",
        "duration_minutes": 45,
        "mastery_rating": 7.5,
        "notes": "Good understanding"
    }


@pytest.fixture
def sample_review_data():
    """Sample review data for testing"""
    return {
        "topic": "Docker Basics",
        "note_path": "notes/docker.md",
        "initial_interval_days": 1
    }
