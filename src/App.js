import React, { useState } from 'react';
import { Search, TrendingUp, Users, FileText, Zap, CheckCircle, AlertCircle } from 'lucide-react';

const App = () => {
  const [formData, setFormData] = useState({
    product: '',
    industry: 'Technology',
    apiKey: ''
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);

  const downloadReport = async (format) => {
    try {
      const response = await fetch(`http://localhost:8000/api/download/${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product: formData.product, results })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `market_research_${formData.product.replace(/\s+/g, '_')}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsAnalyzing(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          script: 'market_research_advanced'
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setResults(data);
      } else {
        setResults({ status: 'failed', error: data.error });
      }
    } catch (error) {
      setResults({ status: 'failed', error: 'Connection failed' });
    }
    
    setIsAnalyzing(false);
  };

  const getAgentStatus = (index) => {
    if (!isAnalyzing) return 'ready';
    if (index === 0) return 'running';
    return 'pending';
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
            AI Market Research System
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Analyze any competitor in minutes using AI agents
          </p>
        </div>

        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="card">
            <h2 className="text-2xl font-semibold mb-6">Start Analysis</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Competitor Product
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g., Slack, Zoom, Salesforce"
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
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isAnalyzing}
                className="btn-primary w-full"
              >
                {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
              </button>
            </form>
          </div>

          {/* Agent Status */}
          <div className="card">
            <h2 className="text-2xl font-semibold mb-6">AI Agents</h2>
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
                        {agent.name === 'Web Research' ? 'Gathering product information' :
                         agent.name === 'Sentiment Analysis' ? 'Analyzing customer feedback' :
                         agent.name === 'Feature Extraction' ? 'Categorizing capabilities' :
                         agent.name === 'Competitive Intel' ? 'Assessing market position' :
                         'Creating executive summary'}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      {getAgentStatus(index) === 'running' ? (
                        <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
                      ) : results?.status === 'completed' ? (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      ) : (
                        <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
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