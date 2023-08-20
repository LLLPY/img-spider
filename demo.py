import hashlib

a = '111'
print(hashlib.md5(a.encode(encoding='utf8')).hexdigest())