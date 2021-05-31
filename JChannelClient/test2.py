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
print(empty_list)



def generator_test(shared):
    result = None
    while 1:
        yield result
        if len(shared) > 0 :
            result = shared[0]
            del shared[0]
        else:
            
while 1:
    print()
