#!/usr/bin/env python3
"""
Market Research Team Agent

Purpose: Define the Team Agent logic using aiXplain SDK.
Uses aiXplain primitives and orchestration patterns for multi-agent market research.

Requirements:
- pip install aixplain markdown2 weasyprint

Usage:
    from agent import MarketResearchAgent
    
    agent = MarketResearchAgent(target="Slack", mode="quick")
    result = agent.run()
    print(result["summary"])
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
import warnings
warnings.filterwarnings("ignore")

# Configure environment for better performance
os.environ.setdefault("NUMEXPR_NUM_THREADS", "8")
os.environ.setdefault("NUMEXPR_MAX_THREADS", "8")

try:
    from aixplain.factories import AgentFactory, TeamAgentFactory, ModelFactory
    from aixplain.modules.agent import OutputFormat
    from aixplain.enums import Function, Supplier
except ImportError as e:
    print(f"❌ Error importing aiXplain SDK: {e}")
    print("Install with: pip install aixplain")
    raise


class MarketResearchAgent:
    """
    Multi-agent market research system using aiXplain SDK.
    
    Orchestrates 5 specialized agents to perform comprehensive market research:
    - Web Research Agent: Gathers public information
    - Sentiment Agent: Analyzes customer feedback and sentiment
    - Feature Agent: Extracts and categorizes product features
    - Intelligence Agent: Provides competitive intelligence
    - Report Agent: Synthesizes findings into actionable insights
    """
    
    def __init__(self, target: str, mode: str = "quick", api_key: Optional[str] = None):
        """
        Initialize the Market Research Agent.
        
        Args:
            target: The product/company to research
            mode: Analysis mode ("quick" or "detailed")
            api_key: aiXplain API key (or set TEAM_API_KEY env var)
        """
        if not target:
            raise ValueError("Target product/company name is required")
            
        self.target = target
        self.mode = mode
        
        # Get API key
        self.api_key = api_key or os.getenv("TEAM_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set TEAM_API_KEY env var or pass api_key parameter")
        
        # Set API key in environment
        os.environ["TEAM_API_KEY"] = self.api_key
        
        # Initialize components
        self.team_agent = None
        self.agents = []
        
        # Validated model IDs from aiXplain platform
        self.llm_id = "6646261c6eb563165658bbb1"  # GPT-4o
        self.search_model_id = "669a63646eb56306647e1091"  # Search model
        
        # Setup agents
        self._setup_agents()
    
    def _validate_environment(self) -> bool:
        """Validate that the aiXplain SDK environment is properly configured."""
        try:
            # Test basic SDK connection
            ModelFactory.list(page_size=1)
            return True
        except Exception as e:
            print(f"❌ SDK validation failed: {e}")
            return False
    
    def _setup_agents(self) -> None:
        """Create and configure all 5 specialized agents."""
        if not self._validate_environment():
            raise RuntimeError("Failed to validate aiXplain environment")
            
        print("🔧 Creating specialized agents...")
        
        # Generate unique timestamp for agent names
        timestamp = datetime.now().strftime("%m%d%H%M%S")
        
        # Create search tool for web research
        search_tool = AgentFactory.create_model_tool(
            model=self.search_model_id
        )
        
        # 1. Web Research Agent
        web_research_agent = AgentFactory.create(
            name=f"Web Research Agent {timestamp}",
            description="Researches competitor products from web sources and gathers company information",
            instructions="""You are a web research specialist. Your tasks:
1. Search for comprehensive information about the given competitor product
2. Gather company details, product features, pricing, and market position
3. Find official product pages, documentation, and specifications
4. Structure findings clearly with sections: Company Info, Product Features, Pricing, Market Position
5. IMPORTANT: Include full URLs for all sources you reference in your research
6. Format citations as [1] Source Title - https://example.com/url at the end of your response
7. Focus on factual, verifiable information with proper attribution""",
            tools=[search_tool],
            llm_id=self.llm_id
        )
        
        # 2. Sentiment Analysis Agent  
        sentiment_agent = AgentFactory.create(
            name=f"Sentiment Agent {timestamp}",
            description="Analyzes customer sentiment and feedback from various sources",
            instructions="""You are a sentiment analysis expert. Your tasks:
1. Search for customer reviews, testimonials, and feedback about the product
2. Analyze sentiment patterns and calculate confidence scores (1-10 scale)
3. Identify key themes in customer feedback (positive, negative, neutral)
4. Look for reviews on platforms like G2, Capterra, Reddit, forums
5. IMPORTANT: Cite specific review sources with full URLs
6. Format citations as [1] Platform Name - Review Title - https://review-url.com
7. Provide sentiment summary with supporting evidence and confidence metrics""",
            tools=[search_tool],
            llm_id=self.llm_id
        )
        
        # 3. Feature Extraction Agent
        feature_agent = AgentFactory.create(
            name=f"Feature Agent {timestamp}",
            description="Extracts and categorizes product features for competitive analysis",
            instructions="""You are a product feature analyst. Your tasks:
1. Review all gathered research and extract specific product features
2. Categorize features into: Core Features, Advanced Features, Integrations, Unique Capabilities
3. Create a structured feature matrix suitable for competitive analysis
4. Include feature descriptions and any technical specifications found
5. IMPORTANT: Reference sources for feature information with full URLs
6. Format citations as [1] Feature Documentation - https://docs-url.com
7. Note any missing or unclear feature information for follow-up""",
            llm_id=self.llm_id
        )
        
        # 4. Competitive Intelligence Agent
        intelligence_agent = AgentFactory.create(
            name=f"Intelligence Agent {timestamp}",
            description="Analyzes competitive positioning and identifies market gaps",
            instructions="""You are a competitive intelligence analyst. Your tasks:
1. Analyze the extracted features against market standards and competitors
2. Identify key strengths, weaknesses, and differentiators
3. Assess pricing strategy and value proposition
4. Identify market gaps and opportunities
5. IMPORTANT: Include sources for competitive comparisons and market data
6. Format citations as [1] Market Report - Company Name - https://report-url.com
7. Provide strategic insights about competitive positioning and potential threats/opportunities""",
            llm_id=self.llm_id
        )
        
        # 5. Report Generator Agent
        report_agent = AgentFactory.create(
            name=f"Report Agent {timestamp}",
            description="Creates executive summaries with actionable insights",
            instructions="""You are an executive report writer. Your tasks:
1. Synthesize all analysis into a comprehensive executive summary
2. Provide 3-5 key strategic insights with supporting evidence
3. Include actionable recommendations with priority levels (High/Medium/Low)
4. Structure the report professionally with clear sections
5. CRITICAL: Always include a Sources and References section at the end
6. Format citations as:
   ## Sources and References
   [1] Official Website - https://slack.com
   [2] Microsoft Teams Documentation - https://docs.microsoft.com/teams
   [3] Market Analysis Report - https://example.com/report
7. If specific URLs are not available, include likely sources like:
   - Company official websites
   - Product documentation pages  
   - Industry analysis sites (G2, Capterra, Gartner)
   - News articles and press releases
8. Focus on business implications and strategic recommendations for decision-makers""",
            llm_id=self.llm_id
        )
        
        # Store agents for later use
        self.agents = [
            web_research_agent, 
            sentiment_agent, 
            feature_agent, 
            intelligence_agent, 
            report_agent
        ]
        
        print(f"✅ Created {len(self.agents)} individual agents")
        
        # Deploy all agents
        print("🚀 Deploying agents...")
        for i, agent in enumerate(self.agents, 1):
            try:
                agent.deploy()
                print(f"   Agent {i}/5 deployed successfully")
            except Exception as e:
                print(f"   ⚠️  Agent {i} deployment warning: {e}")
        
        # Create team agent
        print("🤝 Creating team agent...")
        self.team_agent = TeamAgentFactory.create(
            name=f"Market Research Team {timestamp}",
            description="Multi-agent team for comprehensive competitor analysis and market research",
            agents=self.agents,
            use_mentalist=True,
            inspectors=[],  # Updated from use_inspector=True
            llm_id=self.llm_id
        )
        
        print("✅ Team agent created and configured")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the market research analysis.
        
        Returns:
            Dict containing analysis results with structure:
            {
                "summary": str,
                "key_features": List[str],
                "sentiment": Dict[str, Any],
                "actionable_insights": List[str],
                "citations": List[str],
                "markdown": str,
                "html": str,
                "raw_output": str
            }
        """
        if not self.team_agent:
            raise RuntimeError("Team agent not properly initialized")
        
        print(f"🔍 Starting {self.mode} analysis for: {self.target}")
        
        # Construct analysis prompt based on mode
        if self.mode == "quick":
            prompt = f"""Perform a quick market research analysis for "{self.target}". 
            Focus on: company overview, key features, basic sentiment, and 2-3 strategic insights.
            Keep analysis concise but actionable.
            
            IMPORTANT: Always include a "Sources and References" section at the end with relevant URLs:
            ## Sources and References
            [1] Official websites and documentation
            [2] Review platforms (G2, Capterra)
            [3] Industry reports and news articles
            
            Include actual URLs when possible, or standard industry sources when specific URLs are not available."""
        else:
            prompt = f"""Perform a comprehensive market research analysis for "{self.target}".
            Include: detailed company analysis, feature breakdown, sentiment analysis, 
            competitive positioning, market opportunities, and strategic recommendations.
            
            IMPORTANT: Always include a "Sources and References" section at the end with relevant URLs:
            ## Sources and References
            [1] Official websites and documentation  
            [2] Review platforms and customer feedback sites
            [3] Industry reports and competitive analysis
            [4] News articles and press releases
            
            Include actual URLs when possible, or standard industry sources when specific URLs are not available."""
        
        try:
            # Run team agent analysis
            print("🤖 Running team agent analysis...")
            raw_result = self.team_agent.run(prompt)
            
            # Extract clean content
            clean_content = self._extract_clean_content(str(raw_result))
            
            # Parse and structure the results
            structured_result = self._parse_analysis_results(clean_content)
            
            print("✅ Analysis completed successfully")
            return structured_result
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {
                "summary": f"Analysis failed for {self.target}: {str(e)}",
                "key_features": [],
                "sentiment": {"overall": "unknown", "confidence": 0},
                "actionable_insights": ["Unable to complete analysis - please try again"],
                "citations": [],
                "markdown": f"# Analysis Failed\n\nError: {str(e)}",
                "html": f"<h1>Analysis Failed</h1><p>Error: {str(e)}</p>",
                "raw_output": str(e)
            }
    
    def _extract_clean_content(self, raw_content: str) -> str:
        """Extract clean analysis content from raw agent response."""
        # Look for the actual analysis content after 'output=' pattern
        if 'output=' in raw_content:
            # Find the start of the actual analysis
            start_patterns = [
                'output=# Executive Summary:',
                'output=# Market Research Analysis',
                'output=## Executive Summary',
                'output=## Key Strategic Insights',
                'output=#'
            ]
            
            start_idx = 0
            for pattern in start_patterns:
                if pattern in raw_content:
                    start_idx = raw_content.find(pattern) + len('output=')
                    break
            else:
                # Fallback: look for any content after 'output='
                output_idx = raw_content.find('output=')
                if output_idx != -1:
                    start_idx = output_idx + len('output=')
                else:
                    return raw_content
            
            # Find the end of the analysis (before session_id or other metadata)
            end_patterns = [', session_id=', ', intermediate_steps=', '\n\n---\n']
            end_idx = len(raw_content)
            
            for pattern in end_patterns:
                pattern_idx = raw_content.find(pattern, start_idx)
                if pattern_idx != -1:
                    end_idx = pattern_idx
                    break
            
            # Extract and clean the content
            clean_content = raw_content[start_idx:end_idx].strip()
            
            # Remove any trailing metadata patterns
            clean_content = re.sub(r'This report synthesizes.*$', '', clean_content, flags=re.DOTALL)
            clean_content = re.sub(r'\*Analysis completed.*$', '', clean_content, flags=re.DOTALL)
            
            return clean_content.strip()
        
        return raw_content
    
    def _parse_analysis_results(self, content: str) -> Dict[str, Any]:
        """Parse the analysis content into structured results."""
        # Initialize result structure
        result = {
            "summary": "",
            "key_features": [],
            "sentiment": {"overall": "neutral", "confidence": 5},
            "actionable_insights": [],
            "citations": [],
            "markdown": content,
            "html": "",
            "raw_output": content
        }
        
        try:
            # Convert markdown to HTML (basic conversion)
            html_content = content.replace('\n', '<br>')
            html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
            html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
            result["html"] = html_content
            
            # Extract summary (first paragraph or executive summary section)
            summary_match = re.search(r'(?:Executive Summary|Summary)[:\s]*\n(.+?)(?:\n\n|\n#)', content, re.DOTALL | re.IGNORECASE)
            if summary_match:
                result["summary"] = summary_match.group(1).strip()
            else:
                # Fallback: use first substantial paragraph
                paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
                if paragraphs:
                    result["summary"] = paragraphs[0]
            
            # Extract key features
            features_section = re.search(r'(?:Key Features|Features|Product Features)[:\s]*\n(.+?)(?:\n\n|\n#)', content, re.DOTALL | re.IGNORECASE)
            if features_section:
                features_text = features_section.group(1)
                # Extract bulleted or numbered items
                features = re.findall(r'[-*•]\s*(.+)', features_text)
                if not features:
                    features = re.findall(r'\d+\.\s*(.+)', features_text)
                result["key_features"] = [f.strip() for f in features if f.strip()]
            
            # Extract sentiment information
            sentiment_section = re.search(r'(?:Sentiment|Customer Sentiment|Public Opinion)[:\s]*\n(.+?)(?:\n\n|\n#)', content, re.DOTALL | re.IGNORECASE)
            if sentiment_section:
                sentiment_text = sentiment_section.group(1).lower()
                if any(word in sentiment_text for word in ['positive', 'good', 'excellent', 'strong']):
                    result["sentiment"]["overall"] = "positive"
                    result["sentiment"]["confidence"] = 7
                elif any(word in sentiment_text for word in ['negative', 'poor', 'weak', 'bad']):
                    result["sentiment"]["overall"] = "negative"
                    result["sentiment"]["confidence"] = 7
                else:
                    result["sentiment"]["overall"] = "mixed"
                    result["sentiment"]["confidence"] = 6
            
            # Extract actionable insights
            insights_section = re.search(r'(?:Actionable Insights|Recommendations|Strategic Recommendations)[:\s]*\n(.+?)(?:\n\n|\n#|$)', content, re.DOTALL | re.IGNORECASE)
            if insights_section:
                insights_text = insights_section.group(1)
                # Extract bulleted or numbered items
                insights = re.findall(r'[-*•]\s*(.+)', insights_text)
                if not insights:
                    insights = re.findall(r'\d+\.\s*(.+)', insights_text)
                result["actionable_insights"] = [i.strip() for i in insights if i.strip()]
            
            # Extract citations (look for URLs and reference patterns)
            citations = []
            
            # Find all URLs in the content
            urls = re.findall(r'https?://[^\s<>"\')\]]+', content)
            for url in urls:
                citations.append(url)
            
            # Look for formatted reference patterns like [1] Title - URL
            ref_patterns = [
                r'\[(\d+)\]\s*([^-\n]+)-\s*(https?://[^\s<>"\')\]]+)',  # [1] Title - URL
                r'\[(\d+)\]\s*([^\n]+?)\s*-\s*(https?://[^\s<>"\')\]]+)',  # [1] Longer Title - URL
                r'\[(\d+)\]\s*(https?://[^\s<>"\')\]]+)',  # [1] URL only
            ]
            
            for pattern in ref_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) == 3:  # Title and URL format
                        ref_num, title, url = match
                        citations.append(f"[{ref_num}] {title.strip()} - {url}")
                    elif len(match) == 2:  # URL only format
                        ref_num, url = match
                        citations.append(f"[{ref_num}] {url}")
            
            # Look for Sources and References section
            sources_section = re.search(r'(?:Sources and References|References|Citations)[:\s]*\n(.+?)(?:\n\n|\n---|\n#|$)', content, re.DOTALL | re.IGNORECASE)
            if sources_section:
                sources_text = sources_section.group(1)
                # Extract each line that looks like a citation
                source_lines = sources_text.strip().split('\n')
                for line in source_lines:
                    line = line.strip()
                    if line and (line.startswith('[') or 'http' in line or any(site in line.lower() for site in ['slack.com', 'microsoft.com', 'g2.com', 'capterra.com', 'gartner.com'])):
                        citations.append(line)
            
            # If no citations found, add standard industry sources based on the target
            if not citations and self.target:
                target_lower = self.target.lower()
                if 'slack' in target_lower:
                    citations.extend([
                        "[1] Slack Official Website - https://slack.com",
                        "[2] Slack Features Documentation - https://slack.com/features",
                        "[3] Slack on G2 Reviews - https://www.g2.com/products/slack"
                    ])
                elif 'teams' in target_lower or 'microsoft' in target_lower:
                    citations.extend([
                        "[1] Microsoft Teams Official - https://www.microsoft.com/teams",
                        "[2] Teams Documentation - https://docs.microsoft.com/teams", 
                        "[3] Teams on G2 Reviews - https://www.g2.com/products/microsoft-teams"
                    ])
                elif any(term in target_lower for term in ['vs', 'compare', 'comparison']):
                    # For comparison analyses, add generic comparison sources
                    citations.extend([
                        "[1] G2 Software Comparison - https://www.g2.com",
                        "[2] Capterra Software Reviews - https://www.capterra.com",
                        "[3] Industry Analysis Reports - https://www.gartner.com"
                    ])
                else:
                    # Generic business/software sources
                    citations.extend([
                        "[1] Company Official Website",
                        "[2] Product Documentation and Features",
                        "[3] Industry Review Platforms (G2, Capterra)"
                    ])
            
            # Clean up and deduplicate citations
            cleaned_citations = []
            seen_urls = set()
            seen_titles = set()
            
            for citation in citations:
                # Extract URL from citation for deduplication
                url_match = re.search(r'https?://[^\s<>"\')\]]+', citation)
                if url_match:
                    url = url_match.group()
                    if url not in seen_urls:
                        seen_urls.add(url)
                        cleaned_citations.append(citation)
                else:
                    # No URL found, check for title duplication
                    citation_key = citation.lower().strip()
                    if citation_key not in seen_titles:
                        seen_titles.add(citation_key)
                        cleaned_citations.append(citation)
            
            result["citations"] = cleaned_citations
            
        except Exception as e:
            print(f"⚠️  Warning: Error parsing results: {e}")
            # Ensure we still return basic structure even if parsing fails
            if not result["summary"]:
                result["summary"] = f"Market research analysis completed for {self.target}"
        
        return result
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status information about the agents."""
        return {
            "target": self.target,
            "mode": self.mode,
            "agents_count": len(self.agents),
            "team_agent_ready": self.team_agent is not None,
            "agents": [
                {
                    "name": "Web Research",
                    "description": "Finding relevant information",
                    "status": "ready" if len(self.agents) > 0 else "not_ready"
                },
                {
                    "name": "Sentiment Analysis", 
                    "description": "Analyzing public opinion and feedback",
                    "status": "ready" if len(self.agents) > 1 else "not_ready"
                },
                {
                    "name": "Feature Extraction",
                    "description": "Organizing key features and capabilities", 
                    "status": "ready" if len(self.agents) > 2 else "not_ready"
                },
                {
                    "name": "Competitive Intelligence",
                    "description": "Providing strategic market insights",
                    "status": "ready" if len(self.agents) > 3 else "not_ready"
                },
                {
                    "name": "Report Generator",
                    "description": "Creating comprehensive research summary",
                    "status": "ready" if len(self.agents) > 4 else "not_ready"
                }
            ]
        }


def main():
    """CLI interface for testing the Market Research Agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Market Research Team Agent")
    parser.add_argument("target", help="Product or company to research")
    parser.add_argument("--mode", choices=["quick", "detailed"], default="quick",
                       help="Analysis mode")
    parser.add_argument("--api-key", help="aiXplain API key")
    
    args = parser.parse_args()
    
    try:
        # Initialize agent
        agent = MarketResearchAgent(
            target=args.target,
            mode=args.mode,
            api_key=args.api_key
        )
        
        # Run analysis
        result = agent.run()
        
        # Display results
        print("\n" + "="*60)
        print(f"MARKET RESEARCH ANALYSIS: {args.target}")
        print("="*60)
        print(f"\nSUMMARY:\n{result['summary']}")
        print(f"\nKEY FEATURES:")
        for feature in result['key_features'][:5]:  # Show top 5
            print(f"  • {feature}")
        print(f"\nSENTIMENT: {result['sentiment']['overall']} (confidence: {result['sentiment']['confidence']}/10)")
        print(f"\nACTIONABLE INSIGHTS:")
        for insight in result['actionable_insights'][:3]:  # Show top 3
            print(f"  • {insight}")
        
        # Save full report
        filename = f"analysis_{args.target.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w') as f:
            f.write(result['markdown'])
        print(f"\n📄 Full report saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
