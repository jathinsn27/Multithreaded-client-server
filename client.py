import socket

SERVER = '127.0.0.1'
PORT = 9090
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MSG = '!DISCONNECT'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

def send(msg):
    message = msg.encode()

client.send('Hello World'.encode('utf-8'))

print(client.recv(1024).decode('utf-8'))