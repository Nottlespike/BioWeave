import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [target, setTarget] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResponse(null);

    try {
      const res = await axios.post('http://localhost:8001/initiate_discovery', { target });
      setResponse(res.data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Agentic Drug Discovery Framework</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="Enter biological target"
            required
          />
          <button type="submit">Submit</button>
        </form>
        <div className="workflow-container">
          <div className="agent-node">User</div>
          <div className="arrow">→</div>
          <div className="agent-node">Orchestrator</div>
          <div className="arrow">→</div>
          <div className="agent-node">Researcher</div>
          <div className="arrow">→</div>
          <div className="agent-node">Drug Proposal</div>
        </div>
        {response && (
          <div className="response-container">
            <h2>Response:</h2>
            <h3>Research Result:</h3>
            <pre>{JSON.stringify(response.research_result, null, 2)}</pre>
            <h3>Drug Proposal:</h3>
            <pre>{JSON.stringify(response.drug_proposal, null, 2)}</pre>
          </div>
        )}
        {error && (
          <div className="error-container">
            <h2>Error:</h2>
            <pre>{error}</pre>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
