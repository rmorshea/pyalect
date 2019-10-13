class MockTranspiler:
    def __init__(self, dialect):
        self.dialect = dialect

    def transform_src(self, source):
        self.source = source
        return source

    def transform_ast(self, node):
        self.node = node
        return node
