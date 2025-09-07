# Market Research Backend

FastAPI backend for the Market Research Team Agent using aiXplain SDK.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- aiXplain API Key

### Installation

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
export TEAM_API_KEY="your_aixplain_api_key"
```

### Run the Server

```bash
# Development server with auto-reload
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Production server
uvicorn api:app --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## 📚 API Documentation

### Available Endpoints

- `GET /` - API information and status
- `GET /health` - Health check
- `POST /run-agent` - Start market research analysis
- `GET /results/{job_id}` - Get job status and results
- `GET /download/{job_id}.md` - Download markdown report
- `GET /download/{job_id}.pdf` - Download PDF report
- `GET /download/{job_id}/citations.json` - Download citations JSON
- `GET /jobs` - List all jobs
- `DELETE /jobs/{job_id}` - Delete a job

### Interactive Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables
- `TEAM_API_KEY` - Your aiXplain API key (required)
- `MARKET_RESEARCH_STORAGE` - Storage directory for reports (default: "generated_reports")

### Example Usage

```bash
# Start analysis
curl -X POST "http://localhost:8000/run-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "Slack vs Teams",
    "mode": "quick",
    "api_key": "your_aixplain_api_key"
  }'

# Get results
curl -X GET "http://localhost:8000/results/job_id_here"

# Download report
curl -X GET "http://localhost:8000/download/job_id_here.pdf" -o "report.pdf"
```

## 🏗️ Architecture

### Core Components

1. **agent.py** - MarketResearchAgent class using aiXplain SDK
   - Orchestrates 5 specialized agents
   - Web Research, Sentiment Analysis, Feature Extraction, Competitive Intelligence, Report Generator

2. **tools.py** - Utility functions
   - Markdown rendering and PDF generation
   - Job storage and retrieval
   - File handling and sanitization

3. **api.py** - FastAPI application
   - REST API endpoints
   - Async job processing
   - Error handling and validation

### Agent Workflow

1. **Web Research Agent** - Gathers public information and company details
2. **Sentiment Agent** - Analyzes customer feedback and reviews
3. **Feature Agent** - Extracts and categorizes product features
4. **Intelligence Agent** - Provides competitive analysis and market insights
5. **Report Agent** - Synthesizes findings into actionable recommendations

## 🐳 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📦 Dependencies

### Core Dependencies
- **aixplain** - aiXplain SDK for AI agents
- **fastapi** - Modern web framework for APIs
- **uvicorn** - ASGI server
- **pydantic** - Data validation

### Report Generation
- **markdown2** - Markdown processing
- **weasyprint** - HTML to PDF conversion
- **reportlab** - PDF generation

### Cloud Deployment
- **mangum** - AWS Lambda adapter for FastAPI
- **boto3** - AWS SDK
- **aws-lambda-powertools** - Lambda utilities

## 🧪 Testing

```bash
# Run tests
pytest

# Test specific endpoint
pytest -k "test_health_check"

# Run with coverage
pytest --cov=.
```

## 📝 Development

### Code Structure
```
backend/
├── agent.py           # Market Research Agent logic
├── tools.py           # Utility functions
├── api.py             # FastAPI application
├── requirements.txt   # Python dependencies
├── generated_reports/ # Output storage
└── README.md          # This file
```

### Adding New Features
1. Update agent instructions in `agent.py`
2. Add utility functions in `tools.py`
3. Create new API endpoints in `api.py`
4. Update requirements.txt if needed

## 🚦 Error Handling

The API includes comprehensive error handling:
- Input validation with Pydantic models
- Graceful failure handling for AI agent errors
- Proper HTTP status codes and error messages
- Logging for debugging and monitoring

## 📊 Monitoring

- Health check endpoint for uptime monitoring
- Job status tracking for long-running analyses
- Logging integration for debugging
- Metrics collection ready for production deployment
