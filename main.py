from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

PORT_HTTP = 3000

templates_env = Environment(loader=FileSystemLoader('templates')

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
    
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            save_data({
                timestamp: {
                    "username": data["username"],
                    "message": data["message"]
                }
            })

            send_data_to_socket({
                "timestamp": timestamp,
                "data": data
            })
    
            template = templates_env.get_template('message.html')
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
    with open(data_file, 'a') as file:
        json.dump(data, file, indent=4)
        file.write('\n')

def send_data_to_socket(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            server_address = ('localhost', PORT_SOCKET)
            message = json.dumps(data)
            sock.sendto(message.encode('utf-8'), server_address)
    except Exception as e:
        print(f"Помилка відправки даних до сокет-серверу: {str(e}")

if __name__ == '__main__':
    http_server = HTTPServer(('localhost', PORT_HTTP), MyHandler)
    print(f"HTTP server is running on port {PORT_HTTP}")
    http_server.serve_forever()
