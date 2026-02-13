import threading
import time
import typing

from .const import ID
from .object import CObject


class CEvent(CObject):
    """Record attributes of an event"""

    def __init__(self, event_type: str | None = None, **kwargs):
        super().__init__()

        self.new("event_type", event_type)

        for key, value in kwargs.items():
            self.new(key, value)


class CEventTask(CObject):
    """CEventTask is a class to store event task

    Args:
        _id (ID): the id of the task
        target: The function to be called when the event is triggered
    """

    def __init__(
        self,
        _id=ID.AUTO,
        target: typing.Callable[..., None] = None,
    ):
        super().__init__(_id=_id)

        self.new("target", target)


class CEventThread(threading.Thread, CObject):
    """CEventThread is a class to store event tasks and execute them"""

    tasks: list[list[CEventTask | CEvent]] = []
    is_alive = True

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        CObject.__init__(self, _id="event.main_thread")

    def execute_tasks(self):
        for task in self.tasks:
            task[0]["target"](task[1])
            self.tasks.remove(task)

    def run(self):
        while self.is_alive:
            self.execute_tasks()
            time.sleep(0.01)

    def add_task(self, task: CEventTask, event: CEvent):
        self.tasks.append([task, event])


class CEventHandler(CObject):

    basic_event_types = [
        "on_click",
        "on_dbclick",  # NOQA
        "on_draw",
        "on_move",
        "on_resize",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new("event.main_thread", self.find("event.main_thread"))
        self.new("events", {})  # e.g. {"Click": [Target1, Target2]}
        self.create_event_types(self.basic_event_types)

    def create_event_type(self, event_type: str):
        self["events"][event_type] = []

    def create_event_types(self, event_types: typing.List[str]):
        for event_type in event_types:
            self.create_event_type(event_type)

    generate = create_event_type

    def generate_event_signal(self, event_type: str, **kwargs):
        for target in self["events"][event_type]:
            self["event.main_thread"].add_task(
                CEventTask(target=target), CEvent(event_type=event_type, **kwargs)
            )

    trigger = generate_event_signal

    def bind_event(self, event_type: str, target: typing.Callable[..., None]):
        self["events"][event_type].append(target)

    bind = bind_event

    def unbind_event(self, event_type: str, target: typing.Callable[..., None]):
        self["events"][event_type].remove(target)

    unbind = unbind_event
