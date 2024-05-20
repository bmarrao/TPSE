import socket

def main():
    # Server IP address and port
    SERVER_IP = "192.168.0.109"
    SERVER_PORT = 80

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print("Connected to server.")

        # Send a message to the server
        message = "turnLightOn"
        client_socket.sendall(message.encode())
        print(f"Sent message: {message}")

        # Optionally, receive a response from the server
        response = client_socket.recv(1024)
        print("Server response:", response.decode())

    except ConnectionRefusedError:
        print("Connection to server failed. Make sure the server is running.")

    finally:
        # Close the socket
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
