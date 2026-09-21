#!/usr/bin/env python3
"""
server.py: 100% local, zero-dependency HTTP server for Virginia Learner's Permit Quiz.
Serves the web application, detects LAN IP, serves dynamic QR codes for iPad connection,
and handles concurrent local connections using Python's standard library.
"""
import os
import sys
import json
import time
import socket
import subprocess
import argparse
import urllib.parse
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn, TCPServer

import qr_generator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "user_progress.json")

def load_progress(client_id=None):
    """Loads client progress from persistent disk store."""
    default_data = {
        "clientId": client_id or "default",
        "history": [],
        "missedQuestions": [],
        "masteredSigns": [],
        "activeExam": None,
        "theme": "modern",
        "audioEnabled": True,
        "updatedAt": 0
    }
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                store = json.load(f)
            if client_id and "clients" in store and client_id in store["clients"]:
                return store["clients"][client_id]
            if "default" in store and store["default"]:
                res = dict(store["default"])
                if client_id:
                    res["clientId"] = client_id
                return res
            if "history" in store or "missedQuestions" in store:
                return store
        except Exception as e:
            sys.stderr.write(f"Error reading progress file {PROGRESS_FILE}: {e}\n")
    return default_data

def save_progress(payload):
    """Atomically saves client progress to persistent disk store."""
    if not isinstance(payload, dict):
        return False, "Payload must be a JSON object"
    
    client_id = payload.get("clientId") or "default"
    store = {"default": {}, "clients": {}}
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                if isinstance(existing, dict):
                    if "clients" in existing:
                        store = existing
                    else:
                        store["default"] = existing
        except Exception:
            pass

    updated_at = int(time.time() * 1000)
    payload["updatedAt"] = updated_at
    payload["clientId"] = client_id
    store.setdefault("clients", {})[client_id] = payload
    store["default"] = payload  # Most recently active client becomes default

    # Atomic write pattern using temp file and os.replace
    tmp_file = f"{PROGRESS_FILE}.tmp.{os.getpid()}"
    try:
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(store, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, PROGRESS_FILE)
        return True, updated_at
    except Exception as e:
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except OSError:
                pass
        sys.stderr.write(f"Failed to atomically persist progress: {e}\n")
        return False, str(e)

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

        # API: Health Check
        if path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return

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

        # API: Client Progress
        if path == '/api/progress':
            client_id = None
            if '?' in self.path:
                qs = urllib.parse.parse_qs(self.path.split('?', 1)[1])
                client_id = qs.get('clientId', [None])[0]
            progress = load_progress(client_id)
            data_bytes = json.dumps(progress).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data_bytes)))
            self.end_headers()
            self.wfile.write(data_bytes)
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

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        path = self.path.split('?')[0]

        if path == '/api/progress':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                payload = json.loads(body)
                success, info = save_progress(payload)
                if success:
                    res = {
                        "status": "ok",
                        "savedAt": info,
                        "clientId": payload.get("clientId", "default")
                    }
                    res_bytes = json.dumps(res).encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Content-Length', str(len(res_bytes)))
                    self.end_headers()
                    self.wfile.write(res_bytes)
                else:
                    self.send_error(500, f"Error saving progress: {info}")
            except Exception as e:
                self.send_error(400, f"Invalid progress payload: {str(e)}")
            return

        self.send_error(404, "Endpoint not found")

    def guess_type(self, path):
        # Ensure correct MIME types for modern web assets
        if path.endswith('.svg'):
            return 'image/svg+xml'
        if path.endswith('.png'):
            return 'image/png'
        if path.endswith('.jpg') or path.endswith('.jpeg'):
            return 'image/jpeg'
        if path.endswith('.webp'):
            return 'image/webp'
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
