const API_BASE_URL = window.location.origin + '/api';

export async function getConnections() {
  const response = await fetch(`${API_BASE_URL}/connections`, {
    credentials: 'include'
  });
  return response.json();
}

export async function deleteConnection(connectionId) {
  const response = await fetch(`${API_BASE_URL}/connections/${connectionId}`, {
    method: 'DELETE',
    credentials: 'include'
  });
  return response.json();
}

export async function connectToFrappe(credentials) {
  const response = await fetch(`${API_BASE_URL}/connect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(credentials)
  });
  return response.json();
}

export async function getDoctypes(connectionId) {
  const response = await fetch(`${API_BASE_URL}/doctypes/${connectionId}`, {
    credentials: 'include'
  });
  return response.json();
}

export async function getSchema(connectionId, doctype) {
  const response = await fetch(`${API_BASE_URL}/schema/${connectionId}?doctype=${encodeURIComponent(doctype)}`, {
    credentials: 'include'
  });
  return response.json();
}

export async function uploadFile(formData) {
  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    credentials: 'include',
    // Don't set Content-Type header, let the browser set it with the boundary
    body: formData
  });
  return response.json();
}

export async function startImport(jobId, mapping) {
  const response = await fetch(`${API_BASE_URL}/import/${jobId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ mapping })
  });
  return response.json();
}

export async function getImportStatus(jobId) {
  const response = await fetch(`${API_BASE_URL}/status/${jobId}`, {
    credentials: 'include'
  });
  return response.json();
}