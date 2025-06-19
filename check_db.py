#!/usr/bin/env python3
"""
Script to check current MongoDB database entries
"""

from pymongo import MongoClient
from config import Config

def check_databases():
    """Check current entries in both databases"""
    
    # Connect to backend database
    backend_client = MongoClient(Config.MONGODB_URI)
    backend_db = backend_client[Config.MONGODB_DATABASE]

    # Connect to frontend database  
    frontend_client = MongoClient('mongodb://localhost:27017/')
    frontend_db = frontend_client['medical_maestro']

    print('=== CURRENT DATABASE ENTRIES ===')
    print()

    # Check backend database
    print('🔹 BACKEND DATABASE (medmaestro_gmail_agent):')
    medical_records = list(backend_db.medical_records.find())
    email_history = list(backend_db.email_history.find())
    print(f'  Medical Records: {len(medical_records)}')
    print(f'  Email History: {len(email_history)}')

    if medical_records:
        print('  Medical Records Details:')
        for i, record in enumerate(medical_records, 1):
            llm_status = "Yes" if record.get('llm_analysis') else "No"
            pdf_count = len(record.get('pdf_files', []))
            print(f'    {i}. Patient: {record.get("patient_name", "Unknown")} | Request: {record.get("request_id", "Unknown")} | Test: {record.get("test_type", "Unknown")} | PDFs: {pdf_count} | LLM: {llm_status}')

    print()

    # Check frontend database
    print('🔹 FRONTEND DATABASE (medical_maestro):')
    patient_files = list(frontend_db.patient_files.find())
    print(f'  Patient Files: {len(patient_files)}')

    if patient_files:
        print('  Patient Files Details:')
        for i, record in enumerate(patient_files, 1):
            llm_status = "Yes" if record.get('llm_summary') else "No"
            print(f'    {i}. Patient: {record.get("name", "Unknown")} | Date: {record.get("date_processed", "Unknown")} | Request: {record.get("request_id", "Unknown")} | LLM: {llm_status}')

    print()
    print('=== END OF DATABASE CHECK ===')

if __name__ == '__main__':
    check_databases() 