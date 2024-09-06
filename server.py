import http.server
import ssl
import json
import os
import socketserver
import signal
import time
import threading
from dnslib import DNSRecord, DNSHeader, RR, QTYPE, A, AAAA
import sys

# HTTP Server Handler
class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            try:
                with open(html_file, 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        self.send_error(501, "Unsupported method")

    def do_PUT(self):
        self.send_error(501, "Unsupported method")

    def do_DELETE(self):
        self.send_error(501, "Unsupported method")

# DNS Server Handler
class DNSRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]
        request = DNSRecord.parse(data)

        qname = str(request.q.qname).rstrip('.')
        qtype = QTYPE[request.q.qtype]
        print(f"Incoming DNS request type {qtype} for {qname}")

        for record in dns_records:
            if record['hostname'] == qname and record['type'] == qtype:
                reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
                
                if record['type'] == 'A':
                    reply.add_answer(RR(qname, QTYPE.A, rdata=A(record['address']), ttl=60))
                elif record['type'] == 'AAAA':
                    reply.add_answer(RR(qname, QTYPE.AAAA, rdata=AAAA(record['address']), ttl=60))
                
                socket.sendto(reply.pack(), self.client_address)
                print(f"Responded with {record['type']} record for {qname} -> {record['address']}")
                return

        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, rcode=3))  # rcode 3 - NXDOMAIN
        socket.sendto(reply.pack(), self.client_address)
        print(f"Responded with NXDOMAIN for {qname}")

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

# HTTPS Server
def run_https_server(config):
    global html_file
    html_file = config['html_file']

    server_address = (config['server_address'], config['https_port'])
    httpd = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=config['ssl_certfile'], keyfile=config['ssl_keyfile'])
    
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"HTTPS Server running on https://{config['server_address']}:{config['https_port']}/")
    httpd.serve_forever()

# HTTP Server
def run_http_server(config):
    global html_file
    html_file = config['html_file']

    server_address = (config['server_address'], config['http_port'])
    httpd = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)

    print(f"HTTP Server running on http://{config['server_address']}:{config['http_port']}/")
    httpd.serve_forever()

# DNS Server
def run_dns_server(config):
    global dns_records
    dns_records = config['dns_records']

    with socketserver.UDPServer((config['server_address'], 53), DNSRequestHandler) as server:
        print(f"DNS Server running on {config['server_address']}:53")
        server.serve_forever()

def load_config(config_file='config.json'):
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found.")
    with open(config_file, 'r') as file:
        return json.load(file)

def shutdown_servers(signum, frame):
    print("\nShutting down servers...")
    sys.exit(0)

if __name__ == "__main__":
    try:
        config = load_config()
        signal.signal(signal.SIGINT, shutdown_servers)

        if config.get("enable_https_server", True):
            https_thread = threading.Thread(target=run_https_server, args=(config,))
            https_thread.daemon = True
            https_thread.start()

        if config.get("enable_http_server", True):
            http_thread = threading.Thread(target=run_http_server, args=(config,))
            http_thread.daemon = True
            http_thread.start()

        if config.get("enable_dns_server", True):
            run_dns_server(config)

        else:
            try:
                while True:
                    signal.pause()
            except AttributeError:
                # signal.pause() is missing for Windows; wait 1ms and loop instead
                while True:
                    time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
