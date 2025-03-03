# Peer Client (Run multiple instances)
import socket
import os
import threading
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ensure directories exist
SHARED_FOLDER = Path('shared')
DOWNLOADS = Path('downloads')
SHARED_FOLDER.mkdir(exist_ok=True)
DOWNLOADS.mkdir(exist_ok=True)

class Peer:
    def __init__(self, server_ip='localhost', file_server_port=6000, protocol='tcp'):
        self.protocol = protocol.lower()
        self.server_ip = server_ip
        self.file_server_port = file_server_port
        self.start_file_server()
        self.register_files()

    def start_file_server(self):
        def handle_clients():
            if self.protocol == 'tcp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('0.0.0.0', self.file_server_port))
                sock.listen()
                logging.info(f"TCP file server started on port {self.file_server_port}")
                
                while True:
                    conn, addr = sock.accept()
                    try:
                        filename = conn.recv(1024).decode()
                        file_path = SHARED_FOLDER / filename
                        
                        if not file_path.is_file():
                            conn.send(b'FILE_NOT_FOUND')
                            continue
                            
                        conn.send(b'OK')
                        with open(file_path, 'rb') as f:
                            while chunk := f.read(8192):
                                conn.send(chunk)
                                
                    finally:
                        conn.close()
                        
            elif self.protocol == 'udp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('0.0.0.0', self.file_server_port))
                logging.info(f"UDP file server started on port {self.file_server_port}")
                
                while True:
                    data, addr = sock.recvfrom(1024)
                    filename = data.decode()
                    file_path = SHARED_FOLDER / filename
                    
                    if not file_path.is_file():
                        sock.sendto(b'FILE_NOT_FOUND', addr)
                        continue
                        
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    sock.sendto(b'OK:' + file_data, addr)

        self.server_thread = threading.Thread(target=handle_clients, daemon=True)
        self.server_thread.start()

    def register_files(self):
        try:
            files = [f.name for f in SHARED_FOLDER.iterdir() if f.is_file()]
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM if self.protocol == 'udp' else socket.SOCK_STREAM) as s:
                if self.protocol == 'tcp':
                    s.connect((self.server_ip, 5000))
                    
                request = {
                    'command': 'register',
                    'files': files,
                    'ip': f'{self.protocol}:localhost:{self.file_server_port}'
                }
                data = json.dumps(request).encode()
                
                if self.protocol == 'udp':
                    s.sendto(data, (self.server_ip, 5000))
                    response, _ = s.recvfrom(1024)
                else:
                    s.send(data)
                    response = s.recv(1024)
                
                response_str = response.decode().strip()
                if response_str == 'OK':
                    logging.info(f"Successfully registered {len(files)} files")
                else:
                    logging.error(f"Failed to register files: {response_str}")
                    
        except Exception as e:
            logging.error(f"Error registering files: {e}")

    def search_files(self, query):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM if self.protocol == 'udp' else socket.SOCK_STREAM) as s:
                if self.protocol == 'tcp':
                    s.connect((self.server_ip, 5000))
                request = {'command': 'search', 'query': query}
                data = json.dumps(request).encode()
                
                if self.protocol == 'udp':
                    s.sendto(data, (self.server_ip, 5000))
                    response, _ = s.recvfrom(65507)
                else:
                    s.send(data)
                    response = s.recv(1024)
                
                results = json.loads(response.decode())
                logging.info(f"Found {len(results)} results for query '{query}'")
                return results
        except Exception as e:
            logging.error(f"Error searching files: {e}")
            return {}

    def download(self, filename, peer_addr):
        try:
            protocol, host, port = peer_addr.split(':', 2)
            port = int(port)
            
            if protocol == 'tcp':
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.send(filename.encode())
                    response = s.recv(1024)
                    
                    if response == b'FILE_NOT_FOUND':
                        logging.error(f"File {filename} not found on peer {peer_addr}")
                        return False
                    
                    file_path = DOWNLOADS / filename
                    with open(file_path, 'wb') as f:
                        while chunk := s.recv(8192):
                            f.write(chunk)
                        
                    logging.info(f"Successfully downloaded {filename}")
                    return True
                    
            elif protocol == 'udp':
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.sendto(filename.encode(), (host, port))
                    response, _ = s.recvfrom(65507)  # Max UDP packet size
                    
                    if response == b'FILE_NOT_FOUND':
                        logging.error(f"File {filename} not found on peer {peer_addr}")
                        return False
                        
                    if response.startswith(b'OK:'):
                        file_path = DOWNLOADS / filename
                        with open(file_path, 'wb') as f:
                            f.write(response[3:])
                        logging.info(f"Successfully downloaded {filename}")
                        return True
                        
            else:
                logging.error(f"Unsupported protocol: {protocol}")
                return False
                
        except Exception as e:
            logging.error(f"Error downloading {filename} from {peer_addr}: {e}")
            return False

def main():
    # Create a test file if shared folder is empty
    if not list(SHARED_FOLDER.iterdir()):
        with open(SHARED_FOLDER / 'test.txt', 'w') as f:
            f.write('This is a test file')
        logging.info("Created test file in shared folder")

    # Protocol selection
    print("\nSelect Protocol:")
    print("1. TCP")
    print("2. UDP")
    protocol_choice = input("Enter choice (1-2): ").strip()
    protocol = 'tcp' if protocol_choice == '1' else 'udp'
    
    # Start peer with selected protocol
    peer = Peer(protocol=protocol)
    
    while True:
        try:
            print("\nP2P File Sharing Client")
            print("1. Search for files")
            print("2. List shared files")
            print("3. Exit")
            choice = input("Enter your choice (1-3): ")
            
            if choice == '1':
                query = input("Enter search query: ")
                results = peer.search_files(query)
                
                if results:
                    print("\nFound files:")
                    for i, (filename, peers) in enumerate(results.items(), 1):
                        print(f"{i}. {filename} (available from {len(peers)} peers)")
                    
                    file_choice = input("\nEnter number to download (or press Enter to cancel): ")
                    if file_choice.isdigit() and 1 <= int(file_choice) <= len(results):
                        filename, peers = list(results.items())[int(file_choice) - 1]
                        peer.download(filename, peers[0])
                else:
                    print("No files found")
                    
            elif choice == '2':
                files = [f.name for f in SHARED_FOLDER.iterdir() if f.is_file()]
                print("\nShared files:")
                for i, filename in enumerate(files, 1):
                    print(f"{i}. {filename}")
                    
            elif choice == '3':
                break
                
        except Exception as e:
            logging.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    main() 