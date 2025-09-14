#!/usr/bin/env python3
"""
MOSDAC AI Help Bot - Unified Application Launcher

This script starts both the FastAPI backend server and serves the frontend
using Python's built-in HTTP server. It provides a unified development
experience similar to Flask's development server.

Usage:
    python run_app.py [--port PORT] [--api-port API_PORT] [--frontend-port FRONTEND_PORT]

Options:
    --port PORT              Port for the frontend server (default: 3000)
    --api-port API_PORT      Port for the FastAPI backend (default: 8000)
    --frontend-port PORT     Alias for --port
    --help                   Show this help message
"""

import os
import sys
import subprocess
import threading
import time
import signal
import webbrowser
from argparse import ArgumentParser

def run_command(command, cwd=None, shell=False):
    """Run a command and return the process object"""
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return process
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return None

def start_backend(api_port):
    """Start the FastAPI backend server"""
    print(f"🚀 Starting FastAPI backend on port {api_port}...")
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found in current directory")
        return None
    
    backend_process = run_command([
        sys.executable, "main.py"
    ], cwd=".")
    
    if backend_process:
        print(f"✅ Backend server started (PID: {backend_process.pid})")
        # Wait a moment for the server to start
        time.sleep(2)
    else:
        print("❌ Failed to start backend server")
    
    return backend_process

def start_frontend(frontend_port):
    """Start the frontend HTTP server"""
    print(f"🌐 Starting frontend server on port {frontend_port}...")
    
    # Check if frontend directory exists
    if not os.path.exists("frontend"):
        print("❌ Error: frontend directory not found")
        return None
    
    frontend_process = run_command([
        sys.executable, "-m", "http.server", str(frontend_port)
    ], cwd="frontend")
    
    if frontend_process:
        print(f"✅ Frontend server started (PID: {frontend_process.pid})")
        # Wait a moment for the server to start
        time.sleep(1)
    else:
        print("❌ Failed to start frontend server")
    
    return frontend_process

def check_backend_health(api_port, max_retries=10):
    """Check if the backend server is healthy"""
    import requests
    
    url = f"http://localhost:{api_port}/api/v1/status"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print("✅ Backend server is healthy and responding")
                return True
        except requests.RequestException:
            pass
        
        if attempt < max_retries - 1:
            time.sleep(1)
    
    print("❌ Backend server is not responding")
    return False

def open_browser(frontend_port):
    """Open the web browser to the frontend"""
    url = f"http://localhost:{frontend_port}"
    print(f"🌍 Opening browser to {url}")
    
    try:
        webbrowser.open(url)
        print("✅ Browser opened successfully")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")

def monitor_processes(processes):
    """Monitor processes and restart if they crash"""
    try:
        while True:
            for name, process in processes.items():
                if process and process.poll() is not None:
                    print(f"⚠️  {name} process crashed with return code {process.returncode}")
                    print(f"Stderr: {process.stderr.read() if process.stderr else 'No stderr'}")
                    
                    # Restart the process
                    if name == "backend":
                        processes["backend"] = start_backend(processes["api_port"])
                    elif name == "frontend":
                        processes["frontend"] = start_frontend(processes["frontend_port"])
            
            time.sleep(5)
    except KeyboardInterrupt:
        pass

def main():
    parser = ArgumentParser(description="MOSDAC AI Help Bot - Unified Application Launcher")
    parser.add_argument("--port", type=int, default=3000, help="Port for frontend server (default: 3000)")
    parser.add_argument("--api-port", type=int, default=8000, help="Port for FastAPI backend (default: 8000)")
    parser.add_argument("--frontend-port", type=int, help="Alias for --port")
    
    args = parser.parse_args()
    
    # Use frontend-port if specified, otherwise use port
    frontend_port = args.frontend_port if args.frontend_port else args.port
    api_port = args.api_port
    
    print("=" * 60)
    print("🛰️  MOSDAC AI Help Bot - Unified Application Launcher")
    print("=" * 60)
    print(f"Backend API: http://localhost:{api_port}")
    print(f"Frontend:    http://localhost:{frontend_port}")
    print("=" * 60)
    
    # Store processes and ports
    processes = {
        "backend": None,
        "frontend": None,
        "api_port": api_port,
        "frontend_port": frontend_port
    }
    
    # Start backend
    backend_process = start_backend(api_port)
    processes["backend"] = backend_process
    
    if not backend_process:
        print("❌ Cannot continue without backend server")
        return 1
    
    # Check backend health
    if not check_backend_health(api_port):
        print("⚠️  Backend may not be fully functional")
    
    # Start frontend
    frontend_process = start_frontend(frontend_port)
    processes["frontend"] = frontend_process
    
    if not frontend_process:
        print("❌ Cannot continue without frontend server")
        return 1
    
    # Open browser
    open_browser(frontend_port)
    
    print("\n" + "=" * 60)
    print("✅ Both servers are running!")
    print("Press Ctrl+C to stop all servers")
    print("=" * 60)
    print("\nBackend API Docs: http://localhost:8000/docs")
    print("Frontend:         http://localhost:3000")
    print("=" * 60)
    
    # Set up signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down servers...")
        for name, process in processes.items():
            if process and process.poll() is None:
                print(f"Stopping {name} server...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        print("✅ All servers stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_processes, args=(processes,), daemon=True)
    monitor_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    sys.exit(main())
