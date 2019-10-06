# Pyalect

Dynamically transpiling Python for Good


# Console Usage

```
pyalect (activate | deactivate)
pyalect register <transpiler> as <dialect> [--force]
pyalect deregister (<dialect> | <transpiler> [as <dialect])
pyalect config (show | path)
```

Examples:

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


# IPython and Jupyter Support

Dialects are supported in [IPython](http://ipython.org/) and [Jupyter](https://jupyter.org) via magics:

```python
%%dialect html
...
```
