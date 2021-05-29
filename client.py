import threading
import uuid
import grpc

from concurrent import futures

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
        ''' def start_stub(self):
        self.clientStub = ClientStub(self)'''


    def input_loop(self):
        while True:
            print("Input cluster.")
            print(">")
            input_string = input()
    '''
        class ClientStub:

        def __init__(self, client):
            self.client = Client
    '''


