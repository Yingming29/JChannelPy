from concurrent import futures
import grpc
import testbuf_pb2_grpc
import testbuf_pb2


class TestService(testbuf_pb2_grpc.TestServicer):

    print("Start service successfully")

    def ask(self, request_iterator, context):
        print("ask")

        return testbuf_pb2.RepAsk(content="hello, i am server (ask)")

    def start(self, request_iterator, context):
        print("start")

        for each in request_iterator:
            if each.content == "stream request of client":
                print("same")
                yield testbuf_pb2.Response(content="same")
            else:
                print("not same")
                yield testbuf_pb2.Response(content="not same")



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    testbuf_pb2_grpc.add_TestServicer_to_server(TestService(), server)
    server.add_insecure_port('127.0.0.1:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
