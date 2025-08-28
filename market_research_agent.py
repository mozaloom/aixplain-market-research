#!/usr/bin/env python3
"""
Multi-Agent Market Research System
A sophisticated market research system using aiXplain SDK with 5 specialized agents.
"""

import os
import argparse
from datetime import datetime
from typing import Dict, Any

# Configure environment
os.environ.setdefault("NUMEXPR_NUM_THREADS", "8")
os.environ.setdefault("NUMEXPR_MAX_THREADS", "8")

from aixplain.factories import AgentFactory, TeamAgentFactory
from aixplain.modules.agent.agent_task import AgentTask
from aixplain.modules.agent import OutputFormat

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

class MarketResearchSystem:
    """Multi-agent market research system for competitor analysis."""
    
    def __init__(self, api_key: str):
        """Initialize the system with API key."""
        os.environ["TEAM_API_KEY"] = api_key
        self.team_agent = None
        
    def setup_agents(self):
        """Create and configure all 5 specialized agents."""
        
        # Define tasks with dependencies
        tasks = {
            "web_research": AgentTask(
                name="web_research",
                description="Research competitor product from web sources",
                expected_output="Product info: features, pricing, company details"
            ),
            "sentiment_analysis": AgentTask(
                name="sentiment_analysis", 
                description="Analyze customer sentiment from reviews",
                expected_output="Sentiment scores with confidence metrics"
            ),
            "feature_extraction": AgentTask(
                name="feature_extraction",
                description="Extract and categorize product features",
                expected_output="Feature matrix with competitive positioning",
                dependencies=["web_research"]
            ),
            "competitive_intelligence": AgentTask(
                name="competitive_intelligence",
                description="Compare against market standards, identify gaps",
                expected_output="Market position analysis with opportunities",
                dependencies=["feature_extraction", "sentiment_analysis"]
            ),
            "report_generation": AgentTask(
                name="report_generation",
                description="Create executive summary with actionable insights",
                expected_output="Executive summary with 3-5 key insights",
                dependencies=["competitive_intelligence"]
            )
        }
        
        # Generate unique timestamp for agent names
        timestamp = datetime.now().strftime("%m%d%H%M")
        
        # Create agents with minimal but effective instructions
        agents = [
            AgentFactory.create(
                name=f"Web Research Agent {timestamp}",
                description="Researches competitor products from web sources",
                instructions="Use Google search and web scraping to gather: company info, product features, pricing, market position. Structure findings clearly.",
                tasks=[tasks["web_research"]],
                tools=[
                    AgentFactory.create_model_tool("65c51c556eb563350f6e1bb1"),  # Google Search
                    AgentFactory.create_model_tool("66f423426eb563fa213a3531")   # Website Scraper
                ],
                llm_id="67fd9d6aef0365783d06e2ee"
            ),
            AgentFactory.create(
                name=f"Sentiment Analysis Agent {timestamp}", 
                description="Analyzes customer sentiment and feedback",
                instructions="Search for reviews and feedback. Analyze sentiment patterns, calculate confidence scores (1-10), identify key themes.",
                tasks=[tasks["sentiment_analysis"]],
                tools=[AgentFactory.create_model_tool("65c51c556eb563350f6e1bb1")],
                llm_id="67fd9d6aef0365783d06e2ee"
            ),
            AgentFactory.create(
                name=f"Feature Extraction Agent {timestamp}",
                description="Extracts and categorizes product features",
                instructions="Review research findings. Categorize features (Core/Advanced/Integration). Create feature matrix for competitive analysis.",
                tasks=[tasks["feature_extraction"]],
                llm_id="67fd9d6aef0365783d06e2ee"
            ),
            AgentFactory.create(
                name=f"Competitive Intelligence Agent {timestamp}",
                description="Analyzes competitive positioning and market gaps",
                instructions="Analyze features vs market standards. Identify strengths/weaknesses, gaps, opportunities. Assess pricing strategy.",
                tasks=[tasks["competitive_intelligence"]],
                llm_id="67fd9d6aef0365783d06e2ee"
            ),
            AgentFactory.create(
                name=f"Report Generator Agent {timestamp}",
                description="Creates executive summaries with actionable insights",
                instructions="Synthesize findings into executive summary. Provide 3-5 key insights, actionable recommendations with priorities.",
                tasks=[tasks["report_generation"]],
                llm_id="67fd9d6aef0365783d06e2ee"
            )
        ]
        
        # Deploy agents
        for agent in agents:
            agent.deploy()
            
        # Create team
        self.team_agent = TeamAgentFactory.create(
            name=f"Market Research Team {timestamp}",
            description="5-agent team for comprehensive competitor analysis",
            agents=agents,
            use_mentalist=True,
            use_inspector=True,
            llm_id="67fd9d6aef0365783d06e2ee"
        )
        
    def analyze_competitor(self, product_name: str, industry: str = "", depth: str = "detailed") -> Dict[str, Any]:
        """Main analysis method."""
        if not self.team_agent:
            raise ValueError("Team not initialized. Call setup_agents() first.")
            
        query = f"""Analyze competitor: {product_name}
Industry: {industry or "General"}
Depth: {depth}

Complete tasks: 1) Web research 2) Sentiment analysis 3) Feature extraction 4) Competitive intelligence 5) Executive report"""
        
        try:
            result = self.team_agent.run(
                query=query,
                output_format=OutputFormat.MARKDOWN,
                max_iterations=25,
                timeout=600
            )
            return result  # Return the AgentResponseData object directly
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    def generate_report(self, results, output_file: str = None) -> str:
        """Format and save analysis results."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Handle error case (dict)
        if isinstance(results, dict) and "error" in results:
            report = f"""# Market Research Analysis - Error
**Generated:** {timestamp}

**Error:** {results['error']}
"""
        # Handle AgentResponseData object
        elif hasattr(results, 'data'):
            data = results.data
            output_content = data.get('output', 'Analysis completed') if isinstance(data, dict) else str(data)
            session_id = data.get('session_id', 'N/A') if isinstance(data, dict) else 'N/A'
            steps = len(data.get('intermediate_steps', [])) if isinstance(data, dict) else 0
            
            report = f"""# Market Research Analysis Report
**Generated:** {timestamp}

{output_content}

---
**Metadata:** Session {session_id} | {steps} steps
"""
        else:
            report = f"""# Market Research Analysis Report
**Generated:** {timestamp}

{str(results)}
"""
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report saved: {output_file}")
            
        return report

def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(description="Multi-Agent Market Research System")
    parser.add_argument("--product", required=True, help="Competitor product name")
    parser.add_argument("--industry", default="", help="Industry context")
    parser.add_argument("--depth", choices=["basic", "detailed"], default="detailed")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--api-key", help="aiXplain API key")
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.getenv("TEAM_API_KEY")
    if not api_key:
        print("❌ Error: API key required. Use --api-key or set TEAM_API_KEY")
        return 1
    
    print("🚀 Initializing Market Research System...")
    system = MarketResearchSystem(api_key)
    
    print("⚙️ Setting up 5 specialized agents...")
    system.setup_agents()
    
    print(f"🔍 Analyzing: {args.product} ({args.industry or 'General'})")
    print("⏳ Processing (may take 5-10 minutes)...\n")
    
    results = system.analyze_competitor(args.product, args.industry, args.depth)
    
    # Debug: Print results structure
    print(f"\n🔍 Debug - Results type: {type(results)}")
    if hasattr(results, 'data'):
        print(f"🔍 Debug - Has data attribute: {type(results.data)}")
    else:
        print(f"🔍 Debug - Results keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
    
    output_file = args.output or f"analysis_{args.product.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    report = system.generate_report(results, output_file)
    
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE")
    print("="*60)
    print(report[:1000] + "..." if len(report) > 1000 else report)
    
    return 0

if __name__ == "__main__":
    exit(main())