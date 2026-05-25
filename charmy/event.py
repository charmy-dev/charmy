from __future__ import annotations as _

import collections.abc
import re
import threading
import time
import typing
import warnings
from dataclasses import dataclass

from .object import CharmyObject
from .utils import event_types # Expose this as event_types

__all__ = ["EventHandling", "EventTask", "DelayTask", "event_types"]


class EventHandling():

    # # fmt: off
    # EVENT_TYPES: list[str] = [
    #     # Window size & pos
    #     "resize", "move", 
    #     # Widget internal changes
    #     "configure", "update", "draw",
    #     # Mouse events
    #     "mouse_move", "mouse_enter", "mouse_leave", "mouse_press", "mouse_release", "click", 
    #     "double_click",
    #     # Focus events
    #     "focus_gain", "focus_loss", 
    #     # Key events
    #     "key_press", "key_release", "key_repeat", "char", 
    #     # Special events
    #     "delay", "repeat", 
    # ]
    # # fmt: on
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
                    # TODO: *suzaku* Task target 🤔
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
        self.latest_event: Event = Event(None)
        self.tasks: dict[type[Event], list[EventTask]] = {}

    def parse_event_type_str(self, event_type_str: str) -> dict:  # NOQA
        """This function parses event type string.

        Type String Format
        ------------------
        Either in `{Event type}` or `{Event type}[{Param 1}, {Param 2}]`. Example: `MousePressed` 
        or `MousePressed[0]`

        Return Value & Deprecation
        --------------------------
        The return value is a `dict` containing the type and params expressed in string. This kind 
        of return value might be unused in the new events system designed for Charmy. Therefore, 
        this function might be removed in the future.

        :param event_type_str: The event type string to be parsed
        :returns: JSON, parsed event type
        """
        if not re.match(".*\\[.*\\]", event_type_str):  # NOQA
            return {"type": event_type_str, "params": []}
        event_type = re.findall("^(.*?)\\[", event_type_str)[0]
        params_raw = re.findall("\\[(.*?)\\]$", event_type_str)[0]  # NOQA
        assert type(event_type) is str
        assert type(params_raw) is str
        params = params_raw.split(",")
        if len(params) == 1:
            if params[0].strip() == "":
                params = []
        return {"type": event_type, "params": params}

    def trigger(self, event_obj: Event) -> typing.Self:
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
        # TODO: This fuck (trigger() method) should be rewritten
        for task in self.tasks[event_obj.__class__]:
            if task.condition.meets
        return self

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
        try:
            assert isinstance(self, CharmyObject)
        except AssertionError as e:
            raise AssertionError("Each EventHandling object must by a CharmyObject.")
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
        try:
            assert isinstance(self, CharmyObject)
        except AssertionError as e:
            raise AssertionError("Each EventHandling object must by a CharmyObject.")
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


# region Tasks

@dataclass
class EventTask:
    """A class to represent event task when an event is triggered.

    Each object is to represent a task bound to the event.

    Example
    -------
    This is mostly for internal use of Charmy.

    .. code-block:: python
        class EventHandling():
            ...
            def bind(self, ...):
                ...
                task = EventTask(event_id, target, multithread, _keep_at_clear)
                ...
            ...

    This shows where this class is used for storing task properties in most cases.

    :param target: A callable thing, what to do when this task is executed
    :param multithread: If this task should be executed in another thread (False by default)
    :param _internal_task: If the task is internally created and used by Charmy
    """
    target: typing.Callable
    condition: Event
    multithread: bool = False
    _internal_task: bool = False

    task_threads: typing.ClassVar[list[threading.Thread]] = []

    def execute(self, event: Event = Event(None)) -> typing.Any | None:
        """Execute the task.

        :return value: Return value of the target if not multitask, otherwise None
        """
        if self.multithread:
            task_thread = threading.Thread(target=lambda: self.target(event))
            self.__class__.task_threads.append(task_thread)
            task_thread.run()
        else:
            return self.target(event)

class DelayTask(EventTask):
    # TODO: DelayTask
    pass  # NOQA