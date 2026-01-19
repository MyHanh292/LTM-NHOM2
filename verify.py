#!/usr/bin/env python3
"""
Quick verification that everything is working
"""

print("\n" + "="*60)
print("🔍 CHECKING CARRO ONLINE SETUP")
print("="*60 + "\n")

# Check files exist
import os
files_to_check = [
    "server/server.py",
    "server/__init__.py",
    "online/online_game.py",
    "online/__init__.py",
    "offline/login.py",
    "offline/home.py",
    "offline/game.py",
    "offline/__init__.py",
    "setup.py",
    "config.json",
    "requirements.txt"
]

print("[1/4] Checking files...")
missing = []
for f in files_to_check:
    if os.path.exists(f):
        print(f"  ✓ {f}")
    else:
        print(f"  ✗ {f}")
        missing.append(f)

if missing:
    print(f"\n❌ Missing {len(missing)} files!")
    exit(1)

# Check imports
print("\n[2/4] Checking imports...")
try:
    import server.server
    print("  ✓ server.server")
except Exception as e:
    print(f"  ✗ server.server: {e}")
    exit(1)

try:
    import online.online_game
    print("  ✓ online.online_game")
except Exception as e:
    print(f"  ✗ online.online_game: {e}")
    exit(1)

try:
    import offline.login
    print("  ✓ offline.login")
except Exception as e:
    print(f"  ✗ offline.login: {e}")
    exit(1)

# Check accounts
print("\n[3/4] Checking accounts...")
try:
    import json
    with open("users.json", "r") as f:
        users = json.load(f)
    if "player1" in users and "player2" in users:
        print("  ✓ player1 account exists")
        print("  ✓ player2 account exists")
    else:
        print("  ⚠ Run: python setup.py  (to create test accounts)")
except:
    print("  ⚠ Run: python setup.py  (to create users.json)")

# Check server port
print("\n[4/4] Checking server port...")
import socket
try:
    s = socket.socket()
    s.bind(('127.0.0.1', 9999))
    s.close()
    print("  ✓ Port 9999 is available")
except:
    print("  ✗ Port 9999 is in use!")
    print("     (Is server already running? Kill it and try again)")

print("\n" + "="*60)
print("✅ SETUP VERIFICATION COMPLETE!")
print("="*60)
print("""
Ready to play! Follow these steps:

1. Terminal 1:
   python server/server.py

2. Terminal 2:
   python client1.py

3. Terminal 3:
   python client2.py

4. Click squares to play! 🎮
""")
