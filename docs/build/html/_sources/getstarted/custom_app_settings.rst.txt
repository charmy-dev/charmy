Custom main manager settings
============================

You can set the environment variables to customize the main manager settings before import charmy.

.. code-block:: python

   from os import environ

Switch UI framework
^^^^^^^^^^^^^^^^^^^

If you want to switch the ui framework,
you can set the environment variable "UI_FRAMEWORK" to "GLFW" or ...

.. code-block:: python

   environ["UI_FRAMEWORK"] = "GLFW"
