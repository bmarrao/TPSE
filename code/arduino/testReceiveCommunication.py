import http.server
import socketserver
import socket

# Define the handler to process incoming HTTP requests
class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/movementBell':
            print("Received message from Arduino: Button clicked")
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Message received")
        else:
            self.send_response(404)
            self.end_headers()

# Define server address and port
server_address = ('', 3000)
httpd = socketserver.TCPServer(server_address, MyRequestHandler)

# Get the server's actual IP address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This does not need to be reachable
        s.connect(('10.254.254.254', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

ip_address = get_ip_address()

# Print the server address and port
print(f"Serving on IP {ip_address} port 3000")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer is shutting down.")
    httpd.server_close()
except Exception as e:
    print(f"Error occurred: {e}")

