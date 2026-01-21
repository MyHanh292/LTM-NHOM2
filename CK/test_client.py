#!/usr/bin/env python3
"""
Test Flask app with test client
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_api'))

try:
    from app import app, db
    
    print("🧪 FLASK TEST CLIENT TESTING\n")
    
    # Create test client
    with app.app_context():
        db.create_all()  # Ensure tables exist
        client = app.test_client()
        
        # Test 1: Register
        print("Test 1: User Registration")
        resp = client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test12345!'
        })
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.get_json()}\n")
        
        # Test 2: Login  
        print("Test 2: User Login")
        resp = client.post('/api/login', json={
            'username': 'testuser',
            'password': 'Test12345!'
        })
        print(f"Status: {resp.status_code}")
        data = resp.get_json()
        print(f"Response keys: {list(data.keys()) if data else 'None'}")
        if 'token' in (data or {}):
            token = data['token']
            print(f"Token: {token[:30]}...\n")
        else:
            print(f"Response: {data}\n")
        
        # Test 3: Get public documents
        print("Test 3: Get Public Documents")
        resp = client.get('/api/documents/public')
        print(f"Status: {resp.status_code}")
        data = resp.get_json()
        print(f"Response: {data}\n")
        
        print("✅ All tests completed!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
