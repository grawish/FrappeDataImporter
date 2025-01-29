import React, { useEffect, useState } from 'react';
import { connectToFrappe, getConnections, deleteConnection } from '../services/api';
import { Card, CardContent, CardActions, Typography, TextField, Button, Grid, Box, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

function ConnectionForm({ onConnect }) {
  const [formData, setFormData] = useState({
    url: '',
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [savedConnections, setSavedConnections] = useState([]);
  const [showLoginForm, setShowLoginForm] = useState(false);

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
      username: connection.username,
      password: ''
    });
    setShowLoginForm(true);
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Connect to Frappe Instance</Typography>
        {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}

        {savedConnections.length > 0 && !showLoginForm && (
          <>
            <Typography variant="h6" gutterBottom>Saved Connections</Typography>
            <Box sx={{ flexGrow: 1, mb: 3 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                      backgroundColor: 'action.hover',
                      '&:hover': { boxShadow: 6 }
                    }}
                    onClick={() => {
                      setFormData({
                        url: '',
                        username: '',
                        password: ''
                      });
                      setShowLoginForm(true);
                    }}
                  >
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h6" component="div">
                        + New Connection
                      </Typography>
                      <Typography color="textSecondary">
                        Add a new Frappe connection
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                {savedConnections.map((conn) => (
                  <Grid item xs={12} sm={6} md={4} key={conn.id}>
                    <Card 
                      sx={{ 
                        cursor: 'pointer',
                        '&:hover': { boxShadow: 6 }
                      }}
                      onClick={() => handleSelectConnection(conn)}
                    >
                      <CardContent>
                        <Typography variant="h6" noWrap>{conn.url}</Typography>
                        <Typography color="textSecondary" gutterBottom>
                          Username: {conn.username}
                        </Typography>
                        <Typography variant="caption" display="block">
                          Created: {new Date(conn.created_at).toLocaleDateString()}
                        </Typography>
                      </CardContent>
                      <CardActions sx={{ justifyContent: 'flex-end' }}>
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
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </>
        )}

        {showLoginForm && (
          <>
            <Button 
              startIcon={<ArrowBackIcon />} 
              onClick={() => setShowLoginForm(false)} 
              sx={{ mb: 2 }}
            >
              Back to Connections
            </Button>
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
          </>
        )}
      </CardContent>
    </Card>
  );
}

export default ConnectionForm;