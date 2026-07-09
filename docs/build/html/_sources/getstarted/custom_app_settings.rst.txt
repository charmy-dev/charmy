自定义应用设置
==============

你可以在导入 Charmy 之前设置环境变量来自定义运行时行为。

切换后端
--------

目前 Charmy 只内置了 **Genesis** 后端（基于 SDL2 + Cairo），
但架构支持未来接入更多后端。你可以通过环境变量指定要使用的后端：

.. code-block:: python

   from os import environ

   environ["CHARMY_BACKEND"] = "genesis"   # 目前唯一可用的后端

.. note::
   如果不设置，默认使用 ``genesis`` 后端。

调试选项
--------

Charmy 提供了一些调试标志，可以在 ``cm.const.DEBUG_FLAGS`` 中设置：

.. code-block:: python

   import charmy as cm

   # 绘制所有控件的边界框（用于调试布局）
   cm.const.DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY = True

   # 每帧等待 0.5 秒（用于观察绘制过程）
   cm.const.DEBUG_FLAGS.WAIT_AFTER_EACH_FRAME = True

   # 标记被重绘的区域
   cm.const.DEBUG_FLAGS.MARK_REDRAWS = True
