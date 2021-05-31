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


def generator_test():
    # give it a connect request
    result = "None1"
    while 1:
        print(threading.currentThread().getName())
        print("One time:" + str(result))
        next_result = yield result
        result = next_result


a = generator_test()
print(a)
# "main" +
print("main " + a.__next__())
print("main " + str(a.__next__()))
print("main " + str(a.__next__()))
print("main " + str(a.__next__()))
print("Main:  " + str(a.send(1)))

