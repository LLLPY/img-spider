# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 22:01
import asyncio
import random

import aiohttp
import requests
from lxml import etree
import re
import time
import conf.conf as conf
import model.models as model
from selenium.webdriver import Chrome
from typing import *


class BaseSpider:
    API = None
    HEADERS = conf.HEADERS
    SOURCE = None
    # 日志器
    logger = conf.img_spider_logger

    client = conf.img_client

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword
        self.chrome = Chrome(service=conf.CHROMEDRIVER_SERVICE, options=conf.chrome_options)
        self.chrome.set_page_load_timeout(5)

    # get请求
    @classmethod
    def get(cls, url: str):
        success = True
        try:
            res = requests.get(url, headers=cls.HEADERS, verify=False, timeout=(5, 10),
                               proxies={'http': None, 'https': None})
        except Exception as e:
            cls.logger.error(f'请求失败,失败原因:{e},url:{url}')
            res = None
            success = False
        return res, success

    @classmethod
    async def async_get(cls, url: str):
        try:
            timeout = aiohttp.ClientTimeout(total=10)  # 10秒过期
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=cls.HEADERS) as response:
                    text = await response.text(encoding='utf8')
                    return text, True
        except Exception as e:
            return e, False

    # 获取某个页面中上一页和下一页的链接
    @staticmethod
    def get_pre_and_next_links(host: str, html: str):
        res1 = re.findall(r'<a.*?href="(.*?)".*>.*?下一页.*?</a>', html)
        res2 = re.findall(r'<a.*?href="(.*?)".*>.*?page.*?</a>', html)
        res1.extend(res2)
        page_list = []
        for page in res1:
            if not page.startswith('http'):
                page = host + page.strip('/')
                page_list.append(page)
        return list(set(page_list))

    # 获取page和img
    @staticmethod
    def get_page_and_img_links(host: str, html: str):
        pattern = r'<a.*href="(.*?)".*<img.*src="(.*?)".*</a>'
        res = re.findall(pattern, html, re.IGNORECASE)
        for i in range(len(res)):
            page_img = res[i]
            page = str(page_img[0])
            img = str(page_img[1])
            if not page.startswith('http'):
                page = host + page.strip('/')
            if not img.startswith('http'):
                img = host + img.strip('/')
            res[i] = (page, img)
        return res

    # 抽取规则
    @classmethod
    def extract(cls, response):
        pass

    # 结束规则
    @classmethod
    def done(cls, data_list, per_page_count):
        # return True
        return len(data_list) == 0

    # 公共处理爬虫
    @classmethod
    async def common_spider(cls, keyword: str, page_num: int, per_page_count: int, API_url: str,
                            extract_func: Callable,
                            done_func: Callable) -> None:

        cls.logger.warning(f'{cls.__name__}已启动...')

        thumb_img_url_set = set()
        origin_img_url_set = set()
        page_url_set = set()

        start = time.time_ns()

        while True:

            # 统计每一轮的耗时
            tmp_start = time.time_ns()

            # 统计每一轮的数量
            tmp_thumb_img_url_set = set()
            tmp_origin_img_url_set = set()
            tmp_page_url_set = set()

            # 让出cpu，给其他协程提供抢占的机会
            await asyncio.sleep(0)

            api_url = API_url.format(keyword, page_num, per_page_count)
            api_obj = model.API(keyword=keyword, url=api_url, source=cls.SOURCE)

            # 1.请求接口获取图片和页面的地址
            html, success = await cls.async_get(api_url)
            if not success:
                api_obj.status = model.API.STATUS_ERROR
                api_obj.err_msg = html
                continue

            # 2.抽取img和page
            data_list = extract_func(html)

            # 3.检查该api的内容是否更新
            api_md5 = model.API.md5(html)
            api_obj.md5 = api_md5
            api_check_res = await cls.client.is_crawled_api(api_md5)

            if api_check_res['data']['crawled']:
                cls.logger.info('该api的内容已爬取...')
                # 如果是最后一页就退出
                if done_func(data_list, per_page_count):
                    break
                else:
                    continue

            # 4.统计
            img_dict_list = []
            page_dict_list = []

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
                img_obj = model.Img(keyword=keyword, url=origin_img_url, source=cls.SOURCE, thumb_url=thumb_img_url,
                                    page_url=page_url, desc=item['desc'], api=api_obj.uid)
                page_obj = model.Page(keyword=keyword, url=page_url, source=cls.SOURCE, api=api_obj.uid)
                img_dict_list.append(img_obj.to_dict())
                page_dict_list.append(page_obj.to_dict())

            # 5.上传页面到服务器
            api_res = await cls.client.upload_api(api_obj.to_dict())
            if api_res['code'] != '200':
                cls.logger.warning('api上传失败...')

            page_res = await cls.client.upload_page(page_dict_list)
            if page_res['code'] != '200':
                cls.logger.warning(f'页面上传失败...')
            else:
                cls.logger.info(f'页面上传成功,上传了{len(page_dict_list)}个页面...')

            img_res = await cls.client.upload_img(img_dict_list)
            if img_res['code'] != '200':
                cls.logger.warning(f'图片上传失败...')
            else:
                cls.logger.info(f'图片上传成功,上传了{len(page_dict_list)}个图片...')

            # 6.结束 最后一页
            if img_res['data']['done']:
                break

            tmp_end = time.time_ns()
            cls.logger.info(
                f'{cls.__name__}-api抓取,页码:{page_num},抓取了{len(tmp_origin_img_url_set)}个原始图片链接,{len(tmp_thumb_img_url_set)}个缩略图片链接,{len(tmp_page_url_set)}个页面链接,耗时:{(tmp_end - tmp_start) / 1000000000},api地址:{api_url}')

            page_num += len(data_list)  # 页数增加

        end = time.time_ns()
        cls.logger.warning(
            f'{cls.__name__}-api抓取结束,一共抓取了{len(origin_img_url_set)}原始图片链接,{len(thumb_img_url_set)}个缩略图片链接,{len(page_url_set)}个页面链接,耗时:{(end - start) / 1000000000}...')

    # 获取api上的页面和图片
    async def get_page_and_img_on_api(self):
        keyword = self.keyword
        page_num = 1
        per_page_count = 50
        API_url = self.API
        await self.common_spider(keyword, page_num, per_page_count, API_url, self.extract, self.done)

    # 获取页面上的page和img
    async def get_page_and_img_on_page(self):
        time.sleep(random.randint(5, 8))
        self.logger.warning(f'{self.__class__.__name__}开始抓取页面上的链接...')
        while True:

            page_res = await self.client.get_ready_page(keyword=self.keyword)
            if page_res['code'] != '200':
                continue

            page_obj = model.Page.to_obj(page_res['data'])

            try:
                page_url = page_obj.url
                self.chrome.get(page_url)
                time.sleep(3)
                page_obj.status = model.Page.STATUS_CRAWLED
                html = self.chrome.page_source
            except Exception as e:
                self.logger.warning(f'页面加载失败...msg:{e}')
                page_obj.status = model.Page.STATUS_ERROR
                page_obj.err_msg = str(e)
                html = '<a></a>'
            img_link_list = []
            page_link_list = []

            host = page_obj.url.replace('//', '*').split('/', 1)[0].replace('*', '//') + '/'
            # 上一页和下一页的链接
            # pre_next_links = self.get_pre_and_next_links(host, html)
            # page_link_list.extend(pre_next_links)
            img_list = etree.HTML(html).xpath('//body//img/@src')  # 可能是原图链接
            img_list = [host + img.strip('/') if not img.startswith('http') else img for img in img_list]

            img_link_list.extend(img_list)
            page_img_list = self.get_page_and_img_links(host, html)

            for page_img in page_img_list:
                page_link_list.append(page_img[0])
                img_link_list.append(page_img[1])

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

            # 上传服务器
            page_dict = page_obj.to_dict()
            page_res = await self.client.update_page(page_dict)

            if page_res['code'] != '200':
                self.logger.warning(f'page状态更新失败...,page:{page_obj.url}')

            res = await self.client.upload_page(page_dict_list)

            if res['code'] != '200':
                self.logger.warning(f'页面上传失败...')
            else:
                self.logger.info(f'页面上传成功,上传了{len(page_dict_list)}个page...')

            res = await self.client.upload_img(img_dict_list)

            if res['code'] != '200':
                self.logger.warning(f'图片上传失败...')
            else:
                self.logger.info(f'图片上传成功,上传了{len(img_dict_list)}个img...')

            self.logger.info(
                f'图片抽取成功,keyword:{self.keyword},抽取到了{len(img_link_list)}张图片链接,{len(page_link_list)}个页面链接...page:{page_obj.url}')

        # 结束
        # for _ in range(15):
        #     time.sleep(1)
        #     if not conf.page_queue.empty():
        #         break
        # else:
        #     self.logger.warning(f'{self.__class__.__name__}图片抽取结束...')
        #     break

    def __del__(self):
        try:
            self.chrome.close()
        except Exception as e:
            self.logger.error(f'浏览器窗口关闭失败...错误原因:{e}')

    @classmethod
    async def gather_task(cls, keyword: str) -> None:
        spider = cls(keyword)
        await asyncio.gather(
            spider.get_page_and_img_on_api(),
            spider.get_page_and_img_on_page(),
        )

    # 启动
    @classmethod
    def run(cls, keyword: str) -> None:
        asyncio.run(cls.gather_task(keyword))


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
