import typing

from dataclasses import dataclass as _dataclass
import time as _time

from ..object import CharmyObject as _CharmyObject

if typing.TYPE_CHECKING:
    from ..event import EventHandling
    from ..styles import shape
    from ..widgets import window


# region base class

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

Event.latest = Event()


# region Widget events

@_dataclass
class WidgetEvent(Event):
    """The type of events that represents widget events.

    Notes on Param `subject`
    ------------------------
    `subject` should be the widget that is triggered the event.
    """
    type: typing.ClassVar[str] = "widget"

    subject: EventHandling

@_dataclass
class UpdateEvent(WidgetEvent):
    """Will be generated when a widget or window is updated.

    Note on Param `subject`
    -----------------------
    When `subject` is set to none, it means Charmy's global update routine is triggered.
    """
    type: typing.ClassVar[str] = "widget.update"

    subject: EventHandling | None
    redraw: bool | shape.ShapeRange = False

@_dataclass
class DrawEvent(WidgetEvent):
    """Will be generated when a widget or window is redrawn."""
    type: typing.ClassVar[str] = "widget.draw"

    pos: shape.Point = (0, 0)
    size: shape.Size = (0, 0)

@_dataclass
class ConfigureEvent(WidgetEvent):
    """Will be generated when a widget or window has its configuration changed."""
    type: typing.ClassVar[str] = "widget.configure"

    attrs_changed: dict

@_dataclass
class ResizeEvent(WidgetEvent):
    """Will be generated when a widget or window is resized."""
    type: typing.ClassVar[str] = "widget.resize"

    new_size: shape.Size
    old_pos: typing.Optional[shape.Size]

@_dataclass
class MoveEvent(WidgetEvent):
    """Will be generated when a widget or window is moved."""
    type: typing.ClassVar[str] = "widget.move"

    new_pos: shape.Point
    old_pos: typing.Optional[shape.Point]

@_dataclass
class FocusGain(Event):
    """Will be generated when a widget or window gained focus."""
    type: typing.ClassVar[str] = "widget.focus_gain"

@_dataclass
class FocusLoss(Event):
    """Will be generated when a widget or window lose focus."""
    type: typing.ClassVar[str] = "widget.focus_loss"


# region Mouse events

@_dataclass
class MouseEvent(Event):
    """The type of events that represents mouse actions.

    Notes on Param `subject`
    ------------------------
    `subject` should be the window that detected the mouse event.
    """
    subject: window.WindowEntity
    mouse_pos: shape.Point

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