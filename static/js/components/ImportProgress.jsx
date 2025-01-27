import React, { useState, useEffect } from 'react';
import { getImportStatus } from '../services/api';

function ImportProgress({ jobId }) {
  const [status, setStatus] = useState({
    status: 'processing',
    processed_rows: 0,
    total_rows: 0,
    current_batch: 0,
    total_batches: 0,
    error_message: null
  });

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await getImportStatus(jobId);
        setStatus(response);

        if (response.status !== 'completed' && response.status !== 'failed') {
          setTimeout(checkStatus, 2000);
        }
      } catch (err) {
        setStatus(prev => ({
          ...prev,
          status: 'failed',
          error_message: 'Failed to fetch import status'
        }));
      }
    };

    checkStatus();
  }, [jobId]);

  const getProgressPercentage = () => {
    if (status.total_rows === 0) return 0;
    return Math.round((status.processed_rows / status.total_rows) * 100);
  };

  return (
    <div className="card">
      <div className="card-body">
        <h3>Import Progress</h3>

        <div className="progress mb-3">
          <div 
            className="progress-bar" 
            role="progressbar"
            style={{ width: `${getProgressPercentage()}%` }}
            aria-valuenow={getProgressPercentage()}
            aria-valuemin="0"
            aria-valuemax="100"
          >
            {getProgressPercentage()}%
          </div>
        </div>

        <div className="status-details">
          <p>Status: {status.status}</p>
          <p>Processed: {status.processed_rows} / {status.total_rows} rows</p>
          <p>Current Batch: {status.current_batch} / {status.total_batches}</p>

          {status.error_message && (
            <div className="alert alert-danger">
              {status.error_message}
            </div>
          )}

          {status.status === 'completed' && (
            <div className="alert alert-success">
              Import completed successfully!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ImportProgress;