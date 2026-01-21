#!/usr/bin/env python3
"""
start_all_servers.py - Start all 3 servers in background
"""
import subprocess
import time
import sys
import os

def start_socket_server():
    """Start socket server on port 6000"""
    print("🚀 Starting Socket Server (port 6000)...")
    proc = subprocess.Popen(
        [sys.executable, "socket_server/server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)
    if proc.poll() is None:
        print("✅ Socket Server started (PID: {})".format(proc.pid))
        return proc
    else:
        print("❌ Socket Server failed to start")
        return None

def start_flask():
    """Start Flask backend on port 5000"""
    print("🚀 Starting Flask Backend (port 5000)...")
    env = os.environ.copy()
    env['FLASK_ENV'] = 'production'
    proc = subprocess.Popen(
        [sys.executable, "-u", "backend_api/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    time.sleep(2)
    if proc.poll() is None:
        print("✅ Flask Backend started (PID: {})".format(proc.pid))
        return proc
    else:
        print("❌ Flask Backend failed to start")
        return None

def start_frontend():
    """Start frontend on port 8000"""
    print("🚀 Starting Frontend (port 8000)...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000", "--bind", "127.0.0.1"],
        cwd="frontend/web",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(1)
    if proc.poll() is None:
        print("✅ Frontend started (PID: {})".format(proc.pid))
        return proc
    else:
        print("❌ Frontend failed to start")
        return None

def main():
    print("\n" + "="*60)
    print("🎬 STARTING ALL SERVERS")
    print("="*60 + "\n")
    
    processes = []
    
    # Start all servers
    socket_proc = start_socket_server()
    if socket_proc:
        processes.append(socket_proc)
    
    flask_proc = start_flask()
    if flask_proc:
        processes.append(flask_proc)
    
    frontend_proc = start_frontend()
    if frontend_proc:
        processes.append(frontend_proc)
    
    print("\n" + "="*60)
    print("✅ ALL SERVERS RUNNING")
    print("="*60)
    print("\n📍 Access URLs:")
    print("   • Frontend: http://localhost:8000")
    print("   • Backend API: http://localhost:5000")
    print("   • Socket Server: port 6000")
    print("\n💡 To stop servers, press Ctrl+C")
    print("\n" + "="*60 + "\n")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            # Check if any process died
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    print("⚠️  Process {} died".format(i+1))
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping all servers...")
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
        print("✅ All servers stopped")

if __name__ == '__main__':
    main()
