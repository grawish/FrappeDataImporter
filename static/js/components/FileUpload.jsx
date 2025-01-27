import React, { useState } from 'react';
import { uploadFile } from '../services/api';

function FileUpload({ connectionId, onUpload }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState('');

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile.type.includes('excel') || droppedFile.name.match(/\.(xlsx|xls)$/)) {
      setFile(droppedFile);
    } else {
      setError('Please upload an Excel file');
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      const response = await uploadFile(file, connectionId);
      if (response.status === 'success') {
        onUpload(response.job_id);
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Failed to upload file');
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <h3>Upload Excel File</h3>
        {error && <div className="alert alert-danger">{error}</div>}
        
        <div 
          className={`upload-area ${dragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <i data-feather="upload-cloud" className="upload-icon"></i>
          <p>Drag and drop your Excel file here or</p>
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={handleFileChange}
            className="form-control"
          />
        </div>

        {file && (
          <div className="mt-3">
            <p>Selected file: {file.name}</p>
            <button 
              className="btn btn-primary"
              onClick={handleUpload}
            >
              Upload and Continue
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default FileUpload;
