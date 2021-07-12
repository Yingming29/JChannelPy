import datetime
import threading

import grpc

from JChannelClient import testbuf_pb2_grpc, testbuf_pb2, jchannel_pb2

'''
dt = datetime.datetime.now()
timestamp = dt.strftime("%H:%M:%S")
print(timestamp)

input_string = "TO asdas"
if input_string.startswith("TO"):
    print(1)

def yield_test():
    print("there")
    messages = []
    print("here")
    for msg in messages:
        print("one iteration")
        yield msg

a = yield_test()






class yrange:
    def __init__(self, num):
        self.i = 0
        self.n = num

    def add(self, add_num):
        self.n = self.n + add_num

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < self.n:
            i = self.i
            self.i += 1
            return i

        else:
            print("over " + str(self.n))

a =yrange(3)
'''

'''
a = yrange(3)
# list() is the while loop for running the __next__
print(a)
print(a.__next__())
print(a.__next__())
print(a.__next__())
if a.__next__() is None:
    print("none")
print(a.__next__())
print(a.__next__())
a.add(2)
print(a.__next__())
print(a.__next__())
print(a.__next__())

l = []
l.append("a")
l.append("b")
l.append("c")
'''


class input_thread(threading.Thread):
    def __init__(self, shared_list, name):
        threading.Thread.__init__(self)
        self.msg_list = shared_list
        self.name = name
        self.input_lock = threading.RLock

    def run(self):
        print("Start input_thread.")
        while 1:
            input_string = input(">")
            self.input_lock.acquire()
            print(input_string)
            try:
                self.msg_list.append(input_string)
                print("add")
            finally:
                self.input_lock.release()


class check_thread(threading.Thread):
    def __init__(self, shared_list, name, generator):
        threading.Thread.__init__(self)
        self.msg_list = shared_list
        self.name = name
        self.check_lock = threading.RLock()
        self.send_generator = generator

    def run(self):
        print("Check thread:" + threading.currentThread().getName())
        print("Start check_thread.")

        while 1:
            if len(self.msg_list) > 0:
                print("Size > 0 ")
                msg = None
                self.check_lock.acquire()
                try:
                    msg = self.msg_list[0]
                    del self.msg_list[0]
                    print("remove " + msg)
                finally:
                    self.check_lock.release()
                print("call generator for msg:" + msg)
                self.send_generator.send(msg)
                '''try:
                    self.send_generator.send(msg)
                except StopIteration:
                    pass'''
            else:
                pass


class grpc_thread(threading.Thread):
    def __init__(self, generator):
        threading.Thread.__init__(self)
        self.grpc_lock = threading.RLock()
        self.get_input_generator = generator

    def try_ask(self, stub):
        req = testbuf_pb2.ReqAsk(content="ask request of client")
        resp = stub.ask(req)
        if resp.content:
            print(resp)
        else:
            print("none response")

    def run(self):
        def read_response(Response):
            print(Response.content)
        with grpc.insecure_channel("127.0.0.1:50051") as channel:
            stub = testbuf_pb2_grpc.TestStub(channel)
            print("run: " + threading.currentThread().getName())
            print("Try ask")
            self.try_ask(stub)
            print("Try stream")
            self.get_input_generator.send("1")
            response_stream = stub.start(self.get_input_generator)
            thread_read = read_thread(response_stream)
            thread_read.daemon = True
            thread_read.start()



class read_thread(threading.Thread):
    def __init__(self, response_stream):
        threading.Thread.__init__(self)
        self.stream_rep = response_stream

    def run(self):

        while 1:
            try:
                print('Receive message:' + next(self.stream_rep).content)
                print("read_incoming(): " + threading.currentThread().getName())
            except :
                pass




def generator_msg():
    request_msg = "None"
    while 1:
        request_msg = yield request_msg
        print("generate request: " + request_msg)

def run():
    shared_list = ["start"]
    main_lock = threading.RLock()
    a = generator_msg()
    a.send(None)
    print("main: " + threading.currentThread().getName())
    thread = check_thread(shared_list, "check thread name", a)
    thread.setDaemon(True)
    thread.start()
    print("after start the check thread: " + threading.currentThread().getName())

    thread2 = grpc_thread(a)
    thread2.setDaemon(True)
    thread2.start()

    print("after start the grpc thread: " + threading.currentThread().getName())
    while 1:
        input_string = input(">")

        main_lock.acquire()
        try:
            shared_list.append(input_string)
            print("add")
        finally:
            main_lock.release()

def test_message():
    req = jchannel_pb2.Request(
        pyReqMsg=jchannel_pb2.ReqMsgForPyClient(
            conReqPy=jchannel_pb2.ConnectReqPy(
                reconnect=False,
                logical_name=""
            )
        )
    )
    print(req)


test_message()