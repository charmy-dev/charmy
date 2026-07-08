from __future__ import annotations as _

import collections.abc
import re
import threading
import typing
import warnings
from dataclasses import dataclass

from .cm_object import CharmyObject
from .utils import event_types # Expose this as event_types

if typing.TYPE_CHECKING:
    from .utils import var

__all__ = ["EventHandling", "EventTask", "DelayTask", "event_types"]


class EventHandling:

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
    multithread_tasks: list[tuple[EventTask, event_types.Event]] = []
    WORKING_THREAD: threading.Thread

    @staticmethod
    def _execute_task(task: EventTask | DelayTask, event_obj: event_types.Event) -> None:
        """To execute the bound task directly, regardless its props, mainly for internal use."""
        match task.target:
            case _ if callable(task.target):
                task.target(event_obj)
            case _ if isinstance(task.target, collections.abc.Iterable):
                for task_step in task.target:
                    task_step(event_obj)
            case _:
                raise ValueError(
                    "Error type for Charmy Task target! Excepted callable or "
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
        # super().__init__()
        self.latest_event: event_types.Event = event_types.Event()
        self.tasks: dict[type[event_types.Event], list[EventTask]] = {}

        self._mouse_hovering: bool = False
        self._mouse_pressed_buttons: list[int] = []

        self._alive: bool = True

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

    def trigger(self, event_obj: event_types.Event) -> typing.Self:
        """To trigger a type of event

        Args:
            event_type: The type of event to trigger

        Example
        -------
        .. code-block:: python

            class Widget(EventHandling, ...):
                ...

            my_widget = Widget()
            my_widget.trigger(MousePress(pos=(30, 50), button=0))

        This shows triggering a `mouse.press` event in a `Widget`, which inherited
        `EventHandling` so has the ability to handle events.
        """
        if not self._alive:
            return self
        if type(event_obj) in self.tasks:
            for task in self.tasks[type(event_obj)]:
                if event_obj.meets(task.conditions):
                    task.execute(event_obj)
        event_obj.call_chain(self)
        return self

    @typing.overload
    def bind(
        self,
        event_type: type[event_types.Event], 
        target: typing.Callable | typing.Iterable, 
        conditions: dict = {}, 
        multithread: bool = False, 
        _is_internal: bool = False, 
        task_obj_receiver: typing.Optional[var.Var[EventTask]] = None, 
        return_task: typing.Literal[True] = True
        ) -> EventTask: ...

    @typing.overload
    def bind(
        self,
        event_type: type[event_types.Event], 
        target: typing.Callable | typing.Iterable, 
        conditions: dict = {}, 
        multithread: bool = False, 
        _is_internal: bool = False, 
        task_obj_receiver: typing.Optional[var.Var[EventTask]] = None, 
        return_task: typing.Literal[False] = False
        ) -> typing.Self: ...

    def bind(
        self,
        event_type: type[event_types.Event], 
        target: typing.Callable | typing.Iterable[typing.Callable], 
        conditions: typing.Optional[dict] = None, 
        multithread: bool = False, 
        _is_internal: bool = False, 
        task_obj_receiver: typing.Optional[var.Var[EventTask]] = None, 
        return_task: bool = True
    ) -> EventTask | typing.Self:
        """To bind a task to the object when a specific type of event is triggered.

        Example
        -------
        .. code-block:: python

            my_button = Button(...).pack()
            press_down_event = my_button.bind(event_types.Click, lambda _: print("Hello world!"))

        This shows binding a hello world to the button when it's press.

        :param event_type: The type of event to be bound to
        :param target: A (list of) callable thing, what to do when this task is executed
        :param condition: Conditions required for the task to run when event is triggered
        :param multithread: If this task should be executed in another thread (False by default)
        :param _is_internal: If the task is added by Charmy and should be kept when clear bind
        :return: EventTask if `return_task` is True, otherwise the EventHandling itself.
        """
        if conditions is None:
            conditions = {}
        task = EventTask(target, conditions, multithread, _is_internal)
        if not event_type in self.tasks:
            self.tasks[event_type] = []
        self.tasks[event_type].append(task)
        if task_obj_receiver is not None:
            task_obj_receiver.value = task
        if return_task:
            return task
        else:
            return self

    def on(
            self, 
            event_type: type[event_types.Event], 
            conditions: typing.Optional[dict[str, typing.Any]] = None, 
            multithread: bool = False, 
            _is_internal: bool = False, 
            task_obj_receiver: typing.Optional[var.Var[EventTask]] = None, 
            ) -> typing.Callable[[typing.Callable], typing.Callable]:
        """Generate a decorator that binds the event.

        → See `bind()` for parameters description.
        """
        if conditions is None:
            conditions = {}
        def decorator(func: typing.Callable) -> typing.Callable:
            """Binds the function to be decorated to the event."""
            self.bind(event_type, func, conditions, multithread, _is_internal, task_obj_receiver)
            return func
        return decorator

    def unbind(self, target_task: EventTask) -> typing.Self:
        """To unbind a specific task.

        Example
        -------

        .. code-block:: python

            my_button = Button(...)
            my_task = my_button.bind(event_types.Click, lambda: print("Ouch!"))
            my_button.unbind(my_task)

        This show unbinding the task bound to `Click` event from `my_button`.

        :param target_task: The `EventTask` to unbind.
        :return: If success
        """
        for event_type in self.tasks:
            if target_task in self.tasks[event_type]:
                self.tasks[event_type].remove(target_task)
        return self

    def clear_bind(self, target_type: type[event_types.Event]) -> typing.Self:
        """To unbind the tasks bound to a specific type of events.

        Example
        -------

        .. code-block:: python

            my_button = Button(...)
            my_task = my_button.bind(event_types.Click, lambda: print("Ouch!"))
            my_button.clear_bind(event_types.Click)

        This show unbinding all tasks bound to `Click` event from `my_button`.

        :param target_type: The event type to clear bind.
        :return: If success
        """
        self.tasks[target_type] = []
        return self


# region Tasks

@dataclass
class EventTask(CharmyObject):
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
    target: typing.Callable | typing.Iterable[typing.Callable]
    conditions: dict[str, typing.Any]
    multithread: bool = False
    _internal_task: bool = False

    task_threads: typing.ClassVar[list[threading.Thread]] = []

    def execute(self, event: typing.Optional[event_types.Event] = None) -> None:
        """Execute the task.

        :return value: Return value of the target if not multitask, otherwise None
        """
        if event is None:
            event = event_types.Event()
        def execute_list(steps: typing.Iterable[typing.Callable], event: event_types.Event):
            for step in steps:
                step(event)
        if isinstance(self.target, collections.abc.Iterable):
            steps = self.target
            target = lambda event: execute_list(steps, event)
        else:
            target = self.target
        if self.multithread:
            task_thread = threading.Thread(target=lambda: target(event))
            self.__class__.task_threads.append(task_thread)
            task_thread.start()
        else:
            target(event)

class DelayTask(EventTask):
    # TODO: DelayTask
    pass  # NOQA