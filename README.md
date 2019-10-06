# Pyalect

Dynamically transpiling Python for good.


# Installation

```bash
pip install pyalect
```


# Console Usage

```
pyalect (activate | deactivate)
pyalect register <transpiler> as <dialect> [--force]
pyalect deregister (<dialect> | <transpiler> [as <dialect])
pyalect config (show | path)
```


<table>
    <tr>
        <td>
            <code>pyalect activate</code>
        </td>
        <td>
            The current Python interpreter will now automatically apply registered
            transpilers to imported module with a <code># dialect=...</code> comment header.
        </td>
    </tr>
    <tr>
        <td>
            <code>pyalect deactivate</code>
        </td>
        <td>
            The current Python interpreter will no longer apply registered transpilers
            to import modules.
        </td>
    </tr>
    <tr>
        <td>
            <code>pyalect register &ltranspiler&gt as &ltdialect&gt [--force]</code>
        </td>
        <td>
            Save a transpiler to be applied to modules with the given
            <code>&ltdialect&gt</code> header. The <code>%lttranspiler&gt</code> should
            follow one of the following forms:
            <ul>
                <li><code>package.module.submodule</code></li>
                <li><code>package.module.submodule:attribute</code></li>
            </ul>
            If the <code>--force</code> option is provide then it will overwrite
            an existing transpiler (if any).
        </td>
    </tr>
    <tr>
        <td>
            <code>pyalect deregister (&ltdialect&gt | &lttranspiler&gt as &ltdialect&gt)</code>
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
            <code>pyalect config show</code>
        </td>
        <td>
            Prints the current configuration to the console
        </td>
    </tr>
    <tr>
        <td>
            <code>pyalect config path</code>
        </td>
        <td>
            Prints the configuration files's path to the console
        </td>
    </tr>
</table>


## Console Examples:

```bash
pyalect register my_module:MyTranspiler as my_dialect
pyalect activate
pyalect config show
```


# Programatic Usage

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

# this will only be applied within the current interpreter
pyalect.register("my_dialect", MyTranspiler)
```


# Indicating Dialects

```python
# dialect=my_dialect
...
```


# How it Works

Pyalect hooks into Python's import system to register transpilers that are activated
when they find `# dialect=...` comments at the top of files. Registering transpilers
is done:

1. Via the CLI - configures the interpreter where Pyalect is installed.
2. Programatically - applies to modules imported in the current session.


# IPython and Jupyter Support

Dialects are supported in [IPython](http://ipython.org/) and [Jupyter](https://jupyter.org) via magics:

```python
%%dialect html
...
```
