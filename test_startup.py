#!/usr/bin/env python3
"""
Simple test script to verify that the backend can start without errors
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("Testing imports...")
    
    # Test database connection
    from backend.app.database import Base, engine
    print("✓ Database imports successful")
    
    # Test models
    from backend.app.models import (
        User, Manufacturer, Material, Filament, 
        Spool, Printer, PrintJob, ActivityLog
    )
    print("✓ Model imports successful")
    
    # Test auth
    from backend.app.auth.auth import authenticate_user, create_access_token
    print("✓ Auth imports successful")
    
    # Test API routes
    from backend.app.api import (
        auth, users, manufacturers, materials, 
        filaments, spools, printers
    )
    print("✓ API imports successful")
    
    # Test main app
    from backend.app.main import app
    print("✓ Main app import successful")
    
    print("\n🎉 All imports successful! The backend should start without errors.")
    
except Exception as e:
    print(f"\n❌ Error during import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
