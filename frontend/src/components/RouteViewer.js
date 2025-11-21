import React from 'react';

function RouteViewer({ routeData, routeCode }) {
  const formatDuration = (minutes) => {
    const hrs = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    if (hrs > 0) {
      return `${hrs}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const handleMapsClick = () => {
    window.open(routeData.google_maps_url, '_blank');
  };

  return (
    <div>
      <div className="card">
        <div className="route-code">
          <h3>Your Route Code</h3>
          <div className="code">{routeCode}</div>
          <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
            Share this code to access your route on mobile
          </p>
        </div>

        <div className="route-stats">
          <div className="stat">
            <div className="stat-label">Total Distance</div>
            <div className="stat-value">{routeData.total_distance} km</div>
          </div>
          <div className="stat">
            <div className="stat-label">Total Time</div>
            <div className="stat-value">{formatDuration(routeData.total_duration)}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Stops</div>
            <div className="stat-value">{routeData.route.length - 1}</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Optimized Route</h2>
        <ul className="route-list">
          {routeData.route.map((step) => (
            <li
              key={step.step}
              className={`route-item ${step.is_home ? 'home' : ''}`}
            >
              <div className="step-number">{step.step}</div>
              <div className="route-details">
                <div className="route-address">{step.address}</div>
                {step.notes && (
                  <div className="route-notes">{step.notes}</div>
                )}
              </div>
            </li>
          ))}
        </ul>

        <a
          href={routeData.google_maps_url}
          target="_blank"
          rel="noopener noreferrer"
          className="maps-button"
          onClick={handleMapsClick}
        >
          <span>🗺️</span>
          Open in Google Maps
        </a>
      </div>
    </div>
  );
}

export default RouteViewer;

