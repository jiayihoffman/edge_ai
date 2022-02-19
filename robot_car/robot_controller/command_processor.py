#
# Copyright 2022 Jiayi Hoffman. All Rights Reserved.
#
import socket
import pyfirmata
from pyautogo import setup_motor_pins, setup_board, forward, right, back, left, stop_auto
from confluent_kafka import Consumer, KafkaError


def command_direct(message_value):
    if message_value == 4:
        stop_auto()
        isStopped = True
    else:
        if message_value == 0:
          forward()
        elif message_value == 1:
          right()
        elif message_value == 2:
          back()
        elif message_value == 3:
          left()
        isStopped = False

    return isStopped

def create_consumer():
    hostname = socket.gethostname()
    settings = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'command_group',
        'client.id': 'raspi' + hostname,
        'enable.auto.commit': True,
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'latest'}
    }

    c = Consumer(settings)
    c.subscribe(["command_topic"])

    return c

def handle_messages(c):
    try:
        while True:
            msg = c.poll(0.1)
            if msg is None:
                continue
            elif not msg.error():
                print('Received message: {0}'.format(msg.value()))
                isStopped = command_direct(msg.value())
            elif msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()))
            else:
                print('Error occured: {0}'.format(msg.error().str()))

    except KeyboardInterrupt:
        pass

    finally:
        c.close()

if __name__ == "__main__":
    board = setup_board()
    enA, enB, in1, in2, in3, in4 = setup_motor_pins(board)

    # Start iterator to receive input data
    pyfirmata.util.Iterator(board).start()

    c = create_consumer()
    handle_messages(c)