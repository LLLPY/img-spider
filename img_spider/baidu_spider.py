# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/27 11:52
from .base_spider import BaseSpider


class ImgBaiduSpider(BaseSpider):
    API_URL = 'https://graph.baidu.com/s?sign=1226967dba6bed09cebca01645431413&f=all&tn=pc&tn=pc&idctag=nj&idctag=nj&logid=2944232641&pageFrom=graph_upload_bdbox&pageFrom=graph_upload_pcshitu&srcp=&gsid=&extUiData%5BisLogoShow%5D=1&tpl_from=pc&entrance=general'
    CAMERA_XPATH = '//div/span/input'
    INPUT_XPATH = '//div/span/input'
    BUTTON_XPATH = '//div[@class="graph-container"]/div/span[@class="graph-d20-search-btn graph-d20-search-btn-result"]'
    SOURCE = '百度'

    # 页面上page的链接
    link_xpath = '//div[@class="general-imgcol"]/a'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)


