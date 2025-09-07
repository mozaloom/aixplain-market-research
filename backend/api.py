#!/usr/bin/env python3
"""
Market Research API

Purpose: FastAPI backend exposing endpoints for Market Research Team Agent.
Provides REST API endpoints for running analysis, retrieving results, and downloading reports.

Requirements:
- pip install aixplain fastapi uvicorn pydantic markdown2 weasyprint

Demo Curl Commands:
# Health check
curl -X GET "http://localhost:8000/health"

# Start analysis
curl -X POST "http://localhost:8000/run-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "Slack",
    "mode": "quick",
    "api_key": "your_aixplain_api_key"
  }'

# Get results
curl -X GET "http://localhost:8000/results/job_id_here"

# Download markdown report
curl -X GET "http://localhost:8000/download/job_id_here.md" \
  -o "report.md"

# Download PDF report  
curl -X GET "http://localhost:8000/download/job_id_here.pdf" \
  -o "report.pdf"

# Download citations
curl -X GET "http://localhost:8000/download/job_id_here/citations.json" \
  -o "citations.json"

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import json
import os
import re
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# Import our custom modules
from agent import MarketResearchAgent
from tools import (
    render_markdown, markdown_to_pdf, save_job, load_job, list_jobs,
    generate_job_id, sanitize_filename, generate_timestamp,
    export_job_markdown, export_job_pdf, cleanup_old_jobs
)

# Global job storage (in-memory for this implementation)
# In production, consider using Redis or a database
job_store: Dict[str, Dict[str, Any]] = {}
active_tasks: Dict[str, asyncio.Task] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    print("🚀 Market Research API starting up...")
    
    # Cleanup old jobs on startup
    cleanup_old_jobs(days_old=7)
    
    yield
    
    # Shutdown
    print("🛑 Market Research API shutting down...")
    
    # Cancel any running tasks
    for task_id, task in active_tasks.items():
        if not task.done():
            print(f"Cancelling task {task_id}")
            task.cancel()


# Initialize FastAPI app
app = FastAPI(
    title="Market Research API",
    description="Multi-Agent Market Research System using aiXplain SDK",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000", 
        "https://main.d1lnp7miiwrzlm.amplifyapp.com",
        "*"  # For development - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response validation
class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""
    target: str = Field(..., description="Product or company to research", min_length=1)
    mode: str = Field(default="quick", description="Analysis mode: 'quick' or 'detailed'")
    api_key: str = Field(..., description="aiXplain API key", min_length=1)
    
    class Config:
        schema_extra = {
            "example": {
                "target": "Slack",
                "mode": "quick",
                "api_key": "your_aixplain_api_key"
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for analysis endpoint."""
    job_id: str
    status: str
    message: str
    estimated_completion: Optional[str] = None


class JobStatus(BaseModel):
    """Model for job status information."""
    job_id: str
    status: str
    target: str
    mode: str
    created_at: str
    completed_at: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Market Research API",
        "version": "1.0.0",
        "description": "Multi-Agent Market Research System using aiXplain SDK",
        "timestamp": generate_timestamp("iso"),
        "endpoints": {
            "health": "GET /health",
            "start_analysis": "POST /run-agent",
            "get_results": "GET /results/{job_id}",
            "download_markdown": "GET /download/{job_id}.md",
            "download_pdf": "GET /download/{job_id}.pdf",
            "download_citations": "GET /download/{job_id}/citations.json",
            "list_jobs": "GET /jobs",
            "delete_job": "DELETE /jobs/{job_id}"
        },
        "documentation": "/docs",
        "status": "online",
        "active_jobs": len(job_store),
        "running_tasks": len([t for t in active_tasks.values() if not t.done()])
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "v1",
        "timestamp": generate_timestamp("iso"),
        "active_jobs": len(job_store),
        "running_tasks": len([t for t in active_tasks.values() if not t.done()])
    }


@app.post("/run-agent", response_model=AnalysisResponse)
async def run_agent(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Start a market research analysis.
    
    Starts the analysis in the background and returns a job ID for tracking progress.
    """
    try:
        # Validate inputs
        if not request.target.strip():
            raise HTTPException(status_code=400, detail="Target cannot be empty")
        
        if request.mode not in ["quick", "detailed"]:
            raise HTTPException(status_code=400, detail="Mode must be 'quick' or 'detailed'")
        
        # Generate job ID
        job_id = generate_job_id(request.target)
        
        # Initialize job status
        job_data = {
            "job_id": job_id,
            "status": "starting",
            "target": request.target,
            "mode": request.mode,
            "created_at": generate_timestamp("iso"),
            "completed_at": None,
            "progress": {
                "stage": "initializing",
                "agents_ready": False,
                "analysis_started": False,
                "analysis_completed": False
            },
            "result": None,
            "error": None
        }
        
        job_store[job_id] = job_data
        
        # Start background analysis
        if request.mode == "detailed":
            # For detailed analysis, run async
            task = asyncio.create_task(
                run_analysis_async(job_id, request.target, request.mode, request.api_key)
            )
            active_tasks[job_id] = task
            background_tasks.add_task(cleanup_completed_task, job_id)
            
            estimated_time = "10-15 minutes"
        else:
            # For quick analysis, also run async but with faster estimate
            task = asyncio.create_task(
                run_analysis_async(job_id, request.target, request.mode, request.api_key)
            )
            active_tasks[job_id] = task
            background_tasks.add_task(cleanup_completed_task, job_id)
            
            estimated_time = "5-8 minutes"
        
        return AnalysisResponse(
            job_id=job_id,
            status="started",
            message=f"Analysis started for '{request.target}' in {request.mode} mode",
            estimated_completion=estimated_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")


@app.get("/results/{job_id}", response_model=JobStatus)
async def get_results(job_id: str):
    """
    Get the status and results of an analysis job.
    
    Returns job status, progress information, and results if completed.
    """
    try:
        # Check in-memory store first
        if job_id in job_store:
            job_data = job_store[job_id]
        else:
            # Try to load from persistent storage
            stored_job = load_job(job_id)
            if stored_job:
                job_data = stored_job
                # Update in-memory store
                job_store[job_id] = job_data
            else:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return JobStatus(**job_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job: {str(e)}")


@app.get("/download/{job_id}.md")
async def download_markdown(job_id: str):
    """Download markdown report for a completed job."""
    try:
        # Get job data
        if job_id in job_store:
            job_data = job_store[job_id]
        else:
            stored_job = load_job(job_id)
            if not stored_job:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
            job_data = stored_job
        
        if job_data["status"] != "completed" or not job_data["result"]:
            raise HTTPException(status_code=400, detail="Job not completed or no results available")
        
        # Generate markdown content
        markdown_content = render_markdown(job_data["result"])
        
        # Create filename
        target = sanitize_filename(job_data["target"])
        filename = f"analysis_{target}_{job_id[:8]}.md"
        
        # Return as file response
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error downloading markdown for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate markdown: {str(e)}")


@app.get("/download/{job_id}.pdf")
async def download_pdf(job_id: str):
    """Download PDF report for a completed job."""
    try:
        # Get job data
        if job_id in job_store:
            job_data = job_store[job_id]
        else:
            stored_job = load_job(job_id)
            if not stored_job:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
            job_data = stored_job
        
        if job_data["status"] != "completed" or not job_data["result"]:
            raise HTTPException(status_code=400, detail="Job not completed or no results available")
        
        # Generate PDF content
        markdown_content = render_markdown(job_data["result"])
        pdf_bytes = markdown_to_pdf(markdown_content, f"{job_id}.pdf", job_data["target"])
        
        # Create filename
        target = sanitize_filename(job_data["target"])
        filename = f"analysis_{target}_{job_id[:8]}.pdf"
        
        # Return as file response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error downloading PDF for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@app.get("/download/{job_id}/citations.json")
async def download_citations(job_id: str):
    """Download citations as JSON for a completed job."""
    try:
        # Get job data
        if job_id in job_store:
            job_data = job_store[job_id]
        else:
            stored_job = load_job(job_id)
            if not stored_job:
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
            job_data = stored_job
        
        if job_data["status"] != "completed" or not job_data["result"]:
            raise HTTPException(status_code=400, detail="Job not completed or no results available")
        
        # Extract citations
        result = job_data["result"]
        citations_data = {
            "job_id": job_id,
            "target": job_data["target"],
            "generated_at": generate_timestamp("iso"),
            "citations": [],
            "total_citations": 0
        }
        
        # Process citations to include metadata
        raw_citations = result.get("citations", [])
        processed_citations = []
        
        for i, citation in enumerate(raw_citations, 1):
            citation_entry = {
                "id": i,
                "raw": citation,
                "url": None,
                "title": None,
                "formatted": citation
            }
            
            # Try to extract URL and title
            url_match = re.search(r'https?://[^\s<>"\')\]]+', citation)
            if url_match:
                citation_entry["url"] = url_match.group()
                
                # Try to extract title
                if citation.startswith("["):
                    # Format: [1] Title - URL
                    title_match = re.search(r'\[\d+\]\s*([^-]+?)\s*-\s*https?://', citation)
                    if title_match:
                        citation_entry["title"] = title_match.group(1).strip()
                else:
                    # Just URL or other format
                    citation_entry["title"] = citation_entry["url"]
            
            processed_citations.append(citation_entry)
        
        citations_data["citations"] = processed_citations
        citations_data["total_citations"] = len(processed_citations)
        
        # Create filename
        target = sanitize_filename(job_data["target"])
        filename = f"citations_{target}_{job_id[:8]}.json"
        
        # Return as JSON response
        return Response(
            content=json.dumps(citations_data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error downloading citations for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate citations: {str(e)}")


@app.get("/jobs")
async def list_all_jobs():
    """List all jobs (both active and completed)."""
    try:
        jobs = []
        
        # Add active jobs from memory
        for job_id, job_data in job_store.items():
            jobs.append({
                "job_id": job_id,
                "target": job_data["target"],
                "mode": job_data["mode"],
                "status": job_data["status"],
                "created_at": job_data["created_at"],
                "completed_at": job_data.get("completed_at")
            })
        
        # Add persisted jobs
        persisted_jobs = list_jobs()
        for job in persisted_jobs:
            # Avoid duplicates
            if not any(j["job_id"] == job["job_id"] for j in jobs):
                jobs.append(job)
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {"jobs": jobs, "total": len(jobs)}
        
    except Exception as e:
        print(f"❌ Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its associated files."""
    try:
        # Remove from memory
        if job_id in job_store:
            del job_store[job_id]
        
        # Cancel running task if exists
        if job_id in active_tasks:
            task = active_tasks[job_id]
            if not task.done():
                task.cancel()
            del active_tasks[job_id]
        
        # Remove from persistent storage
        job_file = f"generated_reports/jobs/{job_id}.json"
        if os.path.exists(job_file):
            os.remove(job_file)
        
        return {"message": f"Job {job_id} deleted successfully"}
        
    except Exception as e:
        print(f"❌ Error deleting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")


# Background task functions

async def run_analysis_async(job_id: str, target: str, mode: str, api_key: str):
    """Run the market research analysis asynchronously."""
    try:
        # Update job status
        job_store[job_id]["status"] = "running"
        job_store[job_id]["progress"]["stage"] = "creating_agents"
        
        # Initialize agent
        print(f"🤖 Initializing Market Research Agent for {target}")
        agent = MarketResearchAgent(target=target, mode=mode, api_key=api_key)
        
        # Update progress
        job_store[job_id]["progress"]["agents_ready"] = True
        job_store[job_id]["progress"]["stage"] = "running_analysis"
        job_store[job_id]["progress"]["analysis_started"] = True
        
        # Run analysis
        print(f"🔍 Running {mode} analysis for {target}")
        result = agent.run()
        
        # Update job with results
        job_store[job_id]["status"] = "completed"
        job_store[job_id]["completed_at"] = generate_timestamp("iso")
        job_store[job_id]["progress"]["analysis_completed"] = True
        job_store[job_id]["progress"]["stage"] = "completed"
        job_store[job_id]["result"] = result
        
        # Save to persistent storage
        save_job(job_id, result)
        
        print(f"✅ Analysis completed for {target} (Job: {job_id})")
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Analysis failed for {target} (Job: {job_id}): {error_msg}")
        
        # Update job with error
        job_store[job_id]["status"] = "failed"
        job_store[job_id]["completed_at"] = generate_timestamp("iso")
        job_store[job_id]["error"] = error_msg
        job_store[job_id]["progress"]["stage"] = "failed"


async def cleanup_completed_task(job_id: str):
    """Clean up completed background tasks."""
    try:
        # Wait a bit for task to potentially complete
        await asyncio.sleep(30)
        
        # Remove completed task from active tasks
        if job_id in active_tasks:
            task = active_tasks[job_id]
            if task.done():
                del active_tasks[job_id]
                print(f"🧹 Cleaned up completed task for job {job_id}")
    
    except Exception as e:
        print(f"⚠️  Warning: Error cleaning up task {job_id}: {e}")


# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": generate_timestamp("iso")
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    print(f"❌ Unhandled exception: {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": generate_timestamp("iso")
        }
    )


# Main entry point
if __name__ == "__main__":
    print("🚀 Starting Market Research API server...")
    print("📚 Available endpoints:")
    print("   GET  /health - Health check")
    print("   POST /run-agent - Start analysis")
    print("   GET  /results/{job_id} - Get job status/results")
    print("   GET  /download/{job_id}.md - Download markdown report")
    print("   GET  /download/{job_id}.pdf - Download PDF report")
    print("   GET  /download/{job_id}/citations.json - Download citations")
    print("   GET  /jobs - List all jobs")
    print("   DELETE /jobs/{job_id} - Delete a job")
    print("\n🌐 Server will be available at: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
