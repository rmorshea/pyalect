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

Now why would you want to transpile Python one might ask? Well a transpiler probably
isn't the first tool you should reach for when trying to solve a problem, but sometime's
it's the only option. For example, sometimes the easiest way to express a given bit of
logic turns out to be sub-optimal when it comes to performance - in this situation you
could use a transpiler optimize your expressive, but inefficient code. On the otherhand
you may have purely assthetic reasons for using a transpiler to transform pretty, but
invalid syntax into an uglier, but valid form so that it can be executed. For example,
one might want to transpile the following `HTM <https://github.com/developit/htm>`__
style string template:

.. code-block::

    # dialect=html
    dom = html"<div height=10px><p>hello!</p></div>"

Into valid Python:

.. code-block::

    # dialect=html
    dom = html("div", {"height": "10px"}, [html("p", {}, ["hello!"])])


Basic Usage
-----------

So what would it look like to implement the custom syntax above? All you need to do is
register a "dialect" transpiler with Pyalect before importing the module containing the
code in question. Consider the following directory structure:

.. code-block:: text

    my_project/
    |-  entrypoint.py
    |-  my_html_module.py

Inside ``entrypoint.py`` should be a :class:`~pyalect.dialect.Dialect` that implements
two methods:

.. code-block::

    from pyalect import Dialect

    class HtmlDialect(Dialect, name="html"):
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


With all this in place and the methods of ``HtmlDialect`` implemented you should be
able to run ``entrypoint.py`` in your console to find ``my_html_module`` has been
transpiler just before execution:

.. code-block:: bash

    python entrypoint.py

.. note::

    For a real world example implementation of an HTML transpiler check out
    `IDOM <https://idom.readthedocs.io/en/latest/extras.html>`_!


Integrations
------------

In most situations Pyalect should work out of the box, but some tools require special support.


IPython and Jupyter
...................

Dialects are supported in `IPython <http://ipython.org/>`__ and
`Jupyter <https://jupyter.org>`__ via magics:

.. code-block::

    %%dialect html
    ...


Pytest Asserts
..............

Similarly to Pyalect, Pytest uses import hooks to transpile code at import-time. Since
Pyalect's own import hook should take priority over Pytest's you'll have to import the
builtin ``pytest`` dialect and include it in any test files where you're using your own
dialects:

.. code-block::

    import pyalect.builtins.pytest

.. code-block::

    # dialect = my_dialect, pytest

    def test_my_code():
        assert ...


API
---

.. automodule:: pyalect.dialect
    :members:



.. Links
.. =====

.. _issue: https://github.com/rmorshea/pyalect/issues
.. _pull request: https://github.com/rmorshea/pyalect/pulls
