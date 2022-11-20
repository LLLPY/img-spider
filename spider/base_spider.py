# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 22:01  
import asyncio
import hashlib
import aiohttp
import aiofiles
import requests
import os
import sys
from urllib.request import urlretrieve
from lxml import etree
import selenium
import re
import time
from selenium import webdriver

sys.path.append(f'..{os.sep}')

import conf.conf as conf
import conf.model as model

requests.packages.urllib3.disable_warnings()  # 关闭警告


class BaseSpider:
    API = None
    HEADERS = conf.HEADERS

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword

    # get请求
    @classmethod
    def get(cls, url, headers=conf.HEADERS):
        success = True
        try:
            res = requests.get(url, headers=headers, verify=False, timeout=5)
        except Exception as e:
            conf.img_spider_logger.error(f'请求失败,失败原因:{e},url:{url}')
            res = None
            success = False
        return res, success

    # urlretrieve
    @staticmethod
    def urlretrieve_get(url, save_path, is_delete=False):

        urlretrieve(url, save_path)
        # 如果仅仅是临时文件，就将其删除

        with open(save_path, 'r', encoding='utf8') as f:
            content = f.read()

        if is_delete:
            os.remove(save_path)
        return save_path, content

    # chrome get
    @staticmethod
    def chrome_get(url):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_driver = webdriver.Chrome(chrome_options=chrome_options, service=conf.CHROMEDRIVER_SERVICE)
        chrome_driver.get(url)
        time.sleep(1)
        page = chrome_driver.page_source
        chrome_driver.close()
        return page

    # 根据获取一个page上的img链接
    async def get_img_url_on_page(self):
        while True:
            await asyncio.sleep(0)  # 让出cpu

            page_obj = conf.page_ready_to_crawl_queue.get()
            success, res = self.get(page_obj.url)
            # if not success:
            #     conf.page_crawled_set.add(page_obj.url)  # 不成功就添加到已爬取的集合中
            #     conf.img_spider_logger.warning(f'get img url failed from page:{page_obj.url}')
            #     continue
            # html = res.text
            # html=self.chrome_get(page_obj.url)
            _, html = self.urlretrieve_get(page_obj.url,
                                           hashlib.sha1(str(page_obj.url).encode('utf8')).hexdigest() + '.html')
            relate_links = self.get_pre_and_next_links(html)
            conf.img_spider_logger.info(f'page:{page_obj.url}\n,relate_links:{relate_links}')

            try:
                e = etree.HTML(html)
                img_list = e.xpath('//body//img/@src')
                crawled_n = 0
                for img in img_list:
                    img_obj = model.Img(self.keyword, page_obj.url, img)
                    if img not in conf.img_crawled_set:
                        conf.img_ready_to_crawl_queue.put(img_obj)
                    else:
                        crawled_n += 1
                conf.img_spider_logger.info(
                    f'keyword:{self.keyword},extract done，get {len(img_list)} img(s), {crawled_n} have been crawled.page url:{page_obj.url}')
            except Exception as e:
                conf.img_spider_logger.warning(
                    f'keyword:{self.keyword},page url:{page_obj.url},extract failed,error info:{e}')
            conf.page_crawled_set.add(page_obj.url)  # 不管数据有没有抽取成功，都添加到已爬取的集合中

    # 下载图片
    @classmethod
    async def download_img(cls, img_obj: model.Img):
        # 创建下载目录
        dirs = img_obj.save_path.rsplit(os.sep, 1)[0]
        if not os.path.isdir(dirs):
            os.makedirs(dirs)
        success = True
        msg = ''
        try:
            urlretrieve(img_obj.url, img_obj.save_path)
        except Exception as e:
            msg = e
            success = False
        ###############################################################################################################

        # try:
        #     async with aiohttp.ClientSession() as session:
        #         aiohttp.ClientTimeout(5)  # 最大等待时间为5秒
        #         async with session.get(img_obj.url, headers=conf.HEADERS) as res:
        #             dirs = img_obj.save_path.rsplit(os.sep, 1)[0]
        #             if not os.path.isdir(dirs):
        #                 os.makedirs(dirs)
        #             async with aiofiles.open(img_obj.save_path, 'wb') as f:
        #                 content = await res.content.read()
        #                 await f.write(content)
        # except Exception as e:
        # msg=e

        return {'status': success, 'msg': msg, 'img_obj': img_obj}

    @staticmethod
    def download_img_callback(msg):
        result = msg.result()
        status = result['status']
        success = ['失败', '成功'][status]
        msg = result['msg']
        img_obj = result['img_obj']
        conf.img_crawled_set.add(img_obj.url)
        conf.img_spider_logger.info(
            f'下载{success},msg:{msg},剩余{conf.img_ready_to_crawl_queue.qsize()}待爬取...img_url:{img_obj.url}')

    # 下载图片
    async def download_imgs(self):
        while True:
            await asyncio.sleep(0)  # 让出cpu
            task_list = []
            for _ in range(5):  # 每次启动5个任务去下载图片
                if not conf.img_ready_to_crawl_queue.empty():
                    img_obj = conf.img_ready_to_crawl_queue.get()
                    task = asyncio.create_task(self.download_img(img_obj))
                    task_list.append(task)

            # 等待当前批次的下载任务完成之后再进行下一批次的任务进行
            for task in task_list:
                task.add_done_callback(self.download_img_callback)
                await task

            # 结束下载
            if conf.img_ready_to_crawl_queue.empty():
                await asyncio.sleep(10)
                if conf.img_ready_to_crawl_queue.empty():
                    conf.img_spider_logger.info('图片下载结束...')
                    break

    # 获取某个页面中上一页和下一页的链接
    @staticmethod
    def get_pre_and_next_links(html):
        pattern = r'<a.*href="(.*?)".*>.*{}.*</a>'
        tag_list = ['上一页', 'pre', '下一页', 'next', 'page']
        res = []
        for tag in tag_list:
            tmp_res = re.findall(pattern.format(tag), html, re.IGNORECASE)
            res.extend(tmp_res)
        return list(set(res))

    # 抽取规则
    @classmethod
    def extract(cls, response):
        pass

    # 结束规则
    @classmethod
    def done(cls, data_list, per_page_count):
        return len(data_list) == 0

    # 公共处理爬虫
    @classmethod
    async def common_spider(cls, spider_name, keyword, page_num, per_page_count, API_url, extract_func, done_func):
        conf.img_spider_logger.info(f'爬虫{spider_name}已启动...')

        thumb_img_url_set = set()
        origin_img_url_set = set()
        page_url_set = set()
        while True:
            # 统计每一轮的数量
            tmp_thumb_img_url_set = set()
            tmp_origin_img_url_set = set()
            tmp_page_url_set = set()
            await asyncio.sleep(0)
            api_url = API_url.format(keyword, page_num, per_page_count)  # 判断该url是否已爬取
            # 1.判断该接口是否已经爬取过，如果是已经爬取的url，就不用再爬取了
            if api_url in conf.api_crawled_set:
                continue
            # 2.请求该接口获取图片和页面的地址
            res, success = BaseSpider.get(api_url, cls.HEADERS)
            if not success:
                conf.api_crawled_set.add(api_url)  # 将失败的url添加到api_crawled_set集合中
                continue
            # 3.数据抽取，从接口响应的数据中抽取出图片和页面的地址
            data_list = extract_func(res)
            conf.img_spider_logger.info(f'抓取了{len(data_list)}个items从{spider_name}-api:{api_url}')

            for item in data_list:
                origin_img_url = item['origin_img_url']  # 原图
                thumb_img_url = item['thumb_img_url']  # 缩略图
                page_url = item['page_url']  # 图片所在的页面

                # 统计
                origin_img_url_set.add(origin_img_url)
                thumb_img_url_set.add(thumb_img_url)
                page_url_set.add(page_url)

                tmp_origin_img_url_set.add(origin_img_url)
                tmp_thumb_img_url_set.add(thumb_img_url)
                tmp_page_url_set.add(page_url)

                # 4. 将page添加到消费队列
                if page_url not in conf.page_crawled_set:
                    page_obj = model.Page(keyword, page_url)
                    conf.page_ready_to_crawl_queue.put(page_obj)

                # 5.将img添加到消费队列
                if origin_img_url not in conf.img_crawled_set:
                    img_obj = model.Img(keyword, page_url, origin_img_url)
                    conf.img_ready_to_crawl_queue.put(img_obj)  # 添加到消费队列

            # 该url已爬取
            conf.api_crawled_set.add(api_url)

            # 6.结束
            if done_func(data_list, per_page_count):  # 最后一页
                # conf.my_api_pickle.dump(conf.api_crawled_set)  # 写入文件
                conf.img_spider_logger.info(
                    f'{spider_name}api抓取结束,一共抓取了{len(origin_img_url_set)}原始图片链接,{len(thumb_img_url_set)}个缩略图片链接,{len(page_url_set)}个页面链接...')
                break
            conf.img_spider_logger.info(
                f'{spider_name}-api抓取,页码:{page_num},抓取了{len(tmp_origin_img_url_set)}个原始图片链接,{len(tmp_thumb_img_url_set)}个缩略图片链接,{len(tmp_page_url_set)}个页面链接,apid地址:{api_url}')

            page_num += per_page_count  # 页数增加

    # 根据关键字获取图片所在页面的地址
    async def get_page_and_img_by_keyword(self):
        spider_name = self.__class__.__name__
        keyword = self.keyword
        page_num = 1
        per_page_count = 50
        API_url = self.API
        await self.common_spider(spider_name, keyword, page_num, per_page_count, API_url, self.extract, self.done)


if __name__ == '__main__':
    spider = BaseSpider('大海')
    img_obj = model.Img(spider.keyword, '', 'http://edu.chachaba.com/Uploads/2020-03-20/5e74678a17ab4.jpg')
    asyncio.run(spider.download_img(img_obj))
