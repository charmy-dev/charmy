# The Genesis Backend
# 2026 by XiangQinXi & rgzz666

# This is a backend for early development only! 
# It is also used as an example of developing a Charmy backend.

# Under dev

from dataclasses import dataclass
import glfw
import cairo
import typing
import sys
import ctypes
from OpenGL import GL as gl

from . import template


class Backend(template.Backend):
    """The Genesis backend."""

    name =          "genesis"
    friendly_name = "Genesis (early development)"
    version =       "0.1.0"
    author =        ["XiangQinXi", "rgzz666"]

    def __init__(self):
        """APIs are alised here."""
        super().__init__()

        self.WindowBase = WindowBase
    
    def backend_init(self, **kwargs) -> None:
        if not glfw.init():
            raise glfw.GLFWError("GLFW init failed")

        glfw.window_hint(glfw.STENCIL_BITS, 8)
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
        glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, True)
        glfw.window_hint(glfw.SAMPLES, kwargs.get("samples", 4))

        if sys.platform == "win32":
            glfw.window_hint(glfw.WIN32_KEYBOARD_MENU, True)

        if kwargs.get("error_callback", None):
            glfw.set_error_callback(kwargs["error_callback"])


@dataclass
class WindowSupportState(template.WindowSupportState):
    """Flags all supported features."""
    set_title               = True
    set_icon                = True
    resize                  = True
    set_scale_mode          = False
    set_background          = True
    translucent             = True
    set_state               = True
    fullscreen              = True
    customize_titlebar      = False

class WindowBase(template.WindowBase):
    """Window APIs in GLFW backend."""
    
    def __init__(self):
        """Creates a window."""
        super().__init__()

        self.supports = WindowSupportState()

        self.title = "Charmy GLFW Window"
        self.size = (540, 480)

        # mysterious optimization
        glfw.window_hint(glfw.CONTEXT_RELEASE_BEHAVIOR, glfw.RELEASE_BEHAVIOR_NONE)

        glfw.window_hint(glfw.STENCIL_BITS, 8)

        # see https://www.glfw.org/faq#macos
        if sys.platform == "darwin":
            glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, glfw.TRUE)
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        else:  # Windows / Linux
            glfw.window_hint(glfw.SCALE_TO_MONITOR, glfw.TRUE)

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2 if sys.platform == "darwin" else 3)

        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # create window
        self.window = glfw.create_window(self.size[0], self.size[1], self.title, None, None)

        if self.window == None:
            raise RuntimeError("Can't create window")
        
        # Initialize Cairo canvas
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size[0], self.size[1])
        self.cairo_context = cairo.Context(self.surface)

        # Initilize a OpenGL texture to draw Cairo stuff to window, vibed with Doubao
        # TODO: Vibed codes, needs to be checked.
        glfw.make_context_current (self.window)
        self._make_dummy_shader()

        self._vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self._vao)

        self._texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    
    def _make_dummy_shader(self):
        """Dummy shader to preent crash. Vibed with Doubao."""
        # 极简全屏贴图着色器（Core 必须）
        vert = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        frag = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

        gl.glShaderSource(vert, """#version 330
        layout(location=0) in vec2 p;
        out vec2 uv;
        void main(){
            gl_Position = vec4(p,0,1);
            uv = p*0.5+0.5;
        }""")

        gl.glShaderSource(frag, """#version 330
        in vec2 uv;
        uniform sampler2D tex;
        out vec4 c;
        void main(){
            c = texture(tex, vec2(uv.x, 1.0-uv.y));
        }""")

        # 编译+链接
        gl.glCompileShader(vert)
        gl.glCompileShader(frag)

        prog = gl.glCreateProgram()
        gl.glAttachShader(prog, vert)
        gl.glAttachShader(prog, frag)
        gl.glLinkProgram(prog)
        gl.glUseProgram(prog)

        # 固定全屏矩形顶点（只初始化一次）
        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        verts = [-1,-1, 1,-1, -1,1, 1,1]
        gl.glBufferData(gl.GL_ARRAY_BUFFER, (ctypes.c_float*len(verts))(*verts), gl.GL_STATIC_DRAW)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, False, 0, None)

    def show(self) -> typing.Self:
        """Show the window.

        Returns:
            self: The WindowBase itself.
        """
        glfw.show_window(self.window)
        return self

    def set_title(self, new: str) -> typing.Self:
        """Set window title."""
        glfw.set_window_title(self.window, new)
        return self
    
    def update(self):
        """Update the window.
        
        Returns:
            self: The WindowBase itself.
        """
        self.draw_frame()
        
        ## Dump Cairo contents to GLFW window, vibed with Doubao
        w, h = self.size

        # Cairo image to GL texture
        data = self.surface.get_data()
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA8, w, h, 0, gl.GL_BGRA, gl.GL_UNSIGNED_BYTE, data)

        # Full-screen rendering
        gl.glBindVertexArray(self._vao)
        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        ## Some normal update stuff
        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def draw_frame(self) -> None:
        self.cairo_context.set_source_rgb(1, 1, 1)
        self.cairo_context.paint()

        self.cairo_context.arc(270, 240, 80, 0, 6.28)
        self.cairo_context.set_source_rgb(1, 0, 0)
        self.cairo_context.fill()
    
    def mainloop(self):
        while not glfw.window_should_close(self.window):
            self.update()