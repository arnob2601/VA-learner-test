#!/usr/bin/env python3
"""
test_persistence.py: Comprehensive automated test for client progress persistence
across hard server restarts (SIGKILL) and multi-client independence.
"""

import os
import sys
import time
import json
import signal
import urllib.request
import urllib.error
import subprocess

PORT = 8899
BASE_URL = f"http://localhost:{PORT}"
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "data", "user_progress.json")
BACKUP_FILE = PROGRESS_FILE + ".bak_test"

def start_server():
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait for server to respond
    for _ in range(25):
        try:
            req = urllib.request.urlopen(f"{BASE_URL}/api/health", timeout=1)
            if req.status == 200:
                return proc
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("Server failed to start within timeout.")

def kill_server_hard(proc):
    """Simulate sudden crash or ungraceful shutdown (SIGKILL)."""
    try:
        os.kill(proc.pid, signal.SIGKILL)
        proc.wait(timeout=3)
    except Exception:
        pass

def http_get(path):
    req = urllib.request.urlopen(f"{BASE_URL}{path}", timeout=3)
    return req.status, req.headers.get("Content-Type"), req.read()

def http_post(path, data):
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=3)
    return resp.status, json.loads(resp.read().decode("utf-8"))

def main():
    print("=== STARTING CLIENT PERSISTENCE & OFFICIAL ASSET TESTS ===")
    
    # Backup existing progress file if present
    if os.path.exists(PROGRESS_FILE):
        os.replace(PROGRESS_FILE, BACKUP_FILE)
    
    proc = None
    try:
        # Step 1: Start server
        print("1. Launching server...")
        proc = start_server()
        print(f"   Server running on PID {proc.pid}")

        # Step 2: Test official sign image serving
        print("2. Verifying official sign image HTTP endpoints...")
        with open("data/signs.json", "r", encoding="utf-8") as f:
            signs = json.load(f)
        
        tested_signs = ["stop_sign", "yield_sign", "speed_limit_55", "school_zone", "no_u_turn", "added_lane", "two_way_traffic"]
        for sign_id in tested_signs:
            status, ctype, content = http_get(f"/images/signs/{sign_id}.png")
            assert status == 200, f"Failed to fetch sign {sign_id}"
            assert "image/png" in ctype, f"Invalid mime type {ctype} for {sign_id}"
            assert len(content) > 500, f"Sign image {sign_id} is unexpectedly small ({len(content)} bytes)"
        print(f"   Successfully verified official sign image endpoints ({len(tested_signs)} sampled).")

        # Step 3: Check initial empty progress
        print("3. Checking GET /api/progress for nonexistent client...")
        status, _, body = http_get("/api/progress?clientId=client-alpha")
        assert status == 200
        initial_data = json.loads(body.decode("utf-8"))
        assert initial_data.get("clientId") == "client-alpha"
        assert initial_data.get("history") == []
        print("   Returned default initialized progress schema as expected.")

        # Step 4: POST progress for client-alpha
        print("4. Saving progress for client-alpha...")
        sample_progress = {
            "clientId": "client-alpha",
            "history": [
                {
                    "mode": "dmv_real",
                    "passed": True,
                    "correct": 10,
                    "total": 10,
                    "percent": 100,
                    "elapsedSeconds": 45,
                    "timestamp": 1726880000000
                }
            ],
            "missedQuestions": ["gq05", "sq12", "sq27"],
            "masteredSigns": ["stop", "yield", "school_crossing", "speed_limit_55"],
            "activeExam": {
                "mode": "dmv_real",
                "part": 1,
                "currentIndex": 4,
                "correctCount": 4,
                "incorrectCount": 0,
                "elapsedSeconds": 32,
                "hasAnswered": False,
                "selectedOption": 2
            },
            "theme": "kiosk",
            "audioEnabled": False
        }
        status, resp = http_post("/api/progress", sample_progress)
        assert status == 200
        assert resp.get("status") == "ok"
        print("   Progress successfully saved on server.")

        # Verify disk write immediately
        assert os.path.exists(PROGRESS_FILE), "user_progress.json was not created on disk"
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            disk_data = json.load(f)
        assert "clients" in disk_data and "client-alpha" in disk_data["clients"], "client-alpha not found in disk_data['clients']"
        print("   Verified atomic write to data/user_progress.json.")

        # Step 5: Hard crash server using SIGKILL (kill -9)
        print("5. CRASHING SERVER WITH SIGKILL (kill -9)...")
        kill_server_hard(proc)
        time.sleep(1)
        print("   Server process terminated ungracefully.")

        # Step 6: Restart server
        print("6. Restarting server on same port...")
        proc = start_server()
        print(f"   Server restarted on PID {proc.pid}")

        # Step 7: Verify progress persists after server restart
        print("7. Fetching /api/progress after server restart...")
        status, _, body = http_get("/api/progress?clientId=client-alpha")
        assert status == 200
        retrieved = json.loads(body.decode("utf-8"))
        
        assert retrieved.get("theme") == "kiosk", f"Theme mismatch: {retrieved.get('theme')}"
        assert retrieved.get("audioEnabled") is False, f"Audio mismatch: {retrieved.get('audioEnabled')}"
        assert retrieved.get("missedQuestions") == ["gq05", "sq12", "sq27"]
        assert retrieved.get("masteredSigns") == ["stop", "yield", "school_crossing", "speed_limit_55"]
        assert retrieved.get("history")[0]["correct"] == 10
        assert retrieved.get("activeExam")["currentIndex"] == 4
        assert retrieved.get("activeExam")["selectedOption"] == 2
        print("   SUCCESS! All client progress, active exam, theme, and stats persisted across server crash/restart!")

        # Step 8: Multi-client independence test
        print("8. Testing multi-client independence...")
        client_beta_progress = {
            "clientId": "client-beta",
            "theme": "dark",
            "missedQuestions": ["gq01"],
            "masteredSigns": ["stop"]
        }
        http_post("/api/progress", client_beta_progress)
        
        _, _, body_alpha = http_get("/api/progress?clientId=client-alpha")
        _, _, body_beta = http_get("/api/progress?clientId=client-beta")
        
        alpha_res = json.loads(body_alpha.decode("utf-8"))
        beta_res = json.loads(body_beta.decode("utf-8"))
        
        assert alpha_res.get("theme") == "kiosk"
        assert beta_res.get("theme") == "dark"
        assert len(alpha_res.get("missedQuestions")) == 3
        assert len(beta_res.get("missedQuestions")) == 1
        print("   Verified client-alpha and client-beta maintain isolated states.")

        print("\n🎉 ALL PERSISTENCE TESTS PASSED CLEANLY!")

    finally:
        if proc:
            kill_server_hard(proc)
        # Restore backup or remove test progress
        if os.path.exists(BACKUP_FILE):
            os.replace(BACKUP_FILE, PROGRESS_FILE)
        elif os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)

if __name__ == "__main__":
    main()
