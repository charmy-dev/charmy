from charmy import *

obj = CharmyObject()
obj.new("name", "obj1")
print(obj.get("name"))  # OUTPUT: obj1
obj.set("name", "obj2")
print(obj.get("name"))  # OUTPUT: obj2


def set_func(value):
    print("User set value:", value)
    return "Hello, " + value


def get_func():
    return f"User get value: {obj.get('title', skip=True)}"


obj.new("title", "default title", set_func=set_func, get_func=get_func)
print(obj.get("title"))  # OUTPUT: default title
obj.set("title", "A")  # OUTPUT: User set value: A
print(obj.get("title"))  # User get value: Hello, A
