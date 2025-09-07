import React, { useState, useEffect } from 'react';
import { Search, TrendingUp, Users, FileText, Zap, CheckCircle, AlertCircle, Clock } from 'lucide-react';

const App = () => {
  const [formData, setFormData] = useState({
    product: '', // This can be a product name or research query
    industry: 'Technology',
    apiKey: ''
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [timer, setTimer] = useState(0);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Timer effect
  useEffect(() => {
    let interval = null;
    if (isAnalyzing) {
      interval = setInterval(() => {
        setTimer(timer => timer + 1);
      }, 1000);
    } else if (!isAnalyzing && timer !== 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isAnalyzing, timer]);

  // Format timer display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const downloadReport = async (format) => {
    if (!currentJobId) {
      alert('No job ID available for download');
      return;
    }

    try {
      let url = '';
      let filename = '';
      
      if (format === 'pdf') {
        url = `${API_BASE_URL}/download/${currentJobId}.pdf`;
        filename = `analysis_${formData.product.replace(/\s+/g, '_')}.pdf`;
      } else if (format === 'markdown') {
        url = `${API_BASE_URL}/download/${currentJobId}.md`;
        filename = `analysis_${formData.product.replace(/\s+/g, '_')}.md`;
      } else if (format === 'citations') {
        url = `${API_BASE_URL}/download/${currentJobId}/citations.json`;
        filename = `citations_${formData.product.replace(/\s+/g, '_')}.json`;
      }

      // Create a temporary link to trigger download
      const response = await fetch(url);
      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Download failed:', error);
      alert(`Download failed: ${error.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsAnalyzing(true);
    setTimer(0); // Reset timer
    setResults(null);
    setJobStatus(null);
    
    try {
      // Start the analysis job
      const response = await fetch(`${API_BASE_URL}/run-agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target: formData.product,
          mode: 'quick', // or 'detailed' based on user preference
          api_key: formData.apiKey
        })
      });
      
      const data = await response.json();
      
      if (response.ok && data.job_id) {
        setCurrentJobId(data.job_id);
        // Start polling for results
        pollForResults(data.job_id);
      } else {
        setResults({ status: 'failed', error: data.error || 'Failed to start analysis' });
        setIsAnalyzing(false);
      }
    } catch (error) {
      setResults({ status: 'failed', error: 'Connection failed' });
      setIsAnalyzing(false);
    }
  };

  const pollForResults = async (jobId) => {
    const maxPolls = 60; // Poll for up to 10 minutes (60 * 10 seconds)
    let pollCount = 0;
    
    const poll = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/results/${jobId}`);
        const jobData = await response.json();
        
        setJobStatus(jobData);
        
        if (jobData.status === 'completed' && jobData.result) {
          // Analysis completed successfully
          setResults({
            status: 'success',
            product_name: jobData.target,
            report: jobData.result.markdown || 'Analysis completed',
            ...jobData.result
          });
          setIsAnalyzing(false);
          return;
        } else if (jobData.status === 'failed') {
          // Analysis failed
          setResults({ 
            status: 'failed', 
            error: jobData.error || 'Analysis failed' 
          });
          setIsAnalyzing(false);
          return;
        }
        
        // Continue polling if still running
        pollCount++;
        if (pollCount < maxPolls) {
          setTimeout(poll, 10000); // Poll every 10 seconds
        } else {
          // Timeout
          setResults({ 
            status: 'failed', 
            error: 'Analysis timed out. Please try again.' 
          });
          setIsAnalyzing(false);
        }
      } catch (error) {
        console.error('Polling error:', error);
        pollCount++;
        if (pollCount < maxPolls) {
          setTimeout(poll, 10000); // Retry polling
        } else {
          setResults({ status: 'failed', error: 'Lost connection to server' });
          setIsAnalyzing(false);
        }
      }
    };
    
    // Start polling after a short delay
    setTimeout(poll, 2000);
  };

  const getAgentStatus = (index) => {
    if (!isAnalyzing) return 'ready';
    
    if (!jobStatus) return index === 0 ? 'running' : 'pending';
    
    const progress = jobStatus.progress || {};
    
    // Map agent index to progress stages
    if (progress.stage === 'creating_agents') {
      return index === 0 ? 'running' : 'pending';
    } else if (progress.stage === 'running_analysis') {
      if (index <= 2) return 'completed';
      if (index === 3) return 'running';
      return 'pending';
    } else if (progress.stage === 'completed') {
      return 'completed';
    } else if (progress.stage === 'failed') {
      return 'failed';
    }
    
    return index === 0 ? 'running' : 'pending';
  };

  const agents = [
    { name: 'Web Research', icon: Search },
    { name: 'Sentiment Analysis', icon: TrendingUp },
    { name: 'Feature Extraction', icon: Users },
    { name: 'Competitive Intel', icon: Zap },
    { name: 'Report Generator', icon: FileText }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
                <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Query Research Assistant
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Ask any market research question and get comprehensive AI-powered analysis
          </p>
        </div>

        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="card">
            <h2 className="text-2xl font-semibold mb-6">Ask Your Research Question</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Research Query
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g., Compare Slack vs Teams, Analyze Zoom's market position"
                  value={formData.product}
                  onChange={(e) => setFormData({...formData, product: e.target.value})}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Industry
                </label>
                <select
                  className="input-field"
                  value={formData.industry}
                  onChange={(e) => setFormData({...formData, industry: e.target.value})}
                >
                  <option>Technology</option>
                  <option>SaaS</option>
                  <option>E-commerce</option>
                  <option>Healthcare</option>
                  <option>Finance</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  aiXplain API Key
                </label>
                <input
                  type="password"
                  className="input-field"
                  placeholder="Enter your API key"
                  value={formData.apiKey}
                  onChange={(e) => setFormData({...formData, apiKey: e.target.value})}
                  autoComplete="current-password"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isAnalyzing}
                className="btn-primary w-full flex items-center justify-center"
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Researching... (This may take 5-10 minutes)
                  </>
                ) : 'Start Research'}
              </button>
            </form>
          </div>

          {/* Agent Status */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold">AI Research Agents</h2>
              {isAnalyzing && (
                <div className="flex items-center text-blue-600">
                  <Clock className="w-5 h-5 mr-2" />
                  <span className="font-medium">{formatTime(timer)}</span>
                </div>
              )}
            </div>
            <div className="space-y-4">
              {agents.map((agent, index) => {
                const Icon = agent.icon;
                return (
                  <div key={agent.name} className="flex items-center p-4 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0 mr-4">
                      <Icon className="w-6 h-6 text-primary-500" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{agent.name}</h3>
                      <p className="text-sm text-gray-500">
                        {agent.name === 'Web Research' ? 'Finding relevant information for your query' :
                         agent.name === 'Sentiment Analysis' ? 'Analyzing public opinion and feedback' :
                         agent.name === 'Feature Extraction' ? 'Organizing key features and capabilities' :
                         agent.name === 'Competitive Intel' ? 'Providing strategic market insights' :
                         'Creating comprehensive research summary'}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      {getAgentStatus(index) === 'running' ? (
                        <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
                      ) : getAgentStatus(index) === 'completed' ? (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      ) : getAgentStatus(index) === 'failed' ? (
                        <AlertCircle className="w-5 h-5 text-red-500" />
                      ) : results?.status === 'success' ? (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      ) : (
                        <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Job Status Display */}
            {isAnalyzing && jobStatus && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-800">
                      Job Status: {jobStatus.status}
                    </p>
                    {jobStatus.progress && (
                      <p className="text-xs text-blue-600">
                        Stage: {jobStatus.progress.stage || 'initializing'}
                      </p>
                    )}
                  </div>
                  {currentJobId && (
                    <p className="text-xs text-blue-500 font-mono">
                      ID: {currentJobId.substring(0, 8)}...
                    </p>
                  )}
                </div>
              </div>
            )}
            
            {/* Progress Notice */}
            {isAnalyzing && timer > 300 && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
                  <p className="text-sm text-yellow-800">
                    Complex queries may take 5-10 minutes. Please keep this page open while research is in progress.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results */}
        {results && (
          <div className="max-w-6xl mx-auto mt-8">
            <div className="card">
              {results.status === 'success' ? (
                <>
                  <div className="flex items-center mb-6">
                    <CheckCircle className="w-8 h-8 text-green-500 mr-3" />
                    <div>
                      <h2 className="text-2xl font-semibold">Analysis Complete</h2>
                      <p className="text-sm text-gray-600">Using: {results.script_used || 'market_research_advanced'}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div className="text-center p-6 bg-blue-50 rounded-lg">
                      <div className="text-3xl font-bold text-blue-600">{results.product_name}</div>
                      <div className="text-sm text-gray-600">Product Analyzed</div>
                    </div>
                    <div className="text-center p-6 bg-purple-50 rounded-lg">
                      <div className="text-3xl font-bold text-purple-600">{formData.industry}</div>
                      <div className="text-sm text-gray-600">Industry</div>
                    </div>
                  </div>

                  {results.report && (
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-4">Analysis Report</h3>
                      <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                        <pre className="whitespace-pre-wrap text-sm text-gray-700">{results.report}</pre>
                      </div>
                    </div>
                  )}

                  {results.citations && results.citations.length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold mb-4">Sources and References</h3>
                      <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                        <div className="space-y-2">
                          {results.citations.map((citation, index) => {
                            // Extract URL from citation
                            const urlMatch = citation.match(/https?:\/\/[^\s<>"')\]]+/);
                            const url = urlMatch ? urlMatch[0] : null;
                            
                            if (url) {
                              // Clean citation text (remove URL for display)
                              const cleanText = citation.replace(url, '').replace(/\s*-\s*$/, '').trim();
                              const displayText = cleanText || `Source ${index + 1}`;
                              
                              return (
                                <div key={index} className="flex items-start">
                                  <span className="text-gray-500 text-sm mr-2">[{index + 1}]</span>
                                  <a 
                                    href={url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:text-blue-800 text-sm underline"
                                  >
                                    {displayText}
                                  </a>
                                </div>
                              );
                            } else {
                              return (
                                <div key={index} className="flex items-start">
                                  <span className="text-gray-500 text-sm mr-2">[{index + 1}]</span>
                                  <span className="text-gray-700 text-sm">{citation}</span>
                                </div>
                              );
                            }
                          })}
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="pt-6 border-t border-gray-200">
                    <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                      <div className="flex space-x-4">
                        <button 
                          onClick={() => downloadReport('pdf')}
                          className="btn-primary"
                        >
                          Download PDF Report
                        </button>
                        <button 
                          onClick={() => downloadReport('markdown')}
                          className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                        >
                          Download Markdown
                        </button>
                        <button 
                          onClick={() => downloadReport('citations')}
                          className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                        >
                          Download Citations
                        </button>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                  <h2 className="text-xl font-semibold text-red-600 mb-2">Analysis Failed</h2>
                  <p className="text-gray-600 mb-2">{results.error || 'Unknown error occurred'}</p>
                  {results.script_used && (
                    <p className="text-sm text-gray-500">Script used: {results.script_used}</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <footer className="text-center py-8 border-t border-gray-200 bg-white/50">
        <div className="flex justify-center items-center space-x-2">
          <span className="text-sm text-gray-500"></span>
          <img 
            src="/powered_by_cirrusgo_200*42.png" 
            alt="CirrusGo" 
            className="h-8 opacity-70 hover:opacity-100 transition-opacity"
            style={{ maxHeight: '32px', width: 'auto' }}
          />
        </div>
      </footer>
    </div>
  );
};

export default App;