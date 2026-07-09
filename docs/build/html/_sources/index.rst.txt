Charmy GUI 文档
================

.. sidebar:: 作者 / 项沁曦 (Xiang Qinxi)

   来自 ``中国`` 的一名高中生。

   .. image:: xqx_logo.jpg
       :alt: xqx_logo

   "我写的代码就像一坨💩。😭😭"

欢迎来到 **Charmy GUI** 的文档！

**Charmy GUI** 是一个跨平台的 Python GUI 库，采用**三层架构**（后端 → 图形层 → 控件层），
支持在不同后端之间切换，从而在保持轻量的同时实现跨平台。

.. note::
   Charmy 目前处于早期开发阶段，API 可能发生变动。
   当前唯一可用的后端是 **Genesis** （基于 SDL2 + Cairo）。

.. tip::
   项目原名为 Suzaku，因底层缺陷导致性能问题而重构为现在的 Charmy。

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
