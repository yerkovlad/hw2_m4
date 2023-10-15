from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

PORT_HTTP = 3000

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
    with open(data_file, 'a') as file:
        json.dump(data, file, indent=4)
        file.write('\n')

if __name__ == '__main__':
    http_server = HTTPServer(('localhost', PORT_HTTP), MyHandler)
    print(f"HTTP server is running on port {PORT_HTTP}")
    http_server.serve_forever()
