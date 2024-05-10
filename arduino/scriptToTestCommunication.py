import socket

SERVER_IP = '192.168.0.109'
SERVER_PORT = 80

message = "turnLightOn"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    print("CONNECT\n")
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print("SENDALL\n")
    client_socket.sendall(message.encode())
    
    print("Message sent successfully:", message)

except ConnectionRefusedError:
    print("Connection to the server failed. Please make sure the server is running.")

finally:
    client_socket.close()
