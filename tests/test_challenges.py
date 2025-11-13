"""
Tests for challenge management tools
"""
import pytest
import json
import learning_server
from learning_server import (
    create_challenge,
    list_challenges,
    get_challenge,
    update_challenge_status
)


@pytest.mark.asyncio
async def test_create_challenge(mock_data_path, sample_challenge_data):
    """Test creating a challenge"""
    result = await create_challenge(
        sample_challenge_data["topic"],
        sample_challenge_data["difficulty"],
        sample_challenge_data["challenge_type"],
        sample_challenge_data.get("description")
    )

    assert len(result) == 1
    assert "Challenge Created" in result[0].text
    assert sample_challenge_data["topic"] in result[0].text

    # Verify file was created
    assert learning_server.CHALLENGES_FILE.exists()

    # Verify data structure
    data = json.loads(learning_server.CHALLENGES_FILE.read_text())
    assert len(data) == 1
    challenge = list(data.values())[0]
    assert challenge["topic"] == sample_challenge_data["topic"]
    assert challenge["difficulty"] == sample_challenge_data["difficulty"]
    assert challenge["status"] == "pending"


@pytest.mark.asyncio
async def test_create_challenge_without_description(mock_data_path):
    """Test creating a challenge without custom description"""
    result = await create_challenge("Python Basics", "beginner", "knowledge")

    assert len(result) == 1
    assert "Challenge Created" in result[0].text
    assert "Research and summarize" in result[0].text  # Default template


@pytest.mark.asyncio
async def test_list_challenges_empty(mock_data_path):
    """Test listing challenges when none exist"""
    result = await list_challenges()

    assert len(result) == 1
    assert "No challenges found" in result[0].text


@pytest.mark.asyncio
async def test_list_challenges(mock_data_path, sample_challenge_data):
    """Test listing challenges"""
    # Create a challenge first
    await create_challenge(
        sample_challenge_data["topic"],
        sample_challenge_data["difficulty"],
        sample_challenge_data["challenge_type"]
    )

    result = await list_challenges()

    assert len(result) == 1
    assert sample_challenge_data["topic"] in result[0].text
    assert "Pending" in result[0].text


@pytest.mark.asyncio
async def test_list_challenges_with_filters(mock_data_path):
    """Test listing challenges with filters"""
    # Create multiple challenges
    await create_challenge("Topic 1", "beginner", "knowledge")
    await create_challenge("Topic 2", "intermediate", "practical")

    # Filter by difficulty
    result = await list_challenges(difficulty="beginner")
    assert "Topic 1" in result[0].text
    assert "Topic 2" not in result[0].text


@pytest.mark.asyncio
async def test_get_challenge(mock_data_path, sample_challenge_data):
    """Test getting a specific challenge"""
    # Create a challenge
    create_result = await create_challenge(
        sample_challenge_data["topic"],
        sample_challenge_data["difficulty"],
        sample_challenge_data["challenge_type"]
    )

    # Extract ID from result
    lines = create_result[0].text.split('\n')
    challenge_id = None
    for line in lines:
        if line.startswith('**ID**:'):
            challenge_id = line.split(':', 1)[1].strip()
            break

    assert challenge_id is not None

    # Get the challenge
    result = await get_challenge(challenge_id)

    assert len(result) == 1
    assert sample_challenge_data["topic"] in result[0].text
    assert challenge_id in result[0].text


@pytest.mark.asyncio
async def test_get_challenge_not_found(mock_data_path):
    """Test getting a non-existent challenge"""
    result = await get_challenge("ch_invalid")

    assert len(result) == 1
    assert "not found" in result[0].text


@pytest.mark.asyncio
async def test_update_challenge_status(mock_data_path, sample_challenge_data):
    """Test updating challenge status"""
    # Create a challenge
    create_result = await create_challenge(
        sample_challenge_data["topic"],
        sample_challenge_data["difficulty"],
        sample_challenge_data["challenge_type"]
    )

    # Extract ID
    lines = create_result[0].text.split('\n')
    challenge_id = None
    for line in lines:
        if line.startswith('**ID**:'):
            challenge_id = line.split(':', 1)[1].strip()
            break

    # Update status
    result = await update_challenge_status(
        challenge_id,
        "in_progress",
        "Starting work on this"
    )

    assert len(result) == 1
    assert "status updated" in result[0].text

    # Verify in file
    data = json.loads(learning_server.CHALLENGES_FILE.read_text())
    assert data[challenge_id]["status"] == "in_progress"
    assert len(data[challenge_id]["notes"]) == 1


@pytest.mark.asyncio
async def test_update_challenge_status_not_found(mock_data_path):
    """Test updating a non-existent challenge"""
    result = await update_challenge_status("ch_invalid", "completed")

    assert len(result) == 1
    assert "not found" in result[0].text


@pytest.mark.asyncio
async def test_challenge_types(mock_data_path):
    """Test all challenge types generate appropriate descriptions"""
    types = ["knowledge", "practical", "teaching", "analysis", "creative"]

    for challenge_type in types:
        result = await create_challenge(
            f"Test {challenge_type}",
            "intermediate",
            challenge_type
        )
        assert len(result) == 1
        assert challenge_type.title() in result[0].text


@pytest.mark.asyncio
async def test_difficulty_levels(mock_data_path):
    """Test all difficulty levels work"""
    levels = ["beginner", "intermediate", "advanced", "expert"]

    for difficulty in levels:
        result = await create_challenge(
            f"Test {difficulty}",
            difficulty,
            "knowledge"
        )
        assert len(result) == 1
        assert difficulty.title() in result[0].text
