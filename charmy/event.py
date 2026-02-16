from __future__ import annotations as _

import collections.abc
import re
import threading
import time
import typing
import warnings

from .const import ID
from .object import CharmyObject


class EventHandling(CharmyObject):

    # fmt: off
    EVENT_TYPES: list[str] = [
        # Window size & pos
        "resize", "move", 
        # Widget internal changes
        "configure", "update", "draw",
        # Mouse events
        "mouse_move", "mouse_enter", "mouse_leave", "mouse_press", "mouse_release", "click", 
        "double_click",
        # Focus events
        "focus_gain", "focus_loss", 
        # Key events
        "key_press", "key_release", "key_repeat", "char", 
        # Special events
        "delay", "repeat", 
    ]
    # fmt: on
    multithread_tasks: list[tuple[EventTask, Event]] = []
    WORKING_THREAD: threading.Thread

    @staticmethod
    def _execute_task(task: EventTask | DelayTask, event_obj: Event) -> None:
        """To execute the bound task directly, regardless its props, mainly for internal use."""
        match task.target:
            case _ if callable(task.target):
                task.target(event_obj)
            case _ if isinstance(task.target, collections.abc.Iterable):
                for task_step in task.target:
                    task_step(event_obj)
            case _:
                raise ValueError(
                    "Error type for suzaku Task target! Excepted callable or "
                    f"iterable but received {type(task.target)}"
                )

    def __init__(self):
        """A class containing event handling abilities.

        Example
        -------
        This is mostly for internal use of Charmy.

        .. code-block:: python

            class Widget(EventHandling, ...):
                def __init__(self):
                    super().__init__(self)
            ...

        This shows subclassing EventHandling to let Widget gain the ability of handling events.
        """
        super().__init__()
        self.latest_event: Event = Event(widget=None, event_type="NO_EVENT")
        self.tasks: dict[str, list[EventTask]] = {}
        ## Initialize tasks list
        for event_type in self.__class__.EVENT_TYPES:
            self.tasks[event_type] = []

    def parse_event_type_str(self, event_type_str: str) -> dict:  # NOQA
        """This function parses event type string.

        :param event_type_str: The event type string to be parsed
        :returns: JSON, parsed event type
        """
        if not re.match(".*\\[.*\\]", event_type_str):  # NOQA
            return {"type": event_type_str, "params": []}
        event_type = re.findall("^(.*?)\\[", event_type_str)[0]
        params_raw = re.findall("\\[(.*?)\\]$", event_type_str)[0]  # NOQA
        params = params_raw.split(",")
        if len(params) == 1:
            if params[0].strip() == "":
                params = []
        return {"type": event_type, "params": params}

    def execute_task(self, task: EventTask, event_obj: Event | None = None):
        """To execute a task

        Example
        -------
        .. code-block:: python

            my_task = Widget.bind("delay[5]", lambda: print("Hello Suzaku"))
            Widget.execute_task(my_task)

        """
        if event_obj is None:
            event_obj = Event()
        assert event_obj is not None
        if event_obj.widget is None:
            event_obj.widget = self
        if not task.multithread:
            # If not multitask, execute directly
            EventHandling._execute_task(task, event_obj)
            # If is a delay event, it should be removed right after execution
            if isinstance(task, DelayTask):
                self.unbind(task)
        else:
            # Otherwise add to multithread tasks list and let the working thread to deal with it
            # If is a delay task, should add some code to let it unbind itself, here is a way,
            # which is absolutely not perfect, though works, to implement this mechanism, by
            # overriding its target with a modified version
            def self_destruct_template(task, event_obj):
                EventHandling._execute_task(task, event_obj)
                self.unbind(task)

            if isinstance(task, DelayTask):
                task.target = lambda event_obj: self_destruct_template(task, event_obj)
            EventHandling.multithread_tasks.append((task, event_obj))

    def trigger_event(self, event_obj: Event) -> None:
        """To trigger a type of event

        Args:
            event_type: The type of event to trigger

        Example
        -------
        .. code-block:: python

            class Widget(EventHandling, ...):
                ...

            my_widget = Widget()
            my_widget.trigger("mouse_press")

        This shows triggering a `mouse_press` event in a `Widget`, which inherited
        `EventHandling` so has the ability to handle events.
        """
        # Parse event type string
        parsed_event_type = self.parse_event_type_str(event_obj.event_type)
        # Create a default Event object if not specified
        if event_obj is None:
            event_obj = Event(widget=self, event_type=tuple(parsed_event_type.keys())[0])
        # Add the event to event lists (the widget itself and the global list)
        self.latest_event = event_obj
        Event.latest = event_obj
        # Find targets
        targets = [parsed_event_type["type"]]
        if not parsed_event_type["params"]:
            targets.append(parsed_event_type["type"] + "[*]")
        else:
            targets.append(event_obj.event_type)
        # if parsed_event_type["params"][0] in ["", "*"]: # If match all
        #     targets.append(parsed_event_type["type"])
        #     targets.append(parsed_event_type["type"] + "[*]")
        for target in targets:
            if target in self.tasks:
                for task in self.tasks[target]:
                    # To execute all tasks bound under this event
                    self.execute_task(task, event_obj)

    trigger = trigger_event  # Alias for trigger

    def bind(
        self,
        event_type: str,
        target: typing.Callable | typing.Iterable,
        multithread: bool = False,
        _keep_at_clear: bool = False,
    ) -> EventTask | bool:
        """To bind a task to the object when a specific type of event is triggered.

        Example
        -------
        .. code-block:: python

            my_button = Button(...).pack()
            press_down_event = my_button.bind("mouse_press", lambda _: print("Hello world!"))

        This shows binding a hello world to the button when it's press.

        :param event_type: The type of event to be bound to
        :param target: A (list of) callable thing, what to do when this task is executed
        :param multithread: If this task should be executed in another thread (False by default)
        :param _keep_at_clear: If the task should be kept when cleaning the event's binding
        :return: EventTask that is bound to the task if success, otherwise False
        """
        parsed_event_type = self.parse_event_type_str(event_type)
        if parsed_event_type["type"] not in self.__class__.EVENT_TYPES:
            # warnings.warn(f"Event type {event_type} is not present in {self.__class__.__name__}, "
            #                "so the task cannot be bound as expected.")
            # return False
            self.EVENT_TYPES.append(event_type)
        if event_type not in self.tasks:
            self.tasks[event_type] = []
        task_id = f"{self.id}.{event_type}.{len(self.tasks[event_type])}"
        # e.g. CButton114.focus_gain.514 / CEventHandling114.focus_gain.514
        match parsed_event_type["type"]:
            case "delay":
                raise NotImplementedError("Delay tasks are not implemented yet!")
                task = DelayTask(  # NOQA
                    target,  # I will fix this type error later (ignore is ur type check is off)
                    parsed_event_type["params"][0],
                    multithread,
                    _keep_at_clear,
                    task_id,  # NOQA
                )
            case "repeat":
                raise NotImplementedError("Repeat tasks is not implemented yet!")
            case _:  # All normal event types
                task = EventTask(target, multithread, _keep_at_clear, task_id)
        self.tasks[event_type].append(task)
        return task

    def find_task(self, task_id: str) -> EventTask | bool:
        """To find an event task using task ID.

        Example
        -------

        .. code-block:: python

            my_button = Button(...)
            press_task = my_button.find_task("Button114.mouse_press.514")

        This shows getting the `EventTask` object of task with ID `Button114.mouse_press.514`
        from bound tasks of `my_button`.

        :return: The EventTask object of the task, or False if not found
        """
        task_id_parsed = task_id.split(".")
        if len(task_id_parsed) == 2:  # If is a shortened ID (without widget indicator)
            task_id_parsed.insert(0, self.id)  # We assume that this indicates self
        for task in self.tasks[task_id_parsed[1]]:
            if task.id == task_id:
                return task
        else:
            return False

    def unbind(self, target_task: str | EventTask | DelayTask) -> bool:
        """To unbind the task with specified task ID.

        Example
        -------

        .. code-block:: python

            my_button = Button(...)
            my_button.unbind("Button114.mouse_press.514")

        This show unbinding the task with ID `Button114.mouse_press.514` from `my_button`.

        .. code-block:: python

            my_button = Button(...)
            my_button.unbind("Button114.mouse_press.*")
            my_button.unbind("mouse_release.*")

        This show unbinding all tasks under `mouse_press` and `mouse_release` event from
        `my_button`.

        :param target_task: The task ID or `EventTask` to unbind.
        :return: If success
        """
        match target_task:
            case str():  # If given an ID string
                for task_index, task in enumerate(self.tasks[target_task]):
                    if task.id == target_task:
                        self.tasks[target_task].pop(task_index)
                        return True
                else:
                    return False
            case EventTask():
                for event_type in self.tasks:
                    if target_task in self.tasks[event_type]:
                        self.tasks[event_type].remove(target_task)
                        return True
                else:
                    return False
            case _:
                warnings.warn(
                    "Wrong type for unbind()! Must be event ID or task object",
                    UserWarning,
                )
                return False


class Event(CharmyObject):
    """Used to represent an event."""

    latest: "Event"

    def __init__(  # NOQA
        self,
        widget: EventHandling | None = None,
        event_type: str = "[Unspecified]",
        **kwargs,
    ):
        """This class is used to represent events.

        Some properties owned by all types of events are stored as attributes, such as widget and type.
        Others are stored as items, which can be accessed or manipulated just like dict, e.g.
        `CEvent["x"]` for get and `CEvent["y"] = 16` for set.

        Included in description.

        :param widget: The widget of the event, None by default
        :param event_type: Type of the event, in string, `"[Unspecified]"` by default
        :param **kwargs: Other properties of the event, will be added as items
        """
        self.event_type: str = event_type  # Type of event
        self.widget: typing.Optional[typing.Any] = widget  # Relating widget
        self.window_base: typing.Optional[typing.Any] = None  # WindowBase of the current window
        self.window: typing.Optional[typing.Any] = None  # Current window
        self.event_data: dict = {}
        # Not all properties above will be used
        # Update stuff from args into attributes
        for prop in kwargs.keys():
            if prop not in ["widget", "event_type"]:
                self[prop] = kwargs[prop]

    def __setitem__(self, key: str, value: typing.Any):
        self.event_data[key] = value

    def __getitem__(self, key: str) -> typing.Any:
        if key in self.event_data:
            return self.event_data[key]
        else:
            return None  # If no such item avail, returns None


Event.latest = Event(widget=None, event_type="NO_EVENT")


class EventTask:
    """A class to represent event task when an event is triggered."""

    def __init__(
        self,
        target: typing.Callable | typing.Iterable,
        multithread: bool = False,
        _keep_at_clear: bool = False,
        id_: str | int | typing.Literal[ID.AUTO] = ID.AUTO,
    ):
        """Each object is to represent a task bound to the event.

        Example
        -------
        This is mostly for internal use of suzaku.

        .. code-block:: python

            class EventHandling():
                def bind(self, ...):
                    ...
                    task = EventTask(event_id, target, multithread, _keep_at_clear)
                    ...

        This shows where this class is used for storing task properties in most cases.

        :param target: A callable thing, what to do when this task is executed
        :param multithread: If this task should be executed in another thread (False by default)
        :param _keep_at_clear: If the task should be kept when cleaning the event's binding
        :param id_: The task id of this task
        """
        self.id: str | int | typing.Literal[ID.AUTO] = id_
        self.target: typing.Callable | typing.Iterable = target
        self.multithread: bool = multithread
        self.keep_at_clear: bool = _keep_at_clear


class DelayTask(EventTask):
    NotImplemented  # NOQA


class WorkingThread(threading.Thread, CharmyObject):
    """CWorkingThread is a class represent the event working thread."""

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        CharmyObject.__init__(self, id_="event.main_thread")
        self.tasks: list[tuple[Event, EventTask | DelayTask]] = []  # [(event, task), ...]
        self.is_alive: bool = True
        self.lock: threading.Lock = threading.Lock()

    def execute_tasks(self):
        self.lock.acquire()
        for task in self.tasks:
            if callable(task[1].target):
                task[1].target(task[0])
            elif isinstance(task[1], collections.abc.Iterable):
                # Function list
                for func in task[1]:
                    func(task[0])
            self.tasks.remove(task)
        else:
            # warnings.warn("")
            pass
        self.lock.release()

    def run(self):
        while self.is_alive:
            self.execute_tasks()
            if len(self.tasks) == 0:
                # If idle, then rest for 0.02s to save CPU time
                time.sleep(0.02)

    def add_task(self, task: EventTask | DelayTask, event: Event):
        self.tasks.append((event, task))
