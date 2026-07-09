第一个应用
==========

下面带你一步步创建第一个 Charmy 应用。

1. 导入 Charmy
--------------

.. code-block:: python

   import charmy as cm

2. 创建窗口
-----------

.. code-block:: python

   window = cm.Window(size=(400, 300), title="我的第一个 Charmy 应用")
   window.background = (230, 230, 230)  # 浅灰色背景

3. 添加按钮
-----------

.. code-block:: python

   def on_button_click():
       print("按钮被点击了！")

   button = cm.Button(window, text="点我", on_click=on_button_click)
   button.place((50, 50), (120, 40))

4. 运行应用
-----------

.. code-block:: python

   cm.mainloop()

完整的代码
----------

.. code-block:: python

   import charmy as cm

   def on_click():
       print("Hello from Charmy!")

   window = cm.Window(size=(400, 300), title="我的第一个 Charmy 应用")
   window.background = (230, 230, 230)

   button = cm.Button(window, text="点我", on_click=on_click)
   button.place((50, 50), (120, 40))

   cm.mainloop()

运行后你会看到一个浅灰色窗口，中间有一个按钮，点击按钮会在控制台输出 ``Hello from Charmy!``。
