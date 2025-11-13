# Obsidian Learning Extension MCP Server

A Model Context Protocol (MCP) server that extends the official Obsidian MCP server with intelligent learning and second-brain features.

## Features

### 🎯 Challenge System
- **AI-Generated Challenges**: Create personalized learning challenges based on topic, difficulty, and type
- **Progress Tracking**: Monitor time spent and status for each challenge
- **Challenge Types**: Knowledge, Practical, Teaching, Analysis, Creative
- **Difficulty Levels**: Beginner, Intermediate, Advanced, Expert

### 📊 Progress Analytics
- **Activity Recording**: Track learning sessions with duration and mastery ratings
- **Statistics Dashboard**: View time spent, average mastery, and activity trends
- **Topic Analysis**: See time distribution across different topics
- **Performance Insights**: Identify areas for improvement

### 🔄 Spaced Repetition
- **Smart Scheduling**: Automatically schedule reviews based on spaced repetition algorithm
- **Performance-Based Intervals**: Review intervals adjust based on how well you remember
- **Due Review Tracking**: Get notifications for overdue reviews
- **Note Integration**: Link reviews directly to Obsidian notes

### 🧠 Knowledge Gap Analysis
- **Identify Weak Areas**: Find topics with low mastery scores
- **Activity Tracking**: See which topics haven't been practiced recently
- **Personalized Suggestions**: Get AI-powered recommendations for what to study next
- **Focus Analysis**: Analyze specific areas or your entire knowledge base

## Prerequisites

- Docker and Docker Compose
- Official Obsidian MCP server (from Docker) already set up
- Claude Desktop configured with Obsidian MCP

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/obsidian-learning-extension.git
cd obsidian-learning-extension
```

### 2. Build the Docker Image

```bash
docker-compose build
```

### 3. Test the Server

```bash
docker-compose up
```

The server should start and wait for stdio communication.

## Configuration

### Add to Claude Desktop Config

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the learning extension server alongside your existing Obsidian server:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "OBSIDIAN_HOST",
        "-e", "OBSIDIAN_API_KEY",
        "mcp/obsidian"
      ],
      "env": {
        "OBSIDIAN_HOST": "host.docker.internal",
        "OBSIDIAN_API_KEY": "YOUR_API_KEY"
      }
    },
    "obsidian-learning": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/ABSOLUTE/PATH/TO/obsidian-learning-extension/data:/data:rw",
        "obsidian-learning-extension:latest"
      ]
    }
  }
}
```

**Important**: Replace `/ABSOLUTE/PATH/TO/obsidian-learning-extension` with your actual path!

### Restart Claude Desktop

Completely quit and reopen Claude Desktop to load the new server.

## Available Tools

### Challenge Management

#### `create_challenge`
Create a new learning challenge with AI-generated content.

**Parameters**:
- `topic` (string): Topic to learn (e.g., "Docker Networking")
- `difficulty` (enum): beginner, intermediate, advanced, expert
- `challenge_type` (enum): knowledge, practical, teaching, analysis, creative
- `description` (string, optional): Custom challenge description

**Example**:
```
"Create an intermediate practical challenge on Docker networking"
```

#### `list_challenges`
List all challenges with optional filtering.

**Parameters**:
- `status` (enum, optional): pending, in_progress, completed, archived
- `difficulty` (enum, optional): Filter by difficulty level

**Example**:
```
"Show me all my in-progress challenges"
```

#### `get_challenge`
Get detailed information about a specific challenge.

**Parameters**:
- `challenge_id` (string): ID of the challenge

#### `update_challenge_status`
Update challenge status and add notes.

**Parameters**:
- `challenge_id` (string): Challenge ID
- `status` (enum): pending, in_progress, completed, archived
- `notes` (string, optional): Notes about the status change

**Example**:
```
"Mark challenge ch_abc123 as completed with notes: Built a working multi-container app"
```

### Progress Tracking

#### `record_progress`
Record a learning session.

**Parameters**:
- `topic` (string): What you studied
- `activity` (string): What you did
- `duration_minutes` (number): Time spent
- `mastery_rating` (number): Self-assessment 0-10
- `challenge_id` (string, optional): Link to a challenge
- `notes` (string, optional): Additional notes

**Example**:
```
"Record 45 minutes learning Docker volumes, mastery 7/10, completed tutorial"
```

#### `get_progress_stats`
View learning statistics and analytics.

**Parameters**:
- `topic` (string, optional): Filter by topic
- `days` (number, optional): Days to look back (default: 30)

**Example**:
```
"Show my learning stats for the last 7 days"
```

### Spaced Repetition

#### `schedule_review`
Schedule a review for spaced repetition.

**Parameters**:
- `topic` (string): Topic to review
- `note_path` (string): Path to note in Obsidian
- `initial_interval_days` (number, optional): First review interval

**Example**:
```
"Schedule a review for Docker networking, note at Software Development/Docker Networking.md"
```

#### `get_due_reviews`
Get all reviews that are due or overdue.

**Example**:
```
"What reviews are due today?"
```

#### `complete_review`
Mark a review as completed and schedule the next one.

**Parameters**:
- `review_id` (string): Review ID
- `performance` (enum): weak, moderate, strong, perfect
- `notes` (string, optional): Review notes

**Example**:
```
"Complete review rv_abc123 with strong performance"
```

### Knowledge Analysis

#### `suggest_next_topic`
Get AI suggestions for what to study next.

**Parameters**:
- `area` (string, optional): Focus area (e.g., "Docker")

**Example**:
```
"What should I study next?"
```

#### `analyze_knowledge_gaps`
Analyze your learning to find gaps and weak areas.

**Parameters**:
- `focus_area` (string, optional): Area to analyze

**Example**:
```
"Analyze my knowledge gaps in programming"
```

## Usage Examples

### Getting Started

```
Claude: "Create a beginner knowledge challenge on Python async/await"
Claude: "List all my pending challenges"
Claude: "Update challenge ch_abc123 to in_progress"
```

### During Learning

```
Claude: "Record 30 minutes studying async programming, mastery 6/10"
Claude: "What are my learning stats this week?"
```

### Maintaining Knowledge

```
Claude: "Schedule a review for async programming at Python/Async.md"
Claude: "What reviews are due?"
Claude: "Complete review rv_xyz789 with strong performance"
```

### Getting Insights

```
Claude: "What should I study next?"
Claude: "Analyze my knowledge gaps"
Claude: "Show challenges with low mastery scores"
```

## Data Storage

All data is stored in JSON files in the `data/` directory:

- `challenges.json`: Challenge definitions and status
- `progress.json`: Learning activity log
- `reviews.json`: Spaced repetition schedule

These files are automatically created and maintained by the server.

## Architecture

```
┌─────────────────┐
│  Claude Desktop │
└────────┬────────┘
         │
    ┌────┴─────────────────┐
    │                      │
┌───▼────────┐    ┌───────▼────────┐
│ Official   │    │   Learning     │
│ Obsidian   │    │   Extension    │
│ MCP Server │    │   MCP Server   │
└───┬────────┘    └────────┬───────┘
    │                      │
┌───▼────────────┐    ┌────▼──────┐
│ Obsidian Vault │    │   JSON    │
│  (via REST)    │    │   Data    │
└────────────────┘    └───────────┘
```

Both servers work together:
- **Official server**: Handles all Obsidian file operations
- **Learning extension**: Provides intelligent learning features

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python learning_server.py
```

### Building Docker Image

```bash
docker-compose build
```

### Viewing Logs

```bash
# With docker-compose
docker-compose logs -f

# With docker
docker logs obsidian-learning -f
```

### Debugging

Use the MCP Inspector for debugging:

```bash
npx @modelcontextprotocol/inspector python learning_server.py
```

## Troubleshooting

### Server Won't Start
- Check Docker is running: `docker ps`
- Rebuild image: `docker-compose build --no-cache`
- Check logs: `docker-compose logs`

### Tools Not Showing in Claude
- Verify Claude Desktop config JSON is valid
- Ensure data directory path is absolute (not relative)
- Restart Claude Desktop completely
- Check Claude logs: `~/Library/Logs/Claude/` (macOS)

### Data Not Persisting
- Verify volume mount in docker-compose.yml
- Check data directory permissions
- Ensure path is absolute

### Permission Errors
```bash
# Fix data directory permissions
chmod 755 data/
```

## Roadmap

### Phase 2 (Planned)
- [ ] Knowledge graph visualization
- [ ] Automatic note linking based on topics
- [ ] Learning streak tracking
- [ ] Challenge templates library
- [ ] Export progress reports

### Phase 3 (Future)
- [ ] Machine learning for personalized difficulty adjustment
- [ ] Collaborative challenges
- [ ] Integration with external learning platforms
- [ ] Mobile notifications for reviews
- [ ] Advanced analytics dashboard

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - feel free to use and modify!

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/obsidian-learning-extension/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/obsidian-learning-extension/discussions)

## Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io/)
- Complements the [Official Obsidian MCP Server](https://hub.docker.com/mcp/server/obsidian)
- Inspired by spaced repetition research and second brain methodology
