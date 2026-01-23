#!/usr/bin/env python3
"""
Test if Flask app initializes correctly
"""
import sys
import os

# Add backend_api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_api'))

try:
    print("Attempting to import Flask app...")
    from app import app
    
    print("✅ App imported successfully")
    print(f"App name: {app.name}")
    
    # Count routes
    with app.app_context():
        routes = list(app.url_map.iter_rules())
        print(f"✅ Total routes: {len(routes)}")
        
        # Show first 10 routes
        print("\nFirst 10 routes:")
        for i, rule in enumerate(routes[:10]):
            print(f"  {i+1}. {rule.rule} -> {rule.endpoint} ({rule.methods})")
    
    print("\n✅ App initialization test PASSED")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
