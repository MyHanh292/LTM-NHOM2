#!/usr/bin/env python3
"""
Quick Start - Chạy Server + Client dễ dàng
"""

import subprocess
import sys
import os
import time

def start_server():
    """Khởi động server"""
    print("\n" + "="*60)
    print("🖥️  KHỞI ĐỘNG SERVER")
    print("="*60 + "\n")
    
    try:
        subprocess.Popen([sys.executable, "server/run_server.py"])
        print("[✓] ✅ Server đã khởi động!")
        print("[i] Nhấn CTRL+C để dừng server\n")
        time.sleep(2)
    except Exception as e:
        print(f"[✗] ❌ Lỗi: {e}")
        return False
    
    return True

def start_client():
    """Khởi động client"""
    print("\n" + "="*60)
    print("🎮 KHỞI ĐỘNG CLIENT")
    print("="*60 + "\n")
    
    try:
        subprocess.Popen([sys.executable, "client1.py"])
        print("[✓] ✅ Client đã khởi động!\n")
    except Exception as e:
        print(f"[✗] ❌ Lỗi: {e}")
        return False
    
    return True

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║          🎮 CỜ CARO ONLINE - QUICK START 🎮                  ║
╚════════════════════════════════════════════════════════════════╝

Chọn chế độ:
1️⃣  Chỉ khởi động Server
2️⃣  Khởi động Server + 1 Client
3️⃣  Khởi động 2 Client (server phải chạy sẵn)
4️⃣  Kiểm tra kết nối LAN
5️⃣  Xem hướng dẫn LAN

Nhập lựa chọn (1-5):
""".strip())
    
    choice = input("> ").strip()
    
    if choice == "1":
        start_server()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[i] Server dừng")
    
    elif choice == "2":
        if start_server():
            time.sleep(3)
            start_client()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[i] Dừng")
    
    elif choice == "3":
        print("\n[i] Chạy 2 client...")
        try:
            subprocess.Popen([sys.executable, "client1.py"])
            subprocess.Popen([sys.executable, "client2.py"])
            print("[✓] ✅ 2 Client đã khởi động!\n")
            
            while True:
                time.sleep(1)
        except Exception as e:
            print(f"[✗] ❌ Lỗi: {e}")
        except KeyboardInterrupt:
            print("\n[i] Dừng")
    
    elif choice == "4":
        subprocess.run([sys.executable, "test_lan_connection.py"])
    
    elif choice == "5":
        if os.path.exists("LAN_GUIDE.md"):
            os.startfile("LAN_GUIDE.md")
        else:
            print("[!] File LAN_GUIDE.md không tìm thấy")
    
    else:
        print("[!] Lựa chọn không hợp lệ")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[i] Thoát")
