窗口配置
========

你可以通过属性来读取和修改窗口的各项配置。

窗口标题
--------

.. code-block:: python

   window = cm.Window()
   window.title = "我的窗口"          # 设置标题
   print(window.title)               # 读取标题

窗口大小
--------

.. code-block:: python

   window.size = (800, 600)          # 设置大小 (width, height)
   print(window.size)                # 读取大小

窗口位置
--------

.. code-block:: python

   window.pos = (100, 100)           # 设置位置 (x, y)
   print(window.pos)                 # 读取位置

窗口背景
--------

背景色使用 (R, G, B) 或 (R, G, B, A) 元组表示：

.. code-block:: python

   window.background = (255, 255, 255)   # 白色背景
   window.background = (0, 0, 0, 200)    # 半透明黑色背景

窗口图标
--------

.. code-block:: python

   window.icon = "path/to/icon.png"   # 从文件设置
   # 或使用 bytes 数据
   with open("icon.png", "rb") as f:
       window.icon = f.read()
