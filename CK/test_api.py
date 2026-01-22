#!/usr/bin/env python3
import requests
import json

print("🧪 API ENDPOINT TESTING\n")

# Test 1: Check Flask is serving
print("Test 1: Flask Health Check")
try:
    resp = requests.get('http://127.0.0.1:5000/', timeout=2)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 404:
        print("✅ Flask is running (route not found is expected for /)")
except Exception as e:
    print(f"❌ Flask not responding: {e}")

print("\nTest 2: Register User")
try:
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test12345!'
    }
    resp = requests.post('http://127.0.0.1:5000/api/auth/register', json=data, timeout=2)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest 3: Login")
try:
    data = {
        'username': 'testuser',
        'password': 'Test12345!'
    }
    resp = requests.post('http://127.0.0.1:5000/api/auth/login', json=data, timeout=2)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Login successful")
except Exception as e:
    print(f"Error: {e}")

print("\n✅ API Testing Complete")
