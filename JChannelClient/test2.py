import threading

import grpc
import jchannel_pb2
import jchannel_pb2_grpc

input_string = "TO JC HELLO"
splited_string = input_string.split(" ", 2)

msg = jchannel_pb2.Request(
    messageRequest=jchannel_pb2.MessageReq(
        source="uuid",
        jchannel_address="self.client.jchannel_address",
        cluster="self.client.cluster",
        content=splited_string[2],
        timestamp="time_str",
        destination=splited_string[1]
    ))
msg2 = jchannel_pb2.Response(
    updateResponse=jchannel_pb2.UpdateRep(
        addresses="addresses11111111"
    ))

field = msg2.WhichOneof("oneType")
print(field)


def print_msg(msg1):
    print("[JChannel] " + msg1.jchannel_address + ":" + str(msg1.content))


sub_msg = msg.messageRequest
print_msg(sub_msg)


def yield_test():
    print("there")
    messages = [1, 2, 3, 4, 5]
    print("here")
    for msg in messages:
        print("one iteration")
        yield msg


a = yield_test()
print(a.__next__())
print(a.__next__())
print(a.__next__())
print(a.__next__())

"""
message StateRep{
  int32 size = 1;
  repeated string oneOfHistory = 2;
}"""

mes = jchannel_pb2.Response(
    stateRep=jchannel_pb2.StateRep(
        size=2,
        oneOfHistory=["one chat", "two chat"]
    )
)
if mes.stateRep.size > 0:
    print(">")
for i in mes.stateRep.oneOfHistory:
    print(i)

new_list = [1, 2, 3]
empty_list = []
empty_list.extend(new_list)


# print(empty_list)


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
                        return self.iteration_msg[self.current_index - 1]
                    else:
                        pass
                        # always check the shared_list
                        # length_msg = len(self.iteration_msg)
                        # print(str(self.current_index) + "  "  + str(length_msg))
        except StopIteration:
            pass


class input_thread(threading.Thread):
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


a = test_iterator([1, 2, 3])

thread_input = input_thread(a)
thread_input.setDaemon(True)
thread_input.start()
while 1:
    print(a.__next__())
# a.__add__("new")

'''new_lock = threading.RLock()
new_lock.acquire()
try:
    a.__add__("new_value")
finally:
    new_lock.release()
print(a.__next__())
print(a.__next__())'''
