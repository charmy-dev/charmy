事件处理
========================================

Charmy 的事件系统采用 **发布-订阅模式** ，控件可以"监听"特定事件并做出响应。

基本用法
----------------------------------------

使用 ``bind()`` 方法将事件绑定到回调函数：

.. code-block:: python

   import charmy as cm

   window = cm.Window(size=(400, 300))

   def on_click(event):
       print("Clicked")

   button = cm.Button(window, text="Click me!")
   button.bind(cm.event_types.MouseClick, on_click)
   button.place((50, 50), (120, 40))

   cm.mainloop()

``bind()`` 的参数：

- **event_type**: 事件类型类（如 ``MouseClick`` 、 ``MouseMove`` ）
- **target**: 回调函数，接收一个事件对象作为参数
- **conditions** （可选）: 过滤条件字典
- **multithread** （可选）: 是否在独立线程中执行
- **task_obj_receiver** （可选）：
  如果提供一个 ``Var`` 对象，将设定该对象值为该事件的 ``EventTask`` ，用于解绑。

.. note::
   ``Button`` 的 ``on_click`` 参数只是 ``bind()`` 的语法糖，
   内部已经绑定了 ``MouseClick`` 事件。

装饰器写法 ``@widget.on()``
----------------------------------------

除了 ``bind()`` 方法，还可以用 ``@widget.on()`` **装饰器** 来注册事件：

.. code-block:: python

   import charmy as cm

   window = cm.Window(size=(400, 300))
   button = cm.Button(window, text="decorator")
   button.place((50, 50), (120, 40))

   @button.on(cm.event_types.MouseClick)
   def handle_click(event):
       print(f"Button is clicked : {event.mouse_pos}")

   cm.mainloop()

``on()`` 也支持条件过滤和多线程参数：

.. code-block:: python

   # 只响应鼠标左键
   @button.on(cm.event_types.MouseClick, conditions={"button": 0})
   def left_click(event):
       print("Left click")

   # 响应右键（button=2），且启用多线程
   @button.on(cm.event_types.MouseClick, conditions={"button": 2}, multithread=True)
   def right_click(event):
       print("Right click (multithreaded)")

.. tip::
   装饰器方式适合让代码更紧凑。内部实现其实就是调用 ``bind()``：

   .. code-block:: python

      # 以下两种写法等价

      # 写法 A：装饰器
      @button.on(cm.event_types.MouseClick)
      def handler(event):
          ...

      # 写法 B：bind()
      def handler(event):
          ...
      button.bind(cm.event_types.MouseClick, handler)

事件对象
----------------------------------------

回调函数接收到的事件对象包含事件的详细信息：

.. code-block:: python

   def on_mouse_move(event):
       print(f"Mouse Pos: {event.mouse_pos}")
       print(f"Source: {event.subject}")

   window.bind(cm.event_types.MouseMove, on_mouse_move)

常用事件属性：

.. list-table::
   :header-rows: 1

   * - 事件类型
     - 属性
     - 说明
   * - ``MouseMove``
     - ``mouse_pos``, ``subject``
     - 鼠标位置、所属窗口
   * - ``MousePress``
     - ``mouse_pos``, ``button``
     - 位置、按下的按键 (0=左, 1=中, 2=右)
   * - ``MouseRelease``
     - ``mouse_pos``, ``button``
     - 位置、释放的按键
   * - ``MouseClick``
     - ``mouse_pos``, ``button``
     - 位置、点击的按键
   * - ``MouseEnter``
     - ``subject``
     - 鼠标进入控件
   * - ``MouseLeave``
     - ``subject``
     - 鼠标离开控件
   * - ``WidgetResize``
     - ``new_size``
     - 新大小 ``(width, height)``
   * - ``WidgetMove``
     - ``new_pos``
     - 新位置 ``(x, y)``

条件过滤
----------------------------------------

只当满足某些条件时才执行回调：

.. code-block:: python

   # 只响应鼠标左键点击
   button.bind(cm.event_types.MouseClick, on_left_click,
               conditions={"button": 0})

   # 只响应鼠标右键点击
   button.bind(cm.event_types.MouseClick, on_right_click,
               conditions={"button": 2})

   # 右键也触发 context_menu
   button.bind(cm.event_types.MouseClick, show_context_menu,
               conditions={"button": 2})

事件链
----------------------------------------

某些事件会自动级联触发其他事件：

::

   鼠标在按钮上按下 (MousePress) → 按钮接收 MousePress
   鼠标在按钮上释放 (MouseRelease) → 按钮接收 MouseRelease
       ↓
   如果 MousePress 和 MouseRelease 发生同一控件上 → 触发 MouseClick
       ↓
   执行 on_click() 回调

鼠标悬停跟踪：

::

   MouseMove
     ├─ 对鼠标位置下的所有控件触发 MouseMove 事件
     ├─ 鼠标新进入的控件 → 触发 MouseEnter
     └─ 鼠标离开的控件 → 触发 MouseLeave

这意味着你不需要手动计算鼠标是否在控件范围内，Charmy 会自动处理：

.. code-block:: python

   button.bind(cm.event_types.MouseEnter, lambda e: print("Entered"))
   button.bind(cm.event_types.MouseLeave, lambda e: print("Left"))

解绑事件
----------------------------------------

``bind()`` 会返回一个 ``EventTask`` 对象，可以用它来解绑：

.. code-block:: python

   task = button.bind(cm.event_types.MouseClick, on_click)

   # 后续解绑
   button.unbind(task)

   # 或清除所有非内部绑定
   button.clear_bind()

如果是直接使用@button.on()装饰器绑定的事件，也可以通过 ``task_obj_receiver`` 参数获取 ``EventTask`` 对象：

.. code-block:: python

   task_var = cm.Var()

   @button.on(cm.event_types.MouseClick, task_obj_receiver=task_var)
   def on_click(event):
       print("Clicked")

   # 后续解绑
   button.unbind(task_var.value)

多线程事件
----------------------------------------

.. caution::
   多线程支持处于 **实验阶段** 。

对于耗时操作，可以启用多线程避免阻塞 UI：

.. code-block:: python

   def heavy_work(event):
       import time
       time.sleep(3)           # 模拟耗时操作
       print("Done.")

   button.bind(cm.event_types.MouseClick, heavy_work,
               multithread=True)

.. warning::
   多线程回调中 **不要直接操作 UI 对象** （如修改控件属性、创建窗口等）。
   如果需要更新 UI，请通过事件机制传递消息（暂未实现，敬请期待）。

窗口事件
----------------------------------------

窗口本身也是事件源：

.. code-block:: python

   window.bind(cm.event_types.WidgetResize, lambda e: print(f"resize {e.new_size}"))
   window.bind(cm.event_types.WidgetMove, lambda e: print(f"moved {e.new_pos}"))
   window.bind(cm.event_types.FocusGain, lambda e: print("focus gained"))
   window.bind(cm.event_types.FocusLoss, lambda e: print("focus lost"))

内部事件与用户事件
----------------------------------------

Charmy 的控件内部也会使用 ``bind()`` 来实现自身行为。
例如，Button 内部绑定了以下事件：

.. code-block:: python

   # Button.__init__ 内部（简化）
   self.bind(MouseClick, lambda _: self.on_click(),
             {"button": 0}, _is_internal=True)
   self.bind(MouseEnter, lambda _: self.config(state="hover"),
             _is_internal=True)
   self.bind(MouseLeave, lambda _: self.config(state="normal"),
             _is_internal=True)

这些内部绑定使用 ``_is_internal=True`` 标记。当调用 ``clear_bind()`` 时，
内部绑定会被保留，只有用户绑定被清除。

可用的事件类型一览
----------------------------------------

.. code-block:: python

   # 控件事件
   cm.event_types.WidgetUpdate     # 控件更新
   cm.event_types.WidgetDraw       # 控件重绘
   cm.event_types.WidgetConfigure  # 配置改变（位置、大小等）
   cm.event_types.WidgetResize     # 大小改变
   cm.event_types.WidgetMove       # 位置改变
   cm.event_types.WidgetDestroy    # 销毁

   # 焦点事件
   cm.event_types.FocusGain        # 获得焦点
   cm.event_types.FocusLoss        # 失去焦点

   # 鼠标事件
   cm.event_types.MouseMove        # 鼠标移动
   cm.event_types.MousePress       # 鼠标按下
   cm.event_types.MouseRelease     # 鼠标释放
   cm.event_types.MouseClick       # 鼠标点击
   cm.event_types.MouseEnter       # 鼠标进入
   cm.event_types.MouseLeave       # 鼠标离开
   cm.event_types.MouseScroll      # 滚轮

   # 通用事件
   cm.event_types.EventTriggered   # 任何事件发生时触发

.. seealso::
   更详细的事件类型定义请参考 :doc:`event_types API 文档 </api/utils/event_types>`。
