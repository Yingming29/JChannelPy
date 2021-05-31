import threading


class Thread_a(threading.Thread):
    def __init__(self, shared_generator):
        threading.Thread.__init__(self)
        self.g = shared_generator

    def run(self):
        self.g.send("one send")

class Thread_a(threading.Thread):
    def __init__(self, shared_generator):
        threading.Thread.__init__(self)
        self.g = shared_generator

    def run(self):
        print(self.g)