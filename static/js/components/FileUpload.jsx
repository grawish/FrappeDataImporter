import React, { useState, useEffect } from "react";
import { uploadFile, getDoctypes } from "../services/api";
import { 
  Card, CardContent, Typography, TextField, 
  Button, LinearProgress, Alert, Autocomplete,
  Box, Input, Checkbox, FormControlLabel, Modal,
  List, ListItem, ListItemIcon, ListItemText,
  Paper, Tabs, Tab
} from '@mui/material';
import { getSchema } from '../services/api';
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
  const [schema, setSchema] = useState(null);
  const [selectedFields, setSelectedFields] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [activeTab, setActiveTab] = useState('recommended');
  const [config, setConfig] = useState({}); // Added state for config

  useEffect(() => {
    // Fetch config.json
    fetch('/static/js/config.json')
      .then(response => response.json())
      .then(data => setConfig(data))
      .catch(error => console.error('Error loading config.json:', error));
  }, []);

  const handleSelectAll = (checked) => {
    setSelectAll(checked);
    if (checked) {
      // Get main fields
      const mainFields = schema.docs[0].fields
        .filter(field => !field.hidden && !field.read_only && 
          !['Section Break', 'Column Break', 'Tab Break', 'Table', 'Read Only'].includes(field.fieldtype))
        .map(field => field.fieldname);

      // Get child table fields
      const childFields = schema.docs[0].fields
        .filter(field => field.fieldtype === 'Table')
        .flatMap(tableField => {
          const childDoc = schema.docs.find(d => d.name === tableField.options);
          return childDoc ? childDoc.fields
            .filter(field => !field.hidden && !field.read_only &&
              !['Section Break', 'Column Break', 'Tab Break', 'Table', 'Read Only'].includes(field.fieldtype))
            .map(field => `${tableField.fieldname}.${field.fieldname}`) : [];
        });

      setSelectedFields([...mainFields, ...childFields]);
      setSelectMandatory(false);
      setSelectRecommended(false);
    } else {
      setSelectedFields([]);
    }
  };

  const handleSelectMandatory = (checked) => {
    setSelectMandatory(checked);
    const mandatoryFields = schema.docs[0].fields
      .filter(field => !field.hidden && !field.read_only && field.reqd &&
        !['Section Break', 'Column Break', 'Tab Break', 'Table', 'Read Only'].includes(field.fieldtype))
      .map(field => field.fieldname);

    if (checked) {
      setSelectedFields(mandatoryFields);
      setSelectAll(false);
      setSelectRecommended(false);
    } else {
      setSelectedFields(selectedFields.filter(field => !mandatoryFields.includes(field)));
    }
  };

  const handleSelectRecommended = (checked) => {
    setSelectRecommended(checked);
    if (checked && selectedDoctype && config.recommended_fields) {
      const recommendedFields = config.recommended_fields[selectedDoctype] || [];
      setSelectedFields(recommendedFields);
      setSelectAll(false);
      setSelectMandatory(false);
    } else {
      setSelectedFields([]);
    }
  };

  useEffect(() => {
    if (selectedDoctype) {
      getSchema(connectionId, selectedDoctype)
        .then(response => {
          setSchema(response);
          setSelectedFields([]);
        })
        .catch(err => setError("Failed to load schema"));
    }
  }, [selectedDoctype]);

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
      formData.append("frappe_url", "");
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
          {schema && (
            <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
              <Button 
                variant="contained"
                sx={{ mt: 2 }}
                onClick={() => setOpenModal(true)}>
                Select Fields ({selectedFields.length} selected)
              </Button>

              <Modal
                open={openModal}
                onClose={() => setOpenModal(false)}
                aria-labelledby="field-selection-modal"
              >
                <Box sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  width: 500,
                  bgcolor: 'background.paper',
                  boxShadow: 24,
                  p: 4,
                  maxHeight: '80vh',
                  overflow: 'auto',
                  borderRadius: 2
                }}>
                  <Typography variant="h6" gutterBottom>
                    Select Fields
                  </Typography>
                  <Box sx={{ width: '100%', mb: 2 }}>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
                        <Tab label="Recommended Fields" value="recommended" />
                        <Tab label="Mandatory Fields" value="mandatory" />
                        <Tab label="All Fields" value="all" />
                      </Tabs>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={
                              schema?.docs[0]?.fields.filter(field => {
                                const baseFilter = !field.hidden && !field.read_only &&
                                  !['Section Break', 'Column Break', 'Tab Break', 'Read Only'].includes(field.fieldtype);
                                
                                switch(activeTab) {
                                  case 'mandatory':
                                    return baseFilter && field.reqd;
                                  case 'recommended':
                                    return baseFilter && config.recommended_fields?.[selectedDoctype]?.includes(field.fieldname);
                                  default: // 'all'
                                    return baseFilter;
                                }
                              }).every(field => selectedFields.includes(field.fieldname))
                            }
                            onChange={(e) => {
                              const filteredFields = schema?.docs[0]?.fields.filter(field => {
                                const baseFilter = !field.hidden && !field.read_only &&
                                  !['Section Break', 'Column Break', 'Tab Break', 'Read Only'].includes(field.fieldtype);
                                
                                switch(activeTab) {
                                  case 'mandatory':
                                    return baseFilter && field.reqd;
                                  case 'recommended':
                                    return baseFilter && config.recommended_fields?.[selectedDoctype]?.includes(field.fieldname);
                                  default: // 'all'
                                    return baseFilter;
                                }
                              }).map(field => field.fieldname);

                              if (e.target.checked) {
                                setSelectedFields([...new Set([...selectedFields, ...filteredFields])]);
                              } else {
                                setSelectedFields(selectedFields.filter(field => !filteredFields.includes(field)));
                              }
                            }}
                          />
                        }
                        label="Select All"
                      />
                    </Box>
                    <List>
                    {schema?.docs[0]?.fields
                      .filter(field => {
                        const baseFilter = !field.hidden && !field.read_only &&
                          !['Section Break', 'Column Break', 'Tab Break', 'Read Only'].includes(field.fieldtype);
                        
                        switch(activeTab) {
                          case 'mandatory':
                            return baseFilter && field.reqd;
                          case 'recommended':
                            return baseFilter && config.recommended_fields?.[selectedDoctype]?.includes(field.fieldname);
                          default: // 'all'
                            return baseFilter;
                        }
                      })
                      .map(field => (
                        <ListItem key={field.fieldname}>
                          <FormControlLabel
                            sx={{
                              bgcolor: 'background.paper',
                              p: 1,
                              borderRadius: 1,
                              '&:hover': { bgcolor: 'action.hover' }
                            }}
                            control={
                              <Checkbox
                                checked={selectedFields.includes(field.fieldname)}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setSelectedFields([...selectedFields, field.fieldname]);
                                  } else {
                                    setSelectedFields(selectedFields.filter(f => f !== field.fieldname));
                                  }
                                }}
                              />
                            }
                            label={
                              <Typography 
                                component="span" 
                                sx={{ 
                                  color: field.reqd ? 'error.main' : 'text.primary',
                                  fontWeight: field.reqd ? 500 : 400
                                }}
                              >
                                {field.label} {field.reqd ? '*' : ''}
                              </Typography>
                            }
                          />
                        </ListItem>
                    ))}
                    </List>
                  </Box>
                </Box>
              </Modal>

              <Button
                variant="outlined"
                onClick={async () => {
                  try {
                    const response = await fetch(`/api/template/${connectionId}`, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        doctype: selectedDoctype,
                        fields: selectedFields
                      })
                    });

                    if (!response.ok) throw new Error('Failed to generate template');

                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${selectedDoctype}_template.xlsx`;
                    a.click();
                  } catch (err) {
                    setError('Failed to download template');
                  }
                }}
                disabled={selectedFields.length === 0}
                sx={{ mt: 2 }}
              >
                Download Template
              </Button>
            </Box>
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