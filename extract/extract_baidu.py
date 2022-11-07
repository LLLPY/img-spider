# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/6 22:57  

import re

# 解析加密的url
def parse_encrypt_url(encrypt_url: str = 'ippr_z2C$qAzdH3FAzdH3Fi7wkwg_z&e3Bv54AzdH3FrtgfAzdH3F8ddal9lcaAzdH3F') -> str:
    mapping = {
        'w': "a",
        'k': "b",
        'v': "c",
        '1': "d",
        'j': "e",
        'u': "f",
        '2': "g",
        'i': "h",
        't': "i",
        '3': "j",
        'h': "k",
        's': "l",
        '4': "m",
        'g': "n",
        '5': "o",
        'r': "p",
        'q': "q",
        '6': "r",
        'f': "s",
        'p': "t",
        '7': "u",
        'e': "v",
        'o': "w",
        '8': "1",
        'd': "2",
        'n': "3",
        '9': "4",
        'c': "5",
        'm': "6",
        '0': "7",
        'b': "8",
        'l': "9",
        'a': "0",
        '_z2C$q': ":",
        "_z&e3B": ".",
        'AzdH3F': "/"
    }  # 映射表
    encrypt_url = re.sub('AzdH3F', '/', encrypt_url)  # 替换
    encrypt_url = re.sub("_z&e3B", ".", encrypt_url)
    encrypt_url = re.sub('_z2C\$q', ":", encrypt_url)
    url_list = []
    for c in encrypt_url:
        if c in mapping:  # 替换掉加密的url中的一些字符
            c = mapping[c]
        url_list.append(c)
    return ''.join(url_list)

if __name__ == '__main__':
    objURL="ipprf_z2C$qAzdH3FAzdH3F2t42d_z&e3Bkwt17_z&e3Bv54AzdH3Ft4w2j_fjw6viAzdH3Ff6v=ippr%nA%dF%dFikt42_z&e3Bka_z&e3B7rwty7g_z&e3Bv54%dFwb80cbw898m1bucwdbjacb81jkmanbalm9unm9vumdwj-AGOlnv_uomcb&6juj6=ippr%nA%dF%dFikt42_z&e3Bka_z&e3B7rwty7g_z&e3Bv54&wrr=daad&ftzj=ullll,8aaaa&q=wba&g=a&2=ag&u4p=w7p5?fjv=8m0ann0adc&p=ukubcnk1dbdb9ja01j11jck1uwna0vvc"

    url=parse_encrypt_url(objURL)
    print(url)