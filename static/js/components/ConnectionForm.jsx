import React, { useState } from 'react';
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
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Failed to connect to Frappe instance');
    }
  };

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
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              required
            />
          </div>
          <div className="mb-3">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-control"
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
