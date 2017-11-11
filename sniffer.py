import socket
import os

# host address to listen
host = "127.0.0.1"

# create raw socket and bind the public interface
if os.name=="nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# Add IP header to capture result
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# enable to promiscas mode use ioctl if Windows
if os.name=="nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# read a packet
print(sniffer.recvfrom(65565))

# disable to promiscas mode if Windows
if os.name=="nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
