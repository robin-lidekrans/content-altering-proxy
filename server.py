import socket
import re
import sys

HOST = ''
BACKLOG = 10

if len(sys.argv) != 2:
    print("Invalid number of arguments. Please only provide the port number.")
    sys.exit(1)

try:
    PORT = int(sys.argv[1])
    if PORT < 1024 or PORT > 65535:
        raise Exception("Port number must be between 1024 and 65535.")
except:
    print("Invalid port number.")
    raise
    sys.exit(1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
print('Server: Waiting for client')
s.listen(BACKLOG)
client_conn, client_addr = s.accept()
with client_conn:
    print('Server: client connected from ', client_addr)
    while True:
        print('Server: waiting for connections...')
        new_conn, new_addr = s.accept()
        print('Server: got connection from ', new_addr)
        data = new_conn.recv(4096)
        print('Server: received %s bytes, forwarding to client' % len(data))
        if data == b'':
            continue
        client_conn.sendall(data)

        response = b''
        response_buffer = client_conn.recv(4096)
        response += response_buffer
        if len(response_buffer) >= 4096:
            # If fill all 4096 bytes of of the response buffer we need to do
            # multiple recieves
            while True:
                # Check how many bytes of content we have recieved so far
                bytes_received = len(response.split(b'\r\n\r\n', maxsplit=1)[1])

                # Extract the headers and check the value of content-length
                header = response.split(b'\r\n\r\n', maxsplit=1)[0]
                if header != b'':
                    content_length_regex_str = "(?<=Content-Length:[ \\t])([0-9]*){1}"
                    header_text = header.decode('utf-8')
                    content_length = int(re.search(content_length_regex_str, header_text, flags=re.IGNORECASE).group(0))
                print("Received %s out of %s bytes" % (bytes_received, content_length))
                if ((response_buffer == b'') or (content_length == bytes_received)):
                    break
                response_buffer = client_conn.recv(4096)
                response += response_buffer
        print("Server: received %s byte response from client, forwarding" % len(response))
        new_conn.sendall(response)
