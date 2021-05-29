from concurrent import futures
import grpc
import jchannel_pb2_grpc
import jchannel_pb2


def make_message(input_string):
    req = jchannel_pb2.Request(
        messageRequest=jchannel_pb2.MessageReq(
            source="uuid",
            content=input_string
        )
    )

    print("Generated message")
    print(req)
    return req

def run():

    with grpc.insecure_channel("127.0.0.1:50051") as channel:
        stub = jchannel_pb2_grpc.JChannelsServiceStub(channel)

        input_string = input("content input:")

        responses = stub.connect(make_message(input_string))

        for response in responses:
            print("Receive: " + response)


if __name__ == '__main__':
    run()