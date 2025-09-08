#!/usr/bin/env python3
"""
Market Research Tools

Purpose: Utility functions for handling markdown, PDF generation, citations, and storage.
Provides helper functions for report formatting, file operations, and data persistence.

Requirements:
- pip install markdown2 weasyprint

Usage:
    from tools import render_markdown, markdown_to_pdf, save_job, load_job
    
    # Render markdown from results
    md_content = render_markdown(analysis_result)
    
    # Generate PDF
    pdf_bytes = markdown_to_pdf(md_content, "report.pdf")
    
    # Save/load job results
    save_job("job123", analysis_result)
    result = load_job("job123")
"""

import os
import json
import re
import tempfile
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Try to import optional dependencies with graceful fallbacks
try:
    import markdown2
    HAS_MARKDOWN2 = True
except ImportError:
    HAS_MARKDOWN2 = False
    print("⚠️  Warning: markdown2 not installed. Using basic markdown conversion.")

try:
    import weasyprint
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False
    print("⚠️  Warning: weasyprint not installed. PDF generation will use basic method.")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("⚠️  Warning: reportlab not installed. PDF generation fallback available.")


# Global configuration - use /tmp for Lambda
STORAGE_DIR = os.getenv("MARKET_RESEARCH_STORAGE", "/tmp/generated_reports")
JOBS_DIR = os.path.join(STORAGE_DIR, "jobs")

# Ensure directories exist
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for filesystem use.
    
    Args:
        filename: The original filename
        
    Returns:
        A sanitized filename safe for use on any filesystem
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores and trim
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('_. ')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized


def generate_timestamp(format_type: str = "filename") -> str:
    """
    Generate a timestamp string in various formats.
    
    Args:
        format_type: Type of format ("filename", "display", "iso")
        
    Returns:
        Formatted timestamp string
    """
    now = datetime.now()
    
    if format_type == "filename":
        return now.strftime("%Y%m%d_%H%M%S")
    elif format_type == "display":
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "iso":
        return now.isoformat()
    else:
        return str(now)


def generate_job_id(target: str) -> str:
    """
    Generate a unique job ID based on target and timestamp.
    
    Args:
        target: The research target
        
    Returns:
        Unique job ID string
    """
    timestamp = generate_timestamp("filename")
    sanitized_target = sanitize_filename(target.lower().replace(" ", "_"))
    
    # Add a hash for uniqueness
    hash_input = f"{target}{timestamp}{os.getpid()}"
    hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    return f"{sanitized_target}_{timestamp}_{hash_suffix}"


def render_markdown(result: Dict[str, Any]) -> str:
    """
    Render analysis results into formatted markdown.
    
    Args:
        result: Dictionary containing analysis results
        
    Returns:
        Formatted markdown string
    """
    if not result:
        return "# Analysis Error\n\nNo results available."
    
    # Start with existing markdown if available
    if "markdown" in result and result["markdown"]:
        base_content = result["markdown"]
    else:
        # Generate markdown from structured data
        base_content = f"# Market Research Analysis Report\n\n"
        
        if "summary" in result and result["summary"]:
            base_content += f"## Executive Summary\n\n{result['summary']}\n\n"
        
        if "key_features" in result and result["key_features"]:
            base_content += "## Key Features\n\n"
            for feature in result["key_features"]:
                base_content += f"- {feature}\n"
            base_content += "\n"
        
        if "sentiment" in result and result["sentiment"]:
            sentiment = result["sentiment"]
            base_content += f"## Sentiment Analysis\n\n"
            base_content += f"**Overall Sentiment:** {sentiment.get('overall', 'Unknown')}\n"
            base_content += f"**Confidence Level:** {sentiment.get('confidence', 0)}/10\n\n"
        
        if "actionable_insights" in result and result["actionable_insights"]:
            base_content += "## Actionable Insights\n\n"
            for i, insight in enumerate(result["actionable_insights"], 1):
                base_content += f"{i}. {insight}\n"
            base_content += "\n"
    
    # Add metadata section
    metadata_section = f"""
---

## Analysis Metadata

- **Generated:** {generate_timestamp("display")}
- **Analysis Framework:** Multi-Agent aiXplain System
- **Processing Status:** Completed Successfully

"""
    
    # Add citations if available
    if "citations" in result and result["citations"]:
        citations_section = "\n## Sources and References\n\n"
        for i, citation in enumerate(result["citations"], 1):
            if citation.startswith("["):
                # Already formatted citation
                citations_section += f"{citation}\n"
            elif citation.startswith("http"):
                # Just a URL - format it nicely
                citations_section += f"[{i}] {citation}\n"
            else:
                # Other format - ensure it has a number
                if not re.match(r'^\[\d+\]', citation):
                    citations_section += f"[{i}] {citation}\n"
                else:
                    citations_section += f"{citation}\n"
        citations_section += "\n"
        base_content += citations_section
    
    # Combine all sections
    full_markdown = base_content + metadata_section
    
    # Clean up any formatting issues
    full_markdown = re.sub(r'\n{3,}', '\n\n', full_markdown)  # Remove excessive newlines
    full_markdown = full_markdown.strip()
    
    return full_markdown


def markdown_to_pdf(md_content: str, filename: str, target: str = "Unknown") -> bytes:
    """
    Convert markdown content to PDF.
    
    Args:
        md_content: Markdown content string
        filename: Target filename for the PDF
        target: The research target for cover page
        
    Returns:
        PDF content as bytes
    """
    try:
        if HAS_WEASYPRINT:
            return _markdown_to_pdf_weasyprint(md_content, filename, target)
        elif HAS_REPORTLAB:
            return _markdown_to_pdf_reportlab(md_content, filename, target)
        else:
            return _markdown_to_pdf_basic(md_content, filename, target)
    except Exception as e:
        print(f"⚠️  Warning: PDF generation failed: {e}")
        # Return a basic PDF with error message
        return _create_error_pdf(str(e), filename)


def _markdown_to_pdf_weasyprint(md_content: str, filename: str, target: str) -> bytes:
    """Generate PDF using WeasyPrint (best quality)."""
    # Convert markdown to HTML
    if HAS_MARKDOWN2:
        html_content = markdown2.markdown(md_content, extras=['fenced-code-blocks', 'tables'])
    else:
        # Basic markdown conversion
        html_content = _basic_markdown_to_html(md_content)
    
    # Create full HTML document with styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Market Research Report - {target}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 40px auto;
                padding: 40px;
                color: #333;
            }}
            .cover-page {{
                text-align: center;
                margin-bottom: 100px;
                page-break-after: always;
            }}
            .cover-title {{
                font-size: 2.5em;
                color: #2c5aa0;
                margin-bottom: 30px;
            }}
            .cover-subtitle {{
                font-size: 1.5em;
                color: #666;
                margin-bottom: 50px;
            }}
            .cover-date {{
                font-size: 1.2em;
                color: #888;
            }}
            h1 {{ color: #2c5aa0; border-bottom: 3px solid #2c5aa0; padding-bottom: 10px; }}
            h2 {{ color: #34495e; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }}
            h3 {{ color: #34495e; }}
            blockquote {{
                border-left: 4px solid #2c5aa0;
                margin-left: 0;
                padding-left: 20px;
                background: #f8f9fa;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 4px;
                border-radius: 3px;
            }}
            @page {{
                margin: 1in;
                @bottom-center {{
                    content: counter(page);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="cover-page">
            <h1 class="cover-title">Market Research Analysis</h1>
            <h2 class="cover-subtitle">{target}</h2>
            <p class="cover-date">Generated on {generate_timestamp("display")}</p>
            <p style="margin-top: 50px; color: #666;">
                Powered by Multi-Agent aiXplain System
            </p>
        </div>
        {html_content}
    </body>
    </html>
    """
    
    # Generate PDF
    pdf = weasyprint.HTML(string=full_html).write_pdf()
    return pdf


def _markdown_to_pdf_reportlab(md_content: str, filename: str, target: str) -> bytes:
    """Generate PDF using ReportLab (good quality)."""
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#666666'),
        spaceAfter=50,
        alignment=1  # Center
    )
    
    # Cover page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Market Research Analysis", title_style))
    story.append(Paragraph(target, subtitle_style))
    story.append(Paragraph(f"Generated on {generate_timestamp('display')}", styles['Normal']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Powered by Multi-Agent aiXplain System", styles['Normal']))
    story.append(PageBreak())
    
    # Convert markdown to paragraphs (basic conversion)
    lines = md_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 12))
        elif line.startswith('# '):
            story.append(Paragraph(line[2:], styles['Heading1']))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], styles['Heading2']))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles['Heading3']))
        elif line.startswith('- ') or line.startswith('* '):
            story.append(Paragraph(f"• {line[2:]}", styles['Normal']))
        else:
            if line:
                story.append(Paragraph(line, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def _basic_markdown_to_html(md_content: str) -> str:
    """Basic markdown to HTML conversion without external dependencies."""
    html = md_content
    
    # Headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # Line breaks
    html = html.replace('\n', '<br>')
    
    return html


def _markdown_to_pdf_basic(md_content: str, filename: str, target: str) -> bytes:
    """Basic PDF generation fallback."""
    # Create a simple HTML file and try to use system tools
    html_content = _basic_markdown_to_html(md_content)
    
    # Return HTML as "PDF" (browsers can convert HTML to PDF)
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Market Research Report - {target}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #2c5aa0; }}
            h2 {{ color: #34495e; }}
        </style>
    </head>
    <body>
        <h1>Market Research Analysis: {target}</h1>
        <p><em>Generated on {generate_timestamp("display")}</em></p>
        <hr>
        {html_content}
    </body>
    </html>
    """
    
    return full_html.encode('utf-8')


def _create_error_pdf(error_msg: str, filename: str) -> bytes:
    """Create a simple error PDF when generation fails."""
    error_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Generation Error</title>
    </head>
    <body>
        <h1>PDF Generation Error</h1>
        <p>Unable to generate PDF: {error_msg}</p>
        <p>Please install required dependencies:</p>
        <ul>
            <li>pip install weasyprint</li>
            <li>pip install reportlab</li>
        </ul>
    </body>
    </html>
    """
    return error_html.encode('utf-8')


def save_job(job_id: str, result: Dict[str, Any]) -> None:
    """
    Save job result to persistent storage.
    
    Args:
        job_id: Unique job identifier
        result: Analysis result dictionary
    """
    try:
        job_file = os.path.join(JOBS_DIR, f"{job_id}.json")
        
        # Add metadata
        job_data = {
            "job_id": job_id,
            "created_at": generate_timestamp("iso"),
            "status": "completed",
            "result": result
        }
        
        with open(job_file, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Job {job_id} saved successfully")
        
    except Exception as e:
        print(f"⚠️  Warning: Failed to save job {job_id}: {e}")


def load_job(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Load job result from persistent storage.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Job data dictionary or None if not found
    """
    try:
        job_file = os.path.join(JOBS_DIR, f"{job_id}.json")
        
        if not os.path.exists(job_file):
            return None
        
        with open(job_file, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
        
        return job_data
        
    except Exception as e:
        print(f"⚠️  Warning: Failed to load job {job_id}: {e}")
        return None


def list_jobs() -> List[Dict[str, Any]]:
    """
    List all saved jobs.
    
    Returns:
        List of job metadata dictionaries
    """
    jobs = []
    
    try:
        if not os.path.exists(JOBS_DIR):
            return jobs
        
        for filename in os.listdir(JOBS_DIR):
            if filename.endswith('.json'):
                job_id = filename[:-5]  # Remove .json extension
                job_data = load_job(job_id)
                if job_data:
                    jobs.append({
                        "job_id": job_id,
                        "created_at": job_data.get("created_at"),
                        "status": job_data.get("status", "unknown"),
                        "target": job_data.get("result", {}).get("target", "Unknown")
                    })
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
    except Exception as e:
        print(f"⚠️  Warning: Failed to list jobs: {e}")
    
    return jobs


def cleanup_old_jobs(days_old: int = 30) -> int:
    """
    Clean up job files older than specified days.
    
    Args:
        days_old: Number of days after which to delete jobs
        
    Returns:
        Number of jobs cleaned up
    """
    cleaned = 0
    
    try:
        if not os.path.exists(JOBS_DIR):
            return 0
        
        import time
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        
        for filename in os.listdir(JOBS_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(JOBS_DIR, filename)
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    cleaned += 1
        
        print(f"✅ Cleaned up {cleaned} old job files")
        
    except Exception as e:
        print(f"⚠️  Warning: Failed to cleanup jobs: {e}")
    
    return cleaned


def export_job_markdown(job_id: str, output_dir: str = None) -> Optional[str]:
    """
    Export job result as markdown file.
    
    Args:
        job_id: Job identifier
        output_dir: Output directory (defaults to STORAGE_DIR)
        
    Returns:
        Path to exported file or None if failed
    """
    try:
        job_data = load_job(job_id)
        if not job_data:
            return None
        
        result = job_data.get("result", {})
        markdown_content = render_markdown(result)
        
        # Determine output path
        if output_dir is None:
            output_dir = STORAGE_DIR
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        target = result.get("target", job_id)
        safe_target = sanitize_filename(target)
        filename = f"{safe_target}_{job_id}.md"
        output_path = os.path.join(output_dir, filename)
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_path
        
    except Exception as e:
        print(f"⚠️  Warning: Failed to export job {job_id}: {e}")
        return None


def export_job_pdf(job_id: str, output_dir: str = None) -> Optional[str]:
    """
    Export job result as PDF file.
    
    Args:
        job_id: Job identifier
        output_dir: Output directory (defaults to STORAGE_DIR)
        
    Returns:
        Path to exported file or None if failed
    """
    try:
        job_data = load_job(job_id)
        if not job_data:
            return None
        
        result = job_data.get("result", {})
        markdown_content = render_markdown(result)
        target = result.get("target", job_id)
        
        # Generate PDF
        pdf_bytes = markdown_to_pdf(markdown_content, f"{job_id}.pdf", target)
        
        # Determine output path
        if output_dir is None:
            output_dir = STORAGE_DIR
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        safe_target = sanitize_filename(target)
        filename = f"{safe_target}_{job_id}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # Write file
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return output_path
        
    except Exception as e:
        print(f"⚠️  Warning: Failed to export PDF for job {job_id}: {e}")
        return None


# Convenience functions for backward compatibility
def get_clean_report(results: Dict[str, Any]) -> str:
    """Legacy function - use render_markdown instead."""
    return render_markdown(results)


def create_pdf_report(content: str, product_name: str, filename: str) -> bytes:
    """Legacy function - use markdown_to_pdf instead.""" 
    return markdown_to_pdf(content, filename, product_name)


if __name__ == "__main__":
    # Test the tools
    print("🧪 Testing Market Research Tools...")
    
    # Sample result for testing
    test_result = {
        "summary": "Test summary of market research analysis",
        "key_features": ["Feature 1", "Feature 2", "Feature 3"],
        "sentiment": {"overall": "positive", "confidence": 8},
        "actionable_insights": ["Insight 1", "Insight 2"],
        "citations": ["https://example.com", "[1] Reference example"],
        "markdown": "# Test\n\nThis is a test report.",
        "target": "Test Product"
    }
    
    # Test markdown rendering
    markdown_content = render_markdown(test_result)
    print(f"✅ Markdown rendered ({len(markdown_content)} chars)")
    
    # Test job storage
    test_job_id = generate_job_id("test_product")
    save_job(test_job_id, test_result)
    loaded_result = load_job(test_job_id)
    print(f"✅ Job storage test: {'PASS' if loaded_result else 'FAIL'}")
    
    # Test PDF generation
    try:
        pdf_bytes = markdown_to_pdf(markdown_content, "test.pdf", "Test Product")
        print(f"✅ PDF generated ({len(pdf_bytes)} bytes)")
    except Exception as e:
        print(f"⚠️  PDF test failed: {e}")
    
    print("🧪 Tools testing completed!")
