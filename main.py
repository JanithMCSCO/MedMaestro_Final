#!/usr/bin/env python3
"""
Main entry point for the Medical Test Results Backend
Handles command line arguments and integrates with the Gmail processing system
"""

import sys
import argparse
import logging
from gmail_to_mongo import GmailToMongoProcessor
from models import DatabaseManager, MedicalRecord
from pymongo import MongoClient
from config import Config
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_patient_emails(patient_name: str = None, max_emails: int = 20):
    """
    Process emails for a specific patient or all recent emails
    """
    logger.info("🚀 Starting Medical Test Results Backend Processing")
    logger.info("=" * 60)
    
    if patient_name:
        logger.info(f"🏥 Processing emails for patient: {patient_name}")
    else:
        logger.info(f"📧 Processing last {max_emails} emails for all patients")
    
    try:
        # Initialize the Gmail processor
        processor = GmailToMongoProcessor()
        
        # Process recent emails
        stats = processor.process_recent_emails(max_emails)
        
        # If specific patient requested, also update the frontend database
        if patient_name:
            update_frontend_database(patient_name)
        
        # Print summary
        processor.print_processing_summary(stats)
        
        logger.info("✅ Backend processing completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Backend processing failed: {str(e)}")
        return False

def update_frontend_database(patient_name: str):
    """
    Update the frontend database with processed results
    This creates records in the format expected by the frontend
    """
    logger.info(f"🔄 Updating frontend database for patient: {patient_name}")
    
    try:
        # Connect to backend MongoDB
        backend_client = MongoClient(Config.MONGODB_URI)
        backend_db = backend_client[Config.MONGODB_DATABASE]
        medical_records = backend_db.medical_records
        
        # Connect to frontend MongoDB
        frontend_client = MongoClient("mongodb://localhost:27017/")
        frontend_db = frontend_client["medical_maestro"]
        patient_files = frontend_db["patient_files"]
        
        # Get all records for this patient from backend
        backend_records = list(medical_records.find({"patient_name": patient_name}))
        
        if not backend_records:
            logger.info(f"ℹ️ No backend records found for patient: {patient_name}")
            return
        
        logger.info(f"📋 Found {len(backend_records)} backend records for {patient_name}")
        
        # Process each backend record
        for record in backend_records:
            try:
                # Create frontend record
                frontend_record = {
                    "name": patient_name,
                    "date_processed": record.get('created_at', datetime.now()).strftime('%Y-%m-%d'),
                    "request_id": record.get('request_id', ''),
                    "test_type": record.get('test_type', 'Unknown'),
                    "llm_summary": record.get('llm_analysis', ''),  # Only use LLM analysis, not test_summary
                    "extracted_text": record.get('extracted_text', ''),
                    "created_at": datetime.now(),
                    "source": "gmail_processor"
                }
                
                # Add PDF file paths (simulated - in real implementation, these would be actual file paths)
                test_type = record.get('test_type', 'Unknown')
                if 'blood' in test_type.lower():
                    frontend_record["Blood Test"] = f"processed_files/{patient_name.replace(' ', '_')}_blood_{record.get('request_id', 'unknown')}.pdf"
                elif 'ct' in test_type.lower():
                    frontend_record["CT Scan"] = f"processed_files/{patient_name.replace(' ', '_')}_ct_{record.get('request_id', 'unknown')}.pdf"
                else:
                    # Generic file path
                    frontend_record[test_type] = f"processed_files/{patient_name.replace(' ', '_')}_{test_type.lower().replace(' ', '_')}_{record.get('request_id', 'unknown')}.pdf"
                
                # Check if record already exists in frontend
                existing = patient_files.find_one({
                    "name": patient_name,
                    "request_id": record.get('request_id', '')
                })
                
                if existing:
                    # Update existing record
                    patient_files.update_one(
                        {"_id": existing["_id"]},
                        {"$set": frontend_record}
                    )
                    logger.info(f"   ✅ Updated frontend record for request {record.get('request_id', 'unknown')}")
                else:
                    # Create new record
                    patient_files.insert_one(frontend_record)
                    logger.info(f"   ✅ Created frontend record for request {record.get('request_id', 'unknown')}")
                    
            except Exception as e:
                logger.error(f"   ❌ Error processing record {record.get('request_id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"✅ Frontend database updated for patient: {patient_name}")
        
    except Exception as e:
        logger.error(f"❌ Error updating frontend database: {str(e)}")

def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Medical Test Results Backend Processor')
    parser.add_argument('--patient', type=str, help='Process emails for specific patient')
    parser.add_argument('--max-emails', type=int, default=20, help='Maximum number of emails to process')
    parser.add_argument('--update-frontend', action='store_true', help='Update frontend database after processing')
    
    args = parser.parse_args()
    
    try:
        # Process emails
        success = process_patient_emails(args.patient, args.max_emails)
        
        if success:
            logger.info("🎉 All processing completed successfully!")
            sys.exit(0)
        else:
            logger.error("💥 Processing failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 