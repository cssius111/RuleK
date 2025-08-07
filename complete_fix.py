#!/usr/bin/env python3
"""
Complete the RuleK API fixes - Final step
"""
import subprocess
import sys
import time

print("""
╔══════════════════════════════════════════════════════════════╗
║           RuleK API - Final Fix & Test                       ║
╚══════════════════════════════════════════════════════════════╝

Current Status:
✅ Rule creation - WORKING
✅ AI functionality - WORKING  
❌ Turn advancement - ONE ISSUE LEFT

Applying final fix...
""")

# Apply the final NPC fix
print("\n1️⃣ Applying NPC creation fix...")
result = subprocess.run([sys.executable, "final_npc_fix.py"], capture_output=False)

# Kill existing server
print("\n2️⃣ Stopping existing server...")
subprocess.run(["pkill", "-f", "python.*start_web_server"], capture_output=True)
time.sleep(2)

# Start new server
print("\n3️⃣ Starting fresh server...")
server_process = subprocess.Popen(
    [sys.executable, "start_web_server.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print("⏳ Waiting for server to start...")
time.sleep(5)

# Run final test
print("\n4️⃣ Running final test...")
test_result = subprocess.run([sys.executable, "final_test.py"], capture_output=False)

if test_result.returncode == 0:
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🎉 SUCCESS! 🎉                            ║
╚══════════════════════════════════════════════════════════════╝

✅ All RuleK API issues have been fixed!

The API is now fully functional at:
- Main: http://localhost:8000
- Docs: http://localhost:8000/docs

All features working:
✅ Game creation
✅ Rule creation with proper validation
✅ Turn advancement with NPC handling
✅ AI dialogue and action generation

Press Ctrl+C to stop the server.
""")
    
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server_process.terminate()
        
else:
    print("""
⚠️ Some issues remain. Please check the output above.

Manual debugging steps:
1. Check server logs for errors
2. Verify all files were updated correctly
3. Try running tests individually

If you need to manually fix:
- Edit: web/backend/services/game_service.py
- Look for NPC creation code
- Ensure 'id' is not passed twice
""")
    
    server_process.terminate()
    sys.exit(1)
