# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/27 11:52  
from selenium.webdriver.common.by import By
import asyncio
from .base_spider import BaseSpider
import model.models as model


class BaiduSpider(BaseSpider):
    API_URL = 'https://graph.baidu.com/s?sign=1226967dba6bed09cebca01645431413&f=all&tn=pc&tn=pc&idctag=nj&idctag=nj&logid=2944232641&pageFrom=graph_upload_bdbox&pageFrom=graph_upload_pcshitu&srcp=&gsid=&extUiData%5BisLogoShow%5D=1&tpl_from=pc&entrance=general'
    CAMERA_XPATH = '//div/span/input'
    INPUT_XPATH = '//div/span/input'
    BUTTON_XPATH = '//div[@class="graph-container"]/div/span[@class="graph-d20-search-btn graph-d20-search-btn-result"]'
    SOURCE = '百度'

    def __init__(self, keyword):
        super().__init__(keyword)

    # 通过图片搜索，获取相似图片的页面，提取页面中相似图片所在的页面链接
    async def get_img_and_page_by_img(self, img_obj: model.Img):
        self.chrome.get(self.API_URL)
        self.chrome.find_element(By.XPATH, self.CAMERA_XPATH).click()
        self.chrome.find_element(By.XPATH, self.INPUT_XPATH).send_keys(img_obj.url)
        self.chrome.find_element(By.XPATH, self.BUTTON_XPATH).click()

        # 等待5秒用于加载
        await asyncio.sleep(5)

        # 启动页面下拉定时器
        self.chrome.execute_script(self.setInterval_js)

        page_url_set = set()
        img_url_set = set()
        while True:

            await asyncio.sleep(3)

            item_list = self.chrome.find_elements(By.XPATH, '//div[@class="general-imgcol"]/a')
            for item in item_list:
                page_url = item.get_attribute('href')  # 节点的属性值
                page_url_set.add(page_url)

                img = item.find_element(By.TAG_NAME, 'img')
                img_url = img.get_attribute('src')
                img_url_set.add(img_url)

            # 结束抽取
            end = False
            if len(item_list) > self.MAX_PER_PAGE:
                end = True
            else:
                for _ in range(5):
                    await asyncio.sleep(1)
                    if len(item_list) != len(
                            set(self.chrome.find_elements(By.XPATH, '//div[@class="general-imgcol"]/a'))):
                        break
                else:
                    end = True

            if end:
                self.logger.warning(f'[{self.__class__.__name__}]抽取结束,共抽取到{len(item_list)}个item...')
                break

        page_dict_list = []
        img_dict_list = []

        for page_url in page_url_set:
            page_obj = model.Page(keyword=self.keyword, url=page_url, source=self.SOURCE)
            page_dict_list.append(page_obj.to_dict())

        cur_page_obj = model.Page(keyword=self.keyword, url=self.chrome.current_url, source=self.SOURCE,
                                  status=model.Page.STATUS_CRAWLED, deep=4)
        page_dict_list.append(cur_page_obj.to_dict())

        for img_url in img_url_set:
            new_img_obj = model.Img(keyword=self.keyword, url=img_url, source=self.SOURCE, thumb_url=img_url,
                                    page_url=self.chrome.current_url)
            img_dict_list.append(new_img_obj.to_dict())

        # 上传服务器
        img_obj.status = model.Img.STATUS_CRAWLED
        img_res = await self.client.update_img([img_obj.to_dict()])
        if img_res['code'] != '200':
            self.logger.warning(f'[{self.__class__.__name__}]图片状态更新失败...')

        if len(page_dict_list) > 0:
            page_res = await self.client.upload_page(page_dict_list)
            if page_res['code'] == '200':
                self.logger.info(f'[{self.__class__.__name__}]页面上传成功,上传了{len(page_dict_list)}个页面...')
            else:
                msg = page_res['msg']
                self.logger.info(f'[{self.__class__.__name__}]页面上传失败,msg:{msg}...')

        if len(img_dict_list) > 0:
            img_res = await self.client.upload_img(img_dict_list)
            if img_res['code'] == '200':
                self.logger.info(f'[{self.__class__.__name__}]图片上传成功,上传了{len(img_dict_list)}张图片...')
            else:
                msg = img_res['msg']
                self.logger.info(f'[{self.__class__.__name__}]图片上传失败,msg:{msg}...')

        try:
            self.chrome.execute_script(self.delInterval_js)
        except Exception as e:
            self.logger.error(f'[{self.__class__.__name__}]浏览器中的定时器删除失败,msg:{e}...')


if __name__ == '__main__':
    baidu_spider = BaiduSpider('大象')
    baidu_spider.run_img_spider()
