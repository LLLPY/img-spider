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
    link_xpath = '//div[@jsname]/div[@data-ved]'

    def __init__(self, keyword: str) -> None:
        super().__init__(keyword)

    async def get_page(self, img_obj: model.Img) -> None:
        self.chrome.get(self.API_URL)
        self.chrome.find_element(By.XPATH, '//div/img[@alt="Camera search"]/..').click()  # 相机
        await asyncio.sleep(3)
        self.chrome.find_element(By.XPATH, '//input[@text="text"]').send_keys(img_obj.url)  # 输入框
        self.chrome.find_element(By.XPATH, '//div[@role="button" and contains(text(),"Search")]').click()  # 提交
        await asyncio.sleep(2)
        a = '''//a[@aria-label="Find image source
"]'''
        link = self.chrome.find_element(By.XPATH, a).get_attribute('href')
        self.chrome.get(link)
        await asyncio.sleep(5)
        try:
            self.chrome.find_element(By.XPATH, '//div/h3').click()  # 相似图片的链接
            await asyncio.sleep(2)
            self.chrome.execute_script(self.setInterval_js)
        except Exception as res:
            print(f'没有相似图片...{res}')
            return

    # 通过图片搜索，获取相似图片的页面，提取页面中相似图片所在的页面链接
    async def get_img_and_page_by_img(self, img_obj: model.Img) -> None:

        await self.get_page(img_obj)

        while True:

            await asyncio.sleep(3)

            item_list = self.chrome.find_elements(By.XPATH, self.link_xpath)

            # 结束抽取
            end = False
            if len(item_list) > self.MAX_PER_PAGE:
                end = True
            else:
                for _ in range(5):
                    await asyncio.sleep(1)
                    if len(item_list) != len(
                            set(self.chrome.find_elements(By.XPATH, self.link_xpath))):
                        break
                else:
                    end = True

            if end:
                self.logger.warning(
                    f'[{self.__class__.__name__}]抽取结束,共抽取到{len(item_list)}个item...')
                break
        try:
            self.chrome.execute_script(self.delInterval_js)
        except Exception as e:
            self.logger.error(
                f'[{self.__class__.__name__}]浏览器中的定时器删除失败,msg:{e}...')

        for item in self.chrome.find_elements(By.XPATH, self.link_xpath):
            try:
                item.click()
                await asyncio.sleep(3)
                page = self.chrome.find_element(By.XPATH,
                                                '//*[@id="Sva75c"]/div[2]/div/div[2]/div[2]/div[2]//c-wiz/div[2]/div[1]/div[1]/div[2]/div/a')
                if page:
                    page_url = page.get_attribute('href')
                img = self.chrome.find_element(By.XPATH,
                                               '//*[@id="Sva75c"]/div[2]/div/div[2]/div[2]/div[2]//c-wiz/div[2]/div[1]/div[1]/div[2]/div/a/img')
                if img:
                    img_url = img.get_attribute('src')

                print(1111, page_url, img_url)
                #TODO 上传img和page到服务器


            except Exception as res:
                print(res)
