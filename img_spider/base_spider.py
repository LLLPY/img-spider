# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/27 11:38

import conf.conf as conf
from selenium.webdriver import Chrome
import model.models as model
import asyncio
from selenium.webdriver.common.by import By


# 以图搜图
class BaseSpider:
    HEADERS = conf.headers

    # js注入
    # 间隔一定时间将页面下拉,用于加载更多的图片
    setInterval_js = 'scroll_page=setInterval(function(){document.documentElement.scrollTop=10000000000000000},2000)'
    # 删除页面下拉的定时器
    delInterval_js = 'clearInterval(scroll_page)'

    # 每页图片抽取的最大值
    MAX_PER_PAGE = 400

    # 日志器
    logger = conf.img_spider_logger

    # 客户端
    client = conf.img_client

    # chrome池,通过chrome请求网页
    # chrome_pool = ChromeWorkerManager(5)

    API_URL = ''
    CAMERA_XPATH = ''
    INPUT_XPATH = ''
    BUTTON_XPATH = ''
    SOURCE = ''
    # 页面上page的链接
    link_xpath = ''

    # 初始化时只需要知道keyword即可

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword
        self.chrome = Chrome(
            service=conf.CHROMEDRIVER_SERVICE, options=conf.chrome_options)
        self.chrome.maximize_window()
        self.logger.warning(f'[{self.__class__.__name__}]已启动...')

    def __del__(self) -> None:
        try:
            self.chrome.close()
        except Exception as e:
            conf.img_spider_logger.error(
                f'[{self.__class__.__name__}]浏览器窗口关闭失败...错误原因:{e}')

    async def get_page(self, img_obj: model.Img) -> None:
        self.chrome.get(self.API_URL)
        self.chrome.find_element(By.XPATH, self.CAMERA_XPATH).click()
        self.chrome.find_element(
            By.XPATH, self.INPUT_XPATH).send_keys(img_obj.url)
        self.chrome.find_element(By.XPATH, self.BUTTON_XPATH).click()

        # 等待5秒用于加载
        await asyncio.sleep(5)

        # 启动页面下拉定时器
        self.chrome.execute_script(self.setInterval_js)

    # 通过图片搜索，获取相似图片的页面，提取页面中相似图片所在的页面链接
    async def get_img_and_page_by_img(self, img_obj: model.Img) -> None:

        await self.get_page(img_obj)
        page_url_set = set()
        img_url_set = set()
        while True:

            await asyncio.sleep(3)

            item_list = self.chrome.find_elements(By.XPATH, self.link_xpath)
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
                            set(self.chrome.find_elements(By.XPATH, self.link_xpath))):
                        break
                else:
                    end = True

            if end:
                self.logger.warning(
                    f'[{self.__class__.__name__}]抽取结束,共抽取到{len(item_list)}个item...')
                break

        page_dict_list = []
        img_dict_list = []

        for page_url in page_url_set:
            page_obj = model.Page(keyword=self.keyword,
                                  url=page_url, source=self.SOURCE)
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
                self.logger.info(
                    f'[{self.__class__.__name__}]页面上传成功,上传了{len(page_dict_list)}个页面...')
            else:
                msg = page_res['msg']
                self.logger.info(
                    f'[{self.__class__.__name__}]页面上传失败,msg:{msg}...')

        if len(img_dict_list) > 0:
            img_res = await self.client.upload_img(img_dict_list)
            if img_res['code'] == '200':
                self.logger.info(
                    f'[{self.__class__.__name__}]图片上传成功,上传了{len(img_dict_list)}张图片...')
            else:
                msg = img_res['msg']
                self.logger.info(
                    f'[{self.__class__.__name__}]图片上传失败,msg:{msg}...')

        try:
            self.chrome.execute_script(self.delInterval_js)
        except Exception as e:
            self.logger.error(
                f'[{self.__class__.__name__}]浏览器中的定时器删除失败,msg:{e}...')

    # 执行img_spider
    async def run_img_spider(self) -> None:

        while True:
            img_res = await self.client.get_uncrawl_img_by_keyword(self.keyword)
            if img_res['code'] != '200':
                msg = img_res['msg']
                self.logger.error(
                    f'[{self.__class__.__name__}]获取img失败,msg:{msg}...')
                return

            img_dict = img_res['data']
            if not img_dict:
                self.logger.warning(
                    f'[{self.__class__.__name__}]无可供识图的img,爬取结束...')
                return

            img_obj = model.Img.to_obj(img_dict)
            await self.get_img_and_page_by_img(img_obj)

    @classmethod
    async def gather_task(cls, keyword: str) -> None:
        spider = cls(keyword)
        await asyncio.gather(
            spider.run_img_spider(),
        )

    # 启动
    @classmethod
    def run(cls, keyword: str) -> None:
        asyncio.run(cls.gather_task(keyword))
