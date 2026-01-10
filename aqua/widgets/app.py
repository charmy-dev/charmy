import typing
import warnings

from ..const import UIFrame
from ..object import AqObject


class AqApp(AqObject):
    """The base of AqApp Class

    Attributes:
        ui.framework: What UI Framework will be used
        ui.is_vsync: Is vsync enabled
        ui.samples: UI Samples
    """

    def __init__(
        self,
        ui: UIFrame = UIFrame.GLFW,
        vsync: bool = True,
        samples: int = 4,
    ):
        super().__init__()

        if self.instance_count >= 1:
            warnings.warn("There should be only one instance of AqApp.")

        self.new("ui.framework", ui)
        self.new("ui.is_vsync", vsync)
        self.new("ui.samples", samples)

        self.new("windows", [])

        self._init_ui_framework()

    def _init_ui_framework(self):
        """According to attribute `ui.framework` to init ui framework"""
        match self.get("ui.framework"):
            case UIFrame.GLFW:
                import glfw

                if not glfw.init():
                    raise glfw.GLFWError("Init failed")

                glfw.window_hint(glfw.STENCIL_BITS, 8)
                glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
                glfw.window_hint(glfw.WIN32_KEYBOARD_MENU, True)
                glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, True)
                glfw.window_hint(glfw.SAMPLES, self.get("ui.samples"))
                glfw.set_error_callback(self.error)

    def run(self):
        if not self.get("windows"):
            warnings.warn(
                "At least one window is required to run application!",
            )

    @staticmethod
    def error(error_code: typing.Any, description: bytes):
        """
        处理GLFW错误

        :param error_code: 错误码
        :param description: 错误信息
        :return: None
        """
        raise f"GLFW Error {error_code}: {description.decode()}"
