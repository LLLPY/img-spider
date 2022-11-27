# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/7 21:24

import re
import asyncio
from .base_spider import BaseSpider
import conf.conf as conf
import conf.model as model
import utils.utils as utils


# 关键字爬虫：根据关键字，爬取相关页面，产出imgurl
class BaiduSpider(BaseSpider):
    API = 'https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&fp=result&word={}&cl=2&lm=-1&ie=utf-8&oe=utf-8&pn={}&rn={}'
    HEADERS = {
        'Accept': 'text/plain, */*; q=0.01', 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9', 'Connection': 'keep-alive',
        'Host': 'image.baidu.com',
        'Referer': 'https//image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&dyTabStr=MCwzLDEsNSw0LDcsOCwyLDYsOQ%3D%3D&word=%E7%8B%AE%E5%AD%90',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'cookie': 'BIDUPSID=DAF9F732F5E7194E4C40073E6D597F5C; PSTM=1635870319; __yjs_duid=1_c9e50b0601fb34e9d5496d8d586043011635987389929; BAIDUID=6C15C2AA607EF52C69767D84A939DFCD:FG=1; indexPageSugList=%5B%22%E8%80%81%E9%BC%A0%22%2C%22%E6%89%8B%E9%87%8C%E6%8B%BF%E7%9D%80%E7%83%9F%E7%9A%84%E5%9B%BE%E7%89%87%E7%9C%9F%E5%AE%9E%22%2C%22%E8%87%AA%E5%97%A8%22%2C%22%E8%87%AA%E6%8B%8D%22%2C%22%E6%AF%94%E5%BF%83%E6%89%8B%E5%8A%BF%22%2C%22%E9%A3%9F%E5%93%81%E5%B9%BF%E5%91%8A%22%2C%22%E8%A7%86%E5%B1%8F%E5%B9%BF%E5%91%8A%22%2C%22%E6%8A%A4%E8%82%A4%E5%93%81%E5%B9%BF%E5%91%8A%22%2C%22%E6%B4%97%E9%9D%A2%E5%A5%B6%E5%B9%BF%E5%91%8A%22%5D; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=36553_37691_37771_34812_37777_37726_37794_37537_37673_37741_26350_37479; BAIDUID_BFESS=6C15C2AA607EF52C69767D84A939DFCD:FG=1; BCLID=10509626168540897276; BCLID_BFESS=10509626168540897276; BDSFRCVID=EDtOJeC62lJHcXTjfOFFJnMfFeXfHWTTH6aoHImG5mdPvRWmchMZEG0P3M8g0KubwlTDogKKKgOTHICF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; BDSFRCVID_BFESS=EDtOJeC62lJHcXTjfOFFJnMfFeXfHWTTH6aoHImG5mdPvRWmchMZEG0P3M8g0KubwlTDogKKKgOTHICF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; H_BDCLCKID_SF=tb4qoD-htCD3fb7Nb4k_-P6MQtOJWMT-0bFHWpcdKMnxjRQOQxjkhxuEQxovKfvUQNn7_JjOWpTVsI5zbh3-0l-D-U7uXfQxtN4e2CnjtpvhH4313MOobUPUyUJ9LUvA02cdot5yBbc8eIna5hjkbfJBQttjQn3hfIkj0DKLK-oj-DKwe5tM3e; H_BDCLCKID_SF_BFESS=tb4qoD-htCD3fb7Nb4k_-P6MQtOJWMT-0bFHWpcdKMnxjRQOQxjkhxuEQxovKfvUQNn7_JjOWpTVsI5zbh3-0l-D-U7uXfQxtN4e2CnjtpvhH4313MOobUPUyUJ9LUvA02cdot5yBbc8eIna5hjkbfJBQttjQn3hfIkj0DKLK-oj-DKwe5tM3e; delPer=0; PSINO=1; BA_HECTOR=25aga50h84a50k2k8k8lag6h1hnj5fq1e; ZFY=VUXSHNnFX4BfxSdSYesiZTioZSV91VQjThx3iw9fwYU:C; BDRCVFR[-pGxjrCMryR]=mk3SLVN4HKm; BDRCVFR[dG2JNJb_ajR]=mk3SLVN4HKm; ariaDefaultTheme=undefined; RT="z=1&dm=baidu.com&si=7m16wrp3oih&ss=lapaokf9&sl=u&tt=1t38&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=azay&ul=b2uy&hd=b2wa"; userFrom=www.baidu.com; ab_sr=1.0.1_ZmRmNjRhZTg2M2U1ZDk2YmRiN2EyYjRjYzRiMTM4Mzc1NTkzMGY3ZDBkOTlkY2Q5YjUwYzNjMTc0YmZhNDY1MjE1MWVjOTViZjgxMGM2MTBlNjU4MDc5YzdiNjFjMTYyOGQyZmNhYzM5YzgyMGNmNmNhMzY2YTU2ZWU2ODUyN2Y0OWEzNDNhZGYxOWMyNTM3YmI0MDI1Y2I2YmRlNmM2Mw==',
    }

    def __init__(self, keyword: str) -> None:
        super(BaiduSpider, self).__init__(keyword)

    @classmethod
    def extract(cls, response):
        json_content = response.json()
        res = json_content.get('data', [])
        data_list = []
        for item in res:
            if item:
                origin_img_url = cls.parse_encrypt_url(item.get('objURL', ''))  # 原图地址
                thumb_img_url = cls.parse_encrypt_url(item.get('objURL', ''))  # 缩略图地址
                page_url = cls.parse_encrypt_url(item.get('fromURL', ''))  #
                item = {
                    'origin_img_url': origin_img_url,
                    'thumb_img_url': thumb_img_url,
                    'page_url': page_url
                }
                img_obj = model.Img('', '', origin_img_url, thumb_img_url)
                if img_obj not in conf.img_set:
                    data_list.append(item)
                return data_list

    # 通过以图搜图的方式来获取相应的page链接
    @utils.clocked
    def get_page_url_by_img(self):
        pass

    # 解析加密的url
    @staticmethod
    def parse_encrypt_url(
            encrypt_url: str = 'ippr_z2C$qAzdH3FAzdH3Fi7wkwg_z&e3Bv54AzdH3FrtgfAzdH3F8ddal9lcaAzdH3F') -> str:
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


async def baidu_spider(keyword: str):
    baidu_spider = BaiduSpider(keyword)
    await asyncio.gather(
        baidu_spider.get_page_and_img_by_keyword(),  # 从接口中获取图片地址和页面地址
        # baidu_spider.get_img_url_on_page(),
        baidu_spider.download_imgs()
    )  # 并发运行


# 执行
def run_baidu_spider(keyword: str):
    asyncio.run(baidu_spider(keyword))
    # conf.img_spider_logger.error(f'baidu_speider done,because of error:{e}...')


if __name__ == '__main__':
    pass
