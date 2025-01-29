import React, { useEffect, useState } from 'react';
import { connectToFrappe, getConnections, deleteConnection } from '../services/api';
import { Card, CardContent, Typography, TextField, Button, List, ListItem, ListItemText, Divider, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

function ConnectionForm({ onConnect }) {
  const [formData, setFormData] = useState({
    url: '',
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [savedConnections, setSavedConnections] = useState([]);

  useEffect(() => {
    const connection = localStorage.getItem('connection');
    if (connection) {
      onConnect(JSON.parse(connection).connection_id);
    }

    // Fetch saved connections
    getConnections()
      .then(response => {
        if (response.status === 'success') {
          setSavedConnections(response.connections);
        }
      })
      .catch(err => console.error('Failed to fetch connections:', err));
  }, [onConnect]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await connectToFrappe(formData);
      if (response.status === 'success') {
        onConnect(response.connection_id);
        localStorage.setItem('connection', JSON.stringify(response));
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Failed to connect to Frappe instance');
    }
  };

  const handleSelectConnection = (connection) => {
    setFormData({
      ...formData,
      url: connection.url,
      username: connection.username
    });
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Connect to Frappe Instance</Typography>
        {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}

        {savedConnections.length > 0 && (
          <>
            <Typography variant="h6" gutterBottom>Saved Connections</Typography>
            <List sx={{ mb: 3 }}>
              {savedConnections.map((conn) => (
                <React.Fragment key={conn.id}>
                  <ListItem 
                    button 
                    onClick={() => handleSelectConnection(conn)}
                    secondaryAction={
                      <IconButton
                        color="error"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (window.confirm('Are you sure you want to delete this connection?')) {
                            deleteConnection(conn.id)
                              .then(() => {
                                setSavedConnections(savedConnections.filter(c => c.id !== conn.id));
                              })
                              .catch(err => setError('Failed to delete connection'));
                          }
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <ListItemText 
                      primary={conn.url}
                      secondary={`Username: ${conn.username} | Created: ${new Date(conn.created_at).toLocaleDateString()}`}
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Frappe URL"
            type="url"
            value={formData.url}
            onChange={(e) => setFormData({...formData, url: e.target.value})}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Username"
            type="text"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
            sx={{ mb: 2 }}
          />
          <Button type="submit" variant="contained" color="primary">
            Connect
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

export default ConnectionForm;