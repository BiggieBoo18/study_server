import sys
import socket
import threading
import argparse

def hexdump(src, length=16):
    result = []
    # digits = 4 if isinstance(src, str) else 2 # python3 need it?
    digits = 2
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = " ".join(["{val:0{l}X}".format(l=2, val=ord(x)) for x in s])
        text = "".join([x if 0x20<=ord(x)<0x7F else b'.' for x in s])
        result.append("{0:04X}    {1:<{l}}    {2}".format(i, hexa, text, l=length*(digits+1)))
    print("\n".join(result))
    
def receive_from(connection):
    buf = ""
    # set timeout
    connection.settimeout(2)

    try:
        # receive data
        while True:
            data = connection.recv(4096).decode("utf-8")
            if not data:
                break
            buf += data
    except:
        pass
    return buf

def request_handler(buf):
    # edit remote packet
    return buf

def response_handler(buf):
    # edit local packet
    return buf

def proxy_handler(client_socket, remote_host, remote_port, receive):
    # connect remote
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    remote_socket.connect((remote_host, remote_port))

    # if receive first
    if receive:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        # hack
        remote_buffer = response_handler(remote_buffer)
        # if send to local
        if len(remote_buffer):
            print("[<==] Sending {0} bytes to localhost.".format(remote_buffer))

    # receive from local -> send to remote -> send to local ...
    while True:
        # receive data from local
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print("[==>] Received {0} bytes from localhost.".format(len(local_buffer)))
            hexdump(local_buffer)
            # hack
            local_buffer = request_handler(local_buffer)
            # send to remote
            remote_socket.send(bytes(local_buffer, "utf-8"))
            print("[==>] Send to remote.")

        # receive data from remote
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] Received {0} bytes from remote.".format(len(remote_buffer)))
            hexdump(remote_buffer)
            # hack
            remote_buffer = response_handler(remote_buffer)
            # send to local
            client_socket.send(bytes(remote_buffer, "utf-8"))
            print("[<==] Send to localhost.")

        # close if receive no data from local or remote
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break
        
            
def server_loop(local_host, local_port, remote_host, remote_port, receive):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on {0}:{1}".format(local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions")
        sys.exit(0)

    print("[*] Listening on {0}:{1}".format(local_host, local_port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        # show local information
        print("[==>] Received incoming connection from {0}:{1}".format(addr[0], addr[1]))
        # start remote to connect with thread
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive))
        proxy_thread.start()

def main():
    # parse argment
    parser = argparse.ArgumentParser()
    parser.add_argument("--lhost",   "-lt", default="127.0.0.1", type=str, help="local  host")
    parser.add_argument("--lport",   "-lp", default=9999,        type=int, help="local  port")
    parser.add_argument("--rhost",   "-rt",                      type=str, help="remote host", required=True)
    parser.add_argument("--rport",   "-rp",                      type=int, help="remote port", required=True)
    parser.add_argument("--receive", "-r",  default=False,                 help="remote port",                action="store_true")
    args = parser.parse_args()

    # run server loop
    server_loop(args.lhost, args.lport, args.rhost, args.rport, args.receive)

main()
