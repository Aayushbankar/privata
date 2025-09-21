#!/usr/bin/env python3
"""
MOSDAC AI Help Bot - Unified Server Launcher

This script starts both the backend API server and frontend development server,
providing a unified development environment similar to VS Code Live Server.

Usage:
    python start_app.py

Features:
- Automatically starts backend API on port 8000 if not running
- Starts frontend server on port 3000
- Provides proper CORS configuration for local development
- Prints access URLs for both servers
- Handles process cleanup on exit
"""

import os
import sys
import time
import signal
import socket
import subprocess
import threading
from pathlib import Path

# Configuration
BACKEND_PORT = 8000
FRONTEND_PORT = 3000
ADMIN_PORT = 9000
FRONTEND_DIR = Path(__file__).parent / "frontend"

def check_port_available(port):
    """Check if a port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def start_backend_server():
    """Start the backend API server."""
    if not check_port_available(BACKEND_PORT):
        print(f"✅ Backend API already running on port {BACKEND_PORT}")
        return None

    print(f"🚀 Starting backend API on port {BACKEND_PORT}...")

    # Start the backend server in a separate process
    backend_process = subprocess.Popen([
        sys.executable, "main.py"
    ], cwd=Path(__file__).parent)

    # Wait a bit for the server to start
    time.sleep(3)

    if backend_process.poll() is None:
        print(f"✅ Backend API started successfully on port {BACKEND_PORT}")
        return backend_process
    else:
        print("❌ Failed to start backend API")
        return None

def start_admin_server():
    """Start the admin dashboard server."""
    if not check_port_available(ADMIN_PORT):
        print(f"✅ Admin dashboard already running on port {ADMIN_PORT}")
        return None

    print(f"🎛️ Starting admin dashboard on port {ADMIN_PORT}...")

    # Start the admin server in a separate process
    admin_process = subprocess.Popen([
        sys.executable, "admin_dashboard.py"
    ], cwd=Path(__file__).parent)

    # Wait a bit for the server to start
    time.sleep(2)

    if admin_process.poll() is None:
        print(f"✅ Admin dashboard started successfully on port {ADMIN_PORT}")
        return admin_process
    else:
        print("❌ Failed to start admin dashboard")
        return None
def start_frontend_server():
    """Start the frontend development server."""
    if not check_port_available(FRONTEND_PORT):
        print(f"✅ Frontend server already running on port {FRONTEND_PORT}")
        return None

    print(f"🌐 Starting frontend server on port {FRONTEND_PORT}...")

    # Start the frontend server in a separate process
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "http.server", str(FRONTEND_PORT)
    ], cwd=FRONTEND_DIR)

    # Wait a bit for the server to start
    time.sleep(2)

    if frontend_process.poll() is None:
        print(f"✅ Frontend server started successfully on port {FRONTEND_PORT}")
        return frontend_process
    else:
        print("❌ Failed to start frontend server")
        return None

def print_server_info():
    """Print server access information."""
    print("\n" + "="*60)
    print("🎉 MOSDAC AI Help Bot - Development Servers Started!")
    print("="*60)
    print(f"📡 Backend API:       http://localhost:{BACKEND_PORT}")
    print(f"   • API Docs:         http://localhost:{BACKEND_PORT}/api/docs")
    print(f"   • Health Check:     http://localhost:{BACKEND_PORT}/api/v1/status")
    print(f"   • Chat Endpoint:    http://localhost:{BACKEND_PORT}/api/v1/chat")
    print()
    print(f"🌐 Frontend App:      http://localhost:{FRONTEND_PORT}")
    print(f"   • Chat Interface:   http://localhost:{FRONTEND_PORT}/index.html")
    print()
    print(f"🎛️ Admin Dashboard:   http://localhost:{ADMIN_PORT}")
    print(f"   • System Monitor:   http://localhost:{ADMIN_PORT}")
    print(f"   • Real-time Stats:  Live system metrics")
    print()
    print("📝 Usage Instructions:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. The chat interface will automatically connect to the API")
    print("   3. Start chatting with the MOSDAC AI Help Bot!")
    print("   4. Access admin dashboard at http://localhost:9000")
    print("="*60)
    print("💡 Tip: All servers will run in the background.")
    print("   Press Ctrl+C to stop all servers.")
    print("="*60 + "\n")

def cleanup_processes(backend_process, frontend_process, admin_process):
    """Clean up running processes."""
    if backend_process and backend_process.poll() is None:
        print("\n🛑 Stopping backend server...")
        backend_process.terminate()
        backend_process.wait()

    if frontend_process and frontend_process.poll() is None:
        print("🛑 Stopping frontend server...")
        frontend_process.terminate()
        frontend_process.wait()

    if admin_process and admin_process.poll() is None:
        print("🛑 Stopping admin dashboard...")
        admin_process.terminate()
        admin_process.wait()

    print("✅ All servers stopped.")

def main():
    """Main function to start all servers."""
    print("🔧 MOSDAC AI Help Bot - Server Launcher")
    print("="*50)

    # Track processes
    backend_process = None
    frontend_process = None
    admin_process = None

    try:
        # Start backend server
        backend_process = start_backend_server()

        # Start admin dashboard
        admin_process = start_admin_server()

        # Start frontend server
        frontend_process = start_frontend_server()

        # Print server information
        print_server_info()

        # Keep the main process alive
        try:
            while True:
                time.sleep(1)
                # Check if any process has died
                if backend_process and backend_process.poll() is not None:
                    print("❌ Backend server has stopped unexpectedly")
                    break
                if frontend_process and frontend_process.poll() is not None:
                    print("❌ Frontend server has stopped unexpectedly")
                    break
                if admin_process and admin_process.poll() is not None:
                    print("❌ Admin dashboard has stopped unexpectedly")
                    break

        except KeyboardInterrupt:
            print("\n🛑 Received shutdown signal...")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    finally:
        cleanup_processes(backend_process, frontend_process, admin_process)
        print("👋 Thanks for using MOSDAC AI Help Bot!")



if __name__ == "__main__":
    main()