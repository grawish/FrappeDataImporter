import React, { useState, useEffect } from "react";
import { uploadFile, getDoctypes } from "../services/api";
import { 
  Card, CardContent, Typography, TextField, 
  Button, LinearProgress, Alert, Autocomplete,
  Box, Input
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

function FileUpload({ connectionId, onUpload }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const [batchSize, setBatchSize] = useState(100);
  const [doctypes, setDoctypes] = useState([]);
  const [selectedDoctype, setSelectedDoctype] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchInput, setSearchInput] = useState("");

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
      formData.append("frappe_url", "https://demo.frappe.cloud");
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
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Upload Data File</Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>Select Doctype</Typography>
          <Autocomplete
            value={selectedDoctype}
            onChange={(event, newValue) => setSelectedDoctype(newValue)}
            inputValue={searchInput}
            onInputChange={(event, newInputValue) => setSearchInput(newInputValue)}
            options={doctypes}
            renderInput={(params) => (
              <TextField {...params} label="Search doctypes" variant="outlined" />
            )}
            sx={{ mb: 2 }}
          />
          {selectedDoctype && (
            <Button
              variant="outlined"
              onClick={() => window.open(`/api/template/${connectionId}?doctype=${encodeURIComponent(selectedDoctype)}`, '_blank')}
              sx={{ mb: 2 }}
            >
              Download Template
            </Button>
          )}
        </Box>

        

        <Box
          sx={{
            border: '2px dashed',
            borderColor: dragging ? 'primary.main' : 'grey.300',
            borderRadius: 1,
            p: 3,
            textAlign: 'center',
            bgcolor: dragging ? 'action.hover' : 'background.paper',
            mb: 2
          }}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile) setFile(droppedFile);
          }}
        >
          <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
          <Typography>Drag and drop your file here or</Typography>
          <Input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            sx={{ mt: 2 }}
          />
        </Box>

        {file && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>Selected file: {file.name}</Typography>
            <Button
              variant="contained"
              onClick={handleUpload}
              disabled={loading || !selectedDoctype}
              startIcon={loading && <LinearProgress sx={{ width: 20 }} />}
            >
              {loading ? "Uploading..." : "Upload and Continue"}
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default FileUpload;