# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/12/18 22:23
import asyncio

from selenium.webdriver.common.by import By

from .base_spider import BaseSpider
import model.models as model


class ImgGoogleSpider(BaseSpider):
    API_URL = 'https://www.google.com/search?q=imgs&hl=en&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiZjZeR6Zr2AhXORd4KHQKuC-gQ_AUoAXoECAEQAw&biw=1536&bih=760&dpr=1.25'

    SOURCE = 'google'

    # 页面上page的链接
    link_xpath = '//div[@class="general-imgcol"]/a'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)

    async def get_page(self, img_obj: model.Img) -> None:
        self.chrome.get(self.API_URL)
        self.chrome.find_element(By.XPATH, '//span[@class="F7UV7d"]').click()  # 相机
        self.chrome.find_element(By.XPATH, '//input[@class="TIjxY"]').send_keys(img_obj.url)  # 输入框
        self.chrome.find_element(By.XPATH, '//input[@type="submit"]').click()  # 提交

        await asyncio.sleep(5)

        try:
            self.chrome.find_element(By.XPATH, '//h3[@role and @class]').click()  # 相似图片的链接
            self.chrome.execute_script(self.setInterval_js)
        except Exception as res:
            print(f'没有相似图片...{res}')
            return
