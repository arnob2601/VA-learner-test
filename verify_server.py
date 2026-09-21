#!/usr/bin/env python3
"""
verify_server.py: Automated end-to-end verification of the local server and all endpoints.
"""
import urllib.request
import json
import time
import subprocess
import sys
import os

def test_endpoints(port=8080):
    base_url = f"http://localhost:{port}"
    print(f"Testing endpoints at {base_url}...")

    endpoints = [
        ("/", 200, "text/html"),
        ("/css/style.css", 200, "text/css"),
        ("/css/kiosk.css", 200, "text/css"),
        ("/js/app.js", 200, "application/javascript"),
        ("/js/exam.js", 200, "application/javascript"),
        ("/js/flashcards.js", 200, "application/javascript"),
        ("/js/speech.js", 200, "application/javascript"),
        ("/manifest.json", 200, "application/json"),
        ("/sw.js", 200, "application/javascript"),
        ("/icons/icon.svg", 200, "image/svg+xml"),
        ("/api/network-info", 200, "application/json"),
        ("/api/qr.svg", 200, "image/svg+xml"),
        ("/api/data", 200, "application/json"),
        ("/data/signs.json", 200, "application/json"),
        ("/data/questions_signs.json", 200, "application/json"),
        ("/data/questions_general.json", 200, "application/json"),
        ("/data/cheat_sheet.json", 200, "application/json")
    ]

    for path, expected_status, expected_mime in endpoints:
        url = base_url + path
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
                content_type = resp.headers.get("Content-Type", "")
                data = resp.read()
                assert status == expected_status, f"Expected status {expected_status}, got {status} for {path}"
                assert expected_mime in content_type, f"Expected MIME {expected_mime}, got {content_type} for {path}"
                assert len(data) > 0, f"Empty response for {path}"
                print(f"  ✓ {path:30} -> {status} OK ({len(data)} bytes, {content_type.split(';')[0]})")
        except Exception as e:
            print(f"  ✗ {path} FAILED: {e}")
            return False

    # Verify API data contents
    with urllib.request.urlopen(f"{base_url}/api/data") as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert "signs" in data and len(data["signs"]) >= 35, "Signs bank too small"
        assert "questions_signs" in data and len(data["questions_signs"]) >= 40, "Part 1 question bank too small"
        assert "questions_general" in data and len(data["questions_general"]) >= 70, "Part 2 question bank too small"
        assert "cheat_sheet" in data, "Missing cheat sheet"
        print(f"\n  ✓ /api/data verified: {len(data['signs'])} signs, {len(data['questions_signs'])} Part 1 questions, {len(data['questions_general'])} Part 2 questions.")

    # Verify Network info API
    with urllib.request.urlopen(f"{base_url}/api/network-info") as resp:
        info = json.loads(resp.read().decode('utf-8'))
        assert "lan_ip" in info and info["lan_ip"], "Missing lan_ip"
        assert "network_url" in info and info["network_url"].startswith("http"), "Invalid network_url"
        print(f"  ✓ /api/network-info verified: Local IP is {info['lan_ip']}, Network URL is {info['network_url']}")

    # Verify QR code endpoint
    with urllib.request.urlopen(f"{base_url}/api/qr.svg") as resp:
        svg = resp.read().decode('utf-8')
        assert svg.startswith("<svg") and "</svg>" in svg, "Invalid SVG output from /api/qr.svg"
        print(f"  ✓ /api/qr.svg verified: Valid SVG QR code ({len(svg)} chars)")

    print("\n🎉 ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    return True

if __name__ == "__main__":
    test_port = 8899
    # Start temporary test server
    proc = subprocess.Popen([sys.executable, "server.py", "--port", str(test_port)])
    time.sleep(1) # wait for bind
    try:
        success = test_endpoints(port=test_port)
        if not success:
            sys.exit(1)
    finally:
        proc.terminate()
        proc.wait()
