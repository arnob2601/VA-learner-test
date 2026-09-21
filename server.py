#!/usr/bin/env python3
"""
server.py: 100% local, zero-dependency HTTP server for Virginia Learner's Permit Quiz.
Serves the web application, detects LAN IP, serves dynamic QR codes for iPad connection,
and handles concurrent local connections using Python's standard library.
"""
import os
import sys
import json
import socket
import subprocess
import argparse
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn, TCPServer

import qr_generator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")

def get_lan_ip():
    """Detects the machine's local Wi-Fi / Ethernet LAN IP address."""
    # Method 1: Check macOS network interfaces
    for iface in ['en0', 'en1', 'en2', 'bridge0']:
        try:
            out = subprocess.check_output(['ipconfig', 'getifaddr', iface], text=True, stderr=subprocess.DEVNULL).strip()
            if out and not out.startswith('127.'):
                return out
        except Exception:
            pass

    # Method 2: UDP probe to local broadcast/gateway
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.168.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        if not ip.startswith('127.'):
            return ip
    except Exception:
        pass

    # Method 3: Standard hostname resolution
    try:
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        if not ip.startswith('127.'):
            return ip
    except Exception:
        pass

    return '127.0.0.1'

class ThreadedHTTPServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True
    daemon_threads = True

class VirginiaQuizRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self):
        # Prevent aggressive mobile caching during local development & study
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        path = self.path.split('?')[0]

        # API: Network Info for iPad modal
        if path == '/api/network-info':
            lan_ip = getattr(self.server, 'lan_ip', '127.0.0.1')
            port = getattr(self.server, 'server_port', 8080)
            network_url = f"http://{lan_ip}:{port}/"
            local_url = f"http://localhost:{port}/"
            
            payload = {
                "lan_ip": lan_ip,
                "port": port,
                "network_url": network_url,
                "local_url": local_url,
                "status": "online"
            }
            data_bytes = json.dumps(payload, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data_bytes)))
            self.end_headers()
            self.wfile.write(data_bytes)
            return

        # API: Dynamic SVG QR code
        if path == '/api/qr.svg':
            lan_ip = getattr(self.server, 'lan_ip', '127.0.0.1')
            port = getattr(self.server, 'server_port', 8080)
            network_url = f"http://{lan_ip}:{port}/"
            svg_content = qr_generator.make_qr_svg(network_url).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml; charset=utf-8')
            self.send_header('Content-Length', str(len(svg_content)))
            self.end_headers()
            self.wfile.write(svg_content)
            return

        # API: Combined data endpoint
        if path == '/api/data':
            signs_file = os.path.join(DATA_DIR, "signs.json")
            q_signs_file = os.path.join(DATA_DIR, "questions_signs.json")
            q_gen_file = os.path.join(DATA_DIR, "questions_general.json")
            cheat_file = os.path.join(DATA_DIR, "cheat_sheet.json")

            try:
                with open(signs_file, 'r', encoding='utf-8') as f: signs = json.load(f)
                with open(q_signs_file, 'r', encoding='utf-8') as f: q_signs = json.load(f)
                with open(q_gen_file, 'r', encoding='utf-8') as f: q_gen = json.load(f)
                with open(cheat_file, 'r', encoding='utf-8') as f: cheat_sheet = json.load(f)

                payload = {
                    "signs": signs,
                    "questions_signs": q_signs,
                    "questions_general": q_gen,
                    "cheat_sheet": cheat_sheet
                }
                data_bytes = json.dumps(payload).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(data_bytes)))
                self.end_headers()
                self.wfile.write(data_bytes)
                return
            except Exception as e:
                self.send_error(500, f"Error loading quiz data: {str(e)}")
                return

        # Serve files from data directory
        if path.startswith('/data/'):
            filename = os.path.basename(path)
            file_path = os.path.join(DATA_DIR, filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception as e:
                    self.send_error(500, f"Error reading data file: {str(e)}")
                    return

        # Default fallback to static directory handler
        return super().do_GET()

    def guess_type(self, path):
        # Ensure correct MIME types for modern web assets
        if path.endswith('.svg'):
            return 'image/svg+xml'
        if path.endswith('.json'):
            return 'application/json; charset=utf-8'
        if path.endswith('.js'):
            return 'application/javascript; charset=utf-8'
        if path.endswith('.css'):
            return 'text/css; charset=utf-8'
        if path.endswith('.html'):
            return 'text/html; charset=utf-8'
        return super().guess_type(path)

    def log_message(self, format, *args):
        # Clean terminal logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def find_available_port(start_port=8080, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return start_port

def run_server(port=None, test_mode=False):
    lan_ip = get_lan_ip()
    target_port = port if port else find_available_port(8080)

    server_address = ('0.0.0.0', target_port)
    httpd = ThreadedHTTPServer(server_address, VirginiaQuizRequestHandler)
    httpd.lan_ip = lan_ip
    httpd.server_port = target_port

    network_url = f"http://{lan_ip}:{target_port}/"
    local_url = f"http://localhost:{target_port}/"

    qr_art = qr_generator.make_qr_ascii(network_url)

    print("\n" + "=" * 68)
    print(" 🚗 VIRGINIA DMV LEARNER'S PERMIT EXAM SIMULATOR (100% LOCAL)")
    print("=" * 68)
    print(f" Local Mac Access:               👉 {local_url}")
    print(f" iPad / iPhone / Tablet Access:  👉 {network_url}")
    print("=" * 68)
    print(" Scan this QR Code with your iPad Camera to open instantly:")
    print("-" * 68)
    print(qr_art)
    print("-" * 68)
    print(" Press Ctrl+C to stop the server at any time.\n")

    if test_mode:
        print("[TEST MODE] Server initialized successfully on port", target_port)
        httpd.server_close()
        return

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Virginia DMV Quiz Server...")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Virginia DMV Learner's Permit Local Server")
    parser.add_argument("--port", type=int, default=None, help="Port to bind (default: 8080)")
    parser.add_argument("--test", action="store_true", help="Initialize and verify server without blocking")
    args = parser.parse_args()

    run_server(port=args.port, test_mode=args.test)
