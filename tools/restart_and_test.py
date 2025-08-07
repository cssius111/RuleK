#!/usr/bin/env python3
"""
Restart server and run full test suite
"""
import subprocess
import time
import os
import signal
import sys

def kill_existing_server():
    """Kill any existing Python web server processes"""
    print("🛑 Stopping existing server...")
    try:
        # Find and kill processes
        result = subprocess.run(
            ["pkill", "-f", "python.*start_web_server"],
            capture_output=True,
            text=True
        )
        
        # Also try with uvicorn
        subprocess.run(
            ["pkill", "-f", "uvicorn"],
            capture_output=True,
            text=True
        )
        
        # Wait a bit for processes to die
        time.sleep(2)
        print("✅ Existing server stopped")
        return True
    except Exception as e:
        print(f"⚠️ Could not stop server: {e}")
        return False


def start_server():
    """Start the web server in background"""
    print("🚀 Starting new server...")
    
    # Start server in background
    process = subprocess.Popen(
        [sys.executable, "start_web_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if sys.platform != "win32" else None
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Check if server started successfully
    import requests
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("✅ Server started successfully")
            return process
    except:
        pass
    
    print("❌ Server failed to start")
    return None


def run_tests():
    """Run the test suite"""
    print("\n" + "=" * 60)
    print("🧪 Running Test Suite")
    print("=" * 60)
    
    # Run verify_fixes.py
    print("\n📝 Running verification tests...")
    result = subprocess.run(
        [sys.executable, "verify_fixes.py"],
        capture_output=False,
        text=True
    )
    
    if result.returncode == 0:
        print("\n✅ Verification tests passed!")
    else:
        print("\n⚠️ Some verification tests failed")
    
    # Run fix_api.py
    print("\n📝 Running full E2E test suite...")
    result = subprocess.run(
        [sys.executable, "fix_api.py"],
        capture_output=False,
        text=True
    )
    
    if result.returncode == 0:
        print("\n✅ E2E tests passed!")
    else:
        print("\n⚠️ Some E2E tests failed")


def main():
    print("=" * 60)
    print("🔄 RuleK Server Restart and Test")
    print("=" * 60)
    
    # Kill existing server
    kill_existing_server()
    
    # Start new server
    server_process = start_server()
    
    if not server_process:
        print("\n❌ Could not start server")
        print("Please check for errors and try:")
        print("  python start_web_server.py")
        return 1
    
    try:
        # Run tests
        run_tests()
        
        print("\n" + "=" * 60)
        print("✅ Testing complete!")
        print("Server is still running at http://localhost:8000")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Keep server running
        server_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping server...")
        if sys.platform != "win32":
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        else:
            server_process.terminate()
        server_process.wait(timeout=5)
        print("✅ Server stopped")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
