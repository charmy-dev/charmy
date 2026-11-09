"""Shared pytest fixtures for Charmy's test suite.

Charmy's widget layer needs a `Window` to attach widgets to, and building a real one opens an SDL 
window. `HeadlessWindow` is a *genuine* `Window` subclass (so every `isinstance(parent, Window)` 
check inside Charmy still passes) whose `__init__` skips the backend completely. That makes the 
widget, container and profile layers testable without a display or an event loop.
"""

import itertools
import pathlib
import shutil
import tempfile

import pytest

from charmy.cm_object import CharmyObject
from charmy.event import EventHandling
from charmy.widgets.container import Container
from charmy.widgets.window import Window


class StubBackendBase:
    """Records the calls `WindowEntity` forwards to its backend, without touching SDL."""

    def __init__(self) -> None:
        self.background = None
        self.title = None
        self.icon = None
        self.pos = None
        self.size = None
        self.closed = False

    def set_pos(self, new):
        self.pos = new
        return self

    def set_size(self, new):
        self.size = new
        return self

    def set_title(self, new):
        self.title = new
        return self

    def set_icon(self, new):
        self.icon = new
        return self

    def show(self):
        return self

    def close(self):
        self.closed = True

    def update(self, *args, **kwargs):
        return self

    def draw_background(self):
        return self


class HeadlessWindow(Window):
    """A real `Window` with no SDL window behind it."""

    def __init__(self, size: tuple[int, int] = (320, 240), background=(255, 255, 255)) -> None:
        # Deliberately NOT calling Window.__init__ / WindowEntity.__init__: those create the backend
        CharmyObject.__init__(self)
        EventHandling.__init__(self)
        Container.__init__(self)
        # Minimal state the drawing and redraw bookkeeping expects
        self.backend_base = StubBackendBase()
        self._size = size
        self._pos = (0, 0)
        self._background = background
        self._drawing_list: list = []
        self._redraw_regions: list = [((0, 0), size)]
        self._requested_redraw_regions: list = []
        self._mouse_hovering_on: list = []
        self.visible = True


@pytest.fixture
def headless_window() -> HeadlessWindow:
    """A `Window` with no backend, suitable for widget tests."""
    return HeadlessWindow()


def _make_temp_dir() -> pathlib.Path:
    """Create a directory test files can actually be written to.

    The platform temp area is where pytest's own `tmp_path` lives, and some restricted environments 
    deny writes to it. Creating a directory there can even succeed while writing into it fails, so 
    the choice is verified with a probe file before it is used.
    """
    try:
        directory = pathlib.Path(tempfile.mkdtemp(prefix="charmy-test-"))
        probe = directory / ".write-probe"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
        return directory
    except OSError:
        fallback = pathlib.Path(__file__).parent / "_tmp_themes"
        fallback.mkdir(exist_ok=True)
        return fallback


@pytest.fixture
def theme_file():
    """Factory that writes a theme JSON file and returns its `pathlib.Path`."""
    directory = _make_temp_dir()
    created: list[pathlib.Path] = []
    counter = itertools.count()

    def make(content: str) -> pathlib.Path:
        path = directory / f"theme_{next(counter)}.json"
        path.write_text(content, encoding="utf-8")
        created.append(path)
        return path

    yield make

    for path in created:
        path.unlink(missing_ok=True)
    if directory.name.startswith("charmy-test-"):
        shutil.rmtree(directory, ignore_errors=True)
    else:
        try:
            directory.rmdir()  # Only succeeds when nothing else is left in there
        except OSError:
            pass
