from .jsonpath import JSONPathParser

parser = JSONPathParser()
query = parser.parse("$[?search(@.a,@.b,@.c)]")
data = [{"a": "ab"}]

# print(query)

# for node in query.find(data):
#     print(node.value)
