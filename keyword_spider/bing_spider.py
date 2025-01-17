# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/17 22:40  

import re
from .base_spider import APISpider
import json
from typing import *


# 关键字爬虫：根据关键字，爬取相关页面，产出imgurl
class KeywordBingSpider(APISpider):
    API = 'https://cn.bing.com/images/async?q={}&first={}&count={}&datsrc=I&layout=RowBased_Landscape&mmasync=1'
    SOURCE = 'bing'
    HEADERS = {
        'cookie': '__guid=16527278.4082153822803365400.1646141706668.241; __huid=11Hvv3UD9R1dvCxvfpzmOac7pj%2BUE2vX1yEBTJb4qyB%2FQ%3D; QiHooGUID=D6991E17ACF01EAEA1F34D30D6B63266.1646280271067; so_huid=11Hvv3UD9R1dvCxvfpzmOac7pj%2BUE2vX1yEBTJb4qyB%2FQ%3D; biz_huid=11Hvv3UD9R1dvCxvfpzmOac7pj%2BUE2vX1yEBTJb4qyB%2FQ%3D; opqopq=19dad04ff4e51811cf8d73967410ac30.1668695144; gtHuid=1; test_cookie_enable=null; tracker=tab_www|1668695215912; erules=p1-10%7Cp4-15%7Ckd-1',
        'referer': 'https://image.so.com/i?q=%E5%A4%A7%E6%B5%B7&src=tab_www',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
        'Connection': 'keep-alive',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)

    @classmethod
    async def done(cls, data_list) -> bool:
        if not cls.per_page_count:
            cls.per_page_count = len(data_list)

        return len(data_list) == 0 or len(data_list) < cls.per_page_count

    @classmethod
    async def extract(cls, html: str) -> List[Dict]:
        data_list = []
        # 数据抽取
        json_content = re.sub(r'&quot;', '"', html)
        res = re.findall('m="(\{.*?\})"', json_content)
        for item in res:
            item = json.loads(item) or {}
            origin_img_url = item.get('murl', '')  # 原始图
            thumb_img_url = item.get('turl', '')  # 缩略图
            page_url = item.get('purl', '')  # 图片所在的页面
            desc = item.get('t', '')
            item = {
                'origin_img_url': origin_img_url,
                'thumb_img_url': thumb_img_url,
                'page_url': page_url,
                'desc': desc
            }
            data_list.append(item)
        return data_list
