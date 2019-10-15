import ast
import sys
from traceback import print_exc
from typing import Any, List, Optional, Type

from . import dialect

try:
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.core.magic import magics_class, Magics, cell_magic
except ImportError:
    pass
else:
    _transpiler_fifo_queue: List[dialect.Transpiler] = []

    class DialectNodeTransformer(ast.NodeTransformer):
        """Node transformer defined to hook into IPython."""

        def visit(self, node: ast.AST) -> ast.AST:
            try:
                if isinstance(node, ast.Module):
                    first_node = next(ast.iter_child_nodes(node))
                    if (
                        isinstance(first_node, ast.Assign)
                        and isinstance(first_node.targets[0], ast.Name)
                        and first_node.targets[0].id == "_DIALECT_"
                        and isinstance(first_node.value, ast.Str)
                    ):
                        node.body.pop(0)
                        node = _transpiler_fifo_queue.pop(0).transform_ast(node)
                    return node
            except Exception:
                print_exc(file=sys.stderr)
                return node
            else:
                return node

    def register_to_ipython_shell(shell: Optional[InteractiveShell] = None) -> None:
        """Register transpiler hooks to IPython shell."""
        shell_inst: InteractiveShell = shell or InteractiveShell.instance()

        @magics_class
        class DialectMagics(Magics):  # type: ignore
            def __init__(self, shell: InteractiveShell, **kwargs: Any) -> None:
                super().__init__(shell, **kwargs)
                for transformer in shell.ast_transformers:
                    if isinstance(transformer, DialectNodeTransformer):
                        break
                else:
                    shell.ast_transformers.insert(0, DialectNodeTransformer())

            @cell_magic  # type: ignore
            def dialect(self, cell_dialect: str, raw_cell: str) -> None:
                transpiler = dialect.transpiler(cell_dialect)
                _transpiler_fifo_queue.append(transpiler)
                self.shell.run_cell(
                    # We need to prepend this since we can't look for
                    # the dialect comment when transforming the AST.
                    f"_DIALECT_ = {cell_dialect!r}\n"
                    + transpiler.transform_src(raw_cell)
                )

        shell_inst.register_magics(DialectMagics)

    if InteractiveShell.initialized():
        register_to_ipython_shell()
    else:
        original = InteractiveShell.instance.__func__

        def wrapper(
            cls: Type[InteractiveShell], *args: Any, **kwargs: Any
        ) -> InteractiveShell:
            inst = original(cls, *args, **kwargs)
            register_to_ipython_shell(inst)
            return inst

        InteractiveShell.instance = classmethod(wrapper)
