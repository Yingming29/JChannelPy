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
        self.uuid = uuid.uuid4()
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
        self.name = name_str
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
        self.grpcStub =  jchannel_pb2_grpc.JChannelsServiceStub(self.channel)

    def judge_request(self, input_string):
        dt = datetime.datetime.now()
        timestamp = dt.strftime("%H:%M:%S")
        if input_string.startswith("TO"):
            splited_string = input_string.split("", 2)

    def start_stub(self):
        None