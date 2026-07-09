贡献指南
==============================

.. sidebar:: 贡献者 / 小白云 (Little White Cloud)

   来自 ``中国`` 的一名高中生。

   编写了 ``charmy.this`` 的中文原文。

   .. image:: xby_logo.jpg
       :alt: xby_logo

   .. image:: xby_content.png
       :alt: xby_content

.. sidebar:: 贡献者 / rgzz666

   来自 ``中国`` 的一名高中生。

   翻译了 ``charmy.this`` 的英文版本。

   .. image:: rgzz666_logo.png
       :alt: rgzz666_logo

.. note::

   GitHub 仓库：https://github.com/XiangQinxi/charmy

如何贡献
------------------------------

1. 在 GitHub 上 Fork 本项目。

.. code-block:: shell

    git clone https://github.com/XiangQinxi/charmy.git

2. 为你的功能或 Bug 修复创建一个新分支。

.. code-block:: shell

    git checkout -b feature/your-feature-name

3. 进行修改并提交。

.. code-block:: shell

    git add .
    git commit -m "简要描述你的改动"

4. 将分支推送到你的 Fork。

.. code-block:: shell

    git push origin feature/your-feature-name

5. 向原始项目提交 Pull Request。

   - 清晰地描述你所做的改动
   - 如果涉及 API 变更，请更新相关文档
   - 如果可能，附上测试用例或运行截图

构建文档
------------------------------

本文档使用 Sphinx 构建。首先安装文档构建所需的依赖：

.. code-block:: shell

   pip install charmy[docs]

然后执行：

.. code-block:: shell

   cd docs
   .\make html          # Windows
   # make html          # Linux / macOS

文档支持 **reStructuredText**（``.rst``）和 **Markdown**（``.md``）两种格式。

API 文档自动生成
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``docs/source/api/`` 下的 API 文档由 ``autoapi.py`` **自动生成**，请勿手动编辑：

.. code-block:: shell

   # 当你新增/修改了 Python 模块后，重新运行自动生成器
   python docs/source/api/autoapi.py

   # 然后重新构建 HTML
   cd docs && .\make html

自动生成器会：

- 扫描 ``charmy/`` 包下所有 ``.py`` 文件（排除彩蛋和空壳文件）
- 为每个模块生成 ``.rst`` 文件（包含 ``autoclasstree`` + ``automodule``）
- 为每个子包生成 ``index.rst``（包含 toctree，链接到所有子模块）
- 自动识别 ``__init__.py`` 作为包索引

.. warning::
   ``autoapi.py`` 会自动覆盖 ``api/`` 目录下的 ``.rst`` 文件。
   如果你需要手动修改 API 文档，请修改源码中的 **docstring**，然后重新运行生成器。

测试指南
------------------------------

目前测试用例位于 ``tests/`` 目录下，主要是手动运行的可执行脚本：

.. code-block:: shell

   # 图形绘制测试
   python tests/graphics.py

   # Button 控件测试
   python tests/button.py

   # 事件系统测试
   python tests/event.py

添加新测试时：

- 功能测试：在 ``tests/`` 下创建 ``test_功能名.py``
- 手动验证测试：创建可以直接 ``python tests/xxx.py`` 运行的脚本
- 后续计划引入 ``pytest`` 自动化测试框架

代码规范
------------------------------

- 遵循 **PEP 8** 编码规范（https://www.python.org/dev/peps/pep-0008/）
- 行长度限制：**100 字符**
- 注释统一使用 **Sphinx** 或 **Google** 风格
- 导入使用绝对导入，避免循环引用（必要时使用 ``TYPE_CHECKING``）

注释风格示例：

.. code-block:: python

   def function_name(param1, param2):
        """函数功能简述。

        Args:
            param1 (int): 第一个参数。
            param2 (str): 第二个参数。

        Returns:
            bool: 返回 True 表示成功，False 表示失败。

        Raises:
            ValueError: 当 `param1` 等于 `param2` 时抛出。
        """

   class SampleClass:
        """类的简要说明。

        更详细的类说明……

        示例::

            >>> sample = SampleClass()
            >>> sample.likes_spam
            False
            >>> sample.eggs
            0

        Attributes:
            likes_spam (bool): 是否喜欢 SPAM。
            eggs (int): 拥有的鸡蛋数量。
        """

        def __init__(self, likes_spam=False):
            """初始化 SampleClass。"""
            self.likes_spam = likes_spam
            self.eggs = 0
