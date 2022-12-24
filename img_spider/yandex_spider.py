# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/12/18 20:47

from .base_spider import BaseSpider
import model.models as model
from urllib.parse import quote
import asyncio


class ImgYandexSpider(BaseSpider):
    API_URL = 'https://yandex.com/images/search?family=yes&rpt=imageview&url={}&cbir_page=similar'
    SOURCE = 'yandex'

    # 页面上page的链接
    link_xpath = '//div/a[@class="serp-item__link"]'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)

    async def get_page(self, img_obj: model.Img):
        try:
            self.chrome.get(self.API_URL.format(quote(img_obj.url)))
        except Exception as e:
            print(e)
        # 等待5秒用于加载
        await asyncio.sleep(10)

        # 启动页面下拉定时器
        self.chrome.execute_script(self.setInterval_js)

        # TODO 点击READMORE 加载跟多图片
        # TODO 图片的使用区分，区分当前图片是用于什么搜索引擎
