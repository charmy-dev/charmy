from __future__ import annotations as _

import typing

from dataclasses import dataclass as _dataclass
import time as _time

from charmy.event import EventHandling, EventHandling as _EventHandling

from ..cm_object import CharmyObject as _CharmyObject

if typing.TYPE_CHECKING:
    from ..event import EventHandling as _EventHandling
    from ..styles import shape as _shape
    from ..widgets import window as _window


# region Base class & generic classes

@_dataclass
class Event(_CharmyObject):
    """Used to represent an event. Can be regarded as a placeholder if directly used."""
    type: typing.ClassVar[str] = "noevent"

    def __init_subclass__(cls):
        cls.latest: typing.Self

    def meets(self, target_condition: dict, allow_inexist: bool = False) -> bool:
        """Check if current event meets the target condition.

        :param target_condition: Condition specified by task etc. to meet
        """
        for condition_name in target_condition.keys():
            if not hasattr(self, condition_name) and not allow_inexist:
                return False
            if getattr(self, condition_name) != target_condition[condition_name]:
                return False
        else:
            return True

    def call_chain(self, subject: _EventHandling) -> None:
        subject.trigger(EventTriggered(subject))

Event.latest = Event()


@_dataclass
class EventTriggered(Event):
    """Triggered when any other kind of event is triggered."""
    type: typing.ClassVar[str] = "event_triggered"

    subject: _EventHandling

    def call_chain(self, subject: EventHandling) -> None:
        pass


# region Widget events

@_dataclass
class WidgetEvent(Event):
    """The type of events that represents widget events.

    Notes on Param `subject`
    ------------------------
    `subject` should be the widget that is triggered the event.
    """
    type: typing.ClassVar[str] = "widget"

    subject: _EventHandling

@_dataclass
class WidgetUpdate(WidgetEvent):
    """Will be generated when a widget or window is updated.

    Note on Param `subject`
    -----------------------
    When `subject` is set to none, it means Charmy's global update routine is triggered.
    """
    type: typing.ClassVar[str] = "widget.update"

    subject: _EventHandling | None
    redraw: bool | _shape.ShapeRange = False

@_dataclass
class WidgetDraw(WidgetEvent):
    """Will be generated when a widget or window is redrawn."""
    type: typing.ClassVar[str] = "widget.draw"

    pos: _shape.Point = (0, 0)
    size: _shape.Size = (0, 0)

@_dataclass
class WidgetConfigure(WidgetEvent):
    """Will be generated when a widget or window has its configuration changed."""
    type: typing.ClassVar[str] = "widget.configure"

    attrs_changed: dict

    def call_chain(self, subject: EventHandling) -> None:
        super().call_chain(subject)
        if "pos" in self.attrs_changed.keys():
            subject.trigger(WidgetMove(subject, self.attrs_changed["pos"]))
        if "size" in self.attrs_changed.keys():
            subject.trigger(WidgetResize(subject, self.attrs_changed["size"]))

@_dataclass
class WidgetResize(WidgetEvent):
    """Will be generated when a widget or window is resized."""
    type: typing.ClassVar[str] = "widget.resize"

    new_size: _shape.Size
    old_size: typing.Optional[_shape.Size] = None

@_dataclass
class WidgetMove(WidgetEvent):
    """Will be generated when a widget or window is moved."""
    type: typing.ClassVar[str] = "widget.move"

    new_pos: _shape.Point
    old_pos: typing.Optional[_shape.Point] = None

@_dataclass
class FocusGain(WidgetEvent):
    """Will be generated when a widget or window gained focus."""
    type: typing.ClassVar[str] = "widget.focus_gain"

@_dataclass
class FocusLoss(WidgetEvent):
    """Will be generated when a widget or window lose focus."""
    type: typing.ClassVar[str] = "widget.focus_loss"

@_dataclass
class WidgetDestroy(WidgetEvent):
    """Will be generated when a widget or window is destroyed."""
    type: typing.ClassVar[str] = "widget.destroy"


# region Window events

@_dataclass
class WindowEvent(Event):
    """The type of events that represents window events.

    Notes on Param `subject`
    ------------------------
    `subject` should be the window where the events happened.
    """
    subject: _window.WindowEntity


# region Mouse events

@_dataclass
class MouseEvent(Event):
    """The type of events that represents mouse actions.

    Notes on Param `subject`
    ------------------------
    `subject` should be the window that detected the mouse event.
    """
    subject: _window.WindowEntity
    mouse_pos: _shape.Point

@_dataclass
class MouseMove(MouseEvent):
    """Will be generated when mouse movement is detected."""
    type: typing.ClassVar[str] = "mouse.move"

@_dataclass
class MousePress(MouseEvent):
    """Will be generated when a mouse button is pressed."""
    type: typing.ClassVar[str] = "mouse.press"

    button: int

@_dataclass
class MouseRelease(MouseEvent):
    """Will be generated when a mouse button is released."""
    type: typing.ClassVar[str] = "mouse.release"

    button: int

@_dataclass
class MouseScroll(MouseEvent):
    """Will be generated when a mouse button is released."""
    type: typing.ClassVar[str] = "mouse.scroll"

    steps: int
    horizontal: bool = False


# region Delay events

@_dataclass
class DelayTriggered(Event):
    type: typing.ClassVar[str] = "delay.triggered"

    delay_time: float
    current_time: float = _time.time()