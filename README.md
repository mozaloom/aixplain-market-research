# AI Market Research System

**Analyze any competitor in minutes using AI agents**

This system uses 5 AI agents to automatically research competitors and generate professional market analysis reports.

## Quick Start (3 steps)

### 1. Install
```bash
pip install aixplain
```

### 2. Get API Key
- Go to [aiXplain Platform](https://platform.aixplain.com/)
- Sign up for free account
- Copy your API key

### 3. Run Analysis
```bash
# Set your API key
export TEAM_API_KEY="your_api_key_here"

# Analyze any competitor
python market_research.py --product "Slack"
```

**That's it!** The system will generate a complete market research report in 5-10 minutes.

## What You Get

The AI system automatically creates:

- **Company Background** - Business details and market position  
- **Product Features** - Complete feature analysis and categorization  
- **Customer Sentiment** - Reviews analysis from multiple sources  
- **Competitive Intelligence** - Strengths, weaknesses, opportunities  
- **Executive Summary** - Key insights and actionable recommendations  

## Usage Examples

### Command Line Analysis
```bash
# Basic analysis
python market_research.py --product "Zoom"

# With industry context
python market_research.py --product "Salesforce" --industry "CRM"

# Save to specific file
python market_research.py --product "Notion" --output my_report.md

# Quick analysis
python market_research.py --product "Airtable" --depth basic
```

### React Web Interface
```bash
# Install dependencies
npm install

# Start development server
npm start
```

**Web Interface Features:**
- Clean, modern UI with real-time agent status
- Form-based competitor analysis input
- Visual progress tracking of AI agents
- Interactive results dashboard
- One-click report download

## How It Works

The system uses 5 specialized AI agents:

1. **Web Research Agent** - Finds company and product information
2. **Sentiment Agent** - Analyzes customer reviews and feedback  
3. **Feature Agent** - Extracts and categorizes product features
4. **Intelligence Agent** - Performs competitive analysis
5. **Report Agent** - Creates executive summary with insights

### Two Modes Available:
- **Command Line**: Generate complete reports via Python script
- **Web Interface**: Interactive React UI with real-time progress

## Command Options

| Option | Description | Example |
|--------|-------------|----------|
| `--product` | Product/company to analyze | `"Slack"` |
| `--industry` | Industry context (optional) | `"SaaS"` |
| `--depth` | Analysis level | `basic` or `detailed` |
| `--output` | Save location | `report.md` |
| `--api-key` | Your aiXplain API key | Alternative to env var |

## Web Interface

The React UI provides:
- **Modern Design** - Clean, professional interface
- **Real-time Status** - Live agent progress tracking  
- **Interactive Forms** - Easy competitor input
- **Visual Results** - Charts and metrics dashboard
- **Export Options** - Download reports in multiple formats

### Running the Web Interface
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI (Terminal 1)
python api.py

# Install React dependencies (Terminal 2)
npm install

# Start React app (opens http://localhost:3000)
npm start
```

## Troubleshooting

**"API key required" error**
```bash
# Set your API key first
export TEAM_API_KEY="your_key_here"
```

**"Agent creation error"**
- Check your API key is valid
- Ensure you have credits in your aiXplain account

**Analysis takes too long**
- Try `--depth basic` for faster results
- Some products may have limited public information

## Tips

- Use specific product names ("Slack" not "messaging app")
- Add industry context for better analysis
- Reports are saved automatically with timestamps
- Analysis typically takes 5-15 minutes

## Sample Report

The system generates professional reports like this:

```markdown
# Market Research Analysis Report

## Company Background
[Detailed company information]

## Product Features
- Core Features: [List]
- Advanced Features: [List] 
- Unique Capabilities: [List]

## Customer Sentiment
- Overall Score: 8.2/10
- Key Themes: [Analysis]

## Competitive Intelligence
- Strengths: [List]
- Weaknesses: [List]
- Opportunities: [List]

## Executive Summary
[3-5 key strategic insights]
```

---

**Need help?** Check the [aiXplain documentation](https://docs.aixplain.com/) or open an issue.