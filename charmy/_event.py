from __future__ import annotations as _

import collections.abc
import re
import threading
import time
import typing
import warnings

# [TODO] Implementation of repeat events
# [TODO] Fix a type error in CEventHandling.bind()
# [TODO] Support unbind for another widget's event


class CBoundTask:
    """A class to represent bound Task when a event is triggered."""

    def __init__(
        self,
        id_: str,
        target: typing.Callable | typing.Iterable,
        multithread: bool = False,
        _keep_at_clear: bool = False,
    ):
        """Each object is to represent a Task bound to the event.

        Example
        -------
        This is mostly for internal use of suzaku.
        .. code-block:: python
            class CEventHandling():
                def bind(self, ...):
                    ...
                    Task = CBoundTask(event_id, target, multithread, _keep_at_clear)
                    ...
        This shows where this class is used for storing Task properties in most cases.

        :param id_: The Task id of this Task
        :param target: A callable thing, what to do when this Task is executed
        :param multithread: If this Task should be executed in another thread (False by default)
        :param _keep_at_clear: If the Task should be kept when cleaning the event's binding
        """
        self.id: str = id_
        self.target: typing.Callable | typing.Iterable = target
        self.multithread: bool = multithread
        self.keep_at_clear: bool = _keep_at_clear


class CDelayTask(CBoundTask):
    """A class to represent delay Tasks"""

    def __init__(
        self,
        id_: str,
        target: typing.Callable | typing.Iterable,
        delay_: str,
        *args,
        **kwargs,
    ):
        """Inherited from CBoundTask, used to store Tasks bound to `delay` events.

        :param delay: Time to delay, in seconds, indicating how log to wait before the Task is
                      executed.
        :param (Other): See `CBoundTask.__init__()`
        """
        CBoundTask.__init__(self, id_, target, *args, **kwargs)  # For other things,same as
        # CBoundTask
        if delay_.endswith("s"):
            if delay_.endswith("ms"):
                delay_ = float(delay_[:-2]) / 1000
            else:
                delay_ = float(delay_[:-1])
        else:
            delay_ = float(delay_)
        self.target_time = float(time.time()) + delay_  # To store when to execute the Task


class CRepeatTask(CBoundTask):
    """A class to represent repeat Tasks"""

    def __init__(self, id_: str, target: typing.Callable, interval, *args, **kwargs):
        """Inherited from CBoundTask, used to store Tasks bound to `repeat` events.

        :param delay: Time to delay, in seconds, indicating how log to wait before the Task is
                      executed.
        """
        CBoundTask.__init__(self, id_, target, *args, **kwargs)  # For other things,same as
        # CBoundTask
        self.target_time = float(time.time()) + interval  # To store when to execute the Task for
        # the next time, will be accumulated after
        # execution of the Task
        self.interval = interval  # Interval of the Task


class CEventHandling:
    """A class containing event handling abilities.

    This class should be inherited by other classes with such abilities.

    Events should be represented in the form of `event_type` or `event_type[args]`. e.g. `delay` or
    `delay[500]`
    """

    # fmt: off
    EVENT_TYPES: list[str] = [
        "resize", "move", 
        "configure", "update", "redraw", 
        "mouse_move", "mouse_enter", "mouse_leave", "mouse_press", "mouse_release", "click", "double_click",
        "focus_gain", "focus_loss", 
        "key_press", "key_release", "key_repeat", "char", 
        "delay", "repeat", # This row shows special event type(s)
    ]
    # fmt: on
    multithread_Tasks: list[tuple[CBoundTask, CEvent]] = []
    WORKING_THREAD: threading.Thread
    instance_count = 0

    @classmethod
    def _working_thread_loop(cls):
        while True:
            try:
                CEventHandling._execute_Task(
                    cls.multithread_Tasks[0][0], cls.multithread_Tasks[0][1]
                )
                # For line above: [0][0] is Task object, [0][1] is CEvent object
            except Exception as e:
                warnings.warn(
                    RuntimeWarning(
                        "Error in multithread suzaku-event-bound Task "
                        f"with ID {cls.multithread_Tasks[0][0].id}, "
                        f'detailed error info: "{str(e)}". '
                        "The working thread will head to the next Task "
                        "(Cipping current causing the error)."
                    )
                )
            cls.multithread_Tasks.pop(0)  # Executed Tasks should be removed, anyway

            if not cls.multithread_Tasks:
                time.sleep(0.01)  # Avoid CPU draining while no Tasks avail
                continue

    @staticmethod
    def _execute_Task(Task: CBoundTask, event_obj: CEvent) -> None:
        """To execute the binded Task directly, regardless its props, mainly for internal use."""
        match Task.target:
            case _ if callable(Task.target):
                Task.target(event_obj)
            case _ if isinstance(Task.target, collections.abc.Iterable):
                for Task_step in Task.target:
                    Task_step(event_obj)
            case _:
                raise ValueError(
                    "Error type for suzaku Task target! Excepted callable or "
                    f"iterable but received {type(Task.target)}"
                )

    def __init__(self):
        """A class containing event handling abilities.

        Example
        -------
        This is mostly for internal use of suzaku.
        .. code-block:: python
            class CWidget(CEventHandling, ...):
                def __init__(self):
                    super().__init__(self)
            ...
        This shows subclassing CEventHandling to let CWidget gain the ability of handling events.
        """
        self.latest_event: CEvent = CEvent(widget=None, event_type="NO_EVENT")
        self.Tasks: dict[str, list[CBoundTask]] = {}
        # Make a initial ID here as it will be needed anyway even if the object does not have an ID.
        self.id = f"{self.__class__.__name__}{self.__class__.instance_count}"
        ## Initialize Tasks list
        for event_type in self.__class__.EVENT_TYPES:
            self.Tasks[event_type] = []
        ## Accumulate instance count
        self.__class__.instance_count += 1
        # Event binds
        self.bind("update", self._check_delay_events, _keep_at_clear=True)  # Delay checking loop

    def parse_event_type_str(self, event_type_str) -> dict:
        """This function parses event type string.

        :param event_type_str: The event type string to be parsed
        :returns: json, parsed event type
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

    def execute_Task(self, Task: CBoundTask, event_obj: CEvent | None = None):
        """To execute a Task

        Example
        -------
        .. code-block:: python
            my_Task = CWidget.bind("delay[5]", lambda: print("Hello Suzaku"))
            CWidget.execute_Task(my_Task)
        """
        if event_obj is None:
            event_obj = CEvent()
        assert event_obj is not None
        if event_obj.widget is None:
            event_obj.widget = self
        if not Task.multithread:
            # If not multiTask, execute directly
            CEventHandling._execute_Task(Task, event_obj)
            # If is a delay event, it should be removed right after execution
            if isinstance(Task, CDelayTask):
                self.unbind(Task)
        else:
            # Otherwise add to multithread Tasks list and let the working thread to deal with it
            # If is a delay Task, should add some code to let it unbind itself, here is a way,
            # which is absolutely not perfect, though works, to implement this mechanism, by
            # overriding its target with a modified version
            def self_destruct_template(Task, event_obj):
                CEventHandling._execute_Task(Task, event_obj)
                self.unbind(Task)

            if isinstance(Task, CDelayTask):
                Task.target = lambda event_obj: self_destruct_template(Task, event_obj)
            CEventHandling.multithread_Tasks.append((Task, event_obj))

    def trigger(self, event_type: str, event_obj: CEvent | None = None) -> None:
        """To trigger a type of event

        Example
        -------
        .. code-block:: python
            class CWidget(CEventHandling, ...):
                ...

            my_widget = CWidget()
            my_widget.trigger("mouse_press")
        This shows triggering a `mouse_press` event in a `CWidget`, which inherited `CEventHandling` so has the
        ability to handle events.

        :param event_type: The type of event to trigger
        """
        # Parse event type string
        parsed_event_type = self.parse_event_type_str(event_type)
        # Create a default CEvent object if not specified
        if event_obj is None:
            event_obj = CEvent(widget=self, event_type=tuple(parsed_event_type.keys())[0])
        # Add the event to event lists (the widget itself and the global list)
        self.latest_event = event_obj
        CEvent.latest = event_obj
        # Find targets
        targets = [parsed_event_type["type"]]
        if not parsed_event_type["params"]:
            targets.append(parsed_event_type["type"] + "[*]")
        else:
            targets.append(event_type)
        # if parsed_event_type["params"][0] in ["", "*"]: # If match all
        #     targets.append(parsed_event_type["type"])
        #     targets.append(parsed_event_type["type"] + "[*]")
        for target in targets:
            if target in self.Tasks:
                for Task in self.Tasks[target]:
                    # To execute all Tasks bound under this event
                    self.execute_Task(Task, event_obj)

    def bind(
        self,
        event_type: str,
        target: typing.Callable | typing.Iterable,
        multithread: bool = False,
        _keep_at_clear: bool = False,
    ) -> CBoundTask | bool:
        """To bind a Task to the object when a specific type of event is triggered.

        Example
        -------
        .. code-block
            my_button = CButton(...).pack()
            press_down_event = my_button.bind("mouse_press", lambda _: print("Hello world!"))
        This shows binding a hello world to the button when it's press.

        :param event_type: The type of event to be bound to
        :param target: A (list of) callable thing, what to do when this Task is executed
        :param multithread: If this Task should be executed in another thread (False by default)
        :param _keep_at_clear: If the Task should be kept when cleaning the event's binding
        :return: CBoundTask that is bound to the Task if success, otherwise False
        """
        parsed_event_type = self.parse_event_type_str(event_type)
        if parsed_event_type["type"] not in self.__class__.EVENT_TYPES:
            # warnings.warn(f"Event type {event_type} is not present in {self.__class__.__name__}, "
            #                "so the Task cannot be bound as expected.")
            # return False
            self.EVENT_TYPES.append(event_type)
        if event_type not in self.Tasks:
            self.Tasks[event_type] = []
        Task_id = f"{self.id}.{event_type}.{len(self.Tasks[event_type])}"
        # e.g. CButton114.focus_gain.514 / CEventHandling114.focus_gain.514
        match parsed_event_type["type"]:
            case "delay":
                Task = CDelayTask(
                    Task_id,
                    target,  # I will fix this type error later (ignore is ur type check is off)
                    parsed_event_type["params"][0],
                    multithread,
                    _keep_at_clear,
                )
            case "repeat":
                raise NotImplementedError("repeat events is not implemented yet!")
            case _:  # All normal event types
                Task = CBoundTask(Task_id, target, multithread, _keep_at_clear)
        self.Tasks[event_type].append(Task)
        return Task

    def find_Task(self, Task_id: str) -> CBoundTask | bool:
        """To find a bound Task using Task ID.

        Example
        -------
        .. code-block:: python
            my_button = CButton(...)
            press_Task = my_button.find_Task("CButton114.mouse_press.514")
        This shows getting the `CBoundTask` object of Task with ID `CButton114.mouse_press.514`
        from bound Tasks of `my_button`.

        :return: The CBoundTask object of the Task, or False if not found
        """
        Task_id_parsed = Task_id.split(".")
        if len(Task_id_parsed) == 2:  # If is a shortened ID (without widget indicator)
            Task_id_parsed.insert(0, self.id)  # We assume that this indicates self
        for Task in self.Tasks[Task_id_parsed[1]]:
            if Task.id == Task_id:
                return Task
        else:
            return False

    def unbind(self, target_Task: str | CBoundTask) -> bool:
        """To unbind the Task with specified Task ID.

        Example
        -------
        .. code-block:: python
            my_button = CButton(...)
            my_button.unbind("CButton114.mouse_press.514")
        This show unbinding the Task with ID `CButton114.mouse_press.514` from `my_button`.

        .. code-block:: python
            my_button = CButton(...)
            my_button.unbind("CButton114.mouse_press.*")
            my_button.unbind("mouse_release.*")
        This show unbinding all Tasks under `mouse_press` and `mouse_release` event from
        `my_button`.

        :param target_Task: The Task ID or `CBoundTask` to unbind.
        :return: If success
        """
        match target_Task:
            case str():  # If given an ID string
                Task_id_parsed = target_Task.split(".")
                if len(Task_id_parsed) == 2:  # If is a shortened ID (without widget indicator)
                    Task_id_parsed.insert(0, self.id)  # We assume that this indicates self
                if Task_id_parsed != self.id:  # If given ID indicates another widget
                    NotImplemented
                    # Still not inplemented, as we currently cannot get a CWidget object itself
                    # only with its ID (waiting for @XiangQinxi)
                    # This part should call the unbind function of the widget with such ID
                for Task_index, Task in enumerate(self.Tasks[Task_id_parsed[1]]):
                    if Task.id == target_Task:
                        self.Tasks[Task_id_parsed[1]].pop(Task_index)
                        return True
                else:
                    return False
            case CBoundTask():
                for event_type in self.Tasks:
                    if target_Task in self.Tasks[event_type]:
                        self.Tasks[event_type].remove(target_Task)
                        return True
                else:
                    return False
            case _:
                warnings.warn(
                    "Wrong type for unbind()! Must be event ID or Task object",
                    UserWarning,
                )
                return False

    def clear_bind(self, event_type: str) -> bool:
        """To clear clear Tasks binded to a spcific event or widget

        Example
        -------
        .. code-block:: python
            my_widget = CWidget(...)
            my_widget.clear_bind("click")
        This shows clearing Tasks bound to `click` event on `my_widget`.

        .. code-block:: python
            my_widget = CWidget(...)
            my_widget.clear_bind("*")
        This shows clearing all events bound to any event on `my_widget`.

        :param event_type: Type of event to clear binds, `*` for all
        :return: Boolean, whether success or not
        """
        if event_type == "*":  # Clear all Tasks of this object
            return not False in [self.clear_bind(this_type) for this_type in self.Tasks]
        else:  # In other cases, this must be an specific event type
            if event_type in self.Tasks:  # If type given existed and include some Tasks
                for Task in self.Tasks[event_type]:
                    if not Task.keep_at_clear:  # Cip any keep_at_clear Tasks
                        self.unbind(Task)
                return True
            else:
                return False

    def _check_delay_events(self, _=None) -> None:
        """To check and execute delay events.

        Example
        -------
        Mostly used by CWidget.update(), which is internal use.

        :param _: To accept an event object if is given, will be ignored
        """
        # print("Checking delayed events...")
        for binded_event_type in tuple(self.Tasks):
            if self.parse_event_type_str(binded_event_type)["type"] == "delay":
                for Task in self.Tasks[binded_event_type]:
                    if isinstance(Task, CDelayTask):
                        if float(time.time()) >= Task.target_time:
                            # print(f"Current time is later than target time of {Task.id}, "
                            #        "execute the Task.")
                            self.execute_Task(Task)


# Initialize working thread
CEventHandling.WORKING_THREAD = threading.Thread(target=CEventHandling._working_thread_loop)


# @daTasklass
class CEvent:
    """Used to represent an event."""

    latest: CEvent

    def __init__(
        self,
        widget: CEventHandling | None = None,
        event_type: str = "[Unspecified]",
        **kwargs,
    ):
        """This class is used to represent events.

        Some properties owned by all types of events are stored as attributes, such as widget and type.
        Others are stored as items, which can be accessed or manipulated just like dict, e.g.
        `CEvent["x"]` for get and `CEvent["y"] = 16` for set.

        Example
        -------
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


CEvent.latest = CEvent(widget=None, event_type="NO_EVENT")
