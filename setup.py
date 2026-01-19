#!/usr/bin/env python3
"""
QUICK START - Tạo account + chơi online ngay
"""

import sys
import os
import json
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILE = os.path.join(BASE_DIR, "users.json")

def hash_password(password: str, username: str) -> str:
    return hashlib.sha256((username + password).encode("utf-8")).hexdigest()

def setup_default_users():
    """Tạo các account mặc định"""
    users = {}
    
    # Account 1
    users["player1"] = {
        "password": hash_password("123456", "player1"),
        "wins": 0,
        "losses": 0
    }
    
    # Account 2
    users["player2"] = {
        "password": hash_password("123456", "player2"),
        "wins": 0,
        "losses": 0
    }
    
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    
    print("✅ Tạo account mặc định:")
    print("   player1 / 123456")
    print("   player2 / 123456")

if __name__ == "__main__":
    print("⚙️  Setup Cờ Caro Online...")
    setup_default_users()
    print("\n✅ Sẵn sàng!")
    print("\nBây giờ chạy:")
    print("  Terminal 1: python server/server.py")
    print("  Terminal 2: python offline/login.py")
    print("  Terminal 3: python offline/login.py")
