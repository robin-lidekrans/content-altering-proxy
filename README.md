# Content-Altering Web Proxy
A content-altering web proxy in Python written for the course Computer Networks (TDTS06) at Linköping University. It will:
- Manipulate HTTP response packages the browser receives to replace any occurance of the word "Stockholm" with "Linköping" and "Smiley" with "Trolly" on any website the user visits.
- Intercept HTTP request messages sent by the browser for a certain image and replace it with [another](http://zebroid.ida.liu.se/fakenews/trolly.jpg) link.
The server and the client are implemented as separate services communicating through a socket. 

## Usage
Start the server by running ```python3 server.py PORT_NUMBER```, where PORT_NUMBER is the port the client should connect through. Then start the client by running the command ```python3 client.py PORT_NUMBER```. The client expects a server to be running on localhost with the port number specified. Any HTTP traffic set up to use a proxy running on localhost will now be fed through the program.
