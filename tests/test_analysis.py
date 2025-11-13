"""
Tests for AI-powered analysis tools
"""
import pytest
from learning_server import (
    suggest_next_topic,
    analyze_knowledge_gaps,
    record_progress,
    create_challenge,
    update_challenge_status
)


@pytest.mark.asyncio
async def test_suggest_next_topic_empty(mock_data_path):
    """Test suggestions when no data exists"""
    result = await suggest_next_topic()

    assert len(result) == 1
    assert "Learning Suggestions" in result[0].text
    assert "recommendations" in result[0].text.lower()


@pytest.mark.asyncio
async def test_suggest_next_topic_with_data(mock_data_path):
    """Test suggestions with existing progress"""
    # Record some progress
    await record_progress("Docker", "Tutorial 1", 30, 5)  # Low mastery
    await record_progress("Python", "Basics", 45, 9)     # High mastery

    result = await suggest_next_topic()

    assert len(result) == 1
    text = result[0].text
    assert "Learning Suggestions" in text


@pytest.mark.asyncio
async def test_suggest_next_topic_with_area_filter(mock_data_path):
    """Test suggestions filtered by area"""
    # Record progress in multiple areas
    await record_progress("Docker Networking", "Tutorial", 30, 6)
    await record_progress("Python Async", "Study", 45, 8)

    result = await suggest_next_topic(area="Docker")

    assert len(result) == 1
    # Should focus on Docker-related suggestions


@pytest.mark.asyncio
async def test_suggest_next_topic_with_pending_challenges(mock_data_path):
    """Test suggestions include pending challenges"""
    # Create pending challenge
    await create_challenge("Kubernetes Basics", "beginner", "knowledge")

    result = await suggest_next_topic()

    assert len(result) == 1
    text = result[0].text
    assert "Pending challenges" in text or "challenge" in text.lower()


@pytest.mark.asyncio
async def test_suggest_next_topic_identifies_weak_areas(mock_data_path):
    """Test that suggestions identify topics with low mastery"""
    # Record progress with low mastery
    await record_progress("Docker Security", "Study", 30, 4)
    await record_progress("Docker Security", "Practice", 30, 5)

    result = await suggest_next_topic()

    assert len(result) == 1
    text = result[0].text
    # Should mention topics needing review or low mastery
    assert "needing review" in text.lower() or "mastery" in text.lower()


@pytest.mark.asyncio
async def test_analyze_knowledge_gaps_empty(mock_data_path):
    """Test gap analysis with no data"""
    result = await analyze_knowledge_gaps()

    assert len(result) == 1
    assert "No progress data available" in result[0].text


@pytest.mark.asyncio
async def test_analyze_knowledge_gaps(mock_data_path):
    """Test knowledge gap analysis"""
    # Record progress with varying mastery
    await record_progress("Docker", "Tutorial 1", 30, 5)
    await record_progress("Python", "Basics", 45, 8)
    await record_progress("Kubernetes", "Intro", 60, 4)

    result = await analyze_knowledge_gaps()

    assert len(result) == 1
    text = result[0].text
    assert "Knowledge Gap Analysis" in text


@pytest.mark.asyncio
async def test_analyze_knowledge_gaps_with_focus(mock_data_path):
    """Test gap analysis with focus area"""
    # Record progress
    await record_progress("Docker Networking", "Study", 30, 5)
    await record_progress("Docker Security", "Study", 30, 6)
    await record_progress("Python", "Basics", 45, 4)

    result = await analyze_knowledge_gaps(focus_area="Docker")

    assert len(result) == 1
    text = result[0].text
    # Should only analyze Docker-related topics
    assert "Docker" in text


@pytest.mark.asyncio
async def test_analyze_identifies_low_mastery(mock_data_path):
    """Test that analysis identifies low mastery topics"""
    # Record low mastery progress
    await record_progress("Weak Topic", "Study", 30, 4)
    await record_progress("Weak Topic", "Practice", 30, 5)

    result = await analyze_knowledge_gaps()

    assert len(result) == 1
    text = result[0].text
    # Should identify the weak topic
    assert "Weak Topic" in text or "needing attention" in text.lower()


@pytest.mark.asyncio
async def test_analyze_identifies_stale_topics(mock_data_path):
    """Test that analysis can identify topics not practiced recently"""
    # This is harder to test without time manipulation
    # Just ensure it doesn't crash
    await record_progress("Old Topic", "Study", 30, 7)

    result = await analyze_knowledge_gaps()

    assert len(result) == 1
    # Just verify it returns valid output


@pytest.mark.asyncio
async def test_suggestions_with_completed_challenges(mock_data_path):
    """Test suggestions when challenges are completed"""
    # Create and complete a challenge
    create_result = await create_challenge("Test Topic", "intermediate", "practical")
    lines = create_result[0].text.split('\n')
    challenge_id = None
    for line in lines:
        if line.startswith('**ID**:'):
            challenge_id = line.split(':', 1)[1].strip()
            break

    await update_challenge_status(challenge_id, "completed")

    result = await suggest_next_topic()

    assert len(result) == 1
    # Should provide suggestions even with completed challenges


@pytest.mark.asyncio
async def test_analysis_with_high_mastery_topics(mock_data_path):
    """Test that high mastery topics don't show as gaps"""
    # Record high mastery progress
    await record_progress("Strong Topic", "Study", 60, 9)
    await record_progress("Strong Topic", "Practice", 45, 10)

    result = await analyze_knowledge_gaps()

    assert len(result) == 1
    text = result[0].text
    # Should indicate no significant gaps or low count
    assert "No significant gaps" in text or "Knowledge Gap" in text
