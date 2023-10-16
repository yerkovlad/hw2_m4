from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
import socket
import threading

PORT_HTTP = 3000
PORT_SOCKET = 5000

templates_env = Environment(loader=FileSystemLoader('templates'))

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('index.html', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/message.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open('message.html', 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                with open('error.html', 'rb') as f:
                    self.wfile.write(f.read())
        except:
            self.send_response(500)
            self.end_headers()

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            template = templates_env.get_template('message.html')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

            save_data({
                timestamp: {
                    "username": data["username"],
                    "message": data["message"]
                }
            })
            response_data = {
                "message": data,
                "timestamp": timestamp
            }
            response = template.render(response_data)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))

def save_data(data):
    data_file = 'storage/data.json'
    os.makedirs(os.path.dirname(data_file), exist_ok=True)

    if not os.path.exists(data_file):
        data_list = []
    else:
        with open(data_file, 'r') as file:
            data_list = json.load(file)
    data_list.append(data)
    with open(data_file, 'w') as file:
        json.dump(data_list, file, indent=4)


def socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', PORT_SOCKET)
    sock.bind(server_address)
    print(f"Socket server is running on {server_address[0]}:{server_address[1]}")

    try:
        while True:
            data, address = sock.recvfrom(1024)
            data_dict = json.loads(data.decode())
            save_data({
                datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'): data_dict
            })
    except KeyboardInterrupt:
        print("Stopping socket server")
    finally:
        sock.close()

socket_thread = threading.Thread(target=socket_server)
socket_thread.daemon = True
socket_thread.start()

if __name__ == '__main__':
    http_server = HTTPServer(('localhost', PORT_HTTP), MyHandler)
    print(f"HTTP server is running on port {PORT_HTTP}")
    http_server.serve_forever()

