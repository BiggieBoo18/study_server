import os
import socket
import struct
from   ctypes import *

# host IP address
host = "127.0.0.1"

# IP header
class IP(Structure):
    _fields_ = [
        ("ihl",          c_uint8, 4),
        ("version",      c_uint8, 4),
        ("tos",          c_uint8, 4),
        ("len",          c_uint16),
        ("id",           c_uint16),
        ("offset",       c_uint16),
        ("ttl",          c_uint8),
        ("protocol_num", c_uint8),
        ("sum",          c_uint16),
        ("src",          c_uint32),
        ("dst",          c_uint32)
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        # mapping to protocol
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        # convert to readable IP address
        self.src_address  = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address  = socket.inet_ntoa(struct.pack("<L", self.dst))

        # convert to readable protocol name
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

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

try:
    while True:
        # read packet
        raw_buffer = sniffer.recvfrom(65565)[0]

        # create IP structure start of 20 packet
        ip_header  = IP(raw_buffer[0:20])

        # output protocol and host
        print("Protocol: {0} {1} -> {2}".format(ip_header.protocol, ip_header.src_address, ip_header.dst_address))
# Ctrl-C
except KeyboardInterrupt:
    # disable promiscas mode
    if os.name=="nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

    
