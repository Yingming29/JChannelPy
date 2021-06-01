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
    for i in input_stream:
        '''print('Receive message:' + next(input_stream).content)
        print("read_incoming(): " + threading.currentThread().getName())'''
        print('Receive message:' + i.content)
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
    with grpc.insecure_channel("127.0.0.1:50051") as channel:
        stub = testbuf_pb2_grpc.TestStub(channel)
        print("run: " + threading.currentThread().getName())
        print("Try ask")
        try_ask(stub)
        print("Try stream")
        # try_stream(stub)
        message = testbuf_pb2.Request(content="connect request")
        # messages = [message, message, message, message, message, message, message, message, message, message]
        # inputstream = stub.start(stream())
        messages = [message]
        iteration_formsg = test_iterator(messages)
        shared = Input_thread(iteration_formsg)
        # shared.setDaemon(True)
        shared.start()
        inputstream = stub.start(iteration_formsg)
        print(inputstream)
        thread2 = threading.Thread(target=read_incoming(inputstream))
        # thread2.daemon = True
        thread2.start()

    print("here")


class Input_thread(threading.Thread):
    def __init__(self, shared_iterator):
        threading.Thread.__init__(self)
        self.iter_toadd = shared_iterator
        self.input_lock = threading.RLock()

    def run(self):
        print("Start input_thread.")
        while 1:
            input_string = input(">")
            self.input_lock.acquire()
            print(input_string)
            try:
                self.iter_toadd.__add__(input_string)
                print("add")
            finally:
                self.input_lock.release()


class test_iterator:
    def __init__(self, l):
        self.iteration_msg = l
        self.current_index = 0

    def __iter__(self):
        return self

    def __add__(self, other):
        self.iteration_msg.append(other)

    def __next__(self):
        try:
            if self.current_index < len(self.iteration_msg):
                self.current_index += 1
                return self.iteration_msg[self.current_index - 1]
            else:
                while 1:
                    if self.current_index < len(self.iteration_msg):
                        self.current_index += 1
                        print("Get message and send: " + str(self.iteration_msg[self.current_index - 1]))
                        message = testbuf_pb2.Request(content=self.iteration_msg[self.current_index - 1])
                        return message
                    else:
                        pass
                        # always check the shared_list
                        # length_msg = len(self.iteration_msg)
                        # print(str(self.current_index) + "  "  + str(length_msg))
        except StopIteration:
            pass


a = test_iterator([1, 2, 3])
if __name__ == '__main__':
    run()
