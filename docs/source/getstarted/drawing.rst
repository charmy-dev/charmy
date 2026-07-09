自定义绘图
========================================

Charmy 的 **图形层** 提供了直接绘制线条、形状和文字的能力。
你可以直接使用 ``graphics`` 模块中的 ``DrawnLine`` 、 ``DrawnShape`` 、 ``DrawnText``
在窗口上绘制内容，无需通过控件。

基本概念
----------------------------------------

图形层位于后端层和控件层之间，三个核心类：

.. list-table::
   :header-rows: 1

   * - 类
     - 用途
     - 示例
   * - ``DrawnLine``
     - 绘制线条
     - 直线、折线、圆弧、贝塞尔曲线
   * - ``DrawnShape``
     - 绘制填充形状
     - 矩形、圆角矩形、多边形、SVG 路径
   * - ``DrawnText``
     - 绘制文字
     - 带样式的文字

所有 ``Drawn*`` 对象创建后需要调用 ``.draw()`` 才会实际加入渲染队列。

绘制线条
----------------------------------------

直线：

.. code-block:: python

   import charmy as cm

   window = cm.Window(size=(400, 300))

   # 直线 (Line)
   line = cm.graphics.DrawnLine(
       window,
       cm.styles.shape.Line([(50, 50), (200, 100)]),  # 起点→终点
       (255, 0, 0),       # 红色纹理（RGB）
       width=3            # 线宽
   ).draw()

折线：

.. code-block:: python

   # 折线 (PolyLine)
   polyline = cm.graphics.DrawnLine(
       window,
       cm.styles.shape.PolyLine([(50, 150), (150, 50), (250, 150), (350, 50)]),
       (0, 100, 255),     # 蓝色
       width=2
   ).draw()

圆弧：

.. code-block:: python

   # 圆弧 (CircleArc)
   #    参数: center, radius, start_orient, end_orient
   #    orient 0°=正上方, 顺时针递增
   arc = cm.graphics.DrawnLine(
       window,
       cm.styles.shape.CircleArc((200, 200), 80, 0, 270),  # 0°→270° 顺时针
       (0, 200, 0),       # 绿色
       width=4
   ).draw()

贝塞尔曲线：

.. code-block:: python

   # 三次贝塞尔曲线 (CubicBezier)
   #    参数: [起点, 控制点1, 控制点2, 终点]
   bezier = cm.graphics.DrawnLine(
       window,
       cm.styles.shape.CubicBezier([(50, 250), (100, 50), (250, 50), (300, 250)]),
       (200, 0, 200),     # 紫色
       width=3
   ).draw()

.. note::
   ``DrawnLine`` 的 ``width`` 参数控制线宽，单位为像素。
   纹理参数可以是 ``(R, G, B)`` 或 ``(R, G, B, A)`` 元组。

绘制形状
----------------------------------------

矩形：

.. code-block:: python

   # 填充矩形
   rect = cm.graphics.DrawnShape(
       window,
       cm.styles.shape.Rect((50, 50), (150, 100)),  # (左上角), (宽, 高)
       (255, 200, 0),      # 填充色
       border_width=3,     # 边框宽度 (0=无边框)
       border_texture=(100, 100, 100)  # 边框色
   ).draw()

圆角矩形：

.. code-block:: python

   # 圆角矩形，圆角半径 20px
   round_rect = cm.graphics.DrawnShape(
       window,
       cm.styles.shape.RoundRect((50, 50), (150, 100), 20),
       (200, 200, 255, 150),   # 半透明蓝色填充
       offset=(50, 100)        # 位置偏移
   ).draw()

多边形（任意形状）：

.. code-block:: python

   # 任意多边形通过 AnyShape 定义
   polygon = cm.graphics.DrawnShape(
       window,
       cm.styles.shape.AnyShape([
           cm.styles.shape.PolyLine([
               (100, 100), (150, 80), (180, 120),
               (140, 160), (80, 140), (100, 100)
           ])
       ]),
       (150, 150, 150),     # 灰色填充
       border_width=4,
       border_texture=(255, 0, 0)  # 红色边框
   ).draw()

.. tip::
   ``DrawnShape`` 的 ``border_width`` 参数：
   正值表示向外扩展边框，负值表示向内收缩。
   0 表示不绘制边框。

   **然而这一特性并未在Genesis中实现，也并未被设计为强制性需要被后端实现的功能。**

绘制文字
----------------------------------------

.. code-block:: python

   text = cm.graphics.DrawnText(
       window,
       "Hello, Charmy!",                         # 文字内容
       cm.styles.text_style.TextStyle(            # 文字样式
           font="Consolas",                       # 字体名
           size=24,                               # 字号
           weight=cm.styles.text_style.WEIGHT.BOLD, # 字重
           underlined=True,                       # 下划线
           italic=False                           # 斜体
       ),
       (0, 0, 0),         # 文字颜色
       offset=(50, 200)   # 位置
   ).draw()

.. note::
   Charmy 使用 Cairo 进行文字渲染，字体名需要是系统中已安装的字体。
   如果指定字体不存在，Cairo 会回退到默认字体。

透明度与纹理
----------------------------------------

纹理（Texture）是 Charmy 中控制颜色的统一方式：

.. code-block:: python

   from charmy.styles.texture import Color, Transparent

   # 纯色 (R, G, B, A)
   texture = Color((255, 0, 0, 200))     # 半透明红色

   # 透明（不绘制）
   transparent = Transparent()

   # 快捷方式：直接使用元组
   line = DrawnLine(window, shape, (255, 0, 0))         # RGB
   line = DrawnLine(window, shape, (255, 0, 0, 128))     # RGBA
   shape = DrawnShape(window, rect, (0, 255, 0, 100))    # 半透明绿色填充

偏移与锚点
----------------------------------------

``DrawnLine`` 和 ``DrawnShape`` 支持 ``offset`` 和 ``anchor`` 参数：

- **offset**: 整体位置的偏移量（相对于原始坐标）
- **anchor**: 锚点位置，即原始坐标中作为基准的点

.. code-block:: python

   # offset 将整个图形向右下偏移 (50, 50)
   shape = cm.graphics.DrawnShape(
       window,
       cm.styles.shape.Rect((0, 0), (100, 100)),
       (255, 0, 0),
       offset=(50, 50)       # 相当于将图形从 (0,0) 移到 (50,50)
   ).draw()

当 ``offset`` 或 ``anchor`` 设置为 ``"auto"`` 时，
会自动使用图形边界框的左上角作为默认值。

SVG 路径绘制
----------------------------------------

Charmy 内置了完整的 SVG 路径解析器，可以直接从 SVG 路径字符串创建形状：

.. code-block:: python

   from charmy.utils.svg import shapes_from_svg_path

   # SVG 路径字符串 → Charmy 形状
   path = "M 10 10 L 100 10 L 100 100 Z"  # 一个正方形
   shape = shapes_from_svg_path(path)

   # 绘制
   drawn = cm.graphics.DrawnShape(window, shape, (100, 200, 255)).draw()

支持的 SVG 命令： ``M`` （移动到）、 ``L`` （直线）、 ``V`` （垂直线）、
``H`` （水平线）、 ``C`` （三次贝塞尔曲线）、 ``S`` （平滑贝塞尔）、 ``Z`` （闭合路径）。

.. warning::
   SVG 解析器目前不支持二次贝塞尔曲线（ ``Q``/``T`` ）和椭圆弧（ ``A`` ）。

.. seealso::
   更多图形绘制 API 请参考 :doc:`graphics 模块 </api/graphics>`、
   :doc:`shape 模块 </api/styles/shape>` 和
   :doc:`texture 模块 </api/styles/texture>`。
