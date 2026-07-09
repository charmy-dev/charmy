抽象层
==============================

Charmy 采用 **三层架构** ，从下到上依次为：

- **后端层 (Backend Layer)** — SDL2 + Cairo (Genesis)
- **图形层 (Graphics Layer)** — DrawnShape, DrawnLine, DrawnText…
- **控件层 (Widget Layer)** — Button, Window, Frame…

为什么需要抽象层
------------------------------

不同的操作系统和图形库有不同的 API。为了让 Charmy 能 **跨平台** 运行，
并且能够在不同后端之间切换，我们需要将后端的具体实现抽象出来。

后端模块的划分
------------------------------

``charmy/backend/`` 目录下的模块：

.. list-table::
   :header-rows: 1

   * - 模块
     - 作用
   * - ``template.py``
     - 定义后端接口模板（抽象基类）
   * - ``genesis.py``
     - Genesis 后端的具体实现（SDL2 + Cairo）
   * - ``loader.py``
     - 后端加载器，根据名称动态加载后端
   * - ``utils.py``
     - 后端工具模块，安全引用 Charmy 上层对象，避免循环引入

后端模板 (template.py)
------------------------------

在 ``charmy/backend/template.py`` 中定义了所有后端的接口模板：

.. code-block:: python

   class Backend:
       name: str                      # 后端标识名
       friendly_name: str             # 可读名称
       WindowBase: type[WindowBase]   # 窗口操作
       LineBase: type[LineBase]       # 线条绘制
       ShapeBase: type[ShapeBase]     # 形状绘制
       TextureBase: type[TextureBase] # 纹理处理
       TextBase: type[TextBase]       # 文字绘制

每个 ``*Base`` 类都有一个 ``supports`` 属性，声明后端支持哪些特性：

.. code-block:: python

   class WindowSupportState(SupportState):
       set_title: bool = False        # 是否支持修改标题
       set_icon: bool = False         # 是否支持修改图标
       set_pos: bool = False          # 是否支持移动窗口
       set_size: bool = False         # 是否支持调整大小
       transparent: bool = False      # 是否支持透明度
       fullscreen: bool = False       # 是否支持全屏

这种设计 allows Charmy 在运行时查询后端能力，选择最优的绘制方式。

.. warning::
   后端模板中使用了一个**循环引用设计**：

   .. code-block:: python

      class WhateverBase:
          Backend: type[Backend] = Backend  # 引用 Backend 类

   每个 ``*Base`` 类持有 ``Backend`` 类引用，而 ``Backend`` 类又持有
   各个 ``*Base`` 类引用。这是为了方便后端内部调度，但会导致
   **Sphinx autodoc 在生成文档时出现递归深度溢出**。
   解决方案见 ``docs/source/conf.py`` 中的 ``_skip_circular_refs`` 函数。

Genesis 后端
------------------------------

目前唯一的后端实现，使用 **SDL2** 创建和管理窗口，使用 **Cairo** 进行 2D 渲染。这一后端为Charmy的上层部分提供一套
可用于可行性验证的API，而并非一个合格且正式的后端选项。您不应该在生产环境内使用它。

**SDL2 负责：**

- 窗口创建与管理
- 事件循环（鼠标、键盘、窗口事件）
- 像素缓冲区管理（SDL Surface）
- 窗口刷新 (SDL_UpdateWindowSurface)

**Cairo 负责：**

- 矢量图形渲染（线条、形状、贝塞尔曲线）
- 文字渲染
- 图像合成

.. note::
   Genesis 后端的一个设计特点是：Cairo 绘制到内存中的 ``ImageSurface``，
   然后通过 ``ctypes.memmove`` 直接拷贝到 SDL2 的窗口 Surface。
   这种方式避免了额外的编码/解码开销，性能较好。

   这一特性是为了拯救Genesis后端那本就不充裕的性能。

事件桥接
------------------------------

Genesis 后端通过 ``sdl2_handle_event()`` 方法将 SDL2 的事件转换为 Charmy 事件：

.. code-block:: python

   # genesis.py (简化)
   def sdl2_handle_event(self, event):
       match event.type:
           case sdl2.SDL_MOUSEMOTION:
               self.charmy_window.trigger(MouseMove(...))
           case sdl2.SDL_MOUSEBUTTONDOWN:
               self.charmy_window.trigger(MousePress(...))
           case sdl2.SDL_MOUSEBUTTONUP:
               self.charmy_window.trigger(MouseRelease(...))
           case sdl2.SDL_WINDOWEVENT:
               # 处理窗口大小变化、移动、焦点事件
               ...
           case sdl2.SDL_QUIT:
               self.charmy_window.destroy()

渲染流程
------------------------------

完整的帧渲染流程：

::

   mainloop() 每帧调用
      │
      ▼
   Window.update()
      │
      ├─ Widget.draw() → 控件更新图形对象
      │     ├─ Button: 更新 DrawnShape + DrawnText
      │     └─ Container: 递归绘制所有子控件
      │
      ├─ Window.draw_frame()
      │     ├─ 绘制背景
      │     ├─ 绘制所有 DrawnLine
      │     ├─ 绘制所有 DrawnShape
      │     └─ 绘制所有 DrawnText
      │
      ├─ Cairo 渲染到 ImageSurface
      │
      ├─ ctypes.memmove → SDL2 Surface
      │
      └─ SDL_UpdateWindowSurface → 屏幕显示

Fallback 机制
------------------------------

Charmy 的线条和形状系统支持 **fallback** ——如果后端不支持某种图形类型，
会自动降级为其他类型绘制。

例如，Genesis 后端支持 ``CircleArc`` （圆弧）的直接绘制，
但如果某个假想的后端只支持 ``CubicBezier`` （三次贝塞尔曲线），
Charmy 会自动将圆弧分解为多条贝塞尔曲线：

.. code-block:: python

   # 用户代码（不关心后端是否支持）
   arc = cm.styles.shape.CircleArc(center=(100, 100), radius=50,
                                    start_orient=0, end_orient=270)
   cm.graphics.DrawnLine(window, arc, (255, 0, 0)).draw()

Fallback 链示例：

::

   CircleArc → 不支持 → CubicBezier(s) → 还不支持？ → PolyLine(s)
                                                              ↓
                                                        Line(s)
                                                              ↓
                                                       警告：无法绘制

这种机制于 ``shape.py`` 中每个线条类的 ``fallback()`` 方法中实现：

.. code-block:: python

   class CircleArc(Curve):
       def fallback(self, _from=[]):
           # 转换为多次贝塞尔曲线
           return [CubicBezier(...), CubicBezier(...), ...]

.. tip::

   如果您是一位足够偷懒的后端开发者，您只需要确保后端支持绘制直线和三次贝塞尔曲线，就可以透过此fallback机制绘制
   Charmy中的任何线条了。

更多细节请参考 ``charmy/backend/`` 目录下的源代码和 ``tests/`` 目录下的测试文件。
