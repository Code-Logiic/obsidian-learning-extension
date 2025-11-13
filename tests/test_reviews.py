"""
Tests for spaced repetition review tools
"""
import pytest
import json
from datetime import datetime, timedelta
import learning_server
from learning_server import (
    schedule_review,
    get_due_reviews,
    complete_review
)


@pytest.mark.asyncio
async def test_schedule_review(mock_data_path, sample_review_data):
    """Test scheduling a review"""
    result = await schedule_review(
        sample_review_data["topic"],
        sample_review_data["note_path"],
        sample_review_data["initial_interval_days"]
    )

    assert len(result) == 1
    assert "Review scheduled" in result[0].text
    assert sample_review_data["topic"] in result[0].text

    # Verify file
    assert learning_server.REVIEWS_FILE.exists()
    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    assert len(data["reviews"]) == 1
    review = data["reviews"][0]
    assert review["topic"] == sample_review_data["topic"]
    assert review["ease_factor"] == 2.5  # Default SM-2 ease factor


@pytest.mark.asyncio
async def test_schedule_review_custom_interval(mock_data_path):
    """Test scheduling with custom interval"""
    result = await schedule_review("Test Topic", "notes/test.md", 7)

    assert len(result) == 1

    # Verify interval
    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review = data["reviews"][0]
    assert review["interval_days"] == 7


@pytest.mark.asyncio
async def test_get_due_reviews_empty(mock_data_path):
    """Test getting due reviews when none exist"""
    result = await get_due_reviews()

    assert len(result) == 1
    assert "No reviews due" in result[0].text


@pytest.mark.asyncio
async def test_get_due_reviews_none_due(mock_data_path):
    """Test when reviews exist but none are due"""
    # Schedule review for tomorrow
    await schedule_review("Test Topic", "notes/test.md", 1)

    result = await get_due_reviews()

    assert len(result) == 1
    assert "No reviews due" in result[0].text


@pytest.mark.asyncio
async def test_get_due_reviews_with_due(mock_data_path):
    """Test getting reviews that are due"""
    # Schedule review for yesterday (overdue)
    await schedule_review("Test Topic", "notes/test.md", 1)

    # Manually adjust the next_review date to make it overdue
    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    data["reviews"][0]["next_review"] = (datetime.now() - timedelta(days=1)).isoformat()
    learning_server.REVIEWS_FILE.write_text(json.dumps(data, indent=2))

    result = await get_due_reviews()

    assert len(result) == 1
    assert "Review(s) Due" in result[0].text
    assert "Test Topic" in result[0].text


@pytest.mark.asyncio
async def test_complete_review(mock_data_path):
    """Test completing a review"""
    # Schedule a review
    await schedule_review("Test Topic", "notes/test.md", 1)

    # Get review ID
    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review_id = data["reviews"][0]["id"]

    # Complete the review
    result = await complete_review(review_id, "strong", "Good recall")

    assert len(result) == 1
    assert "Review completed" in result[0].text
    assert "Next review" in result[0].text

    # Verify review was updated
    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review = data["reviews"][0]
    assert review["repetitions"] == 1
    assert review["last_performance"] == "strong"


@pytest.mark.asyncio
async def test_complete_review_not_found(mock_data_path):
    """Test completing a non-existent review"""
    result = await complete_review("rv_invalid", "strong")

    assert len(result) == 1
    assert "not found" in result[0].text


@pytest.mark.asyncio
async def test_complete_review_performance_levels(mock_data_path):
    """Test SM-2 algorithm with different performance levels"""
    performances = ["weak", "moderate", "strong", "perfect"]

    for performance in performances:
        # Schedule review
        await schedule_review(f"Topic {performance}", "notes/test.md", 1)

        # Get review ID
        data = json.loads(learning_server.REVIEWS_FILE.read_text())
        review_id = data["reviews"][-1]["id"]

        # Complete review
        result = await complete_review(review_id, performance)

        assert len(result) == 1
        assert "Review completed" in result[0].text


@pytest.mark.asyncio
async def test_sm2_algorithm_intervals(mock_data_path):
    """Test that SM-2 algorithm adjusts intervals correctly"""
    # Schedule initial review
    await schedule_review("Test SM-2", "notes/test.md", 1)

    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review_id = data["reviews"][0]["id"]

    # First review with strong performance
    await complete_review(review_id, "strong")

    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review = data["reviews"][0]
    first_interval = review["interval_days"]

    # Second review with strong performance
    await complete_review(review_id, "strong")

    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review = data["reviews"][0]
    second_interval = review["interval_days"]

    # Interval should increase
    assert second_interval > first_interval


@pytest.mark.asyncio
async def test_weak_performance_resets_repetitions(mock_data_path):
    """Test that weak performance resets repetition count"""
    # Schedule and complete multiple times
    await schedule_review("Test Reset", "notes/test.md", 1)

    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review_id = data["reviews"][0]["id"]

    # Complete with strong performance
    await complete_review(review_id, "strong")
    await complete_review(review_id, "strong")

    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    reps_before = data["reviews"][0]["repetitions"]
    assert reps_before > 0

    # Complete with weak performance
    await complete_review(review_id, "weak")

    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review = data["reviews"][0]

    # Repetitions should be reset
    assert review["repetitions"] == 0
    assert review["interval_days"] == 1  # Back to 1 day


@pytest.mark.asyncio
async def test_review_notes(mock_data_path):
    """Test that review notes are saved"""
    await schedule_review("Test Notes", "notes/test.md", 1)

    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review_id = data["reviews"][0]["id"]

    # Complete with notes
    await complete_review(review_id, "strong", "Remembered everything clearly")

    data = json.loads(learning_server.REVIEWS_FILE.read_text())
    review = data["reviews"][0]

    assert "review_notes" in review
    assert len(review["review_notes"]) == 1
    assert review["review_notes"][0]["notes"] == "Remembered everything clearly"
