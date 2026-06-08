from __future__ import annotations as _

import typing as _typing

from dataclasses import dataclass as _dataclass
import time as _time

from ..event import EventHandling as _EventHandling
from ..cm_object import CharmyObject as _CharmyObject
from . import type_checking as _type_checking

if _typing.TYPE_CHECKING:
    from ..event import EventHandling as _EventHandling
    from ..styles import shape as _shape
    from ..widgets import widget as _widget, container as _container
    from ..widgets import window as _window


# region Base class & generic classes

@_dataclass
class Event(_CharmyObject):
    """Used to represent an event. Can be regarded as a placeholder if directly used."""
    type: _typing.ClassVar[str] = "noevent"

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


@_dataclass
class EventTriggered(Event):
    """Triggered when any other kind of event is triggered."""
    type: _typing.ClassVar[str] = "event_triggered"

    subject: _EventHandling

    def call_chain(self, _: _EventHandling) -> None:
        pass


# region Widget events

@_dataclass
class WidgetEvent(Event):
    """The type of events that represents widget events.

    Notes on Param `subject`
    ------------------------
    `subject` should be the widget that is triggered the event.
    """
    type: _typing.ClassVar[str] = "widget"

    subject: _EventHandling

@_dataclass
class WidgetUpdate(WidgetEvent):
    """Will be generated when a widget or window is updated.

    Note on Param `subject`
    -----------------------
    When `subject` is set to none, it means Charmy's global update routine is triggered.
    """
    type: _typing.ClassVar[str] = "widget.update"

    subject: _EventHandling | None
    redraw: bool | _shape.ShapeRange = False

@_dataclass
class WidgetDraw(WidgetEvent):
    """Will be generated when a widget or window is redrawn."""
    type: _typing.ClassVar[str] = "widget.draw"

    pos: _shape.Point = (0, 0)
    size: _shape.Size = (0, 0)

@_dataclass
class WidgetConfigure(WidgetEvent):
    """Will be generated when a widget or window has its configuration changed."""
    type: _typing.ClassVar[str] = "widget.configure"

    attrs_changed: dict

    def call_chain(self, subject: _EventHandling) -> None:
        super().call_chain(subject)
        if "pos" in self.attrs_changed.keys():
            subject.trigger(WidgetMove(subject, self.attrs_changed["pos"]))
        if "size" in self.attrs_changed.keys():
            subject.trigger(WidgetResize(subject, self.attrs_changed["size"]))

@_dataclass
class WidgetResize(WidgetEvent):
    """Will be generated when a widget or window is resized."""
    type: _typing.ClassVar[str] = "widget.resize"

    new_size: _shape.Size
    old_size: _typing.Optional[_shape.Size] = None

@_dataclass
class WidgetMove(WidgetEvent):
    """Will be generated when a widget or window is moved."""
    type: _typing.ClassVar[str] = "widget.move"

    new_pos: _shape.Point
    old_pos: _typing.Optional[_shape.Point] = None

@_dataclass
class FocusGain(WidgetEvent):
    """Will be generated when a widget or window gained focus."""
    type: _typing.ClassVar[str] = "widget.focus_gain"

@_dataclass
class FocusLoss(WidgetEvent):
    """Will be generated when a widget or window lose focus."""
    type: _typing.ClassVar[str] = "widget.focus_loss"

@_dataclass
class WidgetDestroy(WidgetEvent):
    """Will be generated when a widget or window is destroyed."""
    type: _typing.ClassVar[str] = "widget.destroy"


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
if _typing.TYPE_CHECKING:
    _HoveringList: _typing.TypeAlias = _typing.List[_widget.Widget | _container.Container]

@_dataclass
class MouseRawEvent(Event):
    """The type of events that represents mouse actions.

    Notes on Param `subject`
    ------------------------
    `subject` should be the window that detected the mouse event.
    """
    type: _typing.ClassVar[str] = "mouse"
    subject: _window.WindowEntity
    mouse_pos: _shape.Point

    def call_chain(self, subject: _EventHandling) -> None:
        if isinstance(subject, _type_checking.ContainerLike):
            hovering = subject.get_mouse_hover(self.mouse_pos)
            self.subject._mouse_hovering_on = hovering.copy()
            hovering.pop(0) # Ignore subject
            for item in hovering:
                if isinstance(item, _EventHandling):
                    item.trigger(self)

@_dataclass
class MouseMove(MouseRawEvent):
    """Will be generated when mouse movement is detected."""
    type: _typing.ClassVar[str] = "mouse.move"

    def call_chain(self, subject: _EventHandling):
        last_hovering = self.subject._mouse_hovering_on.copy()
        super().call_chain(subject)
        if not subject._mouse_hovering:
            if isinstance(subject, _EventHandling):
                subject._mouse_hovering = True
                subject.trigger(MouseEnter(subject, self))
        if subject is self.subject:
            for item in last_hovering:
                if item not in self.subject._mouse_hovering_on:
                    if isinstance(item, _EventHandling):
                        item._mouse_hovering = False
                        item.trigger(MouseLeave(subject, self))

@_dataclass
class MousePress(MouseRawEvent):
    """Will be generated when a mouse button is pressed."""
    type: _typing.ClassVar[str] = "mouse.press"

    button: int

    def call_chain(self, subject: _EventHandling):
        subject._mouse_pressed_buttons.append(self.button)
        super().call_chain(subject)

@_dataclass
class MouseRelease(MouseRawEvent):
    """Will be generated when a mouse button is released."""
    type: _typing.ClassVar[str] = "mouse.release"

    button: int

    def call_chain(self, subject: _EventHandling):
        if self.button in subject._mouse_pressed_buttons:
            subject.trigger(MouseClick(subject, self, self.button))
            subject._mouse_pressed_buttons.remove(self.button)
        super().call_chain(subject)

@_dataclass
class MouseScroll(MouseRawEvent):
    """Will be generated when a mouse button is released."""
    type: _typing.ClassVar[str] = "mouse.scroll"

    steps: int
    horizontal: bool = False

@_dataclass
class MouseInteractEvent(Event):
    """Will be generated when the mouse interacts with an EventHandling."""
    type: _typing.ClassVar[str] = "mouse_interact"
    subject: _EventHandling
    recent_raw_event: MouseRawEvent

@_dataclass
class MouseEnter(MouseInteractEvent):
    """Will be generated when the mouse enters an EventHandling."""
    type: _typing.ClassVar[str] = "mouse_interact.enter"

@_dataclass
class MouseLeave(MouseInteractEvent):
    """Will be generated when the mouse enters an EventHandling."""
    type: _typing.ClassVar[str] = "mouse_interact.leave"

@_dataclass
class MouseClick(MouseInteractEvent):
    """Will be generated when the mouse clicks an EventHandling."""
    type: _typing.ClassVar[str] = "mouse_interact.click"
    button: int

# region Delay events

@_dataclass
class DelayTriggered(Event):
    type: _typing.ClassVar[str] = "delay.triggered"

    delay_time: float
    current_time: float = _time.time()