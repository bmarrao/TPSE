from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get the length of the data
        content_length = int(self.headers['Content-Length'])
        # Read the data from the request
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Log the received data
        print("Received data:", post_data)
        
        # Check if the received data is "movementBell"
        if post_data == "movementBell":
            print("Movement bell signal received")

        # Send a 200 OK response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Message received')

def get_local_ip():
    # Create a temporary socket to determine the local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external address (doesn't have to be reachable)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def run(server_class=HTTPServer, handler_class=RequestHandler, port=3000):
    # Get the local IP address
    ip_address = get_local_ip()
    server_address = (ip_address, port)
    
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on {ip_address}:{port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
