from .jsonpath import JSONPathParser

parser = JSONPathParser()
query = parser.parse("$[0].a")
data = [{"a": "ab"}]

# TODO:

for node in query.find(data):
    print(node.value)
