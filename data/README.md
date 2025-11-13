# Data Directory

This directory contains your personal learning data. All files here are excluded from git for privacy.

## Files Created by the Server

- **challenges.json**: Your learning challenges and their status
- **progress.json**: Learning session records and progress tracking
- **reviews.json**: Spaced repetition review schedule

## File Structure Examples

### challenges.json
```json
{
  "ch_abc123": {
    "id": "ch_abc123",
    "topic": "Topic Name",
    "difficulty": "intermediate",
    "type": "practical",
    "description": "Challenge description",
    "status": "in_progress",
    "created_at": "2025-11-13T12:00:00.000000",
    "updated_at": "2025-11-13T12:00:00.000000",
    "time_spent_minutes": 45,
    "notes": [
      {
        "timestamp": "2025-11-13T12:00:00.000000",
        "text": "Note text"
      }
    ]
  }
}
```

### progress.json
```json
{
  "entries": [
    {
      "id": "pr_xyz789",
      "topic": "Topic Name",
      "activity": "What you did",
      "duration_minutes": 30,
      "mastery_rating": 7.5,
      "challenge_id": "ch_abc123",
      "notes": "Additional notes",
      "timestamp": "2025-11-13T12:00:00.000000"
    }
  ]
}
```

### reviews.json
```json
{
  "reviews": [
    {
      "id": "rv_def456",
      "topic": "Topic Name",
      "note_path": "path/to/note.md",
      "created_at": "2025-11-13T12:00:00.000000",
      "next_review": "2025-11-14T12:00:00.000000",
      "interval_days": 1,
      "repetitions": 0,
      "ease_factor": 2.5
    }
  ]
}
```

## Privacy

These files contain your personal learning data and should not be committed to version control. The `.gitignore` file is configured to exclude all JSON files in this directory.
