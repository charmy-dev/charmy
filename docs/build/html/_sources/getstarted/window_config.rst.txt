窗口配置
==============================

你可以通过属性来读取和修改窗口的各项配置。所有属性修改会**实时同步**到后端窗口。

.. caution::
   窗口属性必须在 ``mainloop()`` 之前或事件回调中设置。
   如果在主循环运行期间从非 UI 线程修改属性，可能导致未定义行为。

窗口标题
------------------------------

.. code-block:: python

   window = cm.Window()
   window.title = "我的窗口"          # 设置标题，立即更新窗口标题栏
   print(window.title)               # 读取当前标题

窗口大小
------------------------------

.. code-block:: python

   window.size = (800, 600)          # 设置大小 (width, height)
   print(window.size)                # 读取大小

.. note::
   修改 ``size`` 属性会触发后端的 ``set_size()`` 方法，同时重新初始化 Cairo 画布
   （调用 ``cairo_reinit_surface()``）。因此窗口上已有的绘制内容会被清空。

窗口位置
------------------------------

.. code-block:: python

   window.pos = (100, 100)           # 设置位置 (x, y)，相对于屏幕左上角
   print(window.pos)                 # 读取位置

.. note::
   窗口位置由后端 SDL2 管理，``pos`` setter 会调用 ``SDL_SetWindowPosition``。
   Genesis 后端会在窗口初始化时自动同步 SDL2 的窗口位置到 Charmy。

窗口背景
------------------------------

背景使用 (R, G, B) 或 (R, G, B, A) 元组表示，值范围为 0-255：

.. code-block:: python

   window.background = (255, 255, 255)      # 白色背景（不透明）
   window.background = (0, 0, 0, 200)       # 半透明黑色背景（A=200）
   window.background = (150, 150, 150)      # 灰色背景（默认值）

背景色修改会触发窗口重绘。如果设置为透明背景（A=0），
后端仍会绘制一个透明层，但不会遮挡后面的内容。

窗口图标
------------------------------

图标支持多种格式：

.. code-block:: python

   # 从文件路径设置
   window.icon = "path/to/icon.png"

   # 从 bytes 数据设置
   with open("icon.png", "rb") as f:
       window.icon = f.read()

   # 从 PIL Image 对象设置
   from PIL import Image
   img = Image.open("icon.png")
   window.icon = img

.. note::
   Genesis 后端通过 SDL2 的 ``SDL_SetWindowIcon`` 设置图标，
   内部将图标数据写入临时文件再加载。图标格式需要 SDL2 支持的类型（通常是 PNG 或 BMP）。

其他窗口属性
------------------------------

.. code-block:: python

   # 窗口可见性（只读）
   print(window.visible)             # True / False

   # 窗口是否存活（只读，调用 destroy() 后为 False）
   print(window._alive)              # 注意：以下划线开头的属性为内部属性

.. seealso::
   更多窗口相关的 API 请参考 :doc:`WindowEntity </api/widgets/window>` 的自动生成文档。
