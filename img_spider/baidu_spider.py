# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/27 11:52  
from selenium.webdriver.common.by import By
import time
from .base_spider import BaseSpider
import conf.model as model


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

        res = self.client.get_uncrawl_img_by_keyword(self.keyword)
        if res['code'] == '200':
            img_dict = res['data']
            if not img_dict:
                self.logger.warning(f'无满足条件的图片可供识图,爬取结束...')
                return
            img_url = img_dict['url']
        else:
            msg = res['msg']
            self.logger.error(f'爬取错误,msg:{msg}...')
            return

        self.chrome.get(self.API_URL)
        self.chrome.find_element(By.XPATH, self.CAMERA_XPATH).click()
        self.chrome.find_element(By.XPATH, self.INPUT_XPATH).send_keys(img_url)
        self.chrome.find_element(By.XPATH, self.BUTTON_XPATH).click()
        # 等待5秒用于加载
        time.sleep(5)

        # 启动页面下拉定时器
        self.chrome.execute_script(self.setInterval_js)

        upload_page_set = set()
        upload_img_set = set()
        while True:
            time.sleep(3)
            item_list = self.chrome.find_elements(By.XPATH, '//div[@class="general-imgcol"]/a')

            page_list = []
            img_list = []
            for item in item_list:
                page_url = item.get_attribute('href')  # 节点的属性值
                if page_url not in upload_page_set:
                    # 该页面需要再次去访问才能拿到原图的页面链接
                    page_obj = model.Page(keyword=self.keyword, url=page_url, source=self.SOURCE)
                    page_list.append(page_obj.to_dict())
                    upload_page_set.add(page_url)

                img = item.item.find_element(By.TAG_NAME, 'img')
                img_url = img.get_attribute('src')
                if img_url not in upload_img_set:
                    desc = img.get_attribute('title')
                    img_obj = model.Img(keyword=self.keyword, page_url=self.chrome.current_url, url=img_url,
                                        thumb_url=img_url, source=self.SOURCE, desc=desc)
                    img_list.append(img_obj.to_dict())
                    upload_img_set.add(img_url)

            if len(page_list) > 0:
                res_json = self.client.upload_page(page_list)
                msg = res_json['msg']
                if res_json['code'] == '200':
                    self.logger.info(f'[{self.__class__.__name__}]页面上传成功,上传了{len(page_list)}个页面...')
                else:
                    self.logger.info(f'[{self.__class__.__name__}]页面上传失败,msg:{msg}...')

            if len(img_list) > 0:
                res_json = self.client.upload_img(img_list)
                msg = res_json['msg']
                if res_json['code'] == '200':
                    self.logger.info(f'[{self.__class__.__name__}]图片上传成功,上传了{len(page_list)}张图片...')
                else:
                    self.logger.info(f'[{self.__class__.__name__}]图片上传失败,msg:{msg}...')

            # 结束抽取
            end = False
            if len(item_list) > self.MAX_PER_PAGE:
                end = True
            else:
                for _ in range(5):
                    time.sleep(1)
                    if len(item_list) != len(
                            set(self.chrome.find_elements(By.XPATH, '//div[@class="general-imgcol"]/a'))):
                        break
                else:
                    end = True

            if end:
                try:
                    self.chrome.execute_script(self.delInterval_js)
                except Exception as e:
                    self.logger.error(f'[{self.__class__.__name__}]浏览器中的定时器删除失败,msg:{e}...')
                self.logger.warning(f'[{self.__class__.__name__}]抽取结束,共抽取到{len(item_list)}个item...')
                break


if __name__ == '__main__':
    baidu_spider = BaiduSpider('大象')
    baidu_spider.get_img_link_by_img()
