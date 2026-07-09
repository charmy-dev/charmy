贡献指南
========

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
--------

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

   - 清晰地描述你所做的改动。
   - 如果涉及 API 变更，请更新相关文档。

构建文档
--------

本文档使用 Sphinx 构建。首先安装文档构建所需的依赖：

.. code-block:: shell

   pip install charmy[docs]

然后执行：

.. code-block:: shell

   cd docs
   .\make html          # Windows
   # make html          # Linux / macOS

文档支持 reStructuredText（``.rst``）和 Markdown（``.md``）两种格式。

代码规范
--------

- 遵循 **PEP 8** 编码规范（https://www.python.org/dev/peps/pep-0008/）
- 注释统一使用 **Sphinx** 或 **Google** 风格

例如：

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
