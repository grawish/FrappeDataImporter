import React, { useState } from 'react';
import ConnectionForm from './components/ConnectionForm';
import FileUpload from './components/FileUpload';
import DataMapping from './components/DataMapping';
import ImportProgress from './components/ImportProgress';
import { Box, Button, Stepper, Step, StepLabel, Alert } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import LogoutIcon from '@mui/icons-material/Logout';

function App() {
  const [step, setStep] = useState(1);
  const [connectionId, setConnectionId] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [schema, setSchema] = useState(null);
  const [error, setError] = useState(null); // Added error state

  const handleConnection = (connId) => {
    setConnectionId(connId);
    setStep(2);
  };

  const handleFileUpload = (jId) => {
    setJobId(jId);
    setStep(3);
  };

  const handleMapping = () => {
    setStep(4);
  };

  const handleBack = () => {
    setStep(step - 1);
  };

  const handleLogout = () => {
    localStorage.removeItem('connection');
    setConnectionId(null);
    setJobId(null);
    setSchema(null);
    setStep(1);
    setError(null); //Clear error on logout
  };

  const handleError = (err) => {
    setError(err.message); //Update error state
  }

  return (
    <div className="container mt-5">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{ visibility: step > 1 && step !== 2 ? 'visible' : 'hidden' }}
        >
          Back
        </Button>
        <Button
          endIcon={<LogoutIcon />}
          onClick={handleLogout}
          sx={{ visibility: step > 1 ? 'visible' : 'hidden' }}
          color="error"
        >
          Logout
        </Button>
      </Box>

      <h1 className="text-center mb-4">Frappe Data Importer</h1>

      <Stepper activeStep={step - 1} sx={{ mb: 4 }}>
        <Step>
          <StepLabel>Connect</StepLabel>
        </Step>
        <Step>
          <StepLabel>Upload</StepLabel>
        </Step>
        <Step>
          <StepLabel>Import</StepLabel>
        </Step>
      </Stepper>

      {error && ( //Added error handling
        <Alert severity="error" sx={{ mb: 2 }}>
          <div dangerouslySetInnerHTML={{ __html: error }} />
        </Alert>
      )}

      {step === 1 && (
        <ConnectionForm onConnect={handleConnection} onError={handleError}/>
      )}

      {step === 2 && (
        <FileUpload
          connectionId={connectionId}
          onUpload={handleFileUpload}
          onError={handleError}
        />
      )}

      {step === 3 && (
        <ImportProgress jobId={jobId} onError={handleError}/>
      )}
    </div>
  );
}

export default App;