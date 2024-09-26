import socket
import sys
import threading
import os
import time
from datetime import datetime
import mimetypes
from pathlib import Path

host = '127.0.0.1' # Localhost
FORMAT = 'utf-8' # To decode from byte to utf-8
header = 1024 # Number of bytes accepted

# def http_headers(status_code, file_path=None):
#     status_codes = {
#         200: 'OK',
#         400: 'Bad Request', 
#         403: 'Forbidden',
#         404: 'Not Found', 
#     }

# Supported content types
def get_content_type(file_path):
    mime_type, encoding = mimetypes.guess_type(file_path)
    return mime_type

def worker_thread(connection, address, document_root):
    try:
        request = connection.recv(header).decode()
        if not request:
            return
        
        print(f"Request received from {address}: {request}")

        headers = request.split("\r\n") # Used to parse the request since HTTP requests are generally separated by carriage return & new line
        method, path, protocol = headers[0].split()

        if method != "GET":
            send_response(connection, '405', "text/html", "405 Method Not Allowed")
            return

        if path == "/":
            path = '/index.html'

        file_path = Path(document_root + path)

        # file_path = os.path.join(document_root, path.lstrip("/"))

        if not os.path.exists(file_path):
            send_response(connection, '404', "text/html", "404 Not Found")
            return
        
        content_type = get_content_type(file_path)
        print(f"Serving file: {file_path} with content type: {content_type}")

        with open(file_path, 'rb') as file:
            file_data = file.read()
            content_type = get_content_type(file_path)
            send_response(connection, "200 OK", content_type, file_data)

        if protocol == "HTTP/1.1":
            connection.settimeout(10)
            print("Keeping connection alive for HTTP/1.1...")
            # time.sleep(60)  # Simulate persistent connection timeout
        else:
            print("Closing connection for HTTP/1.0...")
            connection.close()

        print(request)

    except Exception as e:
        print(f"Error with the reuqest: {e}")

    connection.close()

def send_response(client_socket, status_code, content_type, content):
    response = f"HTTP/1.1 {status_code}\r\n"
    response += f"Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += f"Content-Length: {len(content)}\r\n"
    response += "Connection: close\r\n\r\n"

    client_socket.sendall(response.encode())
    
    if isinstance(content, str):
        content = content.encode()  # Encode if it's a string
    
    client_socket.sendall(content)

def dispatcher(server):
    connection, address = server.accept()
    print(f"Connection accepted from Address: {address}")

    worker = threading.Thread(target=worker_thread, args=(connection, address, document_root))
    worker.start()
    print(f"Active connections {threading.active_count() - 1}") # subtract 1 beacuse there is start thread always running

def start_server(document_root, port):
    # Passing a int limits the new connections and deletes that are waiting to be connected
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

if len(sys.argv) != 5 or sys.argv[1] != '-document_root' or sys.argv[3] != '-port':
    print("Please use the right command in the format: $ ./server -document_root '/home/moazzeni/webserver_files' -port 8888")
    sys.exit(1)

document_root = sys.argv[2]
port = int(sys.argv[4])

start_server(document_root, port)