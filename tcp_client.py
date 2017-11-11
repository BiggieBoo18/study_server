import socket

#target_host = "192.168.3.3"
#target_port = 9000
target_host = "127.0.0.1" # to proxy
target_port = 9999        # to proxy

# socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect
client.connect((target_host, target_port))

# send
client.send(b"Hello, world")

# recieve
response = client.recv(4096).decode("utf-8")

print(response)
client.close()
