import random
import threading
import time
from concurrent import futures
import grpc
import testbuf_pb2_grpc
import testbuf_pb2

def try_ask(stub):
    req = testbuf_pb2.ReqAsk(content="ask request of client")
    resp = stub.ask(req)
    if resp.content:
        print(resp)
    else:
        print("none response")

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

def read_incoming(input_stream):
    while 1:
        print('Receive message:' + next(input_stream).content)

def run():
    with grpc.insecure_channel("127.0.0.1:50051") as channel:
        stub = testbuf_pb2_grpc.TestStub(channel)
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







if __name__ == '__main__':
    run()
