import server
import proxy
from threading import Thread

server_thread = Thread(target = server)
server_thread.start()
server_thread.join()

proxy_thread = Thread(target = proxy)
proxy_thread.start()
proxy_thread.join()
