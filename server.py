import sys
import socket
import argparse
import threading
import subprocess

def client_sender(buf, target, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect
        client.connect((target, port))
        
        if len(buf):
            client.send(bytes("{}".format(buf), "utf-8"))

        while True:
            # waiting data from target
            recv_len = 1
            response = ""
            while recv_len:
                data      = client.recv(4096)
                recv_len  = len(data)
                response += data.decode("utf-8")
                if recv_len<4096:
                    break
            print(response, end=' ')
            # additional inputs
            buf  = input("")
            buf += "\n"
            # send
            client.send(bytes("{}".format(buf), "utf-8"))
    except:
        import traceback
        traceback.print_exc()
        print("[*] Exception! Exiting.")
        # close socket
        client.close()

def server_loop(target, port, upload, upload_destination, execute, command):
    # "0.0.0.0" if not set "target"
    if not(len(target)):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((target, port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # run server with thread
        client_thread = threading.Thread(target=client_handler, args=(client_socket, upload, upload_destination, execute, command))
        client_thread.start()

def run_command(command):
    # remove newline symbol
    command = command.rstrip()
    # command result
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\n"
    return output.decode("utf-8") if type(output)==bytes else output

def client_handler(client_socket, upload, upload_destination, execute, command):
    # upload
    if len(upload_destination):
        # write all data
        file_buffer = ""
        # recieve data
        while True:
            data = client_socket.recv(1024)
            if len(data)==0:
                break
            else:
                file_buffer += data
        # write data to file
        try:
            fd = open(upload_destination, "wb")
            fd.write(file_buffer)
            fd.close()
            # response
            client_socket.send(
                bytes("Successfully saved file to {0}\n".format(upload_destination), "utf-8"))
        except:
            client_socket.send(
                bytes("Failed to save file to {0}\n".format(upload_destination), "utf-8"))
            
    # execute command
    if len(execute):
        # execute
        output = run_command(execute)
        client_socket.send(bytes("{}".format(output), "utf-8"))

    # command shell
    if command:
        # show shel
        prompt = "<BHP:#> "
        client_socket.send(bytes("{}".format(prompt), "utf-8"))
        while True:
            # recieve command stil "Enter"
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode("utf-8")
            # response
            response  = run_command(cmd_buffer)
            response += prompt
            client_socket.send(bytes("{}".format(response), "utf-8"))
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen",      "-l", action="store_true",    help="listen on [host]:[port] for imcoming connections")
    parser.add_argument("--command",     "-c", action="store_true",    help="initialize a command shell")
    parser.add_argument("--upload",      "-u", action="store_true",    help="--upload=destination - upon recieving connection upload a file and write to [destination]")
    parser.add_argument("--execute",     "-e", type=str, default="",   help="execute the given file upon recieving a connection")
    parser.add_argument("--target",      "-t", type=str, default="",   help="connection target")
    parser.add_argument("--upload_dest", "-d", type=str, default="",   help="upload destination")
    parser.add_argument("--port",        "-p", type=int, default=9999, help="upload destination")
    args = parser.parse_args()

    listen             = args.listen
    command            = args.command
    upload             = args.upload
    execute            = args.execute
    target             = args.target
    upload_destination = args.upload_dest
    port               = args.port

    # input
    if not listen and len(target) and port>0:
        buf = sys.stdin.read() # key press Ctrl-D if don't send
        # send
        client_sender(buf, target, port)

    # server
    if listen:
        server_loop(target, port, upload, upload_destination, execute, command)

main()
