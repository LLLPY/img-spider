# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/27 11:52  
from selenium.webdriver.common.by import By
import time
from .base_spider import BaseSpider
import conf.model as model


# from img_spider.base_spider import BaseSpider


class BaiduSpider(BaseSpider):
    API_URL = 'https://graph.baidu.com/s?sign=1226967dba6bed09cebca01645431413&f=all&tn=pc&tn=pc&idctag=nj&idctag=nj&logid=2944232641&pageFrom=graph_upload_bdbox&pageFrom=graph_upload_pcshitu&srcp=&gsid=&extUiData%5BisLogoShow%5D=1&tpl_from=pc&entrance=general'
    CAMERA_XPATH = '//div/span/input'
    INPUT_XPATH = '//div/span/input'
    BUTTON_XPATH = '//div[@class="graph-container"]/div/span[@class="graph-d20-search-btn graph-d20-search-btn-result"]'
    SOURCE = '百度'  # 来源

    def __init__(self, keyword):
        super().__init__(keyword)

    # 通过图片搜索，获取相似图片的页面，提取页面中相似图片所在的页面链接
    def get_img_link_by_img(self):
        img_url = 'https://img2.baidu.com/it/u=2898829455,2734408317&fm=253&fmt=auto&app=120&f=JPEG?w=1280&h=800'
        self.chrome.get(self.API_URL)
        self.chrome.find_element(By.XPATH, self.CAMERA_XPATH).click()
        self.chrome.find_element(By.XPATH, self.INPUT_XPATH).send_keys(img_url)
        self.chrome.find_element(By.XPATH, self.BUTTON_XPATH).click()
        # 等待3秒用于加载
        time.sleep(3)

        # 启动页面下拉定时器
        self.chrome.execute_script(self.setInterval_js)

        upload_page_set = set()
        while True:
            time.sleep(3)
            item_set = set(self.chrome.find_elements(By.XPATH, '//div[@class="general-imgcol"]/a'))

            page_list = []
            for item in item_set:
                page_url = item.get_attribute('href')  # 节点的属性值
                if page_url not in upload_page_set:
                    page_obj = model.Page(self.keyword, page_url, source=self.SOURCE)
                    page_list.append(page_obj.to_dict())
                    upload_page_set.add(page_url)

            if len(page_list) > 0:

                res = self.client.upload_page(page_list)
                res_json = res.json()
                status = res_json['status']
                msg = res_json['msg']
                if status == 'success':
                    self.logger.info(f'[{self.__class__.__name__}]页面上传成功,上传了{len(page_list)}个页面...')
                else:
                    self.logger.info(f'[{self.__class__.__name__}]页面上传失败,msg:{msg}上传了{len(page_list)}个页面...')

            # 结束抽取
            end = False
            if len(item_set) > self.MAX_PER_PAGE:
                end = True
            else:
                time.sleep(4)
                if len(item_set) == len(set(self.chrome.find_elements(By.XPATH, '//div[@class="general-imgcol"]/a'))):
                    end = True

            if end:
                try:
                    self.chrome.execute_script(self.delInterval_js)
                except Exception as e:
                    self.logger.error(f'[{self.__class__.__name__}]浏览器中的定时器删除失败,msg:{e}...')
                self.logger.warning(f'[{self.__class__.__name__}]抽取结束,共抽取到{len(item_set)}个item...')
                break


if __name__ == '__main__':
    baidu_spider = BaiduSpider('大象')
    baidu_spider.get_img_link_by_img()
