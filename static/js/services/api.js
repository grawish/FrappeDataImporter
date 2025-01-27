const API_BASE_URL = 'http://localhost:5000/api';

export async function connectToFrappe(credentials) {
  const response = await fetch(`${API_BASE_URL}/connect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials)
  });
  return response.json();
}

export async function getSchema(connectionId) {
  const response = await fetch(`${API_BASE_URL}/schema/${connectionId}`);
  return response.json();
}

export async function uploadFile(file, connectionId) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('connection_id', connectionId);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
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
    body: JSON.stringify({ mapping })
  });
  return response.json();
}

export async function getImportStatus(jobId) {
  const response = await fetch(`${API_BASE_URL}/status/${jobId}`);
  return response.json();
}
