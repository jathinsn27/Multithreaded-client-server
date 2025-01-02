import socket
import sys
import threading
import os
import time
from datetime import datetime
import mimetypes
from pathlib import Path

host = '127.0.0.1' # Localhost
max_connections = 10 # Max clients that can connect
max_timeout = 40  # Max timeout for HTTP 1.1 connection
min_timeout = 5  # Min timeout for HTTP 1.1 connection

def dynamic_timeout_heuristic(num_active_connections):
    load_factor = num_active_connections / max_connections 
    dynamic_timeout = max_timeout * (1 - load_factor) # Makes sure that the timeout is more if server is less busy and vice-versa
    return max(min(dynamic_timeout, max_timeout), min_timeout) # Ensures that the timeout is always in the range min and max timeouts

# Supported content types of all types using mime 
def get_content_type(file_path):
    mime_type, encoding = mimetypes.guess_type(file_path)
    return mime_type

# Spawn the worker thread to process the requests depending on the protocol
def worker_thread(connection, address, document_root):

    while True:

        try:
            request = connection.recv(1024).decode()
            if not request:
                break
            
            # print(f"Request received from {address}: {request}")

            headers = request.split("\r\n") # Used to parse the request since HTTP requests are generally separated by carriage return & new line
            
            try:
                method, path, protocol = headers[0].split() 
            except ValueError:
                continue

            # If the method is not GET
            if method != "GET":
                send_response(connection, '405', "text/html", "405 Method Not Allowed", protocol)
                return

            if path == "/":
                path = '/index.html'

            file_path = Path(document_root + path) # Append path to the appropriate folder

            # Check if the file exisits
            if not os.path.exists(file_path):
                send_response(connection, '404', "text/html", "404: Resource Not Found", protocol)
                return
            
            # Check if the file has correct access
            if not os.access(file_path, os.R_OK):
                send_response(connection, '403', "text/html", "403 Forbidden Access Denied", protocol)
                return
            
            content_type = get_content_type(file_path)
            print(f"Serving file: {file_path} with content type: {content_type}")

            with open(file_path, 'rb') as file:
                file_data = file.read()

            if protocol == "HTTP/1.1":
                num_active_connections = threading.active_count() - 1  # Subtract 1 beacuse there is start thread always running
                timeout = dynamic_timeout_heuristic(num_active_connections) # Set the dynamic timeout based in num of active conenctions
                connection.settimeout(timeout)
                send_response(connection, "200 OK", content_type, file_data, protocol, timeout)
            
            else:
                send_response(connection, "200 OK", content_type, file_data, protocol)
                print("Closing connection for HTTP/1.0...")
                break

        except socket.timeout:
            print(f"Connection to {address} timed out")
            break

        except Exception as e:
            print(f"Error with the reuqest: {e}")
            break

    connection.close()
    print(f"Connection to {address} closed")

def send_response(client_socket, status_code, content_type, content, protocol, timeout= None):
    response = f"{protocol} {status_code}\r\n"
    response += f"Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += f"Content-Length: {len(content)}\r\n"
    if protocol == 'HTTP/1.1' and timeout is not None:
        response += f"Keep-Alive: timeout={timeout}, max=40\r\n"
        response += "Connection: keep-alive\r\n\r\n"
    else:
        response += "Connection: close\r\n\r\n"

    client_socket.sendall(response.encode())
    
    if isinstance(content, str):
        content = content.encode()  # Encode if it's a string
    
    client_socket.sendall(content)

def dispatcher(server):
    connection, address = server.accept()
    print(f"Connection accepted from Address: {address}")
    worker = threading.Thread(target=worker_thread, args=(connection, address, document_root))
    worker.daemon = True
    worker.start()
    print(f"Active connections: {threading.active_count() - 1}") 

def start_server(document_root, port):
    ADDRESS = (host, port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # So we don't run into "Address already in use error" if server is not closed properly
    server.bind(ADDRESS)
    server.listen()
    print(f'Server listening on port:{port} for {document_root}')

    while True:
        try:
            dispatcher(server)
        except KeyboardInterrupt:
            print("Shutting Down Server (Keyboard Interrupt)")
            server.close()
            break

        except Exception as e:
            print(f"Error while connecting: {e}")

# Handle incorrect start of the server
if len(sys.argv) != 5 or sys.argv[1] != '-document_root' or sys.argv[3] != '-port':
    print("Please use the right command in the format: $ python3 server.py -document_root '<path>' -port <port>")
    sys.exit(1)

document_root = sys.argv[2]
port = int(sys.argv[4])

start_server(document_root, port)