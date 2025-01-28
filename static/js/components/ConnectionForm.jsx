import React, { useEffect, useState } from 'react';
import { connectToFrappe } from '../services/api';

function ConnectionForm({ onConnect }) {
  const [formData, setFormData] = useState({
    url: '',
    username: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await connectToFrappe(formData);
      if (response.status === 'success') {
        onConnect(response.connection_id);
        // add connection details in localstorage
        localStorage.setItem('connection', JSON.stringify(response));
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Failed to connect to Frappe instance');
    }
  };

  useEffect(() => {
    const connection = localStorage.getItem('connection');
    if (connection) {
      onConnect(JSON.parse(connection).connection_id);
    }
  }, [onConnect]);

  return (
    <div className="card">
      <div className="card-body">
        <h3>Connect to Frappe Instance</h3>
        {error && <div className="alert alert-danger">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Frappe URL</label>
            <input
              type="url"
              className="form-control"
              value={formData.url}
              autoComplete={"on"}
              onChange={(e) => setFormData({...formData, url: e.target.value})}
              required
            />
          </div>
          <div className="mb-3">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-control"
              value={formData.username}
              autoComplete={"username webauthn"}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              required
            />
          </div>
          <div className="mb-3">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-control"
              autoComplete={"current-password webauthn"}
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary">Connect</button>
        </form>
      </div>
    </div>
  );
}

export default ConnectionForm;
