from aqua import *

obj = AqObject()
obj.new("name", "obj1")
print(obj.get("name"))  # OUTPUT: obj1
obj.set("name", "obj2")
print(obj.get("name"))  # OUTPUT: obj2


def set_func(value):
    print("User set value:", value)
    return "Hi" + value


def get_func():
    print("User get value")


obj.new("title", "", set_func=set_func, get_func=get_func)
obj.set("title", "A")
print(obj.get("title"))