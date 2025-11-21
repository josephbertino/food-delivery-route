import React, { useState } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function RouteCodeInput({ onCodeSubmit }) {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!code || code.length !== 8) {
      setError('Please enter a valid 8-character code');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/route/${code.toUpperCase()}`);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Route not found');
      }

      onCodeSubmit(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCodeChange = (e) => {
    const value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8);
    setCode(value);
    setError(null);
  };

  return (
    <div className="card">
      <h2>Enter Route Code</h2>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        Enter the 8-character code to retrieve your optimized route
      </p>

      <form onSubmit={handleSubmit} className="code-input-form">
        <input
          type="text"
          className="code-input"
          value={code}
          onChange={handleCodeChange}
          placeholder="ABCD1234"
          maxLength="8"
          autoFocus
        />

        {error && <div className="error">{error}</div>}

        <button
          type="submit"
          className="submit-button"
          disabled={!code || code.length !== 8 || loading}
        >
          {loading ? 'Loading...' : 'Load Route'}
        </button>
      </form>
    </div>
  );
}

export default RouteCodeInput;

