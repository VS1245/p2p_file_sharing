import socket
import os
import struct
import sys

SERVER_PORT = 5001       # Same port as server
BUFFER_SIZE = 1024

def send_file(SERVER_IP, file_path):
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    # Get the file name and its length
    file_name = os.path.basename(file_path)
    file_name_length = len(file_name)

    # Send the file name length (4 bytes)
    print("sender",file_name_length)
    client_socket.send(struct.pack('!I', file_name_length))
    
    # Then send the file name
    client_socket.send(file_name.encode())

    # Open the file to send
    with open(file_path, 'rb') as file:
        while True:
            # Read bytes from the file
            data = file.read(BUFFER_SIZE)
            if not data:
                break
            client_socket.sendall(data)

    print(f"File {file_name} sent successfully!")
    client_socket.close()



if __name__ == "__main__":
    # file_path = input("Enter the path of the file to send: ")
    if len(sys.argv) < 3:
        print("Usage: python file_sender.py <receiver_ip_address>")
        sys.exit(1)

    receiver_ip = sys.argv[2]

    # Hardcode the file path or make it dynamic
    file_path = sys.argv[1]

    # Send the file to the receiver
    send_file(receiver_ip, file_path)
