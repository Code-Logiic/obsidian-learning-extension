# Contributing to Obsidian Learning Extension

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Project Structure](#project-structure)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Accept responsibility for mistakes

## Getting Started

1. **Fork the repository**
   ```bash
   # Click the 'Fork' button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/obsidian-learning-extension.git
   cd obsidian-learning-extension
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/canoo/obsidian-learning-extension.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (optional, for containerized development)
- Git

### Local Development

1. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   pytest tests/ -v
   ```

4. **Run server locally**
   ```bash
   python learning_server.py
   ```

### Docker Development

1. **Build the image**
   ```bash
   docker-compose build
   ```

2. **Run the container**
   ```bash
   docker-compose up
   ```

## Making Changes

### Branch Strategy

- `main` - Production-ready code
- `dev` - Development branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

### Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our [coding standards](#coding-standards)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   pytest tests/ -v --cov=learning_server
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples:**
```
feat(challenges): add difficulty auto-adjustment
fix(reviews): correct SM-2 interval calculation
docs(readme): update installation instructions
test(progress): add tests for edge cases
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_challenges.py -v

# Run with coverage
pytest tests/ --cov=learning_server --cov-report=html

# Run specific test
pytest tests/test_challenges.py::test_create_challenge -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Name test functions as `test_*`
- Use descriptive test names
- Include docstrings explaining what the test does
- Use fixtures from `conftest.py`

**Example:**
```python
@pytest.mark.asyncio
async def test_create_challenge(mock_data_path, sample_challenge_data):
    """Test creating a challenge with valid data"""
    result = await create_challenge(
        sample_challenge_data["topic"],
        sample_challenge_data["difficulty"],
        sample_challenge_data["challenge_type"]
    )

    assert len(result) == 1
    assert "Challenge Created" in result[0].text
```

### Test Coverage

- Aim for at least 80% code coverage
- Test both success and failure cases
- Test edge cases and boundary conditions
- Test error handling

## Submitting Changes

### Before Submitting

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**
   ```bash
   pytest tests/ -v
   ```

3. **Check code style**
   - Ensure code follows PEP 8
   - Use type hints where appropriate
   - Add docstrings to functions

### Creating a Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

3. **PR Description**
   Include:
   - What the PR does
   - Why the change is needed
   - How to test the changes
   - Screenshots (if applicable)
   - Related issues

**Example PR Description:**
```markdown
## Summary
Adds automatic difficulty adjustment based on user performance

## Motivation
Users requested adaptive challenge difficulty (#42)

## Changes
- Added difficulty adjustment algorithm
- Updated challenge creation flow
- Added tests for new functionality

## Testing
- Run `pytest tests/test_challenges.py`
- Create challenges and complete them
- Verify difficulty adjusts based on mastery ratings

## Related Issues
Closes #42
```

### PR Review Process

1. Automated tests will run (must pass)
2. Maintainers will review your code
3. Address any feedback
4. Once approved, maintainers will merge

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black formatter)
- Use type hints for function parameters and returns

### Documentation

- Add docstrings to all functions
- Use Google-style docstrings
- Update README.md for user-facing changes
- Update CHANGELOG.md

**Example Docstring:**
```python
async def create_challenge(
    topic: str,
    difficulty: str,
    challenge_type: str,
    description: Optional[str] = None
) -> list[TextContent]:
    """
    Create a new learning challenge.

    Args:
        topic: The topic to learn about
        difficulty: Difficulty level (beginner, intermediate, advanced, expert)
        challenge_type: Type of challenge (knowledge, practical, teaching, etc.)
        description: Optional custom description

    Returns:
        List containing TextContent with challenge details

    Raises:
        ValueError: If difficulty or challenge_type is invalid
    """
```

### Code Organization

- Keep functions focused and single-purpose
- Extract complex logic into helper functions
- Use meaningful variable names
- Add comments for complex algorithms

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately
- Validate inputs early

## Project Structure

```
obsidian-learning-extension/
├── learning_server.py      # Main server implementation
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── .github/
│   └── workflows/
│       └── docker-build.yml  # CI/CD pipeline
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest fixtures
│   ├── test_challenges.py
│   ├── test_progress.py
│   ├── test_reviews.py
│   └── test_analysis.py
├── data/                   # User data (gitignored)
│   └── README.md
├── examples/               # Configuration examples
│   ├── README.md
│   └── claude_desktop_config.example.json
└── docs/                   # Documentation
    ├── README.md
    ├── CONTRIBUTING.md
    ├── CHANGELOG.md
    └── ANALYSIS.md
```

## Development Roadmap

See [ANALYSIS.md](ANALYSIS.md) for the project roadmap and planned features.

### Current Priorities

1. **Phase 1: Stabilization** (Current)
   - Automated testing ✅
   - Error handling improvements
   - Data export functionality
   - Logging framework

2. **Phase 2: Enhancement** (Next)
   - Advanced analytics
   - Challenge templates library
   - Enhanced review system
   - Integration features

3. **Phase 3: Advanced Features** (Future)
   - Machine learning integration
   - Knowledge graph visualization
   - Collaborative features
   - External integrations

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/canoo/obsidian-learning-extension/issues)
- **Discussions**: [GitHub Discussions](https://github.com/canoo/obsidian-learning-extension/discussions)
- **Email**: [Project maintainers]

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for their contributions
- README.md contributors section
- Release notes

Thank you for contributing! 🎉
