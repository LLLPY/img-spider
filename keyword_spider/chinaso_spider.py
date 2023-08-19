# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/19 21:08  

import json
from .base_spider import APISpider
from typing import *


# 关键字爬虫：根据关键字，爬取相关页面，产出imgurl
class KeywordChinaSoSpider(APISpider):
    API = 'https://www.chinaso.com/v5/general/v1/search/image?q={}&start_index={}&rn={}'
    SOURCE = '中国搜索'
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
    async def extract(cls, html:str)->List[Dict]:
        data_list = []
        # 数据抽取
        json_content = json.loads(html)
        res = json_content['data'].get('arrRes', [])
        for item in res:
            origin_img_url = item.get('url', '')
            thumb_img_url = item.get('largeimage', '')
            page_url = item.get('web_url', '')  # 图片所在的页面
            desc = item.get('ImageInfo', '')
            item = {
                'origin_img_url': origin_img_url,
                'thumb_img_url': thumb_img_url,
                'page_url': page_url,
                'desc': desc
            }

            data_list.append(item)
        return data_list

