#!/usr/bin/env python3
"""
Script to clear MongoDB databases (both backend and frontend)
"""

from pymongo import MongoClient
from config import Config
import gridfs

def clear_databases():
    """Clear both backend and frontend databases"""
    
    print('🗑️  CLEARING MONGODB DATABASES')
    print('=' * 40)
    
    # Connect to backend database
    backend_client = MongoClient(Config.MONGODB_URI)
    backend_db = backend_client[Config.MONGODB_DATABASE]
    
    # Connect to frontend database  
    frontend_client = MongoClient('mongodb://localhost:27017/')
    frontend_db = frontend_client['medical_maestro']
    
    # Clear backend database
    print('🔹 Clearing BACKEND database (medmaestro_gmail_agent)...')
    
    # Get counts before clearing
    medical_count = backend_db.medical_records.count_documents({})
    email_count = backend_db.email_history.count_documents({})
    
    # Clear GridFS files
    fs = gridfs.GridFS(backend_db)
    fs_count = len(list(fs.find()))
    
    print(f'  📄 Medical Records to delete: {medical_count}')
    print(f'  📧 Email History to delete: {email_count}')
    print(f'  📁 GridFS Files to delete: {fs_count}')
    
    # Delete collections
    backend_db.medical_records.delete_many({})
    backend_db.email_history.delete_many({})
    
    # Clear GridFS
    for file in fs.find():
        fs.delete(file._id)
    
    print('  ✅ Backend database cleared!')
    
    # Clear frontend database
    print()
    print('🔹 Clearing FRONTEND database (medical_maestro)...')
    
    # Get counts before clearing
    patient_files_count = frontend_db.patient_files.count_documents({})
    
    print(f'  📄 Patient Files to delete: {patient_files_count}')
    
    # Delete collections
    frontend_db.patient_files.delete_many({})
    
    print('  ✅ Frontend database cleared!')
    
    print()
    print('🎉 ALL DATABASES CLEARED SUCCESSFULLY!')
    print('=' * 40)

if __name__ == '__main__':
    # Ask for confirmation
    confirm = input('⚠️  Are you sure you want to clear ALL database entries? (yes/no): ')
    if confirm.lower() in ['yes', 'y']:
        clear_databases()
    else:
        print('❌ Database clearing cancelled.') 