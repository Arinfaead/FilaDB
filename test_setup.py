#!/usr/bin/env python3
"""
Simple test script to validate FilaDB setup
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.main import app
        from app.models.user import User
        from app.models.filament import Filament
        from app.models.spool import Spool
        from app.models.file_asset import FileAsset
        from app.core.database import engine
        from app.core.security import get_password_hash
        from app.services.spoolmandb import SpoolmanDBService
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_password_hashing():
    """Test password hashing functionality"""
    try:
        from app.core.security import get_password_hash, verify_password
        password = "test123"
        hashed = get_password_hash(password)
        if verify_password(password, hashed):
            print("✅ Password hashing works")
            return True
        else:
            print("❌ Password verification failed")
            return False
    except Exception as e:
        print(f"❌ Password hashing error: {e}")
        return False

def test_models():
    """Test model creation"""
    try:
        from app.models.user import User, UserRole
        from app.models.filament import Filament
        
        # Test user model
        user = User(
            email="test@example.com",
            hashed_password="hashed",
            role=UserRole.ADMIN
        )
        
        # Test filament model
        filament = Filament(
            manufacturer="Test Manufacturer",
            name="Test Filament {color_name}",
            material="PLA",
            density=1.24,
            weight_g=1000,
            diameter_mm=1.75,
            color_name="Red",
            color_hex="#FF0000"
        )
        
        print("✅ Model creation successful")
        return True
    except Exception as e:
        print(f"❌ Model creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing FilaDB Setup")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_password_hashing,
        test_models
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! FilaDB is ready to run.")
        print("\nTo start the application:")
        print("1. Install Docker and Docker Compose")
        print("2. Run: docker compose up -d")
        print("3. Access: http://localhost:8000")
        print("4. Login: admin@example.com / admin123")
    else:
        print("❌ Some tests failed. Please check the setup.")

if __name__ == "__main__":
    main()
