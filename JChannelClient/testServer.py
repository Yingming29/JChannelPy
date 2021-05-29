from concurrent import futures
import grpc
import jchannel_pb2_grpc


class JChannelsServiceService(jchannel_pb2_grpc.JChannelsServiceServicer):
    def connect(self, request_iterator, context):
        for message in request_iterator:
            yield message


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    jchannel_pb2_grpc.add_JChannelsServiceServicer_to_server(JChannelsServiceService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
