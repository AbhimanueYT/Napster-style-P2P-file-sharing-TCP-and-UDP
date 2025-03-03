# Central Index Server (Run first)
import socket
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Protocol selection
    print("Select Server Protocol:")
    print("1. TCP")
    print("2. UDP")
    choice = input("Enter choice (1-2): ").strip()
    protocol = 'tcp' if choice == '1' else 'udp'

    # Initialize server
    if protocol == 'tcp':
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 5000))
        server.listen()
        logging.info("TCP server started on localhost:5000")
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(('localhost', 5000))
        logging.info("UDP server started on localhost:5000")

    files_index = {}

    while True:
        try:
            if protocol == 'tcp':
                conn, addr = server.accept()
                logging.info(f"New TCP connection from {addr}")
                handle_client(conn, addr, protocol, server, files_index)
            else:
                data, addr = server.recvfrom(1024)
                logging.info(f"New UDP request from {addr}")
                handle_client(None, addr, protocol, server, files_index, data)

        except Exception as e:
            logging.error(f"Connection error: {str(e)}")
            continue

def handle_client(conn, addr, protocol, server, files_index, data=None):
    try:
        if protocol == 'tcp':
            data = conn.recv(1024).decode()
        else:
            data = data.decode()

        request = json.loads(data)
        
        if request['command'] == 'register':
            protocol_peer, host, port = request['ip'].split(':', 2)
            for f in request['files']:
                files_index.setdefault(f, []).append(f"{protocol_peer}:{host}:{port}")
            response = b'OK'
            logging.info(f"Registered files for {request['ip']}: {request['files']}")
        
        elif request['command'] == 'search':
            results = {}
            for filename, peers in files_index.items():
                if request['query'] in filename:
                    results[filename] = peers
            response = json.dumps(results).encode()
            logging.info(f"Search query '{request['query']}' returned {len(results)} results")
        
        else:
            response = b'Invalid command'
            logging.warning(f"Invalid command received: {request['command']}")

        if protocol == 'tcp':
            conn.send(response)
            conn.close()
        else:
            server.sendto(response, addr)

    except json.JSONDecodeError:
        error_response = b'Invalid JSON format'
        if protocol == 'tcp':
            conn.send(error_response)
            conn.close()
        else:
            server.sendto(error_response, addr)
        logging.error("Invalid JSON received")
    
    except Exception as e:
        error_response = b'Server error'
        if protocol == 'tcp':
            conn.send(error_response)
            conn.close()
        else:
            server.sendto(error_response, addr)
        logging.error(f"Error processing request: {str(e)}")

if __name__ == "__main__":
    main() 