from .jsonpath import JSONPathParser

parser = JSONPathParser()
query = parser.parse("$[?@.a<='c']")
data = {"foo": {"bar": 99}}

for node in query.find(data):
    print(node.value)
