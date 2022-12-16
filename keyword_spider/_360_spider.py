# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/17 22:40

import json
from .base_spider import BaseSpider
from typing import *


# 关键字爬虫：根据关键字，爬取相关页面，产出imgurl
class Keyword360Spider(BaseSpider):

    API = 'https://image.so.com/j?q={}&qtag=&pd=1&pn=60&adstar=0&tab=all&sid=15d39fba0b6f9e26589eed4f9434a0c5&ras=6&cn=0&gn=0&kn=11&crn=0&bxn=20&cuben=0&pornn=0&manun=4&sn={}&pc={}'

    SOURCE = '360'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword=keyword)

    # 3.抽取规则，从接口响应的数据中抽取出图片和页面的地址
    @classmethod
    def extract(cls, html: str) -> List[Dict]:
        json_content = json.loads(html)
        res = json_content['list']
        data_list = []
        for item in res:
            origin_img_url = item['img']  # 原图
            thumb_img_url = item['thumb']  # 缩略图
            page_url = item['link']  # 图片所在的页面
            desc = item['title']
            item = {
                'origin_img_url': origin_img_url,
                'thumb_img_url': thumb_img_url,
                'page_url': page_url,
                'desc': desc
            }

            data_list.append(item)

        return data_list
