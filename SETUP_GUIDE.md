# Medical Test Results System - Setup Guide

## Overview

This integrated system combines a Flask frontend with a sophisticated Gmail processing backend for medical test results management.

## Prerequisites

1. **Python 3.8+**
2. **MongoDB** (running on localhost:27017)
3. **Gmail API credentials** (for email processing)
4. **LLM Server** (optional, for AI summaries)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials file as `client_secret.json.json`
6. Place it in the project root directory

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Gmail Configuration
GMAIL_CLIENT_SECRET_FILE=client_secret.json.json
GMAIL_TOKEN_FILE=token.json

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=medmaestro_gmail_agent

# LLM Configuration (choose one)
OPENAI_API_KEY=your_openai_api_key
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key
# OR
SELF_HOSTED_LLM_URL=http://192.168.1.100
SELF_HOSTED_LLM_PORT=8000
USE_SELF_HOSTED_LLM=True

# File Storage
PDF_STORAGE_PATH=pdfs/
MAX_PDF_SIZE_MB=50
```

### 4. Gmail Authentication

Run the authentication process:

```bash
python -c "from gmail_service import GmailService; GmailService()"
```

This will open a browser window for Gmail authentication.

### 5. Database Setup

The system will automatically create the required MongoDB collections:
- `medical_records` (backend data)
- `patient_files` (frontend data)
- `email_history` (processing history)

## Running the System

### 1. Start the Frontend

```bash
python app.py
```

The frontend will be available at `http://localhost:5000`

### 2. Test Backend Processing

```bash
# Process recent emails for all patients
python main.py --max-emails 10

# Process emails for specific patient
python main.py --patient "John Doe"
```

### 3. Setup Test Data (Optional)

```bash
python test_data_setup.py
```

This creates sample test data for testing the frontend.

## System Architecture

### Frontend Components
- **Flask Web Server** (`app.py`)
- **HTML Interfaces** (`static/`)
- **Test Results Screen** (Enhanced with backend integration)

### Backend Components
- **Gmail Processor** (`gmail_to_mongo.py`)
- **PDF Extractor** (`pdf_extractor.py`)
- **Gmail Service** (`gmail_service.py`)
- **Database Models** (`models.py`)
- **Configuration** (`config.py`)
- **Main Entry Point** (`main.py`)

### Database Structure

#### Backend Database: `medmaestro_gmail_agent`
- **medical_records**: Raw Gmail processing data
- **email_history**: Processing history and deduplication

#### Frontend Database: `medical_maestro`
- **users**: User authentication
- **patients**: Patient information
- **appointments**: Appointment scheduling
- **patient_files**: Test results for frontend display

## Usage Workflow

1. **Email Processing**:
   - Gmail emails are monitored for medical test results
   - PDFs are extracted and processed
   - Clinical interpretations are extracted
   - Data is stored in backend database

2. **Frontend Integration**:
   - Backend processing updates frontend database
   - Test results are displayed by date
   - PDF download links are provided
   - LLM summaries are shown

3. **User Interaction**:
   - Select patient from dropdown
   - Click "Process Test Results" to trigger backend
   - View results organized by date
   - Download PDF files
   - Read AI-generated summaries

## Troubleshooting

### Common Issues

1. **Gmail Authentication Failed**
   - Ensure `client_secret.json.json` is in project root
   - Check Gmail API is enabled in Google Cloud Console
   - Run authentication process again

2. **MongoDB Connection Error**
   - Ensure MongoDB is running: `mongod`
   - Check connection string in `.env`

3. **No Test Results Found**
   - Run test data setup: `python test_data_setup.py`
   - Check MongoDB collections have data

4. **Backend Processing Fails**
   - Check Gmail authentication
   - Verify email formats match expected patterns
   - Check MongoDB connectivity

5. **PDF Download Fails**
   - Ensure file paths in database are correct
   - Check file permissions
   - Verify files exist on disk

### Email Format Requirements

The system expects medical emails with subjects in these formats:
- `"Request ID: REQ123 | Test: Blood Work | Patient: John Doe"`
- `"REQ456 - MRI Scan - Jane Smith"`
- `"Request REQ789 Blood Test for Patient Mary Johnson"`

### File Structure Requirements

```
project_root/
├── client_secret.json.json    # Gmail API credentials
├── token.json                 # Gmail authentication token
├── .env                       # Environment variables
├── pdfs/                      # PDF storage directory
└── processed_files/           # Processed test files
```

## Security Considerations

1. **API Keys**: Keep all API keys in `.env` file, never commit to version control
2. **Gmail Access**: Use read-only Gmail scopes when possible
3. **File Access**: PDF files are served through Flask backend, not direct file system
4. **Database**: Use MongoDB authentication in production
5. **HTTPS**: Use HTTPS in production environments

## Performance Tips

1. **Batch Processing**: Process emails in batches to avoid API limits
2. **Indexing**: MongoDB collections are automatically indexed for performance
3. **Caching**: Consider caching frequently accessed patient data
4. **File Storage**: Use cloud storage for PDF files in production

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review system logs for error messages
3. Verify all prerequisites are installed correctly
4. Test with sample data first 