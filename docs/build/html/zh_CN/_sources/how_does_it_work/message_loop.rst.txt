消息循环（事件循环）
==============================

Charmy 使用 **事件驱动** 模型：程序启动后进入一个死循环，不断处理窗口事件和更新界面。

主循环结构
------------------------------

::

   cm.mainloop(interval=0.01)
     │
     ├─ 遍历所有 CharmyManager.instances
     │    （每个 manager 管理一组使用同一后端的窗口）
     │    │
     │    └─ manager.update()
     │         │
     │         ├─ 遍历 manager 下所有存活窗口
     │         │    │
     │         │    └─ window.update()
     │         │         │
     │         │         ├─ 触发 WidgetUpdate 事件
     │         │         ├─ Container.draw_children()
     │         │         │    └─ 递归绘制所有子控件
     │         │         ├─ Window.draw_frame()
     │         │         │    ├─ 绘制背景
     │         │         │    ├─ 后端 LineBase.draw_line()
     │         │         │    ├─ 后端 ShapeBase.draw_shape()
     │         │         │    └─ 后端 TextBase.draw_text()
     │         │         ├─ 后端 update()
     │         │         │    ├─ Cairo → SDL Surface 拷贝
     │         │         │    ├─ SDL_UpdateWindowSurface()
     │         │         │    └─ 处理 SDL2 事件队列
     │         │         └─ 清空 _redraw_regions
     │         │
     │         └─ 触发 WidgetUpdate(manager) 事件
     │
     ├─ 如果没有存活窗口 → manager.destroy()
     │
     └─ time.sleep(interval)  ← 控制帧率

CharmyManager 生命周期
------------------------------

``CharmyManager`` 是窗口管理器，一个后端对应一个 Manager：

.. code-block:: python

   # 自动创建（不指定 manager 时）
   window = cm.Window()
   # → 内部自动创建 CharmyManager(genesis)
   # → window.parent = manager

   # 手动指定 manager
   from charmy.cmm import CharmyManager
   manager = CharmyManager("genesis")
   window = cm.Window(parent=manager)

.. note::
   - Manager 使用 ``CharmyRegisteredObject.instances`` 追踪所有实例
   - 所有 Manager 通过 ``CharmyManager.instances`` 类变量可全局访问
   - 当 Manager 下所有窗口都关闭后，Manager 自动销毁（``_alive = False``）
   - ``mainloop()`` 在所有 Manager 都销毁后退出

增量重绘机制
------------------------------

为了提升性能，Charmy 不会每帧重绘整个窗口，而是只重绘发生变化的区域：

.. code-block:: python

   # window 内部维护 _redraw_regions 列表
   self._redraw_regions: list[ShapeRange] = []

当控件的某个属性改变时，该控件的边界矩形被加入 ``_redraw_regions``。
在下一帧，只重绘这些区域中的图形对象。

.. code-block:: python

   # Window._find_need_redraw() 的实现逻辑
   for drawn_obj in self._drawing_list:
       for region in self._redraw_regions:
           if drawn_obj.boundary 与 region 有重叠:
               result.append(drawn_obj)  # 需要重绘

   # 如果 _redraw_regions 包含整个窗口 → 强制全量重绘
   if ((0, 0), self.size) in self._redraw_regions:
       force_redraw = True

.. tip::
   可以通过 ``DEBUG_FLAGS.MARK_REDRAWS = True`` 来可视化重绘区域：
   每次被标记重绘的区域会显示为紫色半透明矩形。

事件系统详解
------------------------------

Charmy 的事件系统采用 **发布-订阅模式** ，核心组件：

- **事件类型**：用 ``dataclass`` 类表示，具有类型安全的事件匹配
- **EventHandling 混入类**：提供 ``bind()`` / ``trigger()`` / ``on()`` 方法
- **EventTask**：代表一个绑定的任务，包含回调函数和条件

事件类型层次结构
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   Event（基类）
   ├─ EventTriggered           ── 任意事件触发时触发
   ├─ WidgetEvent              ── 控件事件基类
   │   ├─ WidgetUpdate         ── 控件/窗口更新
   │   ├─ WidgetDraw           ── 控件/窗口重绘
   │   ├─ WidgetConfigure      ── 配置改变
   │   ├─ WidgetResize         ── 大小改变
   │   ├─ WidgetMove           ── 位置改变
   │   ├─ FocusGain            ── 获得焦点
   │   ├─ FocusLoss            ── 失去焦点
   │   └─ WidgetDestroy        ── 销毁
   ├─ WindowEvent              ── 窗口事件基类
   ├─ MouseRawEvent            ── 鼠标原始事件
   │   ├─ MouseMove            ── 鼠标移动
   │   ├─ MousePress           ── 鼠标按下
   │   ├─ MouseRelease         ── 鼠标释放
   │   └─ MouseScroll          ── 滚轮
   └─ MouseInteractEvent       ── 鼠标交互事件
       ├─ MouseEnter           ── 鼠标进入
       ├─ MouseLeave           ── 鼠标离开
       └─ MouseClick           ── 鼠标点击

事件链
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

某些事件会自动级联触发其他事件：

::

   MousePress + MouseRelease  (在同一控件上)
       ↓
     MouseClick
       ↓
     回调函数执行

鼠标悬停跟踪：

::

   SDL_MOUSEMOTION
       ↓
     MouseMove  →  event.call_chain()
       │
       ├─ Container.get_mouse_hover(pos)
       │    └─ 递归检查所有子控件，返回悬停路径
       │
       ├─ 对悬停路径上的每个控件触发 MouseMove
       │
       ├─ 检测新进入的控件 → MouseEnter
       │
       └─ 检测离开的控件 → MouseLeave

条件绑定
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``bind()`` 支持按条件过滤事件：

.. code-block:: python

   button.bind(cm.event_types.MouseClick, on_click,
               conditions={"button": 0})  # 只响应左键

   button.bind(cm.event_types.MouseClick, on_right_click,
               conditions={"button": 2})  # 只响应右键

多线程
------------------------------

.. caution::
   多线程支持目前处于 **实验阶段** ，建议在主线程中完成所有 UI 操作。

Charmy 支持将事件处理任务分发到工作线程，避免耗时操作阻塞 UI 刷新：

.. code-block:: python

   def heavy_task(event):
       # 耗时操作，不会阻塞 UI
       import time
       time.sleep(5)
       print("任务完成")

   button.bind(cm.event_types.MouseClick, heavy_task, multithread=True)

.. note::
   启用多线程时，回调函数在 **独立线程** 中运行，不能直接操作 Charmy 的 UI 对象。
   如果需要更新 UI，请使用 ``EventTask`` 的消息传递机制（待实现）。

实例追踪系统
------------------------------

Charmy 使用弱引用（``weakref``）追踪所有 ``CharmyRegisteredObject`` 的实例：

.. code-block:: python

   # 每个子类自动拥有独立的实例列表
   print(cm.Button.instances)         # 所有 Button 实例
   print(cm.Window.instances)         # 所有 Window 实例
   print(CharmyManager.instances)     # 所有 Manager 实例

   # 通过 ID 查找实例
   btn = cm.Button.instances["Button0"]

   # 实例被销毁后自动从列表移除（WeakSet）
   del btn  # Button0 不再出现在 .instances 中

.. seealso::
   更多事件 API 细节请参考 :doc:`event 模块 </api/event>` 和
   :doc:`event_types 模块 </api/utils/event_types>` 的自动生成文档。
