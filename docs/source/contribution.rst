Contribution
============

.. note::

   Github Repository: https://github.com/XiangQinxi/charmy

How to *Contribute*
-------------------

1. Fork the project on GitHub.

.. code-block:: shell

    git clone https://github.com/XiangQinxi/charmy.git

2. Create a new branch for your feature or bug fix.

.. code-block:: shell

    git checkout -b feature/your-feature-name

3. Make your changes and commit them.

.. code-block:: shell

    git add .
    git commit -m "Add your commit message here"

4. Push your branch to your fork.

.. code-block:: shell

    git push origin feature/your-feature-name

5. Open a pull request on the original project.

    - Clearly describe the changes you made.

Build Documents
---------------

The documentation is built with Sphinx.

Run it to install the required packages:

.. code-block:: shell

   pip install charmy[docs]

.. code-block:: shell

   cd docs
   .\make html


When writing documents, markdown or reStructuredText formats can be used.

Code Standards
--------------

We follow the `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ style guide for Python code.

Annotations should be uniformly in ``Sphinx`` or ``Google`` format.

such as

.. code-block:: python

   def function_name(param1, param2):
        """Function summary line.

        Args:
            param1 (int): The first parameter.
            param2 (str): The second parameter.

        Returns:
            bool: The return value. True for success, False otherwise.

        Raises:
            ValueError: If `param1` is equal to `param2`.
        """

   class SampleClass:
        """Summary of class here.

        Longer class information....
        Longer class information....

        Examples:

            >>> sample = SampleClass()
            >>> sample.likes_spam
            False
            >>> sample.eggs
            0

        Attributes:
            likes_spam (bool): A boolean indicating if we like SPAM or not.
            eggs (int): The number of eggs we have.
        """

        def __init__(self, likes_spam=False):
            """Inits SampleClass with blah."""
            self.likes_spam = likes_spam
            self.eggs = 0