"""
Tests for progress tracking tools
"""
import pytest
import json
import learning_server
from learning_server import (
    record_progress,
    get_progress_stats,
    create_challenge
)


@pytest.mark.asyncio
async def test_record_progress(mock_data_path, sample_progress_data):
    """Test recording progress"""
    result = await record_progress(
        sample_progress_data["topic"],
        sample_progress_data["activity"],
        sample_progress_data["duration_minutes"],
        sample_progress_data["mastery_rating"],
        notes=sample_progress_data["notes"]
    )

    assert len(result) == 1
    assert "Progress Recorded" in result[0].text
    assert str(sample_progress_data["duration_minutes"]) in result[0].text

    # Verify file
    assert learning_server.PROGRESS_FILE.exists()
    data = json.loads(learning_server.PROGRESS_FILE.read_text())
    assert len(data["entries"]) == 1
    assert data["entries"][0]["topic"] == sample_progress_data["topic"]


@pytest.mark.asyncio
async def test_record_progress_with_challenge(mock_data_path, sample_progress_data):
    """Test recording progress linked to a challenge"""
    # Create a challenge first
    create_result = await create_challenge("Test Topic", "intermediate", "practical")
    lines = create_result[0].text.split('\n')
    challenge_id = None
    for line in lines:
        if line.startswith('**ID**:'):
            challenge_id = line.split(':', 1)[1].strip()
            break

    # Record progress with challenge link
    result = await record_progress(
        sample_progress_data["topic"],
        sample_progress_data["activity"],
        sample_progress_data["duration_minutes"],
        sample_progress_data["mastery_rating"],
        challenge_id=challenge_id
    )

    assert len(result) == 1
    assert challenge_id in result[0].text

    # Verify challenge time was updated
    challenges = json.loads(learning_server.CHALLENGES_FILE.read_text())
    assert challenges[challenge_id]["time_spent_minutes"] == sample_progress_data["duration_minutes"]


@pytest.mark.asyncio
async def test_record_progress_mastery_bounds(mock_data_path):
    """Test progress recording with various mastery ratings"""
    # Test valid ratings
    for rating in [0, 5, 10]:
        result = await record_progress("Test", "Activity", 30, rating)
        assert len(result) == 1
        assert "Progress Recorded" in result[0].text


@pytest.mark.asyncio
async def test_get_progress_stats_empty(mock_data_path):
    """Test getting stats when no progress exists"""
    result = await get_progress_stats()

    assert len(result) == 1
    assert "No progress data found" in result[0].text


@pytest.mark.asyncio
async def test_get_progress_stats(mock_data_path):
    """Test getting progress statistics"""
    # Record some progress
    await record_progress("Docker", "Tutorial 1", 30, 7)
    await record_progress("Docker", "Tutorial 2", 45, 8)
    await record_progress("Python", "Basics", 60, 6)

    result = await get_progress_stats()

    assert len(result) == 1
    text = result[0].text
    assert "Total Entries**: 3" in text
    assert "Total Time**: 135 minutes" in text
    assert "Docker" in text
    assert "Python" in text


@pytest.mark.asyncio
async def test_get_progress_stats_filtered_by_topic(mock_data_path):
    """Test getting stats filtered by topic"""
    # Record progress for multiple topics
    await record_progress("Docker", "Tutorial", 30, 7)
    await record_progress("Python", "Basics", 45, 8)

    result = await get_progress_stats(topic="Docker")

    assert len(result) == 1
    text = result[0].text
    assert "Docker" in text
    assert "Python" not in text


@pytest.mark.asyncio
async def test_get_progress_stats_filtered_by_days(mock_data_path):
    """Test getting stats filtered by days"""
    # Record progress
    await record_progress("Docker", "Tutorial", 30, 7)

    # Get stats for last 7 days
    result = await get_progress_stats(days=7)

    assert len(result) == 1
    assert "Last 7 days" in result[0].text


@pytest.mark.asyncio
async def test_progress_accumulation(mock_data_path):
    """Test that progress accumulates correctly"""
    # Record multiple sessions
    times = [30, 45, 60]
    for i, duration in enumerate(times):
        await record_progress(f"Topic {i}", "Activity", duration, 7)

    result = await get_progress_stats()

    assert len(result) == 1
    total = sum(times)
    assert f"Total Time**: {total} minutes" in result[0].text


@pytest.mark.asyncio
async def test_average_mastery_calculation(mock_data_path):
    """Test that average mastery is calculated correctly"""
    # Record with specific ratings
    await record_progress("Test", "Activity 1", 30, 6)
    await record_progress("Test", "Activity 2", 30, 8)

    result = await get_progress_stats()

    assert len(result) == 1
    # Average should be 7.0
    assert "Average Mastery**: 7.0/10" in result[0].text
