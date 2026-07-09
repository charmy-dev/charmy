消息循环（事件循环）
====================

Charmy 使用**事件驱动**模型：程序启动后进入一个死循环，不断处理窗口事件和更新界面。

主循环结构
----------::

   cm.mainloop()
     └─ 遍历所有 CharmyManager
          └─ 遍历所有 Window
               ├─ 处理 SDL2 事件（鼠标、键盘、窗口变化）
               ├─ 绘制所有需要重绘的控件
               └─ 触发 WidgetUpdate 事件
     └─ time.sleep(interval)  ← 控制帧率

当前，事件主要使用**同步单线程**方式处理（可选择启用多线程）。

.. mermaid::

    graph TD
    A[主循环开始] --> B{有事件或需要重绘？}
    B -- 是 --> C[处理事件并绘制]
    B -- 否 --> D[等待 interval 秒]
    D --> B
    C --> B

事件系统
--------

Charmy 的事件系统采用**发布-订阅模式**：

- **事件类型**：用 dataclass 类表示（如 ``MouseClick``、``WidgetResize``）
- **事件绑定**：通过 ``widget.bind(event_type, callback)`` 注册
- **事件触发**：通过 ``widget.trigger(event_obj)`` 触发
- **条件过滤**：支持按条件绑定，如只响应鼠标左键点击

.. code-block:: python

   def on_click(event):
       print(f"鼠标在 {event.mouse_pos} 位置点击了按钮")

   button.bind(cm.event_types.MouseClick, on_click,
               conditions={"button": 0})  # 只响应左键

事件链
------

某些事件会自动级联触发其他事件：

::

   MousePress + MouseRelease
       ↓
     MouseClick
       ↓
     on_click() 回调

控件的鼠标悬停跟踪也是通过事件链实现的：

::

   MouseMove
     ├─ 计算鼠标下有哪些控件
     ├─ 对每个控件触发 MouseMove
     └─ 检测进入/离开 → 触发 MouseEnter / MouseLeave

更多细节请参考 :doc:`事件API </api/event>`。

多线程
------

.. caution::
   多线程支持目前处于**实验阶段**，建议在主线程中完成所有 UI 操作。

Charmy 支持将事件处理任务分发到工作线程，避免耗时操作阻塞 UI 刷新：

.. code-block:: python

   def heavy_task(event):
       # 耗时操作，不会阻塞 UI
       ...

   button.bind(cm.event_types.MouseClick, heavy_task, multithread=True)

异步
----

.. admonition:: 等待后续开发
   :class: caution

   异步支持目前尚未实现，计划在后续版本中加入。
