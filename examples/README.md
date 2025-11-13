# Configuration Examples

This directory contains example configuration files to help you get started.

## Claude Desktop Configuration

### macOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
Location: `%APPDATA%\Claude\claude_desktop_config.json`

### Linux
Location: `~/.config/Claude/claude_desktop_config.json`

## Setup Instructions

1. **Copy the example configuration**
   ```bash
   cp examples/claude_desktop_config.example.json ~/path/to/claude_desktop_config.json
   ```

2. **Update the paths**
   - Replace `/absolute/path/to/obsidian-learning-extension` with your actual path
   - Example: `/Users/yourname/projects/obsidian-learning-extension`

3. **Add Obsidian API credentials** (if using official Obsidian MCP)
   - Replace `YOUR_OBSIDIAN_API_KEY_HERE` with your API key
   - Get API key from Obsidian settings

4. **Restart Claude Desktop**
   - Completely quit Claude Desktop (not just close window)
   - Reopen Claude Desktop
   - Check that tools are available by asking Claude "What tools do you have?"

## Configuration Options

### Using Docker Compose

If you prefer to manage the server separately:

```bash
# Start the server
docker-compose up -d

# Configure Claude Desktop to connect to running container
# (Advanced - requires custom MCP transport configuration)
```

### Local Python Development

For local development without Docker:

```json
{
  "mcpServers": {
    "obsidian-learning": {
      "command": "python3",
      "args": [
        "/absolute/path/to/learning_server.py"
      ],
      "env": {
        "DATA_PATH": "/absolute/path/to/data"
      }
    }
  }
}
```

## Environment Variables

You can customize the server behavior with environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATA_PATH` | Directory for data storage | `./data` |

Example with custom data path:

```json
{
  "mcpServers": {
    "obsidian-learning": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/custom/data/path:/data:rw",
        "-e", "DATA_PATH=/data",
        "obsidian-learning-extension:latest"
      ]
    }
  }
}
```

## Troubleshooting

### Tools not showing up
- Verify JSON syntax is valid (use a JSON validator)
- Check that paths are absolute, not relative
- Ensure Docker image is built: `docker-compose build`
- Check Claude logs for errors

### Permission errors
- Ensure data directory exists and is writable
- Check Docker volume permissions
- Try running: `chmod 755 data/`

### Docker connection issues
- Verify Docker is running: `docker ps`
- Test server manually: `docker-compose up`
- Check Docker logs: `docker-compose logs`

## Testing Your Configuration

After configuring, test by asking Claude:

```
"What learning tools do you have available?"
"Create a beginner knowledge challenge on Python basics"
"List my challenges"
```

If you see the challenge tools, your configuration is working correctly!
