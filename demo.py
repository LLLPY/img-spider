from urllib.parse import urlparse

a='https://www.lll.plus/aaa/bb/cc'
host =a.replace('//', '*').split('/', 1)[0].replace('*', '//')
b=urlparse(a)
print(b.hostname)
print(b.path)
print(b.scheme)
