安装 Charmy
==============================

.. caution::

   Python 版本要求 **>= 3.11**！

使用 pip 安装（推荐）
------------------------------

.. code-block:: shell

   pip install charmy-gui

.. warning::
   项目仍处于早期开发阶段，可能尚未发布到 PyPI。
   如果上方命令失败，请使用下面的源码安装方式。

从源码安装
------------------------------

.. code-block:: shell

   git clone https://github.com/XiangQinxi/charmy.git
   cd charmy
   pip install -e .

.. note::
   ``pip install -e .`` 会以可编辑模式安装，你对源码的修改会即时生效，
   适合开发和调试。

后端依赖
------------------------------

Charmy 将底层图形框架抽象为 **后端** 。目前唯一可用的后端是 **Genesis** ，
它使用 SDL2 创建窗口、Cairo 进行 2D 渲染。

安装 Genesis 后端所需的依赖：

.. code-block:: shell

   pip install pysdl2 pysdl2-dll pycairo

各平台注意事项：

.. list-table::
   :header-rows: 1

   * - 平台
     - 注意事项
   * - Windows
     - 通常直接 ``pip install`` 即可，无需额外配置。
         如果 ``pycairo`` 安装失败，尝试从 https://github.com/pygobject/pycairo 下载 wheel。
   * - macOS
     - 可能需要先安装 Cairo 库： ``brew install cairo``
         然后再 ``pip install pycairo``
   * - Linux (Debian/Ubuntu)
     - ``sudo apt install libcairo2-dev pkg-config``
         然后再 ``pip install pycairo``
   * - Linux (Fedora/RHEL)
     - ``sudo dnf install cairo-devel pkg-config``
         然后再 ``pip install pycairo``

.. note::
   ``pysdl2-dll`` 包含了 SDL2 的预编译动态库，通常情况下不需要手动安装 SDL2。
   如果遇到 SDL2 相关的错误，可以尝试从 https://libsdl.org 下载最新版本的 SDL2。

验证安装
------------------------------

创建一个 Python 文件，写入以下代码并运行：

.. code-block:: python

   import charmy as cm

   window = cm.Window(size=(300, 160), title="Charmy GUI")
   cm.mainloop()

如果出现一个灰色窗口，说明安装成功！

常见问题
------------------------------

**Q: 导入 charmy 时报错 ``No module named 'sdl2'``**

A: 没有安装 SDL2 依赖。执行 ``pip install pysdl2 pysdl2-dll``

**Q: 导入 charmy 时报错 ``No module named 'cairo'``**

A: 没有安装 Cairo 依赖。执行 ``pip install pycairo``。如果安装失败，请参考上方各平台注意事项。

**Q: 运行后窗口一闪而过**

A: 检查代码中是否有 ``cm.mainloop()``。如果缺少主循环，程序会立即退出。

**Q: 窗口显示但不响应鼠标**

A: 确认 SDL2 事件循环在工作。在 ``mainloop()`` 之前添加以下代码测试：

.. code-block:: python

   def on_click(event):
       print(f"Clicked: {event.mouse_pos}")

   window.bind(cm.event_types.MouseClick, on_click)
