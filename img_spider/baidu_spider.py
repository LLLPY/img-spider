# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/27 11:52
from .base_spider import BaseSpider


class ImgBaiduSpider(BaseSpider):
    API_URL = 'https://graph.baidu.com/s?card_key=&entrance=GENERAL&extUiData%5BisLogoShow%5D=1&f=all&isLogoShow=1&session_id=1085026259119883556&sign=121509d70cfb7ee2960aa01691164812&tn=pc&tpl_from=pc'
    CAMERA_XPATH = '//div/span/input'
    INPUT_XPATH = '//div/span/input'
    BUTTON_XPATH = '//div[@class="graph-container"]/div/span[@class="graph-d20-search-btn graph-d20-search-btn-result"]'
    SOURCE = '百度'

    # 页面上page的链接
    link_xpath = '//div[@class="general-imgcol"]/a'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)


