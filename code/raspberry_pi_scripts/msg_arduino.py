import socket


def msg_arduino(message):
    # Server IP address and port
    SERVER_IP = "192.168.148.153"
    SERVER_PORT = 80

    # create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to the server
        client_socket.connect((SERVER_IP, SERVER_PORT))
        # print("Connected to server.")

        # send a message to the server
        client_socket.sendall(message.encode())
        print(f"Sent message: {message}")

        # optionally, receive a response from the server
        response = client_socket.recv(1024)
        # print("Server response:", response.decode())

    except ConnectionRefusedError:
        print("Connection to server failed. Make sure the server is running.")

    finally:
        # close the socket
        client_socket.close()
        # print("Connection closed.")
