
# Frappe Data Importer

A web-based tool for importing data into Frappe/ERPNext systems with support for bulk importing and field mapping.

## Features

- Secure connection to Frappe instances using API keys
- Interactive field mapping interface
- Support for mandatory and recommended fields
- Batch processing for large datasets
- Progress tracking for import jobs
- Template generation for data preparation
- Support for child table imports

## Tech Stack

- Backend: Flask (Python)
- Frontend: React with Material-UI
- Database: SQLite
- Build Tool: Webpack

## Setup

1. Clone the project in Replit
2. Install dependencies:
   ```bash
   npm install
   pip install -r requirements.txt
   ```
3. Start the development server:
   ```bash
   python main.py
   ```

## Usage

1. Connect to your Frappe instance by providing URL and credentials
2. Select the DocType you want to import data into
3. Choose fields and download a template
4. Prepare your data using the template
5. Upload the filled template
6. Map the columns if needed
7. Start the import process

## Project Structure

```
├── static/          # Frontend assets
│   ├── css/         # Stylesheets
│   └── js/          # React components and services
├── templates/       # HTML templates
├── uploads/         # Temporary file storage
├── app.py          # Flask application setup
├── models.py       # Database models
├── routes.py       # API endpoints
└── main.py         # Application entry point
```

## API Endpoints

- `/api/connect` - Establish connection to Frappe instance
- `/api/schema/<connection_id>` - Get DocType schema
- `/api/template/<connection_id>` - Generate import template
- `/api/upload` - Upload data file
- `/api/import/<job_id>` - Start import process
- `/api/status/<job_id>` - Check import status
