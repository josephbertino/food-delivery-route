import React, { useState } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function RouteUploader({ onRouteCreated }) {
  const [file, setFile] = useState(null);
  const [homeAddress, setHomeAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a CSV file');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!homeAddress.trim()) {
      setError('Please enter your home address');
      return;
    }
    
    if (!file) {
      setError('Please select a CSV file');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('home_address', homeAddress.trim());

    try {
      const response = await fetch(`${API_BASE_URL}/optimize-route`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to optimize route');
      }

      onRouteCreated(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Create Optimized Route</h2>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        Enter your home address and upload a CSV file with delivery addresses.
      </p>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1.5rem' }}>
          <label htmlFor="home-address" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#333' }}>
            Home Address *
          </label>
          <input
            id="home-address"
            type="text"
            value={homeAddress}
            onChange={(e) => {
              setHomeAddress(e.target.value);
              setError(null);
            }}
            placeholder="123 Main Street, City, State"
            style={{
              width: '100%',
              padding: '0.75rem',
              fontSize: '1rem',
              border: '2px solid #ddd',
              borderRadius: '8px',
              fontFamily: 'inherit'
            }}
            required
          />
        </div>

        <div
          className={`upload-area ${dragging ? 'dragover' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".csv"
            className="file-input"
            onChange={(e) => handleFileSelect(e.target.files[0])}
          />
          {file ? (
            <div>
              <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>✓ {file.name}</p>
              <p style={{ color: '#666', fontSize: '0.9rem' }}>Click to change file</p>
            </div>
          ) : (
            <div>
              <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                📄 Drag & drop CSV file here
              </p>
              <p style={{ color: '#666', fontSize: '0.9rem' }}>or click to browse</p>
            </div>
          )}
        </div>

        {error && <div className="error">{error}</div>}

        <button
          type="submit"
          className="upload-button"
          disabled={!file || !homeAddress.trim() || loading}
        >
          {loading ? 'Optimizing Route...' : 'Optimize Route'}
        </button>
      </form>

      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f8f9ff', borderRadius: '8px' }}>
        <h3 style={{ fontSize: '0.9rem', marginBottom: '0.5rem', color: '#667eea' }}>
          CSV Format:
        </h3>
        <p style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.5rem' }}>
          First column must be the address. Additional columns are optional (notes, metadata, etc.).
          Header row is optional - the app will auto-detect it.
        </p>
        <pre style={{ fontSize: '0.85rem', color: '#666', overflow: 'auto', background: 'white', padding: '0.5rem', borderRadius: '4px' }}>
{`123 Main St, Customer 1
456 Oak Ave, Customer 2, Special instructions
789 Pine Rd

# Or with header:
address,notes
123 Main St, Customer 1
456 Oak Ave, Customer 2`}
        </pre>
      </div>
    </div>
  );
}

export default RouteUploader;

