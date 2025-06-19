#!/usr/bin/env python3
"""
Test data setup script for Medical Test Results functionality.
This script inserts sample data into MongoDB to test the test results screen.
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import os

# MongoDB Setup
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["medical_maestro"]
files_collection = mongo_db["patient_files"]

def create_sample_test_data():
    """Create sample test data for testing"""
    
    # Sample patient names (make sure these exist in your patients table)
    sample_patients = ["John Doe", "Jane Smith", "Bob Johnson"]
    
    # Create test data for each patient
    for patient_name in sample_patients:
        print(f"Creating test data for {patient_name}...")
        
        # Create data for 3 different dates
        for i in range(3):
            test_date = (datetime.now() - timedelta(days=i*30)).strftime("%Y-%m-%d")
            
            # Sample test record
            test_record = {
                "name": patient_name,
                "date_processed": test_date,
                "Blood Test": f"/path/to/blood_test_{patient_name.replace(' ', '_')}_{test_date}.pdf",
                "CT Scan": f"/path/to/ct_scan_{patient_name.replace(' ', '_')}_{test_date}.pdf",
                "MRI": f"/path/to/mri_{patient_name.replace(' ', '_')}_{test_date}.pdf",
                "Urine": f"/path/to/urine_{patient_name.replace(' ', '_')}_{test_date}.pdf",
                "Stool": f"/path/to/stool_{patient_name.replace(' ', '_')}_{test_date}.pdf",
                "llm_summary": f"""
Test Results Summary for {patient_name} - {test_date}

BLOOD TEST RESULTS:
- Complete Blood Count (CBC): Within normal limits
- Comprehensive Metabolic Panel: Glucose slightly elevated at 110 mg/dL
- Lipid Panel: Total cholesterol 195 mg/dL, LDL 120 mg/dL, HDL 45 mg/dL

IMAGING RESULTS:
- CT Scan: No acute abnormalities detected
- MRI: Minor degenerative changes consistent with age

LABORATORY ANALYSIS:
- Urine Analysis: Specific gravity 1.020, no protein or glucose detected
- Stool Analysis: No occult blood detected, normal flora present

CLINICAL RECOMMENDATIONS:
1. Continue current medication regimen
2. Follow up in 3 months for glucose monitoring
3. Consider dietary modifications for cholesterol management
4. Regular exercise recommended

OVERALL ASSESSMENT:
Patient shows stable condition with minor metabolic concerns that can be managed through lifestyle modifications and regular monitoring.
                """.strip()
            }
            
            # Insert the record
            result = files_collection.insert_one(test_record)
            print(f"  Inserted record for {test_date} with ID: {result.inserted_id}")

def create_sample_pdf_files():
    """Create sample PDF files for testing downloads"""
    
    # Create a simple text file to simulate PDFs
    sample_content = """
    SAMPLE MEDICAL TEST RESULT
    
    This is a sample file for testing the download functionality.
    In a real system, this would be a PDF file containing actual test results.
    
    Patient: [Patient Name]
    Test Type: [Test Type]
    Date: [Test Date]
    
    Results: Sample data for testing purposes.
    """
    
    # Create directory for sample files
    os.makedirs("sample_test_files", exist_ok=True)
    
    sample_patients = ["John_Doe", "Jane_Smith", "Bob_Johnson"]
    test_types = ["blood_test", "ct_scan", "mri", "urine", "stool"]
    
    for patient in sample_patients:
        for i in range(3):
            test_date = (datetime.now() - timedelta(days=i*30)).strftime("%Y-%m-%d")
            for test_type in test_types:
                filename = f"sample_test_files/{test_type}_{patient}_{test_date}.txt"
                with open(filename, 'w') as f:
                    content = sample_content.replace("[Patient Name]", patient.replace("_", " "))
                    content = content.replace("[Test Type]", test_type.replace("_", " ").title())
                    content = content.replace("[Test Date]", test_date)
                    f.write(content)
                
                print(f"Created sample file: {filename}")

def update_file_paths():
    """Update the file paths in MongoDB to point to our sample files"""
    
    print("Updating file paths in MongoDB...")
    
    # Get all records
    records = list(files_collection.find({}))
    
    for record in records:
        patient_name = record['name'].replace(' ', '_')
        test_date = record['date_processed']
        
        # Update file paths to point to our sample files
        update_data = {}
        for test_type in ['Blood Test', 'CT Scan', 'MRI', 'Urine', 'Stool']:
            if test_type in record:
                test_type_file = test_type.lower().replace(' ', '_')
                file_path = f"sample_test_files/{test_type_file}_{patient_name}_{test_date}.txt"
                update_data[test_type] = os.path.abspath(file_path)
        
        # Update the record
        files_collection.update_one(
            {'_id': record['_id']},
            {'$set': update_data}
        )
        
        print(f"Updated file paths for {record['name']} - {test_date}")

if __name__ == "__main__":
    print("Setting up test data for Medical Test Results...")
    print("=" * 50)
    
    # Clear existing test data
    print("Clearing existing test data...")
    files_collection.delete_many({})
    
    # Create sample data
    create_sample_test_data()
    print()
    
    # Create sample files
    print("Creating sample PDF files...")
    create_sample_pdf_files()
    print()
    
    # Update file paths
    update_file_paths()
    print()
    
    print("Test data setup complete!")
    print("=" * 50)
    print("You can now test the Medical Test Results screen with the following patients:")
    print("- John Doe")
    print("- Jane Smith") 
    print("- Bob Johnson")
    print()
    print("Each patient has 3 test result records with sample files and LLM summaries.") 