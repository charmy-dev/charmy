自定义应用设置
==============================

你可以在导入 Charmy 之前或运行时设置配置，自定义应用行为。

1. 环境变量设置（导入前）
------------------------------

在导入 ``charmy`` 之前设置环境变量，影响全局行为：

.. code-block:: python

   from os import environ

   environ["CHARMY_BACKEND"] = "genesis"   # 指定后端（目前唯一选项）

.. note::
   如果不设置，``Configs.default_backend`` 默认为 ``"auto"``，
   而 ``"auto"`` 在 ``loader.py`` 中被解析为 ``"genesis"``。

2. 调试标志（运行时）
------------------------------

Charmy 提供了一组调试标志，位于 ``cm.const.DEBUG_FLAGS``：

.. code-block:: python

   import charmy as cm

   # 绘制所有控件的边界框（红色半透明矩形）
   # 用于调试控件布局和碰撞检测
   cm.const.DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY = True

   # 每帧等待时间（用于观察绘制过程或降低 CPU 占用）
   #   True     → 等待 0.5 秒
   #   False    → 不等待（默认）
   #   浮点数   → 自定义等待秒数，如 0.1 表示每秒约 10 帧
   cm.const.DEBUG_FLAGS.WAIT_AFTER_EACH_FRAME = True
   cm.const.DEBUG_FLAGS.WAIT_AFTER_EACH_FRAME = 0.1

   # 标记被重绘的区域
   # 每次重绘的区域会以紫色半透明矩形高亮显示
   cm.const.DEBUG_FLAGS.MARK_REDRAWS = True

3. 主循环帧率控制
------------------------------

``cm.mainloop(interval)`` 的参数 ``interval`` 控制每帧之间的等待时间：

.. code-block:: python

   cm.mainloop(0.016)    # 约 60 FPS（16ms）
   cm.mainloop(0.033)    # 约 30 FPS（33ms）
   cm.mainloop(0)        # 不等待，尽可能快地运行（高 CPU 占用）

.. note::
   如果设置了 ``DEBUG_FLAGS.WAIT_AFTER_EACH_FRAME``，
   它会覆盖 ``mainloop()`` 的 ``interval`` 参数。

4. 自定义后端行为
------------------------------

如果未来你开发了自己的后端，可以通过 ``CharmyManager`` 手动指定：

.. code-block:: python

   from charmy.cmm import CharmyManager
   from my_backend import MyBackend

   manager = CharmyManager(MyBackend())
   window = cm.Window(parent=manager)
