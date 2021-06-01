
import jchannel_pb2
import jchannel_pb2_grpc
import grpc

channel = grpc.insecure_channel('127.0.0.1:50052')

stub = jchannel_pb2_grpc.JChannelsServiceStub(channel)
message = jchannel_pb2.ReqAsk(source="source test")
response = stub.ask(message)
if response.survival:
    print(response.survival)
'''with grpc.insecure_channel('127.0.0.1:50052') as channel:
    stub = jchannel_pb2_grpc.JChannelsServiceStub(channel)
    message = jchannel_pb2.ReqAsk(source="source test")
    response = stub.ask(message)
    if response.survival:
        print(response.survival)'''

'''def try_ask(stub):
    req = jchannel_pb2.ReqAsk(source="ask request of client")

    resp = stub.ask(req)
    if resp.survival:
        print(resp)
    else:
        print("none response")


with grpc.insecure_channel('127.0.0.1:50052') as channel:
    stub = jchannel_pb2_grpc.JChannelsServiceStub(channel)
    try_ask(stub)'''