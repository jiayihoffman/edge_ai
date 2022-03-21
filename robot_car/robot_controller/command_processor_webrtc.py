# echo-server.py

import socket
import os
import json
import argparse
from threading import Thread
import pyfirmata
from pyautogo import setup_motor_pins, setup_board, forward, right, back, left, stop_auto

# SOCKET_PATH = '/tmp/marvin.socket'
SOCKET_PATH = '/tmp/uv4l.socket'
COMMAND_JSON_KEY = 'keycodes'


def command_direct(command, enA, enB, in1, in2, in3, in4):
    if command == 57:
        stop_auto(enA, enB)
        is_stopped = True
    else:
        if command == 103:
            forward(enA, enB, in1, in2, in3, in4)
        elif command == 106:
            right(enA, enB, in1, in2, in3, in4)
        elif command == 108:
            back(enA, enB, in1, in2, in3, in4)
        elif command == 105:
            left(enA, enB, in1, in2, in3, in4)
        is_stopped = False

    return is_stopped

def decode_data(data):
    data = data.decode('utf-8')
    try:
        command = json.loads(data)[COMMAND_JSON_KEY][0]
        print('command received ', command, type(command))
        return command
    except json.decoder.JSONDecodeError:
        return None

def socket_data(socket_path, enA, enB, in1, in2, in3, in4):
    try:
        # Create the socket file if it does not exist
        if not os.path.exists(socket_path):
            f = open(socket_path, 'w')
            f.close()

        os.unlink(socket_path)

        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as s:
            s.bind(socket_path)
            s.listen()
            print('awaiting connection...')
            conn, addr = s.accept()
            with conn:
                print('established the connection with ', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        # the client closed the socket, so exit the loop.
                        break
                    command = decode_data(data)
                    if command is not None:
                        command_direct(command, enA, enB, in1, in2, in3, in4)
                    conn.sendall(data)
    except OSError:
        if os.path.exists(socket_path):
            print("Error accessing %s\nTry running 'sudo chown pi: %s'" % (socket_path, socket_path))
            os._exit(0)
            return
        else:
            print("Socket file not found. Did you configure uv4l-raspidisp to use %s?" % socket_path)
            raise
    except socket.error as err:
        print("socket error: %s" % err)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a ArcHydro schema')
    parser.add_argument('--socket', required=False, default=SOCKET_PATH,
                        help='the path to the socket')
    args = parser.parse_args()

    board = setup_board()
    enA, enB, in1, in2, in3, in4 = setup_motor_pins(board)

    # Start iterator to receive input data
    pyfirmata.util.Iterator(board).start()

    socket_thread = Thread(target=socket_data, args=(args.socket, enA, enB, in1, in2, in3, in4,))
    socket_thread.start()
