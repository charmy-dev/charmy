First application
=================

1. Import ``Charmy``

.. code-block:: python

   import charmy as cm

2. Create a ``App``

.. code-block:: python

   app = cm.App()

3. Create a ``Window``

.. code-block:: python

   window = cm.Window()  # If you want to use other App, pass it as argument

4. Run the application

.. code-block:: python

   app.run()

In all, your first application should look like this:

.. code-block:: python

   import charmy as cm

   app = cm.App()
   window = cm.Window()
   app.run()

Then, you can get a window.

.. image:: first_app_preview.png