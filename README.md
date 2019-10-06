# Pyalect

Dynamically transpiling Python dialect for good.


# Installation

```bash
pip install pyalect
```


# Console Usage

```
pyalect (activate | deactivate)
pyalect register <transpiler> as <dialect> [--force]
pyalect deregister (<dialect> | <transpiler> [as <dialect])
pyalect show config
```

<table>
    <tr>
        <td>
            <code>pyalect activate</code>
        </td>
        <td>
            The current Python interpreter will now automatically apply registered
            transpilers to imported module with a <code># dialect=...</code> comment
            header.
        </td>
    </tr>
    <tr>
        <td>
            <code>pyalect deactivate</code>
        </td>
        <td>
            The current Python interpreter will no longer apply registered transpilers
            to imported modules.
        </td>
    </tr>
    <tr>
        <td>
            <code>pyalect register</code>
        </td>
        <td>
            Save a transpiler that will be applied to modules with the given
            <code>&ltdialect&gt</code> header. The <code>&lttranspiler&gt</code> must
            be of the form <code>dotten.path.to:TranspilerClass</code>. If the
            <code>--force</code> option is provided then it will overwrite an existing
            transpiler (if any).
        </td>
    </tr>
    <tr>
        <td>
            <code>pyalect deregister</code>
        </td>
        <td>
            Remove a transpiler from the dialect registery. Providing just the
            <code>&ltdialect&gt</code> will remove any transpiler that's registered to
            it. Providing a <code>&lttranspiler&gt</code> will remove is from the given
            <code>&ltdialect&gt</code>, however if <code>&ltdialect&gt</code> is
            <code>*</code> it will be deregistered from dialects.
        </td>
    </tr>
    <tr>
        <td>
            <code>pyalect show config</code>
        </td>
        <td>
            Prints the configuration file path and current state.
        </td>
    </tr>
    <tr>
        <td>
            <code>pyalect delete config</code>
        </td>
        <td>
            Deletes the config file. This should be done prior to uninstalling Pyalect.
        </td>
    </tr>
</table>


## Console Examples

```bash
pyalect register my_module:MyTranspiler as my_dialect
pyalect activate
pyalect config show
```


# Programatic Usage

Programatic usage of pyalect only applies within the current Python session and must be
done before importing.

```python
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
```


# Indicating Dialects

If Pyalect has been activated via the console, or has already been imported, then
Pyalect will hook into Python's import system to register transpilers that will be
applied to files with their respecitve dialect comment in the file's header:

```python
# dialect=my_dialect
...
```


# IPython and Jupyter Support

Dialects are supported in [IPython](http://ipython.org/) and [Jupyter](https://jupyter.org) via magics:

```python
%%dialect html
...
```
