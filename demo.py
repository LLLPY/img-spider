import json

a = '{"aaa":"\"公牛性欲\""}'
a = a.replace('\\', '')
print(a)
b = json.loads(a)
print(b)
