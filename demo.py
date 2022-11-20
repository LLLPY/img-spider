# 搜狗相似图片的查找：https://pic.sogou.com/pic/download.jsp?v=5&eid=1951&keyword=大海&index=1&groupIndex=0&xurl=https://i04piccdn.sogoucdn.com/612f94dde230da3d&durl=&category_kind=searchList_bigMode


import queue
import asyncio

import requests

q = queue.Queue()


# while True:
#     q.get()
#     print(1111)

async def foo():
    for i in range(10):
        await asyncio.sleep(1)
        print(i)
    return {'msg': 'done'}


def callback(msg):
    print(msg.result())


async def demo():
    task1 = asyncio.create_task(foo())
    task2 = asyncio.create_task(foo())
    task_list = []
    task_list.append(task1)
    task_list.append(task2)
    for task in task_list:
        task.add_done_callback(callback)
        await task

    print(666)


def process_txt():
    a = '''Accept: text/plain, */*; q=0.01
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Cookie: BIDUPSID=DAF9F732F5E7194E4C40073E6D597F5C; PSTM=1635870319; __yjs_duid=1_c9e50b0601fb34e9d5496d8d586043011635987389929; BAIDUID=6C15C2AA607EF52C69767D84A939DFCD:FG=1; indexPageSugList=%5B%22%E8%80%81%E9%BC%A0%22%2C%22%E6%89%8B%E9%87%8C%E6%8B%BF%E7%9D%80%E7%83%9F%E7%9A%84%E5%9B%BE%E7%89%87%E7%9C%9F%E5%AE%9E%22%2C%22%E8%87%AA%E5%97%A8%22%2C%22%E8%87%AA%E6%8B%8D%22%2C%22%E6%AF%94%E5%BF%83%E6%89%8B%E5%8A%BF%22%2C%22%E9%A3%9F%E5%93%81%E5%B9%BF%E5%91%8A%22%2C%22%E8%A7%86%E5%B1%8F%E5%B9%BF%E5%91%8A%22%2C%22%E6%8A%A4%E8%82%A4%E5%93%81%E5%B9%BF%E5%91%8A%22%2C%22%E6%B4%97%E9%9D%A2%E5%A5%B6%E5%B9%BF%E5%91%8A%22%5D; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=36553_37691_37771_34812_37777_37726_37794_37537_37673_37741_26350_37479; BAIDUID_BFESS=6C15C2AA607EF52C69767D84A939DFCD:FG=1; BCLID=10509626168540897276; BCLID_BFESS=10509626168540897276; BDSFRCVID=EDtOJeC62lJHcXTjfOFFJnMfFeXfHWTTH6aoHImG5mdPvRWmchMZEG0P3M8g0KubwlTDogKKKgOTHICF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; BDSFRCVID_BFESS=EDtOJeC62lJHcXTjfOFFJnMfFeXfHWTTH6aoHImG5mdPvRWmchMZEG0P3M8g0KubwlTDogKKKgOTHICF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; H_BDCLCKID_SF=tb4qoD-htCD3fb7Nb4k_-P6MQtOJWMT-0bFHWpcdKMnxjRQOQxjkhxuEQxovKfvUQNn7_JjOWpTVsI5zbh3-0l-D-U7uXfQxtN4e2CnjtpvhH4313MOobUPUyUJ9LUvA02cdot5yBbc8eIna5hjkbfJBQttjQn3hfIkj0DKLK-oj-DKwe5tM3e; H_BDCLCKID_SF_BFESS=tb4qoD-htCD3fb7Nb4k_-P6MQtOJWMT-0bFHWpcdKMnxjRQOQxjkhxuEQxovKfvUQNn7_JjOWpTVsI5zbh3-0l-D-U7uXfQxtN4e2CnjtpvhH4313MOobUPUyUJ9LUvA02cdot5yBbc8eIna5hjkbfJBQttjQn3hfIkj0DKLK-oj-DKwe5tM3e; delPer=0; PSINO=1; BA_HECTOR=25aga50h84a50k2k8k8lag6h1hnj5fq1e; ZFY=VUXSHNnFX4BfxSdSYesiZTioZSV91VQjThx3iw9fwYU:C; BDRCVFR[-pGxjrCMryR]=mk3SLVN4HKm; BDRCVFR[dG2JNJb_ajR]=mk3SLVN4HKm; ariaDefaultTheme=undefined; RT="z=1&dm=baidu.com&si=7m16wrp3oih&ss=lapaokf9&sl=u&tt=1t38&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=azay&ul=b2uy&hd=b2wa"; userFrom=www.baidu.com; ab_sr=1.0.1_ZmRmNjRhZTg2M2U1ZDk2YmRiN2EyYjRjYzRiMTM4Mzc1NTkzMGY3ZDBkOTlkY2Q5YjUwYzNjMTc0YmZhNDY1MjE1MWVjOTViZjgxMGM2MTBlNjU4MDc5YzdiNjFjMTYyOGQyZmNhYzM5YzgyMGNmNmNhMzY2YTU2ZWU2ODUyN2Y0OWEzNDNhZGYxOWMyNTM3YmI0MDI1Y2I2YmRlNmM2Mw==
Host: image.baidu.com
Referer: https://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&dyTabStr=MCwzLDEsNSw0LDcsOCwyLDYsOQ%3D%3D&word=%E7%8B%AE%E5%AD%90
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36
X-Requested-With: XMLHttpRequest'''
    res = {}
    for i in a.split('\n'):
        i = i.strip()
        k, v = i.rsplit(':', 1)
        k, v = k.strip(), v.strip()
        res[k] = v
    print(res)
    return res


def test_requests(url):
    headers = {
        # ':authority': 'image.so.com',
        # ':method': 'GET',
        # ':path': '/j?callback=jQuery183015169491838470628_1668932079185&q=%E7%BE%8E%E5%A5%B3&qtag=&pd=1&pn=60&correct=%E7%BE%8E%E5%A5%B3&adstar=0&tab=all&sid=42f308f3d240e2d83c9ad9e7c6e661aa&ras=6&cn=0&gn=0&kn=10&crn=0&bxn=20&cuben=0&pornn=0&manun=0&src=st&sn=90&ps=49&pc=49&_=1668932120483',
        # ':scheme': 'https',
        # 'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        # 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'zh-CN,zh;q=0.9',
        # 'cookie': '__guid=16527278.4082153822803365400.1646141706668.241; __huid=11Hvv3UD9R1dvCxvfpzmOac7pj%2BUE2vX1yEBTJb4qyB%2FQ%3D; QiHooGUID=D6991E17ACF01EAEA1F34D30D6B63266.1646280271067; so_huid=11Hvv3UD9R1dvCxvfpzmOac7pj%2BUE2vX1yEBTJb4qyB%2FQ%3D; biz_huid=11Hvv3UD9R1dvCxvfpzmOac7pj%2BUE2vX1yEBTJb4qyB%2FQ%3D; opqopq=3a2ed3b01e359398f6233bee8fb0f31b.1668931721; _S=b1b04cc9ffef0f68eadbb24d3fdbaa55; test_cookie_enable=null; tracker=st|1668932079233; gtHuid=1; erules=kd-63%7Cp1-2%7Cp4-9',
        # 'referer: https': '//image.so.com/i?q=%E7%BE%8E%E5%A5%B3&src=st',
        # 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        # 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty',
        # 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
        # 'x-requested-with': 'XMLHttpRequest'
    }
    res = requests.get(url, headers=headers, verify=False, timeout=5)
    print(res.text)



if __name__ == '__main__':
    # asyncio.run(demo())
    # import random
    # print(random.uniform(1,10))
    process_txt()
    # test_requests('https://image.so.com/j?q=%E7%BE%8E%E5%A5%B3&qtag=&pd=1&pn=60&adstar=0&tab=all&sid=15d39fba0b6f9e26589eed4f9434a0c5&ras=6&cn=0&gn=0&kn=11&crn=0&bxn=20&cuben=0&pornn=0&manun=4&sn=1&ps=1&pc=50')
