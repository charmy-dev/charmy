安装 Charmy
============

.. caution::

   Python 版本要求 **>= 3.11**！

使用 pip 安装（推荐）
---------------------

.. code-block:: shell

   pip install charmy-gui

从源码安装
----------

.. code-block:: shell

   git clone https://github.com/XiangQinxi/charmy.git
   cd charmy
   pip install -e .

后端依赖
--------

Charmy 的架构将 GUI 框架分为三层，底层是**后端**。目前唯一可用的后端是 **Genesis**，
它使用 SDL2 创建窗口、Cairo 进行渲染。

安装 Genesis 后端所需的依赖：

.. code-block:: shell

   pip install pysdl2 pysdl2-dll pycairo

.. note::
   - 如果安装 ``pycairo`` 失败，请先安装系统级的 Cairo 库
   - Windows 用户通常可以直接通过 pip 安装，无需额外配置
   - macOS 用户可能需要 ``brew install cairo``
   - Linux 用户可能需要 ``apt install libcairo2-dev`` （或对应发行版的包管理器）

验证安装
--------

创建一个 Python 文件，写入以下代码并运行：

.. code-block:: python

   import charmy as cm

   window = cm.Window(size=(300, 160), title="Charmy GUI")
   cm.mainloop()

如果出现一个灰色窗口，说明安装成功！
