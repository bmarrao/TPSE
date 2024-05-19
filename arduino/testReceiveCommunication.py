import socket

# Server IP and port
SERVER_IP = '192.168.1.76'
SERVER_PORT = 80  # Use 0 to bind to any available port

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address
server_socket.bind((SERVER_IP, SERVER_PORT))

# Get the port number assigned by the system
assigned_port = server_socket.getsockname()[1]
print(f"Listening on {SERVER_IP}:{assigned_port}")

# Listen for incoming connections
server_socket.listen(1)

while True:
    # Wait for a connection
    print("Waiting for a connection...")
    connection, client_address = server_socket.accept()
    try:
        print(f"Connection from {client_address}")

        # Receive the data in small chunks
        while True:
            data = connection.recv(16)
            if data:
                message = data.decode('utf-8').strip()
                print(f"Received message: {message}")
                if message == "movementBell":
                    print("Received movementBell signal")
            else:
                # No more data from the client
                break

    finally:
        # Clean up the connection
        connection.close()