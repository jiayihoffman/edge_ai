#
# Copyright 2022 Jiayi Hoffman. All Rights Reserved.
#
import socket
import pyfirmata
from pyautogo import setup_motor_pins, setup_board, forward, right, back, left, stop_auto
from confluent_kafka import Consumer, KafkaError
from robot_car.utils.kafka_constants import KAFKA_SERVER, TOPIC_1

def command_direct(message_value, enA, enB, in1, in2, in3, in4):
    if message_value == '4':
        stop_auto(enA, enB)
        isStopped = True
    else:
        if message_value == '0':
          forward(enA, enB, in1, in2, in3, in4)
        elif message_value == '1':
          right(enA, enB, in1, in2, in3, in4)
        elif message_value == '2':
          back(enA, enB, in1, in2, in3, in4)
        elif message_value == '3':
          left(enA, enB, in1, in2, in3, in4)
        isStopped = False

    return isStopped

def create_consumer():
    hostname = socket.gethostname()
    settings = {
        'bootstrap.servers': '{}:9092'.format(KAFKA_SERVER),
        'group.id': 'command_group',
        'client.id': 'raspi-' + hostname,
        'enable.auto.commit': True,
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'}
    }

    c = Consumer(settings)
    c.subscribe([TOPIC_1])

    return c

def handle_messages(c, enA, enB, in1, in2, in3, in4):
    try:
        while True:
            msg = c.poll(0.1)
            if msg is None:
                continue
            elif not msg.error():
                print('Received message: {0}'.format(msg.value()))
                isStopped = command_direct(msg.value().decode('utf-8'), enA, enB, in1, in2, in3, in4)
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
    handle_messages(c,  enA, enB, in1, in2, in3, in4)