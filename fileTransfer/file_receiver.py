import socket
import struct
import os
# from ..p2p_file_sharing.settings import MEDIA_URL

# Server configuration
SERVER_IP = '0.0.0.0'  # Listen on all available interfaces
SERVER_PORT = 5001      
BUFFER_SIZE = 1024

def start_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(1)

    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    
    # Wait for a client connection
    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    # Receive the length of the file name (4 bytes)
    file_name_length = struct.unpack('!I', conn.recv(4))[0]

    print("receiver",file_name_length)

    # Then receive the file name based on the length
    file_name = conn.recv(file_name_length).decode()
    print(f"Receiving file: {file_name}")

    MEDIA_URL = "media"
    # Open file to write data
    os.makedirs(os.path.join(MEDIA_URL, 'received'), exist_ok=True)
    with open(os.path.join(MEDIA_URL,'received',file_name), 'wb') as file:
        while True:
            # Read bytes from the client
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            file.write(data)

    print(f"File received successfully as {file_name}")
    conn.close()

if __name__ == "__main__":
    start_server()