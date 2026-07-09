Charmy GUI 文档
==============================

.. sidebar:: 作者 / 项沁曦 (Xiang Qinxi)

   来自 ``中国`` 的一名高中生。

   .. image:: xqx_logo.jpg
       :alt: xqx_logo

   "我写的代码就像一坨💩。😭😭"

欢迎来到 **Charmy GUI** 的文档！

Charmy 是一个跨平台的 Python GUI 库，采用 **三层架构** 设计，后端可切换，
在保持轻量的同时实现跨平台桌面应用开发。

项目特点
------------------------------

- **三层架构**：后端层 → 图形层 → 控件层，各层职责清晰
- **后端可切换**：同一套 API 可对接不同底层图形库（目前仅 Genesis 后端）
- **事件驱动**：基于发布-订阅模式的事件系统，支持条件过滤和事件链
- **自动 ID 管理**：所有对象自动分配唯一 ID，支持通过 ID 查找
- **弱引用追踪**：使用 ``weakref`` 自动管理对象生命周期，无内存泄漏
- **Fallback 机制**：线条/图形类型自动降级，保证跨后端兼容
- **SVG 路径支持**：内置完整的 SVG path 解析器，可直接绘制 SVG 图形

当前状态
------------------------------

.. caution::
   Charmy 处于 **早期开发阶段** （v0.0.1），API 尚未稳定。

   - ✅ 后端层：完成（Genesis: SDL2 + Cairo）
   - ✅ 图形层：完成（线条、形状、文字绘制）
   - 🚧 控件层：进行中（仅 Button 可用，Frame/Text 为空壳）
   - 🚧 事件系统：基本完成（鼠标事件已桥接）
   - ❌ 布局管理：仅 ``place`` 布局，尚无 pack/grid
   - ❌ 主题系统：基础框架存在，尚未接入控件

快速开始
------------------------------

.. code-block:: python

   import charmy as cm

   window = cm.Window(size=(400, 300), title="我的应用")
   button = cm.Button(window, text="点我", on_click=lambda: print("Hello!"))
   button.place((50, 50), (120, 40))

   cm.mainloop()

项目渊源
------------------------------

.. tip::
   项目原名为 **Suzaku**，因底层架构缺陷导致性能问题，重构为现在的 Charmy。
   部分设计理念继承自 Suzaku，代码中保留了一些"彩蛋"作为纪念（如 ``skhynix.py``）。

.. toctree::
   :maxdepth: 3
   :caption: 主要内容：

   getstarted/index
   how_does_it_work/index
   api/index

.. toctree::
   :maxdepth: 2
   :caption: 其他：

   contribution
