import socket

def get_local_ip():
    # Create a socket and connect to an external address (no data is sent)
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

if __name__ == "__main__":
    print("Local IP Address:", get_local_ip())
