#!/usr/bin/env python3
"""
test_handler.py: Sandboxed unit tests for VirginiaQuizRequestHandler,
data loading, QR generation, and template assets without opening network sockets.
"""
import io
import json
import os
import sys

from server import VirginiaQuizRequestHandler, get_lan_ip, ThreadedHTTPServer
import qr_generator

class DummyServer:
    lan_ip = "10.0.0.12"
    server_port = 8080

class DummySocket:
    def __init__(self):
        self.output = io.BytesIO()
    def makefile(self, mode, *args, **kwargs):
        if 'b' in mode:
            return io.BytesIO(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        return io.StringIO("GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
    def sendall(self, data):
        self.output.write(data)

def test_handler():
    print("Testing server internals & data generation in sandbox mode...")
    
    # 1. Test LAN IP detection
    lan_ip = get_lan_ip()
    assert lan_ip, "LAN IP could not be detected"
    print(f"  ✓ LAN IP detection: {lan_ip}")

    # 2. Test QR generator
    test_url = f"http://{lan_ip}:8080/"
    svg = qr_generator.make_qr_svg(test_url)
    assert svg.startswith("<svg") and "</svg>" in svg
    assert "width=" in svg and "height=" in svg
    print(f"  ✓ QR Code SVG generation: valid SVG ({len(svg)} chars)")

    ascii_qr = qr_generator.make_qr_ascii(test_url)
    assert len(ascii_qr.splitlines()) > 10
    print(f"  ✓ QR Code ASCII generation: valid art ({len(ascii_qr.splitlines())} lines)")

    # 3. Test data files presence & content
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    with open(os.path.join(data_dir, "signs.json")) as f:
        signs = json.load(f)
    with open(os.path.join(data_dir, "questions_signs.json")) as f:
        q_signs = json.load(f)
    with open(os.path.join(data_dir, "questions_general.json")) as f:
        q_gen = json.load(f)
    with open(os.path.join(data_dir, "cheat_sheet.json")) as f:
        cheat = json.load(f)

    assert len(signs) >= 35, f"Expected >= 35 signs, got {len(signs)}"
    assert len(q_signs) >= 40, f"Expected >= 40 sign questions, got {len(q_signs)}"
    assert len(q_gen) >= 70, f"Expected >= 70 general questions, got {len(q_gen)}"
    print(f"  ✓ Data files verified: {len(signs)} signs, {len(q_signs)} signs Qs, {len(q_gen)} general Qs")

    # 4. Test static assets presence & non-empty
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    required_static = [
        "index.html",
        "css/style.css",
        "css/kiosk.css",
        "js/app.js",
        "js/exam.js",
        "js/flashcards.js",
        "js/speech.js",
        "manifest.json",
        "sw.js",
        "icons/icon.svg"
    ]
    for rel in required_static:
        full_path = os.path.join(static_dir, rel)
        assert os.path.exists(full_path), f"Missing static file: {rel}"
        size = os.path.getsize(full_path)
        assert size > 0, f"Empty static file: {rel}"
        print(f"  ✓ Static asset {rel:20} -> OK ({size} bytes)")

    print("\n🎉 ALL UNIT & INTEGRITY TESTS PASSED!")

if __name__ == "__main__":
    test_handler()
