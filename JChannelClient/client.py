import random
import sys
import threading
import time
import uuid

import grpc
import jchannel_pb2
import jchannel_pb2_grpc
from threading import Condition
from concurrent import futures
import datetime


class Client:

    def __init__(self, grpc_address):
        self.address = grpc_address
        self.logical_name = None
        self.lock = threading.RLock()
        # shared part
        self.msgList = []
        self.cluster = None
        self.clientStub = None
        self.clientMembers = []
        self.serverMembers = []
        self.condition = threading.Condition()
        self.isWork = False
        self.down = False

    def start_stub(self):
        self.clientStub = ClientStub(self)

    def input_loop(self):
        while True:
            print("Input")
            print(">")
            input_string = input()
            if self.down is False:
                break
            # print("input loop: " + threading.currentThread().getName())
            if self.isWork is False:
                print("The connection does not work. Store the message.")
            else:
                self.lock.acquire()
                try:
                    self.msgList.append(input_string)
                finally:
                    self.lock.release()

    def start_client(self):
        # start the client stub
        self.start_stub()
        # add the startStub()
        self.clientStub.startStub()
        # start input loop
        self.input_loop()
        print("End.")
        sys.exit(0)


# It is the iterator used for the grpc bidirectional streaming.
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
                        # print("iterator: " + threading.currentThread().getName())
                        # print("Get message in generator: " + str(self.iteration_msg[self.current_index - 1]))
                        # message = jchannel_pb2.Request(content=self.iteration_msg[self.current_index - 1])
                        return self.iteration_msg[self.current_index - 1]
                    else:
                        pass
                        # always check the shared_list
                        # length_msg = len(self.iteration_msg)
                        # print(str(self.current_index) + "  "  + str(length_msg))
        except StopIteration:
            pass


class ClientStub:
    def __init__(self, client):
        self.client = client
        self.condition = client.condition
        self.stubLock = threading.RLock()
        self.serverList = []
        self.channel = grpc.insecure_channel(self.client.address)
        self.grpcStub1 = jchannel_pb2_grpc.JChannelsServiceStub(self.channel)
        self.grpcStub2 = jchannel_pb2_grpc.JChannelsServiceStub(self.channel)

    def print_msg(self, message_rep):
        print("[py_client] " + message_rep.source + ":" + str(message_rep.contentStr))

    def update(self, addresses):
        add_list = addresses.split(" ")
        self.stubLock.acquire()
        try:
            self.serverList.clear()
            self.serverList.extend(add_list)
            # print("update: " + threading.currentThread().getName())
            print("[Client Stub] Update addresses of servers: " + str(self.serverList))
        finally:
            self.stubLock.release()

    def startStub(self):
        control_thread = Control_thread(self.client)
        control_thread.setDaemon(True)
        control_thread.start()

    # add the shread_generator for bi-directional streaming and check thread
    def start_grpc(self, shared_generator):  # start the bi-directional streaming rpc
        stream = self.grpcStub1.connect(shared_generator)
        return stream

    def reconnect(self):
        count = 0
        size = len(self.serverList)

        if len(self.serverList) == 0:
            print("The available server list is null. Cannot select new address of node.")
            self.stubLock.acquire()
            try:
                self.client.down = False
            finally:
                self.stubLock.release()
            return False
        while 1:
            count += 1
            # print("reconnect: " + threading.currentThread().getName())
            random_select = 0
            if not size == 1:
                random_select = random.randint(0, size - 1)

            address = self.serverList[random_select]
            print("[Reconnection]: Random selected server for reconnection:" + address)
            self.channel = grpc.insecure_channel(address)
            self.grpcStub1 = jchannel_pb2_grpc.JChannelsServiceStub(self.channel)
            self.grpcStub2 = jchannel_pb2_grpc.JChannelsServiceStub(self.channel)
            bool_result = self.try_one_connect()
            time.sleep(1)
            if bool_result is True:
                self.client.address = address
                print("[Reconnection]: Reconnect successfully to server-" + self.client.address)
                return True
            if count > 10:
                break
        print("[Reconnection]: Reconnect many times, end.")
        return False

    def try_one_connect(self):

        ask_req = jchannel_pb2.ReqAsk(
            source=self.client.logical_name
        )

        try:
            res = self.grpcStub2.ask(ask_req, timeout=2000)
            print("[Client Stub] try one reconnection, the result: " + str(res))
            return True
        except:
            print("[Reconnection]: The try connection is also not available.")
            return False


class Control_thread(threading.Thread):
    def __init__(self, shared_client):
        threading.Thread.__init__(self)
        self.iter_to_add = None
        self.client = shared_client
        self.control_lock = threading.RLock()
        self.condition = self.client.condition

    def judge_request(self, input_string):
        # generate unicast messge
        if input_string.startswith("To"):
            splited_string = input_string.split(" ", 2)
            req = jchannel_pb2.Request(
                pyReqMsg=jchannel_pb2.ReqMsgForPyClient(
                    msgReqPy=jchannel_pb2.MessageReqPy(
                        source=self.client.logical_name,
                        dest=splited_string[1],
                        contentStr=splited_string[2]
                    )
                )
            )
            return req
        elif input_string == "getState":
            req = jchannel_pb2.Request(
                pyReqMsg=jchannel_pb2.ReqMsgForPyClient(
                    getStateReqPy=jchannel_pb2.StateReqPy(
                        logical_name=self.client.logical_name
                    )
                )
            )
            return req
        elif input_string == "disconnect":
            # disconnect request
            req = jchannel_pb2.Request(
                pyReqMsg=jchannel_pb2.ReqMsgForPyClient(
                    disconReqPy=jchannel_pb2.DisconnectReqPy(
                        logical_name=self.client.logical_name
                    )
                )
            )
            return req
        else:
            # common message request for broadcast
            req = jchannel_pb2.Request(
                pyReqMsg=jchannel_pb2.ReqMsgForPyClient(
                    msgReqPy=jchannel_pb2.MessageReqPy(
                        source=self.client.logical_name,
                        dest="",
                        contentStr=input_string
                    )
                )
            )
            return req

    def run(self):
        # print("Start the control thread.")
        # print("control thread: " + threading.currentThread().getName())
        '''
            4.1
                1. create the iteratior with the first data, connectReq
                2. create the grpc bi-directional stream rpc with the iterator
            4.2 getState() of JChannel, append a getState() request to iterator
            4.3 start the check_loop
            4.4 reconnect part
            4.5 if over the maximum reconnection time, end the client.
            '''
        while 1:
            connect_request = self.generate_connect_request()
            messages = [connect_request]
            self.iter_to_add = test_iterator(messages)
            # create the bi-directional streaming rpc call given the connect request
            responses = None
            try:
                responses = self.client.clientStub.start_grpc(self.iter_to_add)
                # start the read response thread
                read_thread = Read_response(responses, self.client.clientStub, self.client)
                read_thread.setDaemon(True)
                read_thread.start()
            except:
                # print("= False")
                self.control_lock.acquire()
                try:
                    self.client.isWork = False
                finally:
                    self.control_lock.release()
                print("[Client Stub]: onError() of gRPC connection, the client needs to reconnect to the next server.")
            with self.condition:
                #print("wait")
                self.condition.wait()
                #print("break wait")
                #print(str(self.client.isWork))
                #print(str(self.client.down))
            # 4.3
            self.check_loop()
            # 4.4
            reconnect_result = self.client.clientStub.reconnect()
            # 4.5
            if reconnect_result is False:
                self.client.down = False
                # print("End in control thread.")
                break

    def generate_connect_request(self):
        if self.client.down is False and self.client.isWork is False:
            connect_req = jchannel_pb2.Request(
                pyReqMsg=jchannel_pb2.ReqMsgForPyClient(
                    conReqPy=jchannel_pb2.ConnectReqPy(
                        reconnect=False,
                        logical_name=""
                    )
                )
            )
        else:
            connect_req = jchannel_pb2.Request(
                pyReqMsg=jchannel_pb2.ReqMsgForPyClient(
                    conReqPy=jchannel_pb2.ConnectReqPy(
                        reconnect=True,
                        logical_name=self.client.logical_name
                    )
                )
            )
        print("[py_client] The client calls connect() request to a server." + str(connect_req))
        return connect_req

    def check_loop(self):

        while 1:

            if len(self.client.msgList) > 0 and self.client.isWork is True:
                line = self.client.msgList[0]
                msg_request = self.judge_request(line)

                '''
                    1. Add the new request to the generator
                    2. Remove the input string from the shared list
                    '''
                self.control_lock.acquire()
                try:
                    del self.client.msgList[0]
                    # print("add a generated message to iterator")
                    self.iter_to_add.__add__(msg_request)
                finally:
                    self.control_lock.release()
            '''self.control_lock.acquire()
            try:
                print("--------")
                print(str(self.client.isWork))
                print(str(self.client.down))
                print("--------")
            finally:
                self.control_lock.release()'''

            if self.client.isWork is False:
                break
            elif self.client.down is False:
                break
            else:
                continue


class Read_response(threading.Thread):
    def __init__(self, stream, stub, shared_client):
        threading.Thread.__init__(self)
        self.read_stream = stream
        self.client_stub = stub
        self.lock = threading.RLock()
        self.client = shared_client
        self.condition = self.client.condition

    def run(self):

        try:
            for response in self.read_stream:
                #print("Read print response:" + str(response))
                py_response = response.pyRepMsg
                self.judgeResponse(py_response)
        except:
            # print("readResponse make isWork = false")
            self.lock.acquire()
            try:
                self.client.isWork = False
            finally:
                self.lock.release()

            # print(" isWork in the read response: " + str(self.client.isWork))
            # print("error of read thread")

    def judgeResponse(self, response):
        # the response is the Message type, ReqMsgForPyClient
        field = response.WhichOneof("oneType")

        if field == "conRepPy":
            print("Get connect() response from server, the generate address string is:"
                  + response.conRepPy.logical_name)
            self.lock.acquire()
            try:
                self.client.logical_name = response.conRepPy.logical_name
                self.client.down = True
                self.client.isWork = True
            finally:
                self.lock.release()

            with self.condition:
                #print("notify")
                self.condition.notify()
        elif field == "msgRepPy":
            self.client_stub.print_msg(response.msgRepPy)
        elif field == "updateAddPy":
            self.client_stub.update(response.updateAddPy.addresses)
        elif field == "disconRepPy":
            self.lock.acquire()
            try:
                self.client_stub.client.down = False
            finally:
                self.lock.release()
        elif field == "clientViewPy":
            view = response.clientViewPy
            self.client.clientMembers.clear()
            if view.size > 0:
                for i in view.members:
                    self.client.clientMembers.append(i)
            print("** Client View:[" + str(view.coordinator) + "|" + str(view.num) + "] ("
                  + str(view.size) + ")" + str(self.client.clientMembers))
        elif field == "serverViewPy":
            view = response.serverViewPy
            self.client.serverMembers.clear()
            if view.size > 0:
                for i in view.members:
                    self.client.serverMembers.append(i)
            print("** Server View:[" + str(view.coordinator) + "|" + str(view.num) + "] ("
                  + str(view.size) + ")" + str(self.client.serverMembers))
        elif field == "stateRepPy":
            state_rep = response.stateRepPy
            print(str(state_rep.size) + " messages in the chat history.")
            if state_rep.size > 0:
                for i in state_rep.line:
                    print(i)

if __name__ == "__main__":
    new_client = Client(sys.argv[1])
    print("Start python client, and connect to grpc server: " + sys.argv[1])
    new_client.start_client()
