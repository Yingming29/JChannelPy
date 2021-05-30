import datetime

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
    messages = [
        1,
        2,
        3,
        4,
        5
    ]
    print("here")
    for msg in messages:
        print("one iteration")
        yield msg


a = yield_test()
print(a.__next__())
print(a.__next__())
print(a.__next__())
print(a.__next__())

