# Contributing to Market Research AI Agent

Thank you for your interest in contributing to the Market Research AI Agent project! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ and Node.js 16+
- Git and familiarity with GitHub workflows
- aiXplain API Key ([Get one here](https://platform.aixplain.com/))

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/aixplain-market-research.git
   cd aixplain-market-research
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   cp .env.template .env
   # Edit .env with your aiXplain API key
   ```

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── agent.py            # Core agent logic
│   ├── tools.py            # Utility functions
│   ├── api.py              # FastAPI application
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React web interface
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   ├── tests/              # Frontend tests
│   └── package.json        # Node.js dependencies
└── .github/workflows/      # CI/CD pipelines
```

## 🛠️ Development Workflow

### 1. Creating Issues
- Use clear, descriptive titles
- Include steps to reproduce for bugs
- Add labels (bug, enhancement, documentation, etc.)
- Reference related issues or pull requests

### 2. Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/description` - Feature development
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical production fixes

### 3. Making Changes

**Backend Development:**
```bash
cd backend
# Make your changes
python -m pytest tests/          # Run tests
flake8 .                        # Check code style
black .                         # Format code
```

**Frontend Development:**
```bash
cd frontend
# Make your changes
npm test                        # Run tests
npm run lint                    # Check code style
npm run format                  # Format code
```

### 4. Testing
- Write tests for new features
- Ensure all existing tests pass
- Aim for 80%+ code coverage
- Test both happy path and edge cases

### 5. Submitting Pull Requests

**Before Submitting:**
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventions

**Pull Request Process:**
1. Create descriptive title and description
2. Link related issues
3. Add screenshots for UI changes
4. Ensure CI checks pass
5. Request review from maintainers

## 📋 Code Standards

### Python (Backend)
- **Style**: PEP 8 with Black formatting
- **Linting**: Flake8 with line length 127
- **Type Hints**: Required for all functions
- **Docstrings**: Google style for all public methods
- **Testing**: pytest with asyncio support

```python
# Example function with proper styling
async def analyze_market_data(
    target: str, 
    mode: str = "quick"
) -> Dict[str, Any]:
    """Analyze market data for a given target.
    
    Args:
        target: Company or product name to analyze
        mode: Analysis mode ('quick' or 'detailed')
        
    Returns:
        Dictionary containing analysis results
        
    Raises:
        ValueError: If target is empty or invalid
    """
    if not target.strip():
        raise ValueError("Target cannot be empty")
    
    # Implementation here
    return {"status": "completed"}
```

### JavaScript/React (Frontend)
- **Style**: ESLint + Prettier configuration
- **Components**: Functional components with hooks
- **TypeScript**: Preferred for new components
- **Testing**: Jest + React Testing Library
- **Accessibility**: WCAG 2.1 AA compliance

```jsx
// Example component with proper styling
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Market analysis status component
 * @param {Object} props - Component props
 * @param {string} props.jobId - Analysis job ID
 * @param {Function} props.onComplete - Callback when analysis completes
 */
const AnalysisStatus = ({ jobId, onComplete }) => {
  const [status, setStatus] = useState('pending');
  
  useEffect(() => {
    // Implementation here
  }, [jobId]);
  
  return (
    <div className="analysis-status" role="status" aria-live="polite">
      {/* Component content */}
    </div>
  );
};

AnalysisStatus.propTypes = {
  jobId: PropTypes.string.isRequired,
  onComplete: PropTypes.func.isRequired,
};

export default AnalysisStatus;
```

### Git Commit Messages
Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(backend): add sentiment analysis caching
fix(frontend): resolve citation link formatting
docs(readme): update installation instructions
test(api): add integration tests for report generation
```

## 🧪 Testing Guidelines

### Backend Testing
```python
# pytest example
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_analyze_endpoint():
    """Test the analyze endpoint with valid input."""
    response = client.post(
        "/run-agent",
        json={"target": "Slack", "mode": "quick"}
    )
    assert response.status_code == 200
    assert "job_id" in response.json()
```

### Frontend Testing
```jsx
// Jest + React Testing Library example
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AnalysisForm from './AnalysisForm';

test('submits analysis request', async () => {
  render(<AnalysisForm />);
  
  const targetInput = screen.getByLabelText(/target/i);
  const submitButton = screen.getByRole('button', { name: /analyze/i });
  
  fireEvent.change(targetInput, { target: { value: 'Slack' } });
  fireEvent.click(submitButton);
  
  await waitFor(() => {
    expect(screen.getByText(/analyzing/i)).toBeInTheDocument();
  });
});
```

## 📖 Documentation

### Code Documentation
- **Backend**: Google-style docstrings for all public functions
- **Frontend**: JSDoc comments for complex functions
- **API**: OpenAPI/Swagger documentation auto-generated
- **README**: Keep project README up to date

### Writing Guidelines
- Use clear, concise language
- Include code examples
- Update documentation with code changes
- Add inline comments for complex logic

## 🔒 Security Guidelines

### API Security
- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all input parameters
- Implement rate limiting for public endpoints

### Data Handling
- Don't log sensitive information
- Sanitize user inputs
- Follow data privacy best practices
- Use HTTPS in production

## 🚀 Deployment

### Development Deployment
```bash
# Start development servers
cd backend && uvicorn api:app --reload &
cd frontend && npm start
```

### Production Deployment
```bash
# Using Docker Compose
docker-compose up --build

# Or deploy to cloud platforms
# See deployment documentation in README.md
```

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Report inappropriate behavior

### Communication
- **Issues**: Bug reports and feature requests
- **Discussions**: Questions and ideas
- **Pull Requests**: Code contributions
- **Discord/Slack**: Real-time community chat (if available)

## 📋 Checklists

### New Feature Checklist
- [ ] Issue created and discussed
- [ ] Feature branch created
- [ ] Code implemented with tests
- [ ] Documentation updated
- [ ] CI checks pass
- [ ] Pull request submitted
- [ ] Code review completed
- [ ] Merged to develop branch

### Bug Fix Checklist
- [ ] Bug reproduced and understood
- [ ] Root cause identified
- [ ] Fix implemented with tests
- [ ] Regression tests added
- [ ] Documentation updated if needed
- [ ] Pull request submitted
- [ ] Code review completed

### Release Checklist
- [ ] All features tested
- [ ] Documentation updated
- [ ] Version number bumped
- [ ] Changelog updated
- [ ] Release notes prepared
- [ ] Production deployment tested
- [ ] Release tagged and published

## 🆘 Getting Help

### Resources
- **Documentation**: [README.md](./README.md)
- **API Docs**: http://localhost:8000/docs
- **aiXplain Docs**: https://platform.aixplain.com/docs
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions

### Contact
- **Maintainers**: See [CODEOWNERS](.github/CODEOWNERS)
- **Email**: project-maintainers@example.com
- **Community**: [Discord/Slack links if available]

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
