import ast
from typing import Optional, Type, Any

from . import dialect


try:
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.core.magic import magics_class, Magics, cell_magic
except ImportError:
    pass
else:

    class DialectNodeTransformer(ast.NodeTransformer):
        def visit(self, node: ast.AST) -> ast.AST:
            first_node = next(ast.iter_child_nodes(node))
            if (
                isinstance(first_node, ast.Assign)
                and isinstance(first_node.targets[0], ast.Name)
                and first_node.targets[0].id == "_DIALECT_"
                and isinstance(first_node.value, ast.Str)
            ):
                transpiler = dialect.transpiler(first_node.value.s)
                node = transpiler.transform_ast(node)
            return node

    def register_to_ipython_shell(shell: Optional[InteractiveShell] = None) -> None:
        shell_inst: InteractiveShell = shell or InteractiveShell.instance()

        @magics_class
        class DialectMagics(Magics):  # type: ignore
            def __init__(self, shell: InteractiveShell, **kwargs: Any) -> None:
                super().__init__(shell, **kwargs)
                shell.ast_transformers.insert(0, DialectNodeTransformer())

            @cell_magic  # type: ignore
            def dialect(self, cell_dialect: str, raw_cell: str) -> None:
                transpiler = dialect.transpiler(cell_dialect)
                self.shell.run_cell(
                    # We need to prepend this ince we can't look for
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
