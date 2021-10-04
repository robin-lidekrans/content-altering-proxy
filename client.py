import socket
import re
import sys

HOST = '127.0.0.1'
HTTP_PORT = 80

# Takes a HTTP response in the form of a byte array and replaces any occurance
# of "Stockholm" with "Linköping" and "Smiley" with "Trolly"
def censor(data):
    text = data.decode('utf-8')
    content_type = re.search(r'(?<=Content-Type:[ \t])[^\/]*', text, flags=re.IGNORECASE)

    if content_type is None:
        return text.encode('utf-8')
    elif content_type.group(0) == "text":
        text = re.sub(r"(Stockholm)(?![^<]*?>)", "Linköping", text)
        text = re.sub(r"(Smiley)(?![^<]*?>)", "Trolly", text)
    return text.encode('utf-8')


# Takes a HTTP request and replaces any link ending with smiley.jpg with a more
# suitable image link
def censor_image(data):
    smiley_regex_string = r"[^ ]*?\/smiley.jpg"
    replacement_link = r"http://zebroid.ida.liu.se/fakenews/trolly.jpg"
    decoded_text = data.decode('utf-8')
    decoded_text = re.sub(smiley_regex_string, replacement_link, decoded_text, flags=re.IGNORECASE)
    return decoded_text.encode('utf-8')


# Extracts the host field from a HTTP request
def get_request_host(data):
    request = data.decode('ascii')
    host = re.search(r"(?<=host:[ \t]).*", request, flags=re.IGNORECASE)
    return str(host.group(0))


# Checks if a HTTP request is asking for a jpg image
def is_image_request(data):
    text = data.decode('utf-8')
    return re.search(r'(GET.*)(.jpg)', text, flags=re.IGNORECASE) is not None


# Sends data to host, returning the response
def make_request(host, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as target:
        print("Client: connecting to", host)
        target.connect((host.strip(), HTTP_PORT))
        target.sendall(data)
        response = b''
        while True:
            response_buffer = target.recv(4096)
            response += response_buffer
            if response_buffer == b'':
                break
    return response


# Takes a HTTP response data as a byte array and an int difference, and returns
# an updated HTTP response with difference added to the Content-Length value
def fix_length_header(data, difference):
    text = data.decode('utf-8')
    regex_string = "(?<=Content-Length:[ \\t])(\\d+){1}"
    original = re.search(regex_string, text, flags=re.IGNORECASE).group(0)
    text = re.sub(regex_string, str(int(original) + difference), text, flags=re.IGNORECASE)
    return text.encode('utf-8')


# Extracts and returns the status code from a HTTP response
def get_response_status_code(response_data):
    header = response_data.split(b'\r\n\r\n', maxsplit=1)[0]
    if header != b'':
        header_text = header.decode('utf-8')
        reponse_code = re.search(r"((?<=HTTP\/1.\d\s)\d{3}){1}", header_text, flags=re.IGNORECASE)
        return int(reponse_code.group(0))
    return 0


# Makes a GET request to the server and filters out any unwanted content
def handle_get_request(request_data):
    target_host = get_request_host(request_data)
    if is_image_request(request_data):
        request_data = censor_image(request_data)
    response = make_request(target_host, request_data)
    print('Client: recieved response', response)
    if get_response_status_code(response) == 200:
        if not is_image_request(request_data):
            original_size = len(response)
            response = censor(response)
            size_difference = len(response) - original_size
            if size_difference > 0:
                response = fix_length_header(response, size_difference)
    return response

if len(sys.argv) != 2:
    print("Invalid number of arguments. Please only provide the port number.")
    sys.exit(1)

try:
    PORT = int(sys.argv[1])
    if PORT < 1024 or PORT > 65535:
        raise Exception("Port number must be between 1024 and 65535.")
except:
    print("Invalid port number.")
    sys.exit(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    print('Client: connecting to server')
    server.connect((HOST, PORT))
    while True:
        print("Client: waiting for connections")
        data = server.recv(4096)
        if data != b'':
            print('Client: received ', data)
            request_type = data.split(b' ', maxsplit=1)[0].decode('ascii')
            print("Client: request type: ", request_type)
            if request_type == "GET":
                response = handle_get_request(data)
            else:
                print("Client: recieved %s, dropping." % request_type)
            print(response)
            server.sendall(response)
