import socket

target_host = "127.0.0.1"
target_port = 9999

# socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect
client.connect((target_host, target_port))

# send
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# recieve
response = client.recv(4096)

print(response)
client.close()
