import socket
import struct
import os
from cryptography.fernet import Fernet

# Server configuration
SERVER_IP = '0.0.0.0'  # Listen on all available interfaces
SERVER_PORT = 5001      

def receive_exactly(conn, num_bytes):
    """Helper function to receive an exact number of bytes from the connection."""
    data = b""
    while len(data) < num_bytes:
        packet = conn.recv(num_bytes - len(data))
        if not packet:
            return None  # Connection closed or data incomplete
        data += packet
    return data

def start_server():
    try:
        # Create a TCP/IP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(1)

        print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
        
        # Wait for a client connection
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        # Receive the encryption key
        ENCRYPTION_KEY = receive_exactly(conn, 44)  # Fernet keys are 44 bytes
        if ENCRYPTION_KEY is None:
            print("Error: Failed to receive encryption key.")
            conn.close()
            return

        cipher = Fernet(ENCRYPTION_KEY)

        # Receive the length of the file name (4 bytes)
        file_name_length_data = receive_exactly(conn, 4)
        if file_name_length_data is None:
            print("Error: Failed to receive file name length.")
            conn.close()
            return
        file_name_length = struct.unpack('!I', file_name_length_data)[0]

        # Receive the file name
        file_name = receive_exactly(conn, file_name_length).decode()
        if not file_name:
            print("Error: Failed to receive file name.")
            conn.close()
            return
        print(f"Receiving encrypted file: {file_name}")

        # Prepare to receive the file data in chunks
        MEDIA_URL = "media"
        os.makedirs(os.path.join(MEDIA_URL, 'received'), exist_ok=True)
        with open(os.path.join(MEDIA_URL, 'received', file_name), 'wb') as file:
            while True:
                # Receive chunk length (4 bytes)
                chunk_length_data = receive_exactly(conn, 4)
                if chunk_length_data is None:
                    print("Error: Failed to receive chunk length.")
                    break  # End of file or connection issue

                chunk_length = struct.unpack('!I', chunk_length_data)[0]
                if chunk_length == 0:
                    break  # End of file

                # Receive the encrypted chunk
                encrypted_data = receive_exactly(conn, chunk_length)
                if encrypted_data is None:
                    print("File ended or connection issues.")
                    break  # End of file or connection issue

                # Decrypt and write to file
                decrypted_chunk = cipher.decrypt(encrypted_data)
                file.write(decrypted_chunk)

        print(f"File {file_name} received and decrypted successfully!")
        conn.close()
    except Exception as e:
        print(f"Error while receiving file: {e}")

if __name__ == "__main__":
    start_server()
