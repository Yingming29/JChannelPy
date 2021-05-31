import random
import threading
import time
from concurrent import futures
from grpc import aio
import testbuf_pb2_grpc
import testbuf_pb2
import asyncio
import grpc




def try_stream(stub):
    responses = stub.start(generate_messages())
    for response in responses:
        print("Receive message: " + response.content)


def generate_messages():
    message = testbuf_pb2.Request(content="stream request of client")
    messages = [message, message, message, message, message, message, message, message, message, message]
    for msg in messages:
        print("generate a message in stream: " + msg)
        yield msg
        time.sleep(random.uniform(1, 5))


def stream():
    while 1:
        yield testbuf_pb2.Request(content=input(">"))
        print("stream(): " + threading.currentThread().getName())



def read_incoming(input_stream):
    while 1:
        print('Receive message:' + next(input_stream).content)
        print("read_incoming(): " + threading.currentThread().getName())


'''
def run():
    with grpc.insecure_channel("127.0.0.1:50051") as channel:
        stub = testbuf_pb2_grpc.TestStub(channel)
        print("run: " + threading.currentThread().getName())
        print("Try ask")
        try_ask(stub)
        print("Try stream")
        # try_stream(stub)
        
        inputstream = stub.start(stream())
        thread = threading.Thread(target=read_incoming(inputstream))
        thread.daemon = True
        thread.start()

        while 1:
            time.sleep(2)
'''

shared_list = []


def input_loop():
    while 1:
        input_string = input(">")
        print("Input loop, " + input_string)
        print("input: " + threading.currentThread().getName())
        shared_list.append(input_string)


def try_ask(stub):
    req = testbuf_pb2.ReqAsk(content="ask request of client")

    resp = stub.ask(req)
    if resp.content:
        print(resp)
    else:
        print("none response")
def run():

    try:
        with grpc.insecure_channel("127.0.0.1:50051") as channel:
            stub = testbuf_pb2_grpc.TestStub(channel)
            print("run: " + threading.currentThread().getName())
            print("Try ask")
            try_ask(stub)
            print("Try stream")
            # try_stream(stub)
            try:
                inputstream = stub.start(stream())
                thread2 = threading.Thread(target=read_incoming(inputstream))
                thread2.daemon = True
                thread2.start()
            except:
                print("except2")
    except:
        print("except")

    print("here")


if __name__ == '__main__':
    run()
