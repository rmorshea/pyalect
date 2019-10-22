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


Usage
-----

Register a dialect before importing the code you wish to transpile:

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

Now import a module with a dialect header comment. The respective transpiler will be
applied to the file just before executing it:

.. code-block:: python

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
