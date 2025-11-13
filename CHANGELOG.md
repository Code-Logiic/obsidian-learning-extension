# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive testing suite with 100% tool coverage
- Data directory documentation with structure examples
- Configuration examples for Claude Desktop setup
- Project analysis document with roadmap and recommendations
- Examples directory with setup guides

### Changed
- Updated .gitignore to be more specific about excluded files
- Improved data privacy by excluding only JSON files in data directory

### Removed
- Testing artifacts (TEST_RESULTS.md, test_mcp_tools.py) from git tracking

## [1.0.0] - 2025-11-13

### Added
- Initial release with 11 working MCP tools
- Challenge management system
  - `create_challenge`: Create AI-generated learning challenges
  - `list_challenges`: List and filter challenges
  - `get_challenge`: Get detailed challenge information
  - `update_challenge_status`: Update challenge status and notes
- Progress tracking system
  - `record_progress`: Record learning sessions
  - `get_progress_stats`: View learning analytics
- Spaced repetition system (SM-2 algorithm)
  - `schedule_review`: Schedule reviews for topics
  - `get_due_reviews`: Get overdue reviews
  - `complete_review`: Mark reviews complete with performance rating
- AI-powered learning assistance
  - `suggest_next_topic`: Get personalized study recommendations
  - `analyze_knowledge_gaps`: Identify weak areas and topics needing attention
- Docker support with production-ready Dockerfile
- Docker Compose configuration for easy deployment
- Comprehensive documentation
- GitHub Actions CI/CD pipeline
- MIT License

### Technical Details
- Python 3.11+ support
- MCP SDK v1.0.0+
- JSON-based data persistence
- Non-root Docker user for security
- Volume mounting for data persistence

### Security
- All user data gitignored by default
- No external API calls or telemetry
- Local-only data storage
- Privacy-first design

---

## Version History

- **v1.0.0** (2025-11-13): Initial release with core functionality
- More versions coming soon!

## Upgrade Guide

### From v0.x to v1.0.0
This is the first official release. No upgrade path needed.

## Future Releases

See [ANALYSIS.md](ANALYSIS.md) for planned features and roadmap.

### Planned for v1.1.0
- Automated testing infrastructure
- Configuration validation
- Enhanced error handling
- Data export functionality

### Planned for v1.2.0
- Advanced analytics
- Challenge templates library
- Enhanced review system
- Integration features

### Planned for v2.0.0
- Machine learning integration
- Knowledge graph visualization
- Collaborative features
- External integrations
