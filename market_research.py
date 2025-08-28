#!/usr/bin/env python3
"""
Multi-Agent Market Research System
A sophisticated market research system using aiXplain SDK with 5 specialized agents.
"""

import os
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
import json
import re

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
    exit(1)

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

class MarketResearchSystem:
    """Multi-agent market research system for competitor analysis."""
    
    def __init__(self, api_key: str):
        """Initialize the system with API key."""
        if not api_key:
            raise ValueError("API key is required")
        
        # Set API key in environment
        os.environ["TEAM_API_KEY"] = api_key
        self.team_agent = None
        self.agents = []
        
        # Validated model IDs (these are real IDs from aiXplain)
        self.llm_id = "6646261c6eb563165658bbb1"  # GPT-4o
        self.search_model_id = "669a63646eb56306647e1091"  # A working search model
        
    def _validate_environment(self) -> bool:
        """Validate that the environment is properly configured."""
        try:
            # Test basic SDK connection
            ModelFactory.list(page_size=1)
            return True
        except Exception as e:
            print(f"❌ SDK validation failed: {e}")
            return False
    
    def setup_agents(self) -> bool:
        """Create and configure all 5 specialized agents."""
        try:
            if not self._validate_environment():
                return False
                
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
5. Focus on factual, verifiable information""",
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
5. Provide sentiment summary with supporting evidence and confidence metrics""",
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
5. Note any missing or unclear feature information for follow-up""",
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
5. Provide strategic insights about competitive positioning and potential threats/opportunities""",
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
5. Focus on business implications and strategic recommendations for decision-makers""",
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
                use_inspector=True,
                llm_id=self.llm_id
            )
            
            print("✅ Team agent created and configured")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up agents: {e}")
            return False
    
    def analyze_competitor(self, product_name: str, industry: str = "", depth: str = "detailed") -> Dict[str, Any]:
        """Main analysis method."""
        if not self.team_agent:
            return {"error": "Team not initialized. Call setup_agents() first.", "status": "failed"}
        
        # Construct comprehensive analysis query
        query = f"""Conduct a comprehensive market research analysis of: {product_name}

ANALYSIS REQUIREMENTS:
Industry Context: {industry or "General Technology"}
Analysis Depth: {depth}

WORKFLOW INSTRUCTIONS:
1. WEB RESEARCH: Find comprehensive information about {product_name} including:
   - Company background and key details
   - Product features and capabilities  
   - Pricing models and plans
   - Target market and positioning
   - Official documentation and specifications

2. SENTIMENT ANALYSIS: Research customer feedback and sentiment:
   - Search for reviews on G2, Capterra, Reddit, forums
   - Analyze sentiment patterns and themes
   - Calculate confidence scores for sentiment assessment
   - Identify key customer pain points and praise points

3. FEATURE EXTRACTION: Extract and organize product features:
   - Categorize into Core, Advanced, Integration, and Unique features
   - Create structured feature matrix
   - Note technical specifications where available

4. COMPETITIVE INTELLIGENCE: Analyze competitive position:
   - Compare features against market standards
   - Identify strengths, weaknesses, and differentiators
   - Assess pricing strategy and value proposition
   - Identify market opportunities and threats

5. EXECUTIVE REPORT: Create comprehensive summary with:
   - 3-5 key strategic insights with evidence
   - Actionable recommendations (High/Medium/Low priority)
   - Business implications and strategic guidance
   - Professional executive summary format

Please coordinate between all agents to ensure comprehensive coverage of all analysis areas."""

        try:
            print("🔍 Starting comprehensive analysis...")
            print("⏳ This may take 5-15 minutes depending on complexity...")
            
            result = self.team_agent.run(
                query=query,
                output_format=OutputFormat.MARKDOWN,
                max_iterations=30,  # Increased for complex analysis
                timeout=900  # 15 minute timeout
            )
            
            print("✅ Analysis completed successfully")
            return {"status": "success", "result": result}
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Analysis failed: {error_msg}")
            return {
                "error": error_msg, 
                "status": "failed",
                "product": product_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Format and save analysis results."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if results.get("status") == "success" and "result" in results:
            # Handle successful results
            result_obj = results["result"]
            
            # Extract content based on result type
            if hasattr(result_obj, 'data'):
                content = str(result_obj.data)
            elif isinstance(result_obj, dict):
                content = result_obj.get('output', str(result_obj))
            else:
                content = str(result_obj)
            
            # Clean and format the content
            if content:
                report = f"""# 🔍 Market Research Analysis Report

**Generated:** {timestamp}
**Status:** ✅ Analysis Completed Successfully

---

{content}

---

**Analysis Metadata:**
- Processing Status: Completed Successfully
- Generated: {timestamp}
- Analysis Framework: Multi-Agent aiXplain System
"""
            else:
                report = f"""# 🔍 Market Research Analysis Report

**Generated:** {timestamp}
**Status:** ⚠️ Analysis Completed with Limited Data

**Note:** The analysis completed but returned limited data. This may indicate:
- Limited public information available for the analyzed product
- Rate limiting or API restrictions
- Need for more specific search terms

**Raw Result:** {str(result_obj)[:1000]}...

---
**Metadata:** Analysis completed with limited results
"""
        else:
            # Handle error cases
            error_info = results.get("error", "Unknown error")
            report = f"""# 🔍 Market Research Analysis - Error Report

**Generated:** {timestamp}
**Status:** ❌ Analysis Failed

## Error Details
```
{error_info}
```

## Troubleshooting Suggestions
1. **API Key Issues:** Verify your aiXplain API key is valid and has sufficient credits
2. **Network Issues:** Check internet connectivity and firewall settings  
3. **Product Name:** Try more specific or alternative product names
4. **Rate Limits:** Wait a few minutes and try again if hitting API limits

## Debug Information
- Product: {results.get('product', 'Unknown')}
- Timestamp: {results.get('timestamp', 'Unknown')}
- Error Type: {type(error_info).__name__ if hasattr(error_info, '__name__') else 'String'}

---
**Need Help?** Check the aiXplain documentation or contact support.
"""
        
        # Save to file if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"📄 Report saved to: {output_file}")
            except Exception as e:
                print(f"⚠️  Could not save to file {output_file}: {e}")
                
        return report

def main():
    """CLI interface with enhanced error handling."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Market Research System powered by aiXplain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python market_research.py --product "Slack" --industry "Communication"
  python market_research.py --product "Salesforce CRM" --depth basic --output report.md
  
Environment Variables:
  TEAM_API_KEY    Your aiXplain API key (alternative to --api-key)
        """
    )
    
    parser.add_argument("--product", required=True, 
                       help="Competitor product name (e.g., 'Slack', 'Salesforce CRM')")
    parser.add_argument("--industry", default="", 
                       help="Industry context (e.g., 'SaaS', 'E-commerce', 'FinTech')")
    parser.add_argument("--depth", choices=["basic", "detailed"], default="detailed",
                       help="Analysis depth level")
    parser.add_argument("--output", 
                       help="Output file path (default: auto-generated)")
    parser.add_argument("--api-key", 
                       help="aiXplain API key (or set TEAM_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv("TEAM_API_KEY")
    if not api_key:
        print("❌ Error: API key required!")
        print("   Use: --api-key YOUR_KEY")
        print("   Or:  export TEAM_API_KEY=YOUR_KEY")
        print("\n🔗 Get your API key at: https://platform.aixplain.com/")
        return 1
    
    print("🚀 Initializing Multi-Agent Market Research System")
    print(f"📊 Target Product: {args.product}")
    print(f"🏢 Industry: {args.industry or 'General'}")
    print(f"🔍 Analysis Depth: {args.depth}")
    print("-" * 60)
    
    try:
        # Initialize system
        system = MarketResearchSystem(api_key)
        
        # Setup agents
        if not system.setup_agents():
            print("❌ Failed to setup agents. Please check your API key and try again.")
            return 1
        
        print("-" * 60)
        
        # Run analysis
        results = system.analyze_competitor(args.product, args.industry, args.depth)
        
        # Generate report
        output_file = args.output or f"market_analysis_{args.product.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report = system.generate_report(results, output_file)
        
        # Display summary
        print("\n" + "="*80)
        print("📈 MARKET RESEARCH ANALYSIS COMPLETE")
        print("="*80)
        
        # Show first 1500 characters of the report
        preview_length = 1500
        if len(report) > preview_length:
            print(report[:preview_length] + "\n\n... [Report continues in file] ...")
        else:
            print(report)
        
        if results.get("status") == "success":
            print(f"\n✅ Analysis completed successfully!")
            print(f"📄 Full report saved to: {output_file}")
            return 0
        else:
            print(f"\n⚠️  Analysis completed with issues. Check the report for details.")
            return 2
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Analysis interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Try checking your API key and internet connection")
        return 1

if __name__ == "__main__":
    exit(main())