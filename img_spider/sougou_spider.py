# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/12/18 20:30

from .base_spider import BaseSpider


class ImgSougouSpider(BaseSpider):
    API_URL = 'https://pic.sogou.com/ris'
    CAMERA_XPATH = '//a[@class="camera"]'
    INPUT_XPATH = '//div[@class="identify-query"]/input'
    BUTTON_XPATH = '//div[@class="identify-query"]/span'
    SOURCE = '搜狗'

    # 页面上page的链接
    link_xpath = '//li/div[@class="img-layout"]/a[1]'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)
