import React, { useState, useEffect } from 'react';
import { getSchema, startImport } from '../services/api';

function DataMapping({ jobId, onMapping }) {
  const [columns, setColumns] = useState([]);
  const [frappeFields, setFrappeFields] = useState([]);
  const [mapping, setMapping] = useState({});
  const [error, setError] = useState('');

  useEffect(() => {
    const loadSchema = async () => {
      try {
        const schema = await getSchema(jobId);
        setFrappeFields(schema.fields);
      } catch (err) {
        setError('Failed to load Frappe schema');
      }
    };
    loadSchema();
  }, [jobId]);

  const handleMapping = (excelColumn, frappeField) => {
    setMapping({
      ...mapping,
      [excelColumn]: frappeField
    });
  };

  const handleSubmit = async () => {
    try {
      const response = await startImport(jobId, mapping);
      if (response.status === 'success') {
        onMapping();
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Failed to start import');
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <h3>Map Excel Columns to Frappe Fields</h3>
        {error && <div className="alert alert-danger">{error}</div>}
        
        <div className="mapping-container">
          {columns.map(column => (
            <div key={column} className="mapping-row">
              <div className="excel-column">
                {column}
              </div>
              <div className="mapping-arrow">→</div>
              <select
                className="form-select frappe-field"
                onChange={(e) => handleMapping(column, e.target.value)}
                value={mapping[column] || ''}
              >
                <option value="">Select Frappe Field</option>
                {frappeFields.map(field => (
                  <option key={field.fieldname} value={field.fieldname}>
                    {field.label}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>

        <div className="mt-3">
          <button 
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={Object.keys(mapping).length === 0}
          >
            Start Import
          </button>
        </div>
      </div>
    </div>
  );
}

export default DataMapping;
