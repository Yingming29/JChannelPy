import sys
import threading
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
                self.msgList.append(input_string);
            finally:
                self.lock.release()

            if input_string == "disconnect":
                break;

    def start_client(self):
        # set name and cluster
        self.set_name()
        self.set_cluster()
        # start the client stub
        self.start_stub()
        self.clientStub.startStub()
        # start input loop
        self.input_loop()
        print("End.")
        sys.exit(0)


class ClientStub:
    def __init__(self, client):
        self.client = client
        self.stubLock = threading.RLock()
        self.serverList = []
        self.channel = grpc.insecure_channel(client.address)
        self.grpcStub = jchannel_pb2_grpc.JChannelsServiceStub(self.channel)

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

    def judgeResponse(self, response):
        field = response.WhichOneof("oneType")

        if field == "connectResponse":
            print("Get Connect() response.")
        elif field == "messageResponse":
            self.print_msg(response.messageResponse)
        elif field == "updateResponse":
            self.update(response.updateResponse.addresses)
        elif field == "disconnectResponse":
            self.stubLock.acquire()
            try:
                self.client.down = False
            finally:
                self.stubLock.release()
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

    def print_msg(self, message_rep):
        print("[JChannel] " + message_rep.jchannel_address + ":" + str(message_rep.content))

    def update(self, addresses):
        add_list = addresses.split(" ")
        self.stubLock.acquire()
        try:
            self.serverList.clear()
            self.serverList.extend()
        finally:
            self.stubLock.release()

