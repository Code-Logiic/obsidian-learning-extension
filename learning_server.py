#!/usr/bin/env python3
"""
MCP Learning Extension Server
Extends the official Obsidian MCP server with learning and second-brain features
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta
import uuid

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Initialize MCP server
app = Server("obsidian-learning-extension")

# Configuration
DATA_PATH = Path(os.getenv("DATA_PATH", "./data"))
CHALLENGES_FILE = DATA_PATH / "challenges.json"
PROGRESS_FILE = DATA_PATH / "progress.json"
REVIEWS_FILE = DATA_PATH / "reviews.json"

# Ensure data directory and files exist
DATA_PATH.mkdir(parents=True, exist_ok=True)

def load_json_file(filepath: Path, default: Any = None) -> Any:
    """Load JSON file or return default if not exists"""
    if filepath.exists():
        try:
            return json.loads(filepath.read_text())
        except Exception:
            return default or {}
    return default or {}

def save_json_file(filepath: Path, data: Any) -> None:
    """Save data to JSON file"""
    filepath.write_text(json.dumps(data, indent=2))


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available learning extension tools"""
    return [
        Tool(
            name="create_challenge",
            description="Create a learning challenge for a specific topic with AI-generated content",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic for the challenge (e.g., 'Docker Networking', 'Python Async')"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced", "expert"],
                        "description": "Difficulty level of the challenge"
                    },
                    "challenge_type": {
                        "type": "string",
                        "enum": ["knowledge", "practical", "teaching", "analysis", "creative"],
                        "description": "Type of challenge: knowledge (reading/research), practical (build something), teaching (explain to others), analysis (compare/evaluate), creative (design/synthesize)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional custom description for the challenge"
                    }
                },
                "required": ["topic", "difficulty", "challenge_type"]
            }
        ),
        Tool(
            name="list_challenges",
            description="List all challenges with optional filtering by status or difficulty",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "archived"],
                        "description": "Filter by status (optional)"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced", "expert"],
                        "description": "Filter by difficulty (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_challenge",
            description="Get detailed information about a specific challenge",
            inputSchema={
                "type": "object",
                "properties": {
                    "challenge_id": {
                        "type": "string",
                        "description": "ID of the challenge to retrieve"
                    }
                },
                "required": ["challenge_id"]
            }
        ),
        Tool(
            name="update_challenge_status",
            description="Update the status of a challenge",
            inputSchema={
                "type": "object",
                "properties": {
                    "challenge_id": {
                        "type": "string",
                        "description": "ID of the challenge"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "archived"],
                        "description": "New status"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes about the status change"
                    }
                },
                "required": ["challenge_id", "status"]
            }
        ),
        Tool(
            name="record_progress",
            description="Record learning progress for a topic or challenge",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic or subtopic being studied"
                    },
                    "activity": {
                        "type": "string",
                        "description": "What was done (e.g., 'Completed tutorial', 'Built demo project')"
                    },
                    "duration_minutes": {
                        "type": "number",
                        "description": "Time spent in minutes"
                    },
                    "mastery_rating": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Self-assessment of understanding (0-10)"
                    },
                    "challenge_id": {
                        "type": "string",
                        "description": "Optional challenge ID if this progress is related to a challenge"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes or learnings"
                    }
                },
                "required": ["topic", "activity", "duration_minutes", "mastery_rating"]
            }
        ),
        Tool(
            name="get_progress_stats",
            description="Get learning progress statistics and analytics",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Optional topic to filter stats (shows all if not provided)"
                    },
                    "days": {
                        "type": "number",
                        "description": "Number of days to look back (default: 30)"
                    }
                }
            }
        ),
        Tool(
            name="schedule_review",
            description="Schedule a spaced repetition review for a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to review"
                    },
                    "note_path": {
                        "type": "string",
                        "description": "Path to the note in Obsidian vault"
                    },
                    "initial_interval_days": {
                        "type": "number",
                        "description": "Initial review interval in days (default: 1)"
                    }
                },
                "required": ["topic", "note_path"]
            }
        ),
        Tool(
            name="get_due_reviews",
            description="Get all reviews that are due today or overdue",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="complete_review",
            description="Mark a review as completed and schedule next review based on performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "review_id": {
                        "type": "string",
                        "description": "ID of the review"
                    },
                    "performance": {
                        "type": "string",
                        "enum": ["weak", "moderate", "strong", "perfect"],
                        "description": "How well you remembered the material"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes about the review"
                    }
                },
                "required": ["review_id", "performance"]
            }
        ),
        Tool(
            name="suggest_next_topic",
            description="Get AI-powered suggestions for what to study next based on progress and gaps",
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Optional area to focus suggestions on (e.g., 'Docker', 'Python')"
                    }
                }
            }
        ),
        Tool(
            name="analyze_knowledge_gaps",
            description="Analyze your vault and progress to identify knowledge gaps and weak areas",
            inputSchema={
                "type": "object",
                "properties": {
                    "focus_area": {
                        "type": "string",
                        "description": "Optional area to focus the analysis on"
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        if name == "create_challenge":
            return await create_challenge(
                arguments["topic"],
                arguments["difficulty"],
                arguments["challenge_type"],
                arguments.get("description")
            )
        elif name == "list_challenges":
            return await list_challenges(
                arguments.get("status"),
                arguments.get("difficulty")
            )
        elif name == "get_challenge":
            return await get_challenge(arguments["challenge_id"])
        elif name == "update_challenge_status":
            return await update_challenge_status(
                arguments["challenge_id"],
                arguments["status"],
                arguments.get("notes")
            )
        elif name == "record_progress":
            return await record_progress(
                arguments["topic"],
                arguments["activity"],
                arguments["duration_minutes"],
                arguments["mastery_rating"],
                arguments.get("challenge_id"),
                arguments.get("notes")
            )
        elif name == "get_progress_stats":
            return await get_progress_stats(
                arguments.get("topic"),
                arguments.get("days", 30)
            )
        elif name == "schedule_review":
            return await schedule_review(
                arguments["topic"],
                arguments["note_path"],
                arguments.get("initial_interval_days", 1)
            )
        elif name == "get_due_reviews":
            return await get_due_reviews()
        elif name == "complete_review":
            return await complete_review(
                arguments["review_id"],
                arguments["performance"],
                arguments.get("notes")
            )
        elif name == "suggest_next_topic":
            return await suggest_next_topic(arguments.get("area"))
        elif name == "analyze_knowledge_gaps":
            return await analyze_knowledge_gaps(arguments.get("focus_area"))
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# Tool Implementations

async def create_challenge(
    topic: str,
    difficulty: str,
    challenge_type: str,
    description: Optional[str] = None
) -> list[TextContent]:
    """Create a new learning challenge"""
    challenge_id = f"ch_{uuid.uuid4().hex[:8]}"
    
    # Load existing challenges
    challenges = load_json_file(CHALLENGES_FILE, {})
    
    # Generate challenge details based on type and difficulty
    challenge_templates = {
        "knowledge": {
            "beginner": f"Research and summarize the basics of {topic}. Create a note explaining key concepts in simple terms.",
            "intermediate": f"Deep dive into {topic}. Compare different approaches and document your findings with examples.",
            "advanced": f"Critically analyze {topic}. Evaluate trade-offs, edge cases, and best practices.",
            "expert": f"Become an expert on {topic}. Write comprehensive documentation that could teach others."
        },
        "practical": {
            "beginner": f"Build a simple project demonstrating basic {topic} concepts.",
            "intermediate": f"Create a working application using {topic}. Include error handling and documentation.",
            "advanced": f"Develop a production-ready solution using {topic}. Optimize for performance and maintainability.",
            "expert": f"Design and implement a complex system showcasing advanced {topic} patterns."
        },
        "teaching": {
            "beginner": f"Explain {topic} to a beginner. Create analogies and simple examples.",
            "intermediate": f"Write a tutorial on {topic} that helps someone build something real.",
            "advanced": f"Create a comprehensive guide on {topic} covering common pitfalls and advanced techniques.",
            "expert": f"Develop a complete learning curriculum for {topic} with progression path."
        },
        "analysis": {
            "beginner": f"Compare 2-3 different approaches to {topic}. List pros and cons.",
            "intermediate": f"Analyze when and why to use {topic}. Provide concrete use cases.",
            "advanced": f"Evaluate {topic} in production scenarios. Consider scalability, security, and cost.",
            "expert": f"Conduct deep technical analysis of {topic}. Benchmark and document findings."
        },
        "creative": {
            "beginner": f"Design a simple solution using {topic}. Sketch or diagram your idea.",
            "intermediate": f"Create something innovative combining {topic} with other concepts.",
            "advanced": f"Architect a novel system leveraging {topic}. Document design decisions.",
            "expert": f"Pioneer new applications of {topic}. Push boundaries and document discoveries."
        }
    }
    
    generated_description = description or challenge_templates.get(challenge_type, {}).get(difficulty, f"Challenge on {topic}")
    
    challenge = {
        "id": challenge_id,
        "topic": topic,
        "difficulty": difficulty,
        "type": challenge_type,
        "description": generated_description,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "time_spent_minutes": 0,
        "notes": []
    }
    
    challenges[challenge_id] = challenge
    save_json_file(CHALLENGES_FILE, challenges)
    
    result = f"""✨ Challenge Created!

**ID**: {challenge_id}
**Topic**: {topic}
**Difficulty**: {difficulty.title()}
**Type**: {challenge_type.title()}

**Challenge**:
{generated_description}

**Status**: Pending

Use `update_challenge_status` to mark as in_progress when you start!
Use `record_progress` to track your work on this challenge.
"""
    
    return [TextContent(type="text", text=result)]


async def list_challenges(
    status: Optional[str] = None,
    difficulty: Optional[str] = None
) -> list[TextContent]:
    """List all challenges with optional filtering"""
    challenges = load_json_file(CHALLENGES_FILE, {})
    
    if not challenges:
        return [TextContent(type="text", text="No challenges found. Create one with `create_challenge`!")]
    
    # Filter challenges
    filtered = challenges.values()
    if status:
        filtered = [c for c in filtered if c["status"] == status]
    if difficulty:
        filtered = [c for c in filtered if c["difficulty"] == difficulty]
    
    if not filtered:
        return [TextContent(type="text", text=f"No challenges found matching filters (status={status}, difficulty={difficulty})")]
    
    # Group by status
    by_status = {}
    for c in filtered:
        by_status.setdefault(c["status"], []).append(c)
    
    result = "# Your Learning Challenges\n\n"
    
    for status_key in ["in_progress", "pending", "completed", "archived"]:
        items = by_status.get(status_key, [])
        if items:
            result += f"\n## {status_key.replace('_', ' ').title()} ({len(items)})\n\n"
            for c in sorted(items, key=lambda x: x["created_at"], reverse=True):
                icon = {"pending": "⏳", "in_progress": "🔥", "completed": "✅", "archived": "📦"}.get(c["status"], "•")
                result += f"{icon} **{c['topic']}** ({c['difficulty']}, {c['type']})\n"
                result += f"   ID: `{c['id']}` | Created: {c['created_at'][:10]}\n"
                if c.get("time_spent_minutes", 0) > 0:
                    result += f"   Time spent: {c['time_spent_minutes']} minutes\n"
                result += "\n"
    
    return [TextContent(type="text", text=result)]


async def get_challenge(challenge_id: str) -> list[TextContent]:
    """Get detailed challenge information"""
    challenges = load_json_file(CHALLENGES_FILE, {})
    
    if challenge_id not in challenges:
        return [TextContent(type="text", text=f"Challenge not found: {challenge_id}")]
    
    c = challenges[challenge_id]
    
    result = f"""# Challenge: {c['topic']}

**ID**: {c['id']}
**Difficulty**: {c['difficulty'].title()}
**Type**: {c['type'].title()}
**Status**: {c['status'].title()}
**Created**: {c['created_at']}
**Updated**: {c['updated_at']}
**Time Spent**: {c.get('time_spent_minutes', 0)} minutes

## Description
{c['description']}

## Notes
"""
    
    if c.get("notes"):
        for note in c["notes"]:
            result += f"\n- {note['timestamp'][:10]}: {note['text']}"
    else:
        result += "\nNo notes yet."
    
    return [TextContent(type="text", text=result)]


async def update_challenge_status(
    challenge_id: str,
    status: str,
    notes: Optional[str] = None
) -> list[TextContent]:
    """Update challenge status"""
    challenges = load_json_file(CHALLENGES_FILE, {})
    
    if challenge_id not in challenges:
        return [TextContent(type="text", text=f"Challenge not found: {challenge_id}")]
    
    challenges[challenge_id]["status"] = status
    challenges[challenge_id]["updated_at"] = datetime.now().isoformat()
    
    if notes:
        if "notes" not in challenges[challenge_id]:
            challenges[challenge_id]["notes"] = []
        challenges[challenge_id]["notes"].append({
            "timestamp": datetime.now().isoformat(),
            "text": notes
        })
    
    save_json_file(CHALLENGES_FILE, challenges)
    
    return [TextContent(type="text", text=f"✅ Challenge {challenge_id} status updated to: {status}")]


async def record_progress(
    topic: str,
    activity: str,
    duration_minutes: float,
    mastery_rating: float,
    challenge_id: Optional[str] = None,
    notes: Optional[str] = None
) -> list[TextContent]:
    """Record learning progress"""
    progress_data = load_json_file(PROGRESS_FILE, {"entries": []})
    
    entry = {
        "id": f"pr_{uuid.uuid4().hex[:8]}",
        "topic": topic,
        "activity": activity,
        "duration_minutes": duration_minutes,
        "mastery_rating": mastery_rating,
        "challenge_id": challenge_id,
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    }
    
    progress_data["entries"].append(entry)
    save_json_file(PROGRESS_FILE, progress_data)
    
    # Update challenge time if linked
    if challenge_id:
        challenges = load_json_file(CHALLENGES_FILE, {})
        if challenge_id in challenges:
            challenges[challenge_id]["time_spent_minutes"] = challenges[challenge_id].get("time_spent_minutes", 0) + duration_minutes
            save_json_file(CHALLENGES_FILE, challenges)
    
    result = f"""📊 Progress Recorded!

**Topic**: {topic}
**Activity**: {activity}
**Duration**: {duration_minutes} minutes
**Mastery Rating**: {mastery_rating}/10
"""
    if challenge_id:
        result += f"**Linked Challenge**: {challenge_id}\n"
    
    return [TextContent(type="text", text=result)]


async def get_progress_stats(
    topic: Optional[str] = None,
    days: int = 30
) -> list[TextContent]:
    """Get progress statistics"""
    progress_data = load_json_file(PROGRESS_FILE, {"entries": []})
    entries = progress_data["entries"]
    
    # Filter by date
    cutoff = datetime.now() - timedelta(days=days)
    entries = [e for e in entries if datetime.fromisoformat(e["timestamp"]) > cutoff]
    
    # Filter by topic if specified
    if topic:
        entries = [e for e in entries if topic.lower() in e["topic"].lower()]
    
    if not entries:
        return [TextContent(type="text", text=f"No progress data found for the last {days} days" + (f" for topic '{topic}'" if topic else ""))]
    
    # Calculate stats
    total_time = sum(e["duration_minutes"] for e in entries)
    avg_mastery = sum(e["mastery_rating"] for e in entries) / len(entries)
    topics = {}
    for e in entries:
        topics[e["topic"]] = topics.get(e["topic"], 0) + e["duration_minutes"]
    
    result = f"""📈 Learning Statistics (Last {days} days)

**Total Entries**: {len(entries)}
**Total Time**: {total_time:.0f} minutes ({total_time/60:.1f} hours)
**Average Mastery**: {avg_mastery:.1f}/10
**Active Days**: {len(set(e["timestamp"][:10] for e in entries))}

**Time by Topic**:
"""
    
    for t, mins in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]:
        result += f"- {t}: {mins:.0f} minutes ({mins/60:.1f} hours)\n"
    
    return [TextContent(type="text", text=result)]


async def schedule_review(
    topic: str,
    note_path: str,
    initial_interval_days: float = 1
) -> list[TextContent]:
    """Schedule a spaced repetition review"""
    reviews = load_json_file(REVIEWS_FILE, {"reviews": []})
    
    review_id = f"rv_{uuid.uuid4().hex[:8]}"
    next_review = datetime.now() + timedelta(days=initial_interval_days)
    
    review = {
        "id": review_id,
        "topic": topic,
        "note_path": note_path,
        "created_at": datetime.now().isoformat(),
        "next_review": next_review.isoformat(),
        "interval_days": initial_interval_days,
        "repetitions": 0,
        "ease_factor": 2.5
    }
    
    reviews["reviews"].append(review)
    save_json_file(REVIEWS_FILE, reviews)
    
    return [TextContent(type="text", text=f"📅 Review scheduled for {topic} on {next_review.strftime('%Y-%m-%d')}")]


async def get_due_reviews() -> list[TextContent]:
    """Get all due reviews"""
    reviews = load_json_file(REVIEWS_FILE, {"reviews": []})
    now = datetime.now()
    
    due = [r for r in reviews["reviews"] if datetime.fromisoformat(r["next_review"]) <= now]
    
    if not due:
        return [TextContent(type="text", text="🎉 No reviews due! Great job staying on top of your learning.")]
    
    result = f"📚 {len(due)} Review(s) Due\n\n"
    for r in sorted(due, key=lambda x: x["next_review"]):
        days_overdue = (now - datetime.fromisoformat(r["next_review"])).days
        overdue_text = f"({days_overdue} days overdue)" if days_overdue > 0 else "(due today)"
        result += f"**{r['topic']}** {overdue_text}\n"
        result += f"   ID: `{r['id']}`\n"
        result += f"   Note: {r['note_path']}\n"
        result += f"   Repetitions: {r['repetitions']}\n\n"
    
    return [TextContent(type="text", text=result)]


async def complete_review(
    review_id: str,
    performance: str,
    notes: Optional[str] = None
) -> list[TextContent]:
    """Complete a review and schedule next one"""
    reviews = load_json_file(REVIEWS_FILE, {"reviews": []})
    
    review = None
    for r in reviews["reviews"]:
        if r["id"] == review_id:
            review = r
            break
    
    if not review:
        return [TextContent(type="text", text=f"Review not found: {review_id}")]
    
    # Spaced repetition algorithm (simplified SM-2)
    performance_map = {"weak": 0, "moderate": 3, "strong": 4, "perfect": 5}
    quality = performance_map[performance]
    
    if quality >= 3:
        if review["repetitions"] == 0:
            interval = 1
        elif review["repetitions"] == 1:
            interval = 6
        else:
            interval = review["interval_days"] * review["ease_factor"]
        
        review["repetitions"] += 1
        review["ease_factor"] = max(1.3, review["ease_factor"] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    else:
        review["repetitions"] = 0
        interval = 1
    
    review["interval_days"] = interval
    review["next_review"] = (datetime.now() + timedelta(days=interval)).isoformat()
    review["last_performance"] = performance
    
    if notes:
        if "review_notes" not in review:
            review["review_notes"] = []
        review["review_notes"].append({
            "timestamp": datetime.now().isoformat(),
            "performance": performance,
            "notes": notes
        })
    
    save_json_file(REVIEWS_FILE, reviews)
    
    next_date = (datetime.now() + timedelta(days=interval)).strftime('%Y-%m-%d')
    return [TextContent(type="text", text=f"✅ Review completed! Next review: {next_date} ({interval:.1f} days)")]


async def suggest_next_topic(area: Optional[str] = None) -> list[TextContent]:
    """Suggest what to study next"""
    progress_data = load_json_file(PROGRESS_FILE, {"entries": []})
    challenges = load_json_file(CHALLENGES_FILE, {})
    
    # Analyze recent activity
    recent_topics = {}
    for entry in progress_data["entries"][-20:]:
        topic = entry["topic"]
        recent_topics[topic] = recent_topics.get(topic, [])
        recent_topics[topic].append(entry["mastery_rating"])
    
    # Find topics with low mastery
    weak_topics = []
    for topic, ratings in recent_topics.items():
        avg_rating = sum(ratings) / len(ratings)
        if avg_rating < 7:
            weak_topics.append((topic, avg_rating))
    
    # Find pending challenges
    pending = [c for c in challenges.values() if c["status"] == "pending"]
    
    result = "💡 Learning Suggestions\n\n"
    
    if weak_topics:
        result += "**Topics needing review** (low mastery scores):\n"
        for topic, rating in sorted(weak_topics, key=lambda x: x[1])[:5]:
            result += f"- {topic} (avg rating: {rating:.1f}/10)\n"
        result += "\n"
    
    if pending:
        result += f"**Pending challenges** ({len(pending)}):\n"
        for c in pending[:5]:
            result += f"- {c['topic']} ({c['difficulty']}, {c['type']})\n"
        result += "\n"
    
    result += "**General recommendations**:\n"
    result += "- Review topics you haven't practiced in a while\n"
    result += "- Start a pending challenge to build momentum\n"
    result += "- Create a new challenge in an area you want to grow\n"
    
    return [TextContent(type="text", text=result)]


async def analyze_knowledge_gaps(focus_area: Optional[str] = None) -> list[TextContent]:
    """Analyze knowledge gaps"""
    progress_data = load_json_file(PROGRESS_FILE, {"entries": []})
    
    if not progress_data["entries"]:
        return [TextContent(type="text", text="No progress data available yet. Start recording your learning!")]
    
    # Analyze by topic
    topic_analysis = {}
    for entry in progress_data["entries"]:
        topic = entry["topic"]
        if focus_area and focus_area.lower() not in topic.lower():
            continue
        
        if topic not in topic_analysis:
            topic_analysis[topic] = {
                "total_time": 0,
                "ratings": [],
                "last_activity": entry["timestamp"]
            }
        
        topic_analysis[topic]["total_time"] += entry["duration_minutes"]
        topic_analysis[topic]["ratings"].append(entry["mastery_rating"])
        if entry["timestamp"] > topic_analysis[topic]["last_activity"]:
            topic_analysis[topic]["last_activity"] = entry["timestamp"]
    
    # Identify gaps
    gaps = []
    for topic, data in topic_analysis.items():
        avg_rating = sum(data["ratings"]) / len(data["ratings"])
        days_since = (datetime.now() - datetime.fromisoformat(data["last_activity"])).days
        
        if avg_rating < 7 or days_since > 14:
            gaps.append({
                "topic": topic,
                "avg_rating": avg_rating,
                "days_since": days_since,
                "total_time": data["total_time"]
            })
    
    result = "🔍 Knowledge Gap Analysis\n\n"
    
    if gaps:
        result += "**Areas needing attention**:\n\n"
        for gap in sorted(gaps, key=lambda x: (x["avg_rating"], -x["days_since"]))[:10]:
            result += f"**{gap['topic']}**\n"
            result += f"  - Avg mastery: {gap['avg_rating']:.1f}/10\n"
            result += f"  - Last activity: {gap['days_since']} days ago\n"
            result += f"  - Total time: {gap['total_time']:.0f} minutes\n\n"
    else:
        result += "✅ No significant gaps found! Keep up the great work.\n"
    
    return [TextContent(type="text", text=result)]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())