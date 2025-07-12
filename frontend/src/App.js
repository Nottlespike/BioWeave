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
        {response && (
          <div className="response-container">
            <h2>Response:</h2>
            <pre>{JSON.stringify(response, null, 2)}</pre>
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
