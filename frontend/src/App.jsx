import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!prompt) return;
    setLoading(true);
    try {
      const res = await axios.get(
        'http://localhost:8000/fetch-db-schema'
      );
      setResponse(res.data);
    } catch (error) {
      setResponse({ error: error.response?.data?.detail || 'Request failed' });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-3xl mx-auto bg-white p-6 rounded-2xl shadow-md">
        <h1 className="text-2xl font-bold mb-4">🧠 SQL AI Agent</h1>

        <div className="mb-2">
          <label className="block text-sm font-medium">API Key</label>
          <input
            type="text"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full mt-1 p-2 border rounded-md"
            placeholder="Optional"
          />
        </div>

        <textarea
          className="w-full p-3 border rounded-md mb-3"
          rows="4"
          placeholder="Ask in natural language..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        ></textarea>

        <button
          onClick={handleSubmit}
          className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-xl"
          disabled={loading}
        >
          {loading ? 'Thinking...' : 'Submit'}
        </button>

        <div className="mt-6">
          <h2 className="text-lg font-semibold">Response:</h2>
          <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-md mt-2">
            {response ? JSON.stringify(response, null, 2) : 'Nothing yet'}
          </pre>
        </div>
      </div>
    </div>
  );
}

export default App;