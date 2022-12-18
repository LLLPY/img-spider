# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/12/18 12:03  


from .base_spider import BaseSpider


class Img360Spider(BaseSpider):
    API_URL = 'https://st.so.com/stu?a=list&imkey=t024231a799b918f909.jpg&tp=imgurl&src=image&keyword=&guess=&sim=&camtype=1&srcsp=st_search'
    CAMERA_XPATH = '//s[@id="iconSt"]'
    INPUT_XPATH = '//div[@class="st_input"]/input'
    BUTTON_XPATH = '//form/input[@class="st_submit"]'
    SOURCE = '360'

    # 页面上page的链接
    link_xpath = '//li[@class="cell"]/div/a'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)
