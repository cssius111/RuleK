#!/usr/bin/env python3
"""
Complete fix and test workflow for RuleK API
"""
import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    print()
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    
    if result.returncode == 0:
        print(f"\n✅ {description} - SUCCESS")
    else:
        print(f"\n❌ {description} - FAILED")
    
    return result.returncode == 0


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           RuleK API Complete Fix Workflow                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    steps = [
        ("python apply_additional_fixes.py", "Apply additional fixes"),
        ("pkill -f 'python.*start_web_server' || true", "Stop existing server"),
        ("sleep 2", "Wait for server to stop"),
    ]
    
    # Run fix steps
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            if "pkill" not in cmd:  # pkill failing is ok
                print("\n⚠️ Fix failed, but continuing...")
    
    # Start server in background
    print(f"\n{'='*60}")
    print("🚀 Starting server in background...")
    print(f"{'='*60}")
    
    server_process = subprocess.Popen(
        [sys.executable, "start_web_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("⏳ Waiting for server to start (5 seconds)...")
    time.sleep(5)
    
    # Check if server is running
    import requests
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server responded but with error")
    except:
        print("❌ Server is not responding")
        print("\nTry starting manually:")
        print("  python start_web_server.py")
        server_process.terminate()
        return 1
    
    # Run tests
    test_commands = [
        ("python test_unit_fixes.py", "Unit tests"),
        ("python verify_fixes.py", "API verification"),
        ("python fix_api.py", "Full E2E test suite"),
    ]
    
    all_passed = True
    for cmd, desc in test_commands:
        if not run_command(cmd, desc):
            all_passed = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 FINAL RESULTS")
    print(f"{'='*60}")
    
    if all_passed:
        print("""
✅ ✅ ✅ ALL TESTS PASSED! ✅ ✅ ✅

The RuleK API is now fully functional:
- Rule creation works correctly
- Turn advancement processes NPCs properly  
- AI functionality handles priority fields

Server is running at: http://localhost:8000
API docs at: http://localhost:8000/docs

Press Ctrl+C to stop the server.
        """)
        
        # Keep server running
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server_process.terminate()
    else:
        print("""
⚠️ Some tests failed. Please check the output above.

Common issues:
1. Server already running on port 8000
   Fix: pkill -f 'python.*start_web_server'
   
2. Import errors
   Fix: Check that all files were properly updated
   
3. API key missing
   Fix: Add DEEPSEEK_API_KEY to .env file

Try running individual commands to debug:
- python apply_additional_fixes.py
- python start_web_server.py
- python verify_fixes.py
        """)
        
        server_process.terminate()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
