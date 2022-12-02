# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/7 21:24

import re
import asyncio
from .base_spider import BaseSpider
import conf.conf as conf
import conf.model as model
import json

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
        'cookie': 'BIDUPSID=DAF9F732F5E7194E4C40073E6D597F5C; PSTM=1635870319; BD_UPN=12314753; __yjs_duid=1_c9e50b0601fb34e9d5496d8d586043011635987389929; BAIDUID=6C15C2AA607EF52C69767D84A939DFCD:FG=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BAIDUID_BFESS=6C15C2AA607EF52C69767D84A939DFCD:FG=1; ZFY=XUrg3jWgemJTVFpiSSQpTPSVLsGT4AKjYDjak7GWm:BU:C; channel=baidusearch; B64_BOT=1; BD_HOME=1; H_PS_PSSID=37856_36553_37771_37840_34812_37765_37794_37836_37760_37850_26350_37479; delPer=0; BD_CK_SAM=1; PSINO=1; BA_HECTOR=8101850k8k8l2ga18h848ksn1hoc0fv1h; baikeVisitId=3a8b8892-ce10-4062-b40d-823ec6b54aa2; BDRCVFR[tox4WRQ4-Km]=mk3SLVN4HKm; BDRCVFR[-pGxjrCMryR]=mk3SLVN4HKm; ab_sr=1.0.1_Mzc2ODg2NTU0YjUyNTE1ZWI1OWNjNjVmMmE3YjIyMDc4MDk2MDMwYzI5NTNhOTE4ZWJmNTNhMjQyYjk2MDJiNjc3ZjQ5NTgzNjdmNTQ5YTY3YWY0MWViYzM0NWZlOThhODFmMGQ4ZDlkNGM3MDIxODE4MGM4MGJhYTgzYWEzMzhlNTA4YjI0YmQ3YjgxMjQ0NTEwYTk0NDYwNjkzNGExMw==; COOKIE_SESSION=2410_0_5_5_6_11_0_0_4_3_0_2_8156_0_0_0_1669559295_0_1669729129%7C9%23191_7_1669206482%7C3; H_PS_645EC=27f7%2FyFYd1VMsNCQsd%2Ff4Q0gNH1syKuLpfq5Cu2ys3Tt0ZHSicpCtz7Jk0E'
    }
    SOURCE = '百度'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)

    @classmethod
    def extract(cls, response):
        try:
            json_content = response.json()
            item_list = json_content.get('data', [])
        except:
            item_list=cls.extract_with_re(response.text)
        
        data_list = []
        for item in item_list:
            origin_img_url = cls.parse_encrypt_url(item.get('objURL', ''))  # 原图地址
            thumb_img_url = cls.parse_encrypt_url(item.get('objURL', ''))  # 缩略图地址
            page_url = cls.parse_encrypt_url(item.get('fromURL', ''))  # 页面地址
            desc = item.get('fromPageTitleEnc', '') #描述
            if item:
                item = {
                    'origin_img_url': origin_img_url,
                    'thumb_img_url': thumb_img_url,
                    'page_url': page_url,
                    'desc': desc
                }
                data_list.append(item)
        return data_list

    
    @staticmethod
    def extract_with_re(html):
        item_list=[]
        # origin_img_list=re.findall(r'objURL":"(.*?)"',html)
        thumb_img_list=re.findall(r'thumbURL":"(.*?)"',html)
        page_list=re.findall(r'fromURL":"(.*?)"',html)
        desc_list=re.findall(r'fromPageTitleEnc":"(.*?)"',html)
        for item in zip(thumb_img_list,page_list,desc_list):
            item = {
                'objURL': item[0],
                'fromURL': item[1],
                'fromPageTitleEnc': item[2],
            }
            item_list.append(item)
        return item_list
            
        
    
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
        baidu_spider.get_page_and_img_on_api(),  # 从接口中获取图片地址和页面地址
        # baidu_spider.get_img_url_on_page(),
    )  # 并发运行


# 执行
def run_baidu_spider(keyword: str):
    asyncio.run(baidu_spider(keyword))


if __name__ == '__main__':
    pass
