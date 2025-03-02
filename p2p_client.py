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
    def __init__(self, server_ip='localhost', file_server_port=6000):
        self.server_ip = server_ip
        self.file_server_port = file_server_port
        self.start_file_server()
        self.register_files()

    def start_file_server(self):
        def handle_clients():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('0.0.0.0', self.file_server_port))
                sock.listen()
                logging.info(f"File server started on port {self.file_server_port}")
                
                while True:
                    try:
                        conn, addr = sock.accept()
                        logging.info(f"File request from {addr}")
                        
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
                                    
                            logging.info(f"Sent file {filename} to {addr}")
                            
                        except Exception as e:
                            logging.error(f"Error serving file: {e}")
                            
                        finally:
                            conn.close()
                            
                    except Exception as e:
                        logging.error(f"Connection error: {e}")
                        
            except Exception as e:
                logging.error(f"File server error: {e}")
                raise
                
        self.server_thread = threading.Thread(target=handle_clients, daemon=True)
        self.server_thread.start()

    def register_files(self):
        try:
            files = [f.name for f in SHARED_FOLDER.iterdir() if f.is_file()]
            with socket.socket() as s:
                s.connect((self.server_ip, 5000))
                request = {
                    'command': 'register',
                    'files': files,
                    'ip': f'localhost:{self.file_server_port}'  # In real use, get actual IP
                }
                s.send(json.dumps(request).encode())
                response = s.recv(1024).decode()
                
                if response == 'OK':
                    logging.info(f"Successfully registered {len(files)} files")
                else:
                    logging.error(f"Failed to register files: {response}")
                    
        except Exception as e:
            logging.error(f"Error registering files: {e}")

    def search_files(self, query):
        try:
            with socket.socket() as s:
                s.connect((self.server_ip, 5000))
                request = {'command': 'search', 'query': query}
                s.send(json.dumps(request).encode())
                results = json.loads(s.recv(1024).decode())
                logging.info(f"Found {len(results)} results for query '{query}'")
                return results
        except Exception as e:
            logging.error(f"Error searching files: {e}")
            return {}

    def download(self, filename, peer_addr):
        try:
            host, port = peer_addr.split(':')
            port = int(port)
            
            with socket.socket() as s:
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
                
        except Exception as e:
            logging.error(f"Error downloading {filename} from {peer_addr}: {e}")
            return False

def main():
    # Create a test file if shared folder is empty
    if not list(SHARED_FOLDER.iterdir()):
        with open(SHARED_FOLDER / 'test.txt', 'w') as f:
            f.write('This is a test file')
        logging.info("Created test file in shared folder")

    # Start peer
    peer = Peer()
    
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