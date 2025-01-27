import React, { useState } from 'react';
import ConnectionForm from './components/ConnectionForm';
import FileUpload from './components/FileUpload';
import DataMapping from './components/DataMapping';
import ImportProgress from './components/ImportProgress';

function App() {
  const [step, setStep] = useState(1);
  const [connectionId, setConnectionId] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [schema, setSchema] = useState(null);

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

  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">Frappe Data Importer</h1>
      
      {step === 1 && (
        <ConnectionForm onConnect={handleConnection} />
      )}
      
      {step === 2 && (
        <FileUpload 
          connectionId={connectionId}
          onUpload={handleFileUpload}
        />
      )}
      
      {step === 3 && (
        <DataMapping
          jobId={jobId}
          schema={schema}
          onMapping={handleMapping}
        />
      )}
      
      {step === 4 && (
        <ImportProgress jobId={jobId} />
      )}
    </div>
  );
}

export default App;
