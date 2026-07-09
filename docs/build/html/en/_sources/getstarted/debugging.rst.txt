调试与故障排查
========================================

Charmy 提供了一些调试工具来帮助你排查问题。

调试标志
----------------------------------------

在 ``cm.const.DEBUG_FLAGS`` 中提供了几个调试开关：

.. code-block:: python

   import charmy as cm

   # ── 1. 显示控件边界框 ─────────────────────────────────
   # 每个控件的边界会显示为红色半透明矩形
   cm.const.DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY = True

   # ── 2. 降低帧率便于观察 ───────────────────────────────
   # 每帧后等待 0.5 秒，方便观察绘制过程
   cm.const.DEBUG_FLAGS.WAIT_AFTER_EACH_FRAME = True

   # 也可以设置为自定义秒数
   cm.const.DEBUG_FLAGS.WAIT_AFTER_EACH_FRAME = 0.1   # 每秒约 10 帧

   # ── 3. 标记重绘区域 ─────────────────────────────────
   # 每次重绘的区域会显示为紫色半透明矩形
   cm.const.DEBUG_FLAGS.MARK_REDRAWS = True

   # 在设置调试标志后再创建窗口
   window = cm.Window(size=(400, 300))
   button = cm.Button(window, text="调试")
   button.place((50, 50), (120, 40))
   cm.mainloop()

Genesis 后端调试标志
----------------------------------------

Genesis 后端（ ``charmy/backend/genesis.py`` ）也有自己的调试标志：

.. code-block:: python

   from charmy.backend import genesis

   # 绘制文字边界框（红色半透明）
   genesis.DEBUG_FLAGS.DRAW_CAIRO_STOCK_TEXT_BOUND = True

   # 强制闭合形状
   genesis.DEBUG_FLAGS.FORCE_CLOSE_SHAPE = True

   # 观察形状绘制过程（会逐步绘制每条边）
   genesis.DEBUG_FLAGS.OBSERVE_SHAPE_DRAWING = True

   # 检查形状是否闭合（检测不连续的点）
   genesis.DEBUG_FLAGS.WARN_UNCLOSED_SHAPES = True

.. warning::
   这些调试标志会显著影响性能，只应在调试时使用。

运行测试用例
----------------------------------------

项目 ``tests/`` 目录下有一些手动测试脚本，可以用来验证功能是否正常：

.. code-block:: shell

   # 图形绘制测试（绘制线条、形状、文字）
   python tests/graphics.py

   # Button 测试
   python tests/button.py

   # 事件系统测试
   python tests/event.py

   # SVG 路径解析测试
   python tests/svg.py

   # 形状碰撞检测测试
   python tests/shape_hit_test.py

常见问题
----------------------------------------

**Q: 窗口不显示**

A: 检查是否调用了 ``cm.mainloop()`` 。如果没有主循环，程序会立即退出。

**Q: 窗口显示了但按钮不响应点击**

A: 可能的原因：

1. 确认按钮在窗口的可视范围内
2. 检查按钮尺寸是否太小
3. 事件循环需要正常工作——确认 SDL2 事件被正确接收
4. 测试事件是否传递： ``window.bind(cm.event_types.MouseClick, lambda e: print(f"点击 {e.mouse_pos}"))``
5. 如果还没绑定事件，请通过 ``bind()`` 方法绑定，而不是直接调用 ``on_click``
6. 检查是否有其他控件覆盖在按钮上方

**Q: 点击按钮没有调用 on_click**

A: Button 的 ``on_click`` 参数在初始化时绑定到 ``MouseClick`` 事件，
条件是 ``{"button": 0}`` （鼠标左键）。确保：

1. 鼠标事件被正确桥接到 Charmy（确认 Genesis 后端的 ``sdl2_handle_event()`` 在工作）
2. 按钮没有被其他控件遮挡
3. 在 ``on_click`` 之前没有抛出异常

**Q: 窗口闪烁或绘制异常**

A: 可能的原因：

1. 检查是否有多个窗口同时更新
2. 减少每帧的重绘区域数量
3. 确认 Cairo 和 SDL2 的尺寸一致
4. 尝试启用 ``DEBUG_FLAGS.MARK_REDRAWS`` 观察重绘区域

**Q: 出现 ``RecursionError`` 或 ``Recursion depth exceeded``**

A: 这通常是由于后端类之间的循环引用导致的：

::

   Backend.WindowBase.Backend.WindowBase... 无限链

文档构建时已在 ``conf.py`` 中设置了 ``sys.setrecursionlimit(5000)`` 来解决。
如果运行其他脚本时遇到此问题，也需要增加递归限制。

**Q: ``import charmy`` 报错 ``No module named 'sdl2'``**

A: 未安装 SDL2 依赖。执行 ``pip install pysdl2 pysdl2-dll`` 。

**Q: ``import charmy`` 报错 ``No module named 'cairo'``**

A: 未安装 Cairo 依赖。执行 ``pip install pycairo`` 。

**Q: 如何查看控件之间的覆盖关系？**

A: 启用 ``DRAW_OBJECTS_BOUNDARY`` 调试标志，
Charmy 会为每个控件绘制红色边界框，方便观察控件位置和大小。

**Q: 如何查看事件触发的顺序？**

A: 在事件回调中添加打印语句来跟踪：

.. code-block:: python

   button.bind(cm.event_types.MousePress, lambda e: print(f"按下: {e.button}"))
   button.bind(cm.event_types.MouseRelease, lambda e: print(f"释放: {e.button}"))
   button.bind(cm.event_types.MouseClick, lambda e: print(f"点击: {e.button}"))
   button.bind(cm.event_types.MouseEnter, lambda e: print("进入"))
   button.bind(cm.event_types.MouseLeave, lambda e: print("离开"))

结合 ``mainloop(0.5)`` 降低帧率，可以清晰地观察事件触发顺序。

配置文件参考
----------------------------------------

.. list-table::
   :header-rows: 1

   * - 文件/模块
     - 用途
   * - ``charmy/const.py``
     - 全局常量、DEBUG_FLAGS
   * - ``charmy/backend/genesis.py``
     - Genesis 后端、后端级 DEBUG_FLAGS
   * - ``charmy/event.py``
     - 事件处理系统
   * - ``charmy/graphics.py``
     - 图形层对象
   * - ``charmy/styles/shape.py``
     - 线条和形状定义
   * - ``charmy/styles/texture.py``
     - 纹理和颜色定义
