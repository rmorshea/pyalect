import sys
from types import CodeType
from typing import Any, Optional


class DialectError(Exception):
    """Base error for dialects."""

    def __init__(
        self, error: Any, filename: Optional[str] = None, line: Optional[int] = None
    ) -> None:
        super().__init__(error)
        self.filename = filename or "<string>"
        self.line = line or 1


def reraise_dialect_error() -> None:
    """Reraise an exception """
    exc_info = sys.exc_info()

    if exc_info[1] is None:
        raise RuntimeError(
            "No error to reraise - this function must be used inside an 'except:' block"
        )
    if not isinstance(exc_info[1], DialectError):
        raise TypeError(f"Exception must be a 'DialectError', not {exc_info[1]}")

    exc_value: DialectError = exc_info[1]

    # and fake the exception
    line_shift = "\n" * (exc_value.line - 1)
    raise_expr = "raise RuntimeError('dialect failed')"
    code = compile(line_shift + raise_expr, exc_value.filename, "exec")

    if exc_value.__traceback__ is not None:
        location = exc_value.__traceback__.tb_frame.f_code.co_name
        # depending on implementation changing the
        # location might not work so we have to try it
        try:
            code = CodeType(
                0,
                code.co_kwonlyargcount,
                code.co_nlocals,
                code.co_stacksize,
                code.co_flags,
                code.co_code,
                code.co_consts,
                code.co_names,
                code.co_varnames,
                exc_value.filename,
                location,
                code.co_firstlineno,
                code.co_lnotab,
                (),
                (),
            )
        except Exception:
            pass

    # execute the code and catch the new traceback
    try:
        exec(code, {}, {})
    except Exception:
        new_exc_info = sys.exc_info()
        if new_exc_info[2] is None:
            raise RuntimeError("Failed to re-raise") from exc_value
        new_tb = new_exc_info[2].tb_next

    # return without this frame
    raise exc_value.with_traceback(new_tb)
