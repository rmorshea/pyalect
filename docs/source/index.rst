Pyalect |release|
=================

A dynamic dialect transpiler for Python.

.. toctree::
    :maxdepth: 1

    api


Early Days
----------

Pyalect is still young! If you have ideas, now is the time to contribute a `pull request`_.
Of course if you find a bug, and aren't sure how to fix it post an `issue`_ and it'll get
taken care of.


Installation
------------

.. code-block:: bash

    pip install pyalect


Console Usage
-------------

.. code-block:: text

    pyalect (activate | deactivate)
    pyalect register <transpiler> as <dialect> [--force]
    pyalect deregister (<dialect> | <transpiler> [as <dialect])
    pyalect show config

.. list-table::
    :header-rows: 1

    * - Command
      - Description
    * - ``pyalect activate``
      - The current Python interpreter will now automatically apply registered
        transpilers to imported module with a ``# dialect=...`` comment
        header.
    * - ``pyalect deactivate``
      - The current Python interpreter will no longer apply registered transpilers
        to imported modules.
    * - ``pyalect register``
      - Save a transpiler that will be applied to modules with the given
        ``<dialect>`` header. The ``<transpiler>`` must be of the form
        ``dotten.path.to:TranspilerClass``. If the ``--force`` option is
        provided then it will overwrite an existing transpiler (if any).
    * - ``pyalect deregister``
      - Remove a transpiler from the dialect registery. Providing just the
        ``<dialect>`` will remove any transpiler that's registered to
        it. Providing a ``<transpiler>`` will remove is from the given
        ``<dialect>``, however if ``<dialect>`` is ``*`` it will be
        deregistered from dialects.
    * - ``pyalect show config``
      - Prints the configuration file path and current state.
    * - ``pyalect delete config``
      - Deleting the configuration file will also effectively deactivate Pyalect.


Console Examples
................

.. code-block:: text

    pyalect register my_module:MyTranspiler as my_dialect
    pyalect activate
    pyalect config show


Programatic Usage
-----------------

Programatic usage of pyalect only applies within the current Python session and must be
done before importing.

.. code-block::

    import ast
    import pyalect

    class MyTranspiler:

        def transform_src(self, source: str) -> str:
            # modify src ...
            return new_src

        def transform_ast(self, node: ast.AST) -> ast.AST:
            # modify AST ...
            return node

    pyalect.register("my_dialect", MyTranspiler)


Indicating Dialects
-------------------

If Pyalect has been activated via the console, or has already been imported, then
Pyalect will hook into Python's import system to register transpilers that will be
applied to files with their respecitve dialect comment in the file's header:

.. code-block:: text

    # dialect=my_dialect
    ...


IPython and Jupyter Support
---------------------------

Dialects are supported in `IPython <http://ipython.org/>`__ and
`Jupyter <https://jupyter.org>`__ via magics:

.. code-block::

    %%dialect html
    ...


.. Links
.. =====

.. _issue: https://github.com/rmorshea/pyalect/issues
.. _pull request: https://github.com/rmorshea/pyalect/pulls
