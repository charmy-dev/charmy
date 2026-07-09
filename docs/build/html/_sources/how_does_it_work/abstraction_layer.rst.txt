抽象层
======

Charmy 采用**三层架构**，从下到上依次为：

- **后端层 (Backend Layer)** — SDL2 + Cairo (Genesis)
- **图形层 (Graphics Layer)** — DrawnShape, DrawnLine, DrawnText…
- **控件层 (Widget Layer)** — Button, Window, Frame…

为什么需要抽象层
--------------

不同的操作系统和图形库有不同的 API。为了让 Charmy 能**跨平台**运行，
并且能够在不同后端之间切换，我们需要将后端的具体实现抽象出来。

后端模板
--------

在 ``charmy/backend/template.py`` 中定义了所有后端的接口模板：

.. code-block:: python

   class Backend:
       WindowBase: type[WindowBase]   # 窗口操作
       LineBase: type[LineBase]       # 线条绘制
       ShapeBase: type[ShapeBase]     # 形状绘制
       TextureBase: type[TextureBase] # 纹理处理
       TextBase: type[TextBase]       # 文字绘制

每个具体的后端（如 Genesis）必须实现这些接口。

Genesis 后端
-----------

目前唯一的后端实现，使用 **SDL2** 创建和管理窗口，使用 **Cairo** 进行 2D 渲染。

- **SDL2** 负责：窗口创建、事件循环、像素缓冲区管理
- **Cairo** 负责：矢量图形渲染、文字渲染、图像合成

渲染流程
--------

::

   控件 → 图形对象 (DrawnShape/DrawnLine/DrawnText)
      ↓
   后端 ShapeBase/LineBase/TextBase
      ↓
   Cairo 绘制到 ImageSurface
      ↓
   ctypes.memmove 拷贝到 SDL2 surface
      ↓
   SDL_UpdateWindowSurface 刷新显示

Fallback 机制
------------

Charmy 的线条和形状系统支持 **fallback**——如果后端不支持某种图形类型，
会自动降级为其他类型绘制。例如，如果后端不支持椭圆弧，它会被分解为
多条三次贝塞尔曲线来近似绘制。

.. code-block:: python

   # 后端不支持 CircleArc → 自动 fallback 到 CubicBezier 序列
   arc = cm.styles.shape.CircleArc(center=(100, 100), radius=50,
                                    start_orient=0, end_orient=270)
   cm.graphics.DrawnLine(window, arc, (255, 0, 0)).draw()

更多细节请参考 ``charmy/backend/`` 目录下的源代码和测试文件。
