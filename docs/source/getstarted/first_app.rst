第一个应用
==============================

下面带你一步步创建第一个 Charmy 应用。

1. 导入 Charmy
------------------------------

.. code-block:: python

   import charmy as cm

2. 创建窗口
------------------------------

有两种方式创建窗口：

.. code-block:: python

   # 方式一：直接创建 Window（推荐）
   window = cm.Window(size=(400, 300), title="我的窗口")

   # 方式二：先创建 WindowEntity 再转为 Window（内部使用）
   # window = cm.window.Window(size=(400, 300))

``Window`` 继承自 ``WindowEntity`` （后端窗口实体）+ ``Container`` （容器能力）。
大部分时候你只需要用 ``cm.Window()`` 。

设置窗口背景色：

.. code-block:: python

   window.background = (230, 230, 230)  # (R, G, B) 或 (R, G, B, A)

3. 添加按钮
------------------------------

.. code-block:: python

   def on_click():
       print("按钮被点击了！")

   button = cm.Button(window, text="点我", on_click=on_click)
   button.place((50, 50), (120, 40))  # place(pos, size)

``place()`` 方法的参数：

- 第一个参数 ``(x, y)`` ：控件在父容器中的位置（相对于父容器的偏移）
- 第二个参数 ``(width, height)`` （可选）：控件的尺寸

.. tip::
   也可以使用 ``with`` 语句上下文自动设置父容器：

   .. code-block:: python

      with window:
          button = cm.Button(text="点我")
          button.place((10, 10), (100, 30))

   在 ``with window:`` 块内创建的控件会自动以 ``window`` 为父容器。

4. 运行应用
------------------------------

.. code-block:: python

   cm.mainloop()

``mainloop()`` 会进入主事件循环，不断处理窗口事件和更新界面。
程序会一直运行直到所有窗口被关闭。

完整的代码
------------------------------

.. code-block:: python

   import charmy as cm

   def on_click():
       print("Hello from Charmy!")

   window = cm.Window(size=(400, 300), title="我的第一个 Charmy 应用")
   window.background = (230, 230, 230)

   button = cm.Button(window, text="点我", on_click=on_click)
   button.place((50, 50), (120, 40))

   cm.mainloop()

.. note::
   关于 Button 的已知限制：

   - Button 目前使用 Bootstrap 风格的默认样式（浅灰背景、黑色文字）
   - 悬停效果（暗色背景 + 白色文字）由事件系统驱动，需要鼠标事件正确传递
   - ``on_click`` 回调在 Button 初始化时绑定到 ``MouseClick`` 事件（条件：左键）
   - 目前 Button 不支持文本以外的内容（如图标）

更复杂的例子：绑定事件
------------------------------

Button 的 ``on_click`` 参数是最简单的用法。你也可以直接使用 ``bind()`` 方法：

.. code-block:: python

   import charmy as cm

   def on_enter(event):
       print("鼠标进入按钮区域")

   def on_leave(event):
       print("鼠标离开按钮区域")

   window = cm.Window(size=(300, 200))
   btn = cm.Button(window, text="跟踪鼠标")

   btn.bind(cm.event_types.MouseEnter, on_enter)
   btn.bind(cm.event_types.MouseLeave, on_leave)

   btn.place((50, 50), (120, 40))
   cm.mainloop()
