# Market Research AI Agent

A comprehensive market research system using aiXplain SDK with a multi-agent approach for competitive analysis and business intelligence.

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── agent.py            # Market Research Agent logic
│   ├── tools.py            # Utility functions
│   ├── api.py              # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── generated_reports/  # Analysis output storage
│   └── README.md           # Backend documentation
├── frontend/               # React web interface
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   ├── tailwind.config.js  # Tailwind CSS config
│   └── README.md           # Frontend documentation
├── references/             # aiXplain tutorials and examples
├── Dockerfile             # Container configuration
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- aiXplain API Key ([Get one here](https://platform.aixplain.com/))

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export TEAM_API_KEY="your_aixplain_api_key"
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
echo "REACT_APP_API_URL=http://localhost:8000" > .env
npm start
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🤖 AI Agent System

### Multi-Agent Architecture

The system uses 5 specialized AI agents orchestrated by aiXplain's TeamAgent:

1. **🔍 Web Research Agent**
   - Gathers public information and company details
   - Finds official documentation and specifications
   - Structures findings with proper citations

2. **📊 Sentiment Analysis Agent**
   - Analyzes customer reviews and feedback
   - Calculates sentiment scores with confidence levels
   - Sources from G2, Capterra, Reddit, and forums

3. **⚙️ Feature Extraction Agent**
   - Categorizes product features and capabilities
   - Creates competitive feature matrices
   - Identifies unique selling propositions

4. **🎯 Competitive Intelligence Agent**
   - Analyzes market positioning and gaps
   - Assesses pricing strategies and value propositions
   - Identifies threats and opportunities

5. **📋 Report Generator Agent**
   - Synthesizes findings into executive summaries
   - Provides actionable recommendations with priorities
   - Consolidates all sources and citations

### Analysis Modes

- **Quick Mode** (5-8 minutes): Company overview, key features, basic sentiment, strategic insights
- **Detailed Mode** (10-15 minutes): Comprehensive analysis with full competitive positioning

## 📊 Features

### Analysis Capabilities
- **Competitive Analysis** - Compare products and market positions
- **Market Research** - Industry insights and trends
- **Feature Comparison** - Detailed capability analysis
- **Sentiment Analysis** - Customer feedback and satisfaction
- **Strategic Recommendations** - Actionable business insights

### Output Formats
- **Interactive Web Interface** - Real-time results with citations
- **PDF Reports** - Professional formatted documents
- **Markdown Files** - Text-based reports for documentation
- **Citations JSON** - Structured source links and references

### Real-time Features
- **Live Progress Tracking** - Watch agents work in real-time
- **Status Updates** - See which agents are active/completed
- **Background Processing** - Long-running analyses don't block UI
- **Error Recovery** - Graceful handling of analysis failures

## 🔗 API Endpoints

### Core Endpoints
- `POST /run-agent` - Start market research analysis
- `GET /results/{job_id}` - Get job status and results
- `GET /download/{job_id}.{format}` - Download reports (pdf, md)
- `GET /download/{job_id}/citations.json` - Download source links

### Management Endpoints
- `GET /health` - Health check and system status
- `GET /jobs` - List all analysis jobs
- `DELETE /jobs/{job_id}` - Delete specific job

## 🎨 User Interface

### Modern React Frontend
- **Responsive Design** - Works on desktop and mobile
- **Real-time Updates** - Live progress indicators
- **Citation Links** - Clickable sources that open in new tabs
- **Download Options** - Multiple export formats
- **Error Handling** - Clear feedback and retry options

### Tailwind CSS Styling
- **Professional Theme** - Clean blue and gray color scheme
- **Component Library** - Reusable UI elements
- **Animation** - Smooth transitions and loading states
- **Accessibility** - WCAG compliant design

## 🐳 Deployment

### Development
```bash
# Terminal 1 - Backend
cd backend && uvicorn api:app --reload

# Terminal 2 - Frontend  
cd frontend && npm start
```

### Production with Docker
```bash
# Build and run containers
docker-compose up --build

# Or deploy separately
docker build -t market-research-backend ./backend
docker build -t market-research-frontend ./frontend
```

### Cloud Deployment
- **Backend**: AWS Lambda, Google Cloud Run, Heroku
- **Frontend**: Netlify, Vercel, AWS S3 + CloudFront
- **Database**: Optional Redis/PostgreSQL for job persistence

## 🔧 Configuration

### Environment Variables

**Backend (`backend/.env`)**
```bash
TEAM_API_KEY=your_aixplain_api_key
MARKET_RESEARCH_STORAGE=./generated_reports
PORT=8000
```

**Frontend (`frontend/.env`)**
```bash
REACT_APP_API_URL=http://localhost:8000
```

### Customization
- **Agent Instructions** - Modify prompts in `backend/agent.py`
- **UI Theme** - Update colors in `frontend/tailwind.config.js`
- **Storage** - Configure report storage in `backend/tools.py`

## 📚 Documentation

### Detailed Guides
- [Backend Documentation](./backend/README.md) - API setup and agent configuration
- [Frontend Documentation](./frontend/README.md) - UI development and deployment
- [aiXplain Tutorials](./references/) - SDK examples and patterns

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ --cov=.
```

### Frontend Testing
```bash
cd frontend
npm test -- --coverage
```

### Integration Testing
```bash
# Start backend and frontend, then:
curl -X POST "http://localhost:8000/run-agent" \
  -H "Content-Type: application/json" \
  -d '{"target": "Slack", "mode": "quick", "api_key": "your_key"}'
```

## 🚦 Monitoring

### Health Checks
- **Backend**: `GET /health` - API status and active jobs
- **Frontend**: Built-in error boundaries and logging
- **Jobs**: Real-time status tracking and progress updates

### Logging
- **Backend**: Structured logging with FastAPI
- **Frontend**: Console logging and error reporting
- **aiXplain**: SDK-level logging for agent debugging

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes in `backend/` or `frontend/` directories
4. Test thoroughly
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open Pull Request

### Code Standards
- **Python**: PEP 8, type hints, comprehensive docstrings
- **JavaScript**: ESLint, Prettier, JSDoc comments
- **Git**: Conventional commits, descriptive messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **aiXplain** - For the powerful SDK and agent orchestration
- **FastAPI** - For the modern Python web framework
- **React** - For the robust frontend framework
- **Tailwind CSS** - For the utility-first styling approach

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mozaloom/aixplain-market-research/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mozaloom/aixplain-market-research/discussions)
- **aiXplain Docs**: [platform.aixplain.com/docs](https://platform.aixplain.com/docs)

---

**Built with ❤️ using aiXplain SDK**
