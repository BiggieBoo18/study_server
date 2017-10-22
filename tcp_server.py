import socket
import threading

bind_ip   = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((bind_ip, bind_port))
server.listen(5)

print("[*] Listening on {0}:{1}".format(bind_ip, bind_port))

# connect from client method
def handle_client(client_socket):
    # show data from client
    request = client_socket.recv(1024)
    print("[*] Received: {0}".format(request))
    # response
    client_socket.send(b"ACK!")
    client_socket.close()

while True:
    client, addr = server.accept()
    print("[*] Accepted connection from: {0}:{1}".format(addr[0], addr[1]))
    # recieve with thread
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
