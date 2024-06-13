import os
import socket


# code from StackOverflow: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_current_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0.5)       # set timeout to 0.5 seconds

    try:
        # connect to a public Google DNS server (doesn't really matter which one)
        s.connect(('8.8.8.8', 53))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # fallback to localhost
    finally:
        s.close()

    return ip

# # a simple way to get the IP address of the machine
# def get_current_ip():
#     return socket.gethostbyname(socket.gethostname())


# my way of getting the IP address
def get_ip_address():
    # generate a file with the ip address
    os.system("ifconfig en0 | grep 'inet ' > inet.txt")
    inet_file = open('inet.txt', 'r')
    inet_data = inet_file.read()
    inet_file.close()
    inet_data = inet_data.split(' ')
    ip_address = inet_data[1]

    return ip_address


if __name__ == '__main__':
    print(f'Current IP address: {get_current_ip()}')