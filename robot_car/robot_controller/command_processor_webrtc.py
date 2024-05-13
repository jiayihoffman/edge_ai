# echo-server.py

import socket
import os
import json
import argparse
import logging
from utils.log_util import setup_logging, close_std_out_file
from threading import Thread
import pyfirmata
from pyautogo import setup_motor_pins, setup_board, setup_servo_pin, move_servo, forward, right, back, left, stop_auto, stop_servo, SERVO_START_ANGLE

# SOCKET_PATH = '/tmp/marvin.socket'
SOCKET_PATH = '/tmp/uv4l.socket'
COMMAND_JSON_KEY = 'keycodes'

logger = logging.getLogger("robot_controller")
servo_pin = None
servo_angle = SERVO_START_ANGLE

def command_angle(command):
    global servo_angle
    if command == 34:  # 'G' turn left
        servo_angle += 20
    elif command == 35:  # 'H' turn right
        servo_angle -= 20
    elif command == 36:  # 'J' stop servo
        servo_angle = SERVO_START_ANGLE
    servo_angle = move_servo(servo_pin, servo_angle)

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
        logger.debug('command received {}, type {}'.format(command, type(command)))
        return command
    except json.decoder.JSONDecodeError as e:
        logger.error('error on decoding into json for data: {}, exception: {}'.format(data, e))
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
            logger.info('awaiting connection...')
            conn, addr = s.accept()
            with conn:
                logger.info('established the connection with {}'.format(addr))
                while True:
                    data = conn.recv(1024)
                    if not data:
                        # the client closed the socket, so exit the loop.
                        break
                    command = decode_data(data)
                    if command is not None:
                        if command < 40:
                            command_angle(command)
                        else:
                            command_direct(command, enA, enB, in1, in2, in3, in4)
                    conn.sendall(data)
    except OSError:
        if os.path.exists(socket_path):
            logger.error("error accessing {}\nTry running 'sudo chown pi: {}'".format(socket_path, socket_path))
            os._exit(0)
            return
        else:
            logger.error("socket file not found. Did you configure uv4l-raspidisp to use {}?".format(socket_path))
            raise
    except socket.error as err:
        logger.error("socket error: {}".format(err))


if __name__ == '__main__':
    setup_logging()

    parser = argparse.ArgumentParser(description='Create a ArcHydro schema')
    parser.add_argument('--socket', required=False, default=SOCKET_PATH,
                        help='the path to the socket')
    args = parser.parse_args()

    try :
        board = setup_board()
        enA, enB, in1, in2, in3, in4 = setup_motor_pins(board)
        servo_pin = setup_servo_pin(board)
        logger.info('connected with the Arduino board.')

        # Start iterator to receive input data
        pyfirmata.util.Iterator(board).start()

        threads = []
        socket_thread = Thread(target=socket_data, args=(args.socket, enA, enB, in1, in2, in3, in4,))
        threads.append(socket_thread)
        socket_thread.start()

        for index, thread in enumerate(threads):
            thread.join()
            logger.info("Main    : thread {} done".format(index))
    except Exception as e:
        logger.error(e)
    finally:
        logger.info('closing out...')
        if servo_pin:
            stop_servo(servo_pin)
        close_std_out_file()
        logger.info('done')

