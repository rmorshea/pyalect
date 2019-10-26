Pyalect |release|
=================

A dynamic dialect transpiler for Python that you can install with ``pip``!

.. code-block:: bash

    pip install pyalect

.. note::

    Pyalect is still young! If you have ideas or find a problem `let us know <issue>`_!


.. contents::
  :local:
  :depth: 1


But Why?
--------

Now why would you want to transpile Python one might ask? Well the aren't very many
problems that ought to be solved this way, but the most obvious one is the ability to
use special syntax in your normal Python code. For example, one might want to transpile
the following `HTM <https://github.com/developit/htm>`__ style string template:

.. code-block::

    # dialect=html
    dom = html"<div height=10px><p>hello!</p></div>"

Into valid Python:

.. code-block::

    # dialect=html
    dom = html("div", {"height": "10px"}, [html("p", {}, ["hello!"])])

.. note::

    For a real world example implementation of an HTML transpiler check out
    `IDOM <https://idom.readthedocs.io/en/latest/extras.html>`_!


Usage
-----

So what would it look like to implement the custom syntax above? All you need to do is
register a "dialect" transpiler with Pyalect before importing the module containing the
code in question. Consider the following directory structure:

.. code-block:: text

    my_project/
    |-  entrypoint.py
    |-  my_html_module.py

Inside ``entrypoint.py`` should be a transpiler that implements two methods:

.. code-block::

    import pyalect

    @pyalect.register("html")
    class HtmlTranspiler:
        def transform_src(source: str) -> str:
            """Called first to manipulate the module source as a string"""
            # your code goes here...

        def transform_ast(tree: ast.AST) -> ast.AST:
            """Called second to change the AST of the now transformed source"""
            # your code goes here...

    import my_html_module

Where ``my_html_module`` is a normal Python file with a dialect header comment:

.. code-block::

    # dialect=html
    dom = html"<div height=10px><p>hello!</p></div>"


With all this in place and the methods of ``HtmlTranspiler`` implemented you should be
able to run ``entrypoint.py`` in your console to find ``my_html_module`` has been
transpiler just before execution:

.. code-block:: bash

    python entrypoint.py


IPython and Jupyter Support
...........................

Dialects are supported in `IPython <http://ipython.org/>`__ and
`Jupyter <https://jupyter.org>`__ via magics:

.. code-block::

    %%dialect html
    ...


API
---

.. automodule:: pyalect.dialect
    :members:



.. Links
.. =====

.. _issue: https://github.com/rmorshea/pyalect/issues
.. _pull request: https://github.com/rmorshea/pyalect/pulls
