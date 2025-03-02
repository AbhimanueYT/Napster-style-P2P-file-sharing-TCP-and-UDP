# Central Index Server (Run first)
import socket
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 5000))
server.listen()

files_index = {}
logging.info("Server started on localhost:5000")

while True:
    try:
        # Accept connection (fixed the typo from conn.accept() to server.accept())
        conn, addr = server.accept()
        logging.info(f"New connection from {addr}")
        
        try:
            # Receive and process data
            data = conn.recv(1024).decode()
            request = json.loads(data)
            
            # Format: {"command": "register", "files": ["file1.txt"], "ip": "127.0.0.1"}
            #         {"command": "search", "query": "file1"}
            if request['command'] == 'register':
                for f in request['files']:
                    files_index.setdefault(f, []).append(request['ip'])
                conn.send(b'OK')
                logging.info(f"Registered files for {request['ip']}: {request['files']}")
            
            elif request['command'] == 'search':
                results = {k:v for k,v in files_index.items() if request['query'] in k}
                conn.send(json.dumps(results).encode())
                logging.info(f"Search query '{request['query']}' returned {len(results)} results")
            
            else:
                conn.send(b'Invalid command')
                logging.warning(f"Invalid command received: {request['command']}")
                
        except json.JSONDecodeError:
            conn.send(b'Invalid JSON format')
            logging.error("Invalid JSON received")
            
        except Exception as e:
            conn.send(b'Server error')
            logging.error(f"Error processing request: {str(e)}")
            
        finally:
            conn.close()
            
    except Exception as e:
        logging.error(f"Connection error: {str(e)}")
        continue 