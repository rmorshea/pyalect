import re

DIALECT_COMMENT = re.compile(r"^# ?dialect ?= ?(.+)\n?$")
DIALECT_NAME = re.compile(r"^[\w\.]+$")
TRANSPILER_NAME = re.compile(r"^[\w\.]+\:[\w\.]+$")
