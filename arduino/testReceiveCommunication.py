import http.server
import socketserver

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

# Start the server
print("Serving on port 3000")
httpd.serve_forever()
