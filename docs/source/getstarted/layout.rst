布局与定位
========================================

Charmy 的控件通过 **布局配置文件 (LayoutProfile)** 来确定位置和大小。
目前支持手动定位（``PlaceLayout``），自动布局管理（``ManagedLayout``）有待实现。

坐标系
----------------------------------------

Charmy 使用和大多数 GUI 框架相同的坐标系：

- **原点 (0, 0)** 在父容器的左上角
- **X 轴** 向右递增
- **Y 轴** 向下递增

::

   (0, 0) ──────────→ X
      │
      │
      ↓
      Y

绝对位置 (``place``)
----------------------------------------

使用 ``place()`` 方法将控件放置在父容器的指定位置：

.. code-block:: python

   # widget.place(pos, size)
   #   pos  ─ (x, y) 相对于父容器的偏移
   #   size ─ (width, height) 可选，控件的尺寸

   button = cm.Button(window, text="Button")
   button.place((50, 100))              # 只指定位置
   button.place((50, 100), (200, 40))   # 同时指定位置和大小

如果 ``size`` 未指定，控件会使用其 Profile 中定义的默认大小
（Button 的默认大小为 72×28）。

.. note::
   ``place()`` 实际上创建了一个 ``PlaceProfile`` 并赋值给 ``widget.layout_profile``：

   .. code-block:: python

      # 以下等价：
      button.place((50, 50), (120, 40))
      # 等同于：
      button.layout_profile = cm.utils.layout_profiles.PlaceProfile(
          pos=(50, 50), size=(120, 40))

相对位置与绝对位置
----------------------------------------

控件有两个位置属性：

- ``pos`` — 相对于父容器的偏移（局部坐标）
- ``abs_pos`` — 相对于根容器（Window）的偏移（全局坐标）

对于直接放在窗口上的控件，两者相同。
对于嵌套在容器中的控件，``abs_pos`` 会递归累加父容器的位置：

.. code-block:: python

   with window:
       container = cm.Frame()      # 容器放在 window 上
       container.place((30, 30))

       with container:
           btn = cm.Button(text="Button in the Container")
           btn.place((10, 10))     # pos=(10,10), abs_pos=(40,40)

.. caution::
   ``Frame`` 目前是空壳实现，继承自 ``Widget`` + ``Container``，
   但还没有实际的背景绘制和子控件裁剪功能。

容器系统
----------------------------------------

``Container`` 是一个混入类（Mixin），为控件提供容纳子控件的能力。

目前继承 Container 的类：

.. list-table::
   :header-rows: 1

   * - 类
     - 说明
   * - ``Window``
     - 顶层窗口，也是容器
   * - ``Frame``
     - 框架容器（空壳，待实现）
   * - ``Container`` 本身
     - 不直接实例化

子控件的管理：

.. code-block:: python

   window.children          # 所有子控件列表
   button in window         # 检查 button 是否属于 window
   window.add_child(btn)    # 手动添加子控件（通常由 Widget.__init__ 自动调用）

.. note::
   子控件的绘制顺序由 ``Container.draw_children()`` 递归处理：
   先绘制手动放置的控件（``place`` 层），再绘制自动布局的控件（``managed`` 层）。
   同一层内，后添加的控件绘制在上层（显示在前面）。

上下文管理器
----------------------------------------

使用 ``with`` 语句可以自动设置父容器：

.. code-block:: python

   with window:
       # 在此创建的控件自动以 window 为父容器
       button = cm.Button(text="Auto parent")
       button.place((10, 10))

       with frame:
           # 嵌套容器
           inner_btn = cm.Button(text="Inner Button")
           inner_btn.place((5, 5))

这等价于显式指定 parent：

.. code-block:: python

   button = cm.Button(parent=window, text="Parent")

控件大小
----------------------------------------

控件的大小通过以下方式确定（按优先级从高到低）：

1. **布局指定的大小**：``place(pos, size)`` 中的 size 参数
2. **Profile 中指定的大小**：控件 profile 中 ``size`` 属性的值
3. **Profile 回退**：如果当前状态的 profile 未指定 ``size``，
   会逐级回退到 ``default`` 状态的 profile
4. **默认值**：如果都未指定，返回 ``(0, 0)``

.. code-block:: python

   button = cm.Button(window, text="Test")
   button.place((10, 10))           # 使用 profile 默认大小 (72, 28)
   print(button.size)               # → (72, 28)

   button.place((10, 10), (200, 50))  # 使用指定大小
   print(button.size)                  # → (200, 50)

布局支持状态
----------------------------------------

.. caution::
   Charmy 目前 **只支持** ``place`` 布局。
   自动布局（如 ``pack``、``grid``）的 ``ManagedLayoutProfile`` 基类已经定义，
   但尚未实现具体布局算法。

   如果你需要自动布局，目前只能通过手动计算位置来实现：

   .. code-block:: python

      # 手动实现垂直排列
      y = 10
      for i in range(5):
          btn = cm.Button(window, text=f"Button{i}")
          btn.place((10, y), (100, 30))
          y += 40

.. seealso::
   布局相关 API 细节请参考 :doc:`widget 模块 </api/widgets/widget>` 和
   :doc:`layout_profiles 模块 </api/utils/layout_profiles>`。
