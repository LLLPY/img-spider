# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/7 22:01
import asyncio
import random
from urllib.parse import urlparse
import aiohttp
from lxml import etree
import re
import conf.conf as conf
import model.models as model
from selenium.webdriver import Chrome
from typing import *
import utils.utils as utils


class BaseSpider:
    API = None

    SOURCE = None

    HEADERS = conf.headers

    # 日志器
    logger = conf.img_spider_logger

    # 客户端
    client = conf.img_client

    per_page_count = 0

    # 初始化
    def __init__(self, keyword: str) -> None:
        self.logger.warning(f'[{self.__class__.__name__}]已启动...')
        self.keyword = keyword

    # 异步get
    @classmethod
    async def async_get(cls, url: str):
        try:
            timeout = aiohttp.ClientTimeout(total=10)  # 10秒过期
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=cls.HEADERS) as response:
                    text = await response.text(encoding='utf8')
                    return text, True
        except Exception as e:
            cls.logger.warning(e)
            return str(e), False

    @classmethod
    async def gather_task(cls, keyword: str) -> None:
        ...

    # 启动
    @classmethod
    def run(cls, keyword: str) -> None:
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(cls.gather_task(keyword),)
        asyncio.run(cls.gather_task(keyword))


class APISpider(BaseSpider):
    '''APISpider是爬取特定api上的图片和页面，往往只需要执行一次即可'''

    # 抽取规则
    @classmethod
    async def extract(cls, response) -> List[Dict]:
        ...

    # 结束规则
    @classmethod
    async def done(cls, data_list) -> bool:
        if not cls.per_page_count:
            cls.per_page_count = len(data_list)

        return len(data_list) == 0  # or len(data_list) < cls.per_page_count

    # 获取api上的页面和图片
    async def get_page_and_img_on_api(self, page_num: int, per_page_count: int) -> None:

        spider_name = self.__class__.__name__
        self.logger.warning(f'[{spider_name}]开始抓取api上的链接...')

        thumb_img_url_set = set()  # 缩略图
        origin_img_url_set = set()  # 原始图
        page_url_set = set()  # 页面

        while True:

            api_url = self.API.format(self.keyword, page_num, per_page_count)
            api_obj = model.API(keyword=self.keyword, url=api_url, source=self.SOURCE)
            # 1.请求接口获取图片和页面的地址
            html, success = await self.async_get(api_url)
            if not success:
                api_obj.status = model.API.STATUS_ERROR
                api_obj.err_msg = html
                self.client.upload_api(api_obj.to_dict())
                continue

            # 2.检查该api的内容是否更新 # TODO 周期性的去检查，不要每次都进行检查
            api_obj.md5 = model.API.md5(html)
            api_check_res = await self.client.is_crawled_api(api_obj.md5)
            if api_check_res.get('status'):
                self.logger.info(f'[{spider_name}]当前api的内容已爬取...api:{api_obj.url}')
                continue

            # 3.抽取img和page
            data_list = await self.extract(html)

            # 5.解析数据
            img_dict_list = []
            page_dict_list = []

            # 统计每一轮的数量
            tmp_thumb_img_url_set = set()
            tmp_origin_img_url_set = set()
            tmp_page_url_set = set()
            for item in data_list:
                origin_img_url = item['origin_img_url']  # 原图
                thumb_img_url = item['thumb_img_url']  # 缩略图
                page_url = item['page_url']  # 图片所在的页面

                origin_img_url_set.add(origin_img_url)
                thumb_img_url_set.add(thumb_img_url)
                page_url_set.add(page_url)

                tmp_origin_img_url_set.add(origin_img_url)
                tmp_thumb_img_url_set.add(thumb_img_url)
                tmp_page_url_set.add(page_url)

                if page_url:
                    page_obj = model.Page(keyword=self.keyword, url=page_url, source=self.SOURCE, api_url=api_obj.url)
                    page_dict_list.append(page_obj.to_dict())
                if origin_img_url:
                    img_obj = model.Img(keyword=self.keyword, url=origin_img_url, source=self.SOURCE,
                                        thumb_url=thumb_img_url, page_url=page_url, desc=item['desc'],
                                        api_url=api_obj.url)
                    img_dict_list.append(img_obj.to_dict())

            # 5.上传页面到服务器
            res = await self.client.upload_api(api_obj.to_dict())
            if res['code'] != '200':
                self.logger.warning('接口上传失败...')

            res = await self.client.upload_page(page_dict_list)
            if res['code'] != '200':
                self.logger.warning('页面上传失败...')

            res = await self.client.upload_img(img_dict_list)
            if res['code'] != '200':
                self.logger.warning('图片上传失败...')

            if not self.per_page_count:
                self.per_page_count = min(len(data_list), per_page_count)

            # 6.结束 最后一页
            if await self.done(data_list):  # TODO 如果连续3次获得内容一样，可以触发结束
                # if res['data']['done']:
                #     self.logger.info(f'该接口上的所有图片已被抓取，爬取结束...')
                # else:
                self.logger.info(f'爬取结束，最后一页的数量:{len(data_list)}，设置的每页数量:{self.per_page_count}')
                break

            self.logger.info(
                f'[{spider_name}]-api抓取,页码:{page_num},抓取了{len(tmp_origin_img_url_set)}个原始图片链接,{len(tmp_thumb_img_url_set)}个缩略图片链接,{len(tmp_page_url_set)}个页面链接,api地址:{api_url}')

            page_num += len(data_list)  # 页数增加

        self.logger.warning(
            f'[{spider_name}]-api抓取结束,一共抓取了{len(origin_img_url_set)}原始图片链接,{len(thumb_img_url_set)}个缩略图片链接,{len(page_url_set)}个页面链接...')

    @classmethod
    async def gather_task(cls, keyword: str) -> None:
        _spider = cls(keyword)
        await asyncio.gather(
            _spider.get_page_and_img_on_api(0, 100),  # 爬取页面上的页面和图片
        )


class PageSpider(BaseSpider):
    '''
    PageSpider用于爬取页面上的图片，需要用到chrome动态加载页面，
    相较于APISpider速度会慢很多，因此将其与APISpider分离
    '''
    chrome = None

    def refresh_chrome(self):
        if self.chrome:
            self.chrome.quit()
        self.chrome = Chrome(service=conf.CHROMEDRIVER_SERVICE, options=conf.chrome_options)
        self.chrome.set_page_load_timeout(5)

    # 初始化
    def __init__(self, keyword: str) -> None:
        super(PageSpider, self).__init__(keyword)
        self.refresh_chrome()

    # 获取某个页面中上一页和下一页的链接
    @staticmethod
    async def get_pre_and_next_links(host: str, html: str):
        res1 = re.findall(r'<a.*?href="(.*?)".*>.*?下一页.*?</a>', html)
        res2 = re.findall(r'<a.*?href="(.*?)".*>.*?page.*?</a>', html)
        res1.extend(res2)
        return list(set(res1))

    # 修正链接
    @classmethod
    def format_url(cls, url: str, host: str) -> str:
        url_obj = urlparse(url)

        if not url_obj.hostname:
            url = host + '/' + url_obj.path.strip('/')

        if not url_obj.scheme:
            url = 'http://' + url.strip('/')

        return url.strip('/')

    async def wait_until_complete(self, timeout=8, interval=0.5):
        '''
        等待页面内容加载完毕
        timeout:超时时间
        interval:每一轮的时间间隔
        '''
        pre_html = self.chrome
        while True:
            if utils.md5(pre_html) == utils.md5(self.chrome.page_source):
                self.logger.info('页面加载完成...')
                break
            await asyncio.sleep(interval)

            timeout -= interval
            if timeout <= 0:
                self.logger.warning('页面加载超时...')
                break

            # 更新内容
            pre_html = self.chrome.page_source

    # 获取页面上的page和img
    async def get_page_and_img_on_page(self) -> None:

        spider_name = self.__class__.__name__

        self.logger.warning(f'[{spider_name}]开始抓取页面上的链接...')
        while True:

            page_res = await self.client.get_ready_page(keyword=self.keyword)

            page_dict = page_res.get('data')
            if not page_dict:
                self.logger.info(f'无页面可进行爬取，爬取结束...')
                break

            page_obj = model.Page.to_obj(page_dict)

            try:
                self.chrome.get(page_obj.url)
                await asyncio.sleep(random.randint(2, 4))
                page_obj.status = model.Page.STATUS_CRAWLED
                await self.wait_until_complete()
                html = self.chrome.page_source
            except Exception as e:
                self.logger.warning(f'[{spider_name}]页面加载失败...msg:{e}')
                page_obj.status = model.Page.STATUS_ERROR
                page_obj.err_msg = str(e)
                html = '<p></p>'
                self.refresh_chrome()

            host = urlparse(page_obj.url).hostname
            e = etree.HTML(html)

            # 上一页和下一页的链接
            # pre_next_links = self.get_pre_and_next_links(host, html)
            # page_link_list.extend(pre_next_links)

            # 图片链接
            img_link_list = e.xpath('//body//img/@src')
            img_link_list = [self.format_url(img, host) for img in img_link_list]

            # 页面链接
            page_link_list = e.xpath('//a//img/../@href')
            page_link_list = [self.format_url(page, host)
                              for page in page_link_list]

            img_dict_list = []
            page_dict_list = []
            img_link_list = list(set(img_link_list))
            page_link_list = list(set(page_link_list))

            for img in img_link_list:
                new_img_obj = model.Img(keyword=page_obj.keyword, url=img, source=self.SOURCE, thumb_url=img,
                                        page_url=page_obj.url)
                img_dict_list.append(new_img_obj.to_dict())

            for page in page_link_list:
                new_page_obj = model.Page(keyword=page_obj.keyword, url=page, source=self.SOURCE,
                                          deep=page_obj.deep + 1)
                page_dict_list.append(new_page_obj.to_dict())

            # 更新当前page的状态
            page_res = await self.client.update_page(page_obj.to_dict())

            if page_res['code'] != '200':
                self.logger.warning(f'page状态更新失败...,page:{page_obj.url}')

            # 上传page
            if len(page_dict_list) > 0:
                res = await self.client.upload_page(page_dict_list)

                if res['code'] != '200':
                    self.logger.warning(f'页面上传失败...')
                else:
                    self.logger.info(
                        f'页面上传成功,上传了{len(page_dict_list)}个page...')

            # 上传img
            if len(img_dict_list) > 0:
                res = await self.client.upload_img(img_dict_list)

                if res['code'] != '200':
                    self.logger.warning(f'图片上传失败...')
                else:
                    self.logger.info(f'图片上传成功,上传了{len(img_dict_list)}个img...')

            self.logger.info(
                f'图片抽取成功,keyword:{self.keyword},抽取到了{len(img_link_list)}张图片链接,{len(page_link_list)}个页面链接...page:{page_obj.url}')

    def __del__(self) -> None:
        try:
            self.chrome.quit()
        except Exception as e:
            self.logger.error(f'浏览器窗口关闭失败...错误原因:{e}')

    @classmethod
    async def gather_task(cls, keyword: str) -> None:
        _spider = cls(keyword)
        await asyncio.gather(
            _spider.get_page_and_img_on_page(),  # 爬取页面上的页面和图片
        )


if __name__ == '__main__':
    # keyword_spider要实现的功能:
    # 1.请求各个搜索引擎的api，获取keyword对应的img和page(输入)
    # 2.请求page，抽取上面的img和page(输入)
    # 功能1和功能2并发执行
    # img_spider要实现的功能:
    # 1.以图搜图，获取img的相似图片以及图片所在的page(输入)
    # 2.下载img(输出)
    # 功能1和功能2同步执行，功能1执行完成后再执行功能2(主要是为了防止爬取频率过高)

    spider = BaseSpider('大海')
