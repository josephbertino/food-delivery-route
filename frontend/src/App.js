import React, { useState } from 'react';
import './App.css';
import RouteUploader from './components/RouteUploader';
import RouteViewer from './components/RouteViewer';
import RouteCodeInput from './components/RouteCodeInput';

function App() {
  const [view, setView] = useState('upload'); // 'upload' or 'view' or 'code'
  const [routeData, setRouteData] = useState(null);
  const [routeCode, setRouteCode] = useState('');

  const handleRouteCreated = (data) => {
    setRouteData(data);
    setRouteCode(data.route_code);
    setView('view');
  };

  const handleCodeSubmit = (data) => {
    setRouteData(data);
    setView('view');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚴 Food Delivery Route Optimizer</h1>
        <nav className="nav-tabs">
          <button 
            className={view === 'upload' ? 'active' : ''} 
            onClick={() => setView('upload')}
          >
            Create Route
          </button>
          <button 
            className={view === 'code' ? 'active' : ''} 
            onClick={() => setView('code')}
          >
            Enter Code
          </button>
        </nav>
      </header>

      <main className="App-main">
        {view === 'upload' && (
          <RouteUploader onRouteCreated={handleRouteCreated} />
        )}
        {view === 'code' && (
          <RouteCodeInput onCodeSubmit={handleCodeSubmit} />
        )}
        {view === 'view' && routeData && (
          <RouteViewer routeData={routeData} routeCode={routeCode} />
        )}
      </main>
    </div>
  );
}

export default App;
