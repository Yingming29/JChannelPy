import datetime
import threading

'''
dt = datetime.datetime.now()
timestamp = dt.strftime("%H:%M:%S")
print(timestamp)

input_string = "TO asdas"
if input_string.startswith("TO"):
    print(1)

'''

def yield_test():
    print("there")
    messages = []
    print("here")
    for msg in messages:
        print("one iteration")
        yield msg

a = yield_test()






class yrange:
    def __init__(self, num):
        self.i = 0
        self.n = num

    def add(self, add_num):
        self.n = self.n + add_num

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < self.n:
            i = self.i
            self.i += 1
            return i

        else:
            print("over " + str(self.n))

a =yrange(3)
'''
a = yrange(3)
# list() is the while loop for running the __next__
print(a)
print(a.__next__())
print(a.__next__())
print(a.__next__())
if a.__next__() is None:
    print("none")
print(a.__next__())
print(a.__next__())
a.add(2)
print(a.__next__())
print(a.__next__())
print(a.__next__())

l = []
l.append("a")
l.append("b")
l.append("c")
'''
def check_loop(checked_list):

    while 1:
        if len(checked_list) == 0:
            print("None")
        elif len(checked_list) > 0:
            print("Size > 0 ")
            msg = checked_list[0]
            checked_list.remove(0)

class generator_for_msg:
    def __init__(self, shared_list):
        pass


shared_list = []

thread = threading.Thread(target=check_loop(shared_list))
thread.daemon = True
thread.start()
while 1:
    input_string = input(">")
    shared_list.append(input_string)






