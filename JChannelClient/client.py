import random
import sys
import threading
import time
import uuid

import grpc
import jchannel_pb2
import jchannel_pb2_grpc

from concurrent import futures
import datetime


class Client:

    def __init__(self, address):
        self.address = address
        self.name = None
        self.jchannel_address = None
        self.uuid = str(uuid.uuid4())
        self.lock = threading.RLock()
        # shared part
        self.isWork = True
        self.msgList = []
        self.cluster = None
        self.clientStub = None
        self.down = True

    # input and set the name of the client
    def set_name(self):
        print("Input Name.")
        print(">")
        name_str = input()
        name_str.strip()
        self.name = str(name_str)
        self.jchannel_address = "JChannel-" + self.name
        return name_str

    def set_cluster(self):
        print("Input cluster.")
        print(">")
        cluster_str = input()
        cluster_str.strip()
        self.cluster = cluster_str
        return

    def start_stub(self):
        self.clientStub = ClientStub(self)

    def input_loop(self):
        while True:
            print("Input cluster.")
            print(">")
            input_string = input()

            if not self.isWork:
                print("The connection does not work. Store the message.")
            self.lock.acquire()
            try:
                self.msgList.append(input_string)
            finally:
                self.lock.release()

            if input_string == "disconnect":
                break

    def start_client(self):
        # set name and cluster
        self.set_name()
        self.set_cluster()
        # start the client stub
        self.start_stub()
        # add the startStub()
        self.clientStub.startStub()
        # start input loop
        self.input_loop()
        print("End.")
        sys.exit(0)


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
                        print("Get message in generator: " + str(self.iteration_msg[self.current_index - 1]))
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
        self.stubLock = threading.RLock()
        self.serverList = []
        self.channel = grpc.insecure_channel(self.client.address)
        self.grpcStub1 = jchannel_pb2_grpc.JChannelsServiceStub(self.channel)
        self.grpcStub2 = jchannel_pb2_grpc.JChannelsServiceStub(self.channel)

    def print_msg(self, message_rep):
        print("[JChannel] " + message_rep.jchannel_address + ":" + str(message_rep.content))

    def update(self, addresses):
        add_list = addresses.split(" ")
        self.stubLock.acquire()
        try:
            self.serverList.clear()
            self.serverList.extend(add_list)
            print("Update addresses of servers: " + str(self.serverList))
        finally:
            self.stubLock.release()

    def startStub(self):
        control_thread = Control_thread(self.client.msgList, self.client.isWork, self.client)
        control_thread.setDaemon(True)
        control_thread.start()

    # add the shread_generator for bi-directional streaming and check thread
    def start_grpc(self, shared_generator):  # start the bi-directional streaming rpc
        stream = self.grpcStub1.connect(shared_generator)
        return stream

    def reconnect(self):
        count = 0
        size = len(self.serverList)
        while 1:
            count += 1
            random_select = random.randint(0, size)
            address = self.serverList[random_select]
            print("[Reconnection]: Random selected server for reconnection:" + address)
            self.channel = grpc.insecure_channel(address)
            self.grpcStub1 = jchannel_pb2_grpc.JChannelsServiceStub(self.channel)
            self.grpcStub2 = jchannel_pb2_grpc.JChannelsServiceStub(self.channel)
            bool_result = self.try_one_connect()
            if bool_result is True:
                self.client.address = address
                print("[Reconnection]: Reconnect successfully to server-" + self.client.address)
                return True
            if count > 9999:
                break
        print("[Reconnection]: Reconnect many times, end.")
        return False

    def try_one_connect(self):
        time.sleep(5000)
        ask_req = jchannel_pb2.ReqAsk(
            source=self.client.uuid
        )
        try:
            response = self.grpcStub2.ask(ask_req)
            for i in response:
                print(i)
            return True
        except:
            print("[Reconnection]: The new try connection is also not available.")
            return False


class Control_thread(threading.Thread):
    def __init__(self, shared_list, shared_isWork, shared_client):
        threading.Thread.__init__(self)
        self.iter_to_add = None
        self.checked_msg_list = shared_list
        self.checked_isWork = shared_isWork
        self.client = shared_client
        self.control_lock = threading.RLock()

    def judge_request(self, input_string):
        dt = datetime.datetime.now()
        time_str = dt.strftime("%H:%M:%S")
        # generate unicast messge
        if input_string.startswith("TO"):
            splited_string = input_string.split(" ", 2)

            req = jchannel_pb2.Request(
                messageRequest=jchannel_pb2.MessageReq(
                    source=self.client.uuid,
                    jchannel_address=self.client.jchannel_address,
                    cluster=self.client.cluster,
                    content=splited_string[2],
                    timestamp=time_str,
                    destination=splited_string[1]
                )
            )
            return req
        elif input_string == "disconnect":
            # disconnect request
            req = jchannel_pb2.Request(
                disconnectRequest=jchannel_pb2.DisconnectReq(
                    source=self.client.uuid,
                    jchannel_address=self.client.jchannel_address,
                    cluster=self.client.cluster,
                    timestamp=time_str
                )
            )
            return req
        else:
            # common message request for broadcast
            req = jchannel_pb2.Request(
                messageRequest=jchannel_pb2.MessageReq(
                    source=self.client.uuid,
                    jchannel_address=self.client.jchannel_address,
                    cluster=self.client.cluster,
                    content=input_string,
                    timestamp=time_str
                )
            )
            return req

    def run(self):
        print("Start the control thread.")
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
            except:
                self.client.clientStub.channel.close()
                print("[gRPC]: onError() of gRPC connection, the client needs to reconnect to the next server.")
                self.control_lock.acquire()
                try:
                    self.client.isWork = False
                finally:
                    self.control_lock.release()

            # start the read response thread
            read_thread = Read_response(responses, self.client.clientStub)
            read_thread.setDaemon(True)
            read_thread.start()
            # 4.3
            self.check_loop()
            # 4.4
            reconnect_result = self.client.clientStub.reconnect()
            # 4.5
            if reconnect_result is False:
                print("End in control thread.")
                break

    def getState(self):
        state_req = jchannel_pb2.Request(
            stateReq=jchannel_pb2.StateReq(
                source=self.client.uuid,
                cluster=self.client.cluster,
                jchannel_address=self.client.jchannel_address,
            )
        )
        self.control_lock.acquire()
        try:
            del self.checked_msg_list[0]
            print("add a generated getState message to iterator")
            self.iter_to_add.__add__(state_req)
        finally:
            self.control_lock.release()

    def generate_connect_request(self):
        dt = datetime.datetime.now()
        time_str = dt.strftime("%H:%M:%S")
        connect_req = jchannel_pb2.Request(
            connectRequest=jchannel_pb2.ConnectReq(
                source=self.client.uuid,
                jchannel_address=self.client.jchannel_address,
                cluster=self.client.cluster,
                timestamp=time_str
            )
        )
        print(self.client.name + " calls connect() request to Jgroups cluster: " + self.client.cluster)
        lock = threading.RLock()
        lock.acquire()
        try:
            self.client.isWork = True
        finally:
            lock.release()
        return connect_req

    def check_loop(self):
        while 1:
            if len(self.checked_msg_list) > 0 and self.checked_isWork is True:
                line = self.checked_msg_list[0]
                msg_request = self.judge_request(line)
                '''
                    1. Add the new request to the generator
                    2. Remove the input string from the shared list
                    '''
                self.control_lock.acquire()
                try:
                    del self.checked_msg_list[0]
                    print("add a generated message to iterator")
                    self.iter_to_add.__add__(msg_request)
                finally:
                    self.control_lock.release()

            elif self.checked_isWork is False:
                break
            elif self.client.down is False:
                sys.exit(0)


class Read_response(threading.Thread):
    def __init__(self, stream, stub):
        threading.Thread.__init__(self)
        self.read_stream = stream
        self.client_stub = stub
        self.lock = threading.RLock()

    def run(self):
        try:
            for i in self.read_stream:
                print("read_incoming(): " + threading.currentThread().getName())
                self.judgeResponse(i)
        except:
            raise ValueError("error of read thread")

    def judgeResponse(self, response):
        field = response.WhichOneof("oneType")

        if field == "connectResponse":
            print("Get Connect() response.")
        elif field == "messageResponse":
            self.client_stub.print_msg(response.messageResponse)
        elif field == "updateResponse":
            self.client_stub.update(response.updateResponse.addresses)
        elif field == "disconnectResponse":
            self.lock.acquire()
            try:
                self.client_stub.client.down = False
            finally:
                self.lock.release()
        elif field == "viewResponse":
            view = response.viewResponse
            print("** View:[" + str(view.creator) + "|" + str(view.viewNum) + "] ("
                  + str(view.size) + ")" + view.jchannel_addresses)
        elif field == "stateRep":
            state_rep = response.stateRep
            print(str(state_rep.size) + " messages in the chat history.")
            if state_rep.size > 0:
                for i in state_rep.oneOfHistory:
                    print(i)


if __name__ == "__main__":
    new_client = Client(sys.argv[1])
    print("Start client: Will connect to gRPC server: " + sys.argv[1])
    new_client.start_client()

