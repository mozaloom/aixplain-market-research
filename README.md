# Multi-Agent Market Research System

A sophisticated market research system using the aiXplain SDK with 5 specialized agents for comprehensive competitor analysis.

## Features

**Web Research Agent** - Scrapes competitor websites and documentation  
**Sentiment Analysis Agent** - Analyzes customer reviews and feedback  
**Feature Extraction Agent** - Categorizes product features and capabilities  
**Competitive Intelligence Agent** - Compares against market standards  
**Report Generator Agent** - Creates executive summaries with actionable insights  

## Quick Start

### Prerequisites
- Python 3.8+
- aiXplain SDK account and API key

### Installation

```bash
# Clone the repository
git clone https://github.com/mozaloom/aixplain-market-research.git
cd aixplain-market-research

# Install dependencies
pip install aixplain

# Set your API key
export TEAM_API_KEY="your_api_key_here"
```

### Basic Usage

```bash
# Analyze a competitor product
python market_research_agent.py --product "Competitor Product Name" --industry "SaaS" --depth detailed --output report.json

# Example with Slack
python market_research_agent.py --product "Slack" --industry "Business Communication" --depth detailed
```

### Python API Usage

```python
from market_research_agent import MarketResearchSystem

# Initialize system
system = MarketResearchSystem("your_api_key")
system.setup_agents()
system.create_team()

# Run analysis
results = system.analyze_competitor("Product Name", "Industry", "detailed")
report = system.generate_report(results, "output.md")
```

## System Architecture

The system uses 5 specialized agents working in coordination:

1. **Web Research Agent** - Gathers product information from official sources
2. **Sentiment Analysis Agent** - Analyzes customer feedback and reviews
3. **Feature Extraction Agent** - Identifies and categorizes product capabilities
4. **Competitive Intelligence Agent** - Performs market positioning analysis
5. **Report Generator Agent** - Synthesizes findings into actionable insights

## Output Format

The system generates comprehensive reports including:
- Sentiment scores with confidence metrics
- Feature comparison matrix
- Market position analysis
- Competitive gaps and opportunities
- Executive summary with 3-5 key insights
- Raw data exports for further analysis

## Configuration

The system can be customized through:
- Analysis depth levels (basic/detailed)
- Industry context specification
- Output format preferences (JSON/Markdown)
- Custom agent instructions

## License

MIT License - see LICENSE file for details.