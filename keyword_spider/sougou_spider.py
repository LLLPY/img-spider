# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/17 22:40

import asyncio
from .base_spider import BaseSpider
import conf.model as model
import conf.conf as conf


# 关键字爬虫：根据关键字，爬取相关页面，产出imgurl
class SouGouSpider(BaseSpider):
    API = 'https://pic.sogou.com/napi/pc/searchList?mode=1&query={}&start={}&xml_len={}'
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
    SOURCE = '搜狗'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)

    @classmethod
    def extract(cls, response):
        # 数据抽取
        json_content = response.json()
        data = json_content.get('data',{}) or {}
        data_list = []
        # groupPic_json
        for item in data.get('groupPic_json', []):
            for inner_item in item:
                origin_img_url = inner_item.get('picUrl', '')  # 原图
                thumb_img_url = inner_item.get('thumbUrl', '')  # 缩略图
                page_url = inner_item.get('pageUrl', '')
                desc = inner_item.get('title', '')
                item = {
                    'origin_img_url': origin_img_url,
                    'thumb_img_url': thumb_img_url,
                    'page_url': page_url,
                    'desc': desc
                }
                data_list.append(item)

        # items
        for item in data.get('items', []):
            origin_img_url = item.get('oriPicUrl', '')  # 原图
            thumb_img_url = item.get('thumbUrl', '')  # 缩略图
            page_url = item.get('url', '')  # 原图所在的页面
            desc = item.get('title', '')
            item = {
                'origin_img_url': origin_img_url,
                'thumb_img_url': thumb_img_url,
                'page_url': page_url,
                'desc': desc
            }
            data_list.append(item)

        return data_list


async def sougou_spider(keyword: str):
    sougou_spider = SouGouSpider(keyword)
    await asyncio.gather(
        sougou_spider.get_page_and_img_on_api(),
        # _360_spider.get_img_url_on_page(),
    )  # 并发运行


# 执行
def run_sougou_spider(keyword: str):
    asyncio.run(sougou_spider(keyword))


if __name__ == '__main__':
    run_sougou_spider('大海')
