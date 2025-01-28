import React, { useState, useEffect } from "react";
import { uploadFile, getDoctypes } from "../services/api";

function FileUpload({ connectionId, onUpload }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const [batchSize, setBatchSize] = useState(100);
  const [doctypes, setDoctypes] = useState([]);
  const [selectedDoctype, setSelectedDoctype] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchDoctypes = async () => {
      try {
        const response = await getDoctypes(connectionId);
        if (response.message) {
          setDoctypes(response.message);
        }
      } catch (err) {
        console.error("Error fetching doctypes:", err);
        setError("Failed to load doctypes");
      }
    };
    fetchDoctypes();
  }, [connectionId]);

  const acceptedFormats = {
    csv: "text/csv",
    excel: [
      "application/vnd.ms-excel",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ],
  };

  const isValidFileType = (file) => {
    const validTypes = [...acceptedFormats.excel, acceptedFormats.csv];
    return (
      validTypes.includes(file.type) || file.name.match(/\.(xlsx|xls|csv)$/)
    );
  };

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
    if (isValidFileType(droppedFile)) {
      setFile(droppedFile);
      setError("");
    } else {
      setError("Please upload a valid file (Excel or CSV)");
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (isValidFileType(selectedFile)) {
        setFile(selectedFile);
        setError("");
      } else {
        setError("Please upload a valid file (Excel or CSV)");
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }

    if (!selectedDoctype) {
      setError("Please select a doctype");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("connection_id", connectionId);
      formData.append("batch_size", batchSize.toString());
      formData.append("frappe_url", "https://demo.frappe.cloud"); // TODO: Get this from connection
      formData.append("doctype", selectedDoctype);

      const response = await uploadFile(formData);
      if (response.status === "success") {
        onUpload(response.job_id);
      } else {
        setError(response.message || "Failed to upload file");
      }
    } catch (err) {
      setError("Failed to upload file");
      console.error("Upload error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <h3>Upload Data File</h3>
        {error && <div className="alert alert-danger">{error}</div>}

        <div className="mb-3">
          <label className="form-label">Select Doctype</label>
          <div className="doctype-select-container">
            <input
              type="text"
              className="form-control mb-2"
              placeholder="Search doctypes..."
              onChange={(e) => {
                const searchTerm = e.target.value.toLowerCase();
                const filtered = doctypes.filter(doctype => 
                  doctype.toLowerCase().includes(searchTerm)
                );
                setDoctypes(filtered);
                if (!searchTerm) {
                  fetchDoctypes();
                }
              }}
            />
            <select
              className="form-select"
              value={selectedDoctype}
              onChange={(e) => setSelectedDoctype(e.target.value)}
            >
              <option value="">Choose a doctype...</option>
              {doctypes.map((doctype) => (
                <option key={doctype} value={doctype}>
                  {doctype}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-3">
          <label className="form-label">Batch Size</label>
          <input
            type="number"
            className="form-control"
            value={batchSize}
            onChange={(e) =>
              setBatchSize(Math.max(1, parseInt(e.target.value) || 1))
            }
            min="1"
          />
          <small className="form-text text-muted">
            Number of records to process in each batch
          </small>
        </div>

        <div
          className={`upload-area ${dragging ? "dragging" : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <i data-feather="upload-cloud" className="upload-icon"></i>
          <p>Drag and drop your file here or</p>
          <input
            type="file"
            accept=".xlsx,.xls,.csv"
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
              disabled={loading || !selectedDoctype}
            >
              {loading ? "Uploading..." : "Upload and Continue"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default FileUpload;
