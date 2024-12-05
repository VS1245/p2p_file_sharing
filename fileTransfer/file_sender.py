import socket
import os
import struct
import sys
from cryptography.fernet import Fernet

SERVER_PORT = 5001       # Same port as server
BUFFER_SIZE = 1024

# Use a symmetric encryption key (AES key)
ENCRYPTION_KEY = Fernet.generate_key()  # Generate a key only once and save it somewhere secure
cipher = Fernet(ENCRYPTION_KEY)

def send_file(SERVER_IP, file_path):
    try:
        # Create a TCP/IP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))

        # Send the encryption key (for simplicity; use secure exchange in real cases)
        client_socket.send(ENCRYPTION_KEY)

        # Get the file name and its length
        file_name = os.path.basename(file_path)
        file_name_length = len(file_name)

        # Send the file name length (4 bytes)
        client_socket.send(struct.pack('!I', file_name_length))
        client_socket.send(file_name.encode())

        # Send the file in chunks after encrypting
        with open(file_path, 'rb') as file:
            while chunk := file.read(BUFFER_SIZE):
                encrypted_chunk = cipher.encrypt(chunk)  # Encrypt chunk by chunk
                client_socket.sendall(struct.pack('!I', len(encrypted_chunk)))  # Send chunk length
                client_socket.sendall(encrypted_chunk)  # Send chunk data

        print(f"File {file_name} sent successfully with encryption!")
        client_socket.close()
    except Exception as e:
        print(f"Error while sending file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python file_sender.py <file_path> <receiver_ip_address>")
        sys.exit(1)

    file_path = sys.argv[1]
    receiver_ip = sys.argv[2]

    send_file(receiver_ip, file_path)
