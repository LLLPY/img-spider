# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 22:01  
import asyncio
import requests
import os
import sys
from urllib.request import urlretrieve
from lxml import etree
import re
import time
from selenium import webdriver
import conf.conf as conf
import conf.model as model

# 关闭警告
requests.packages.urllib3.disable_warnings()


class BaseSpider:
    API = None
    HEADERS = conf.HEADERS
    SOURCE = None
    # 日志器
    logger = conf.img_spider_logger

    client = conf.img_client

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword

    # get请求
    @classmethod
    def get(cls, url, headers=conf.HEADERS):
        success = True
        try:
            res = requests.get(url, headers=headers, verify=False, timeout=(5, 10),
                               proxies={'http': None, 'https': None})
        except Exception as e:
            cls.logger.error(f'请求失败,失败原因:{e},url:{url}')
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
        # chrome_options.add_argument('--headless') #无头浏览器
        chrome_driver = webdriver.Chrome(chrome_options=chrome_options, service=conf.CHROMEDRIVER_SERVICE)
        chrome_driver.get(url)
        time.sleep(1)
        page = chrome_driver.page_source
        chrome_driver.close()
        return page

    # 根据获取一个page上的img链接
    async def get_img_url_on_page(self):

        self.logger.warning(f'{self.__class__.__name__}开始抓取页面上的链接...')
        while True:

            # 让出cpu
            await asyncio.sleep(0)
            if not conf.page_ready_to_crawl_queue.empty():
                self.logger.info(f'qsize:{conf.page_ready_to_crawl_queue.qsize()}')
                page_obj = conf.page_ready_to_crawl_queue.get()
                res, success = self.get(page_obj.url)
                if not success:
                    conf.page_crawled_set.add(page_obj.url)
                    self.logger.warning(f'页面请求失败:{page_obj.url}')
                else:
                    html = res.text
                    # 上一页和下一页的链接
                    host = page_obj.url.split('/', 1)[0]
                    relate_links = self.get_pre_and_next_links(html)
                    if relate_links:
                        for sub_url in relate_links:
                            print(f'{host}/{sub_url}')
                    self.logger.info(f'page:{page_obj.url}\n,relate_links:{relate_links}')
                    e = etree.HTML(html)
                    img_list = e.xpath('//body//img/@src')

                    for img in img_list:
                        img_obj = model.Img(self.keyword, page_obj.url, img)
                        if img_obj not in conf.img_ready_set and img_obj not in conf.img_crawled_set:
                            conf.img_ready_to_crawl_queue.put(img_obj)
                    self.logger.info(
                        f'图片抽取成功,keyword:{self.keyword},抽取到了{len(img_list)}张图片链接,页面地址:{page_obj.url}')
                    conf.page_crawled_set.add(page_obj.url)  # 不管数据有没有抽取成功，都添加到已爬取的集合中
            else:
                # 结束
                for _ in range(15):
                    await asyncio.sleep(1)
                    if not conf.page_ready_to_crawl_queue.empty():
                        break
                else:
                    self.logger.warning(f'{self.__class__.__name__}图片抽取结束...')
                    break

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
        conf.img_ready_set.discard(img_obj)
        conf.img_crawled_set.add(img_obj)
        BaseSpider.logger.info(
            f'下载{success},msg:{msg},剩余{conf.img_ready_to_crawl_queue.qsize()}待爬取...img_url:{img_obj.url}')

    # 下载图片
    async def download_imgs(self):
        self.logger.warning(f'{self.__class__.__name__}开始下载图片...')
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
                # 如果连续15秒内队列中都没有新的数据，就结束爬取
                for _ in range(15):
                    await asyncio.sleep(1)
                    if not conf.img_ready_to_crawl_queue.empty():
                        break
                else:
                    self.logger.warning(f'{self.__class__.__name__}图片下载结束...')
                    break
                # await asyncio.sleep(15)
                # if conf.img_ready_to_crawl_queue.empty():
                # self.logger.info('图片下载结束...')
                # break

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

    def get_page_links(html):
        pattern = r'<a.*href="(.*?)".*<img.*</a>'
        re.findall(pattern, html, re.IGNORECASE)

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
    async def common_spider(cls, spider_name, keyword, page_num, per_page_count, API_url, extract_func, done_func):
        cls.logger.warning(f'爬虫{spider_name}已启动...')

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

            # 1.判断该接口是否已经爬取过，如果是已经爬取的url，就不用再爬取了
            if api_url in conf.api_crawled_set:
                continue

            # 2.请求该接口获取图片和页面的地址
            res, success = cls.get(api_url, cls.HEADERS)
            if not success:
                conf.api_crawled_set.add(api_url)  # 将失败的url添加到api_crawled_set集合中
                continue

            # 3.数据抽取，从接口响应的数据中抽取出图片和页面的地址，不同的借口对应不同的抽取规则
            data_list = extract_func(res)

            cls.logger.info(f'抓取了{len(data_list)}个items从{spider_name}-api:{api_url}')

            img_dict_list = []
            page_dict_list = []
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

                img_obj = model.Img(keyword=keyword, page_url=page_url, url=origin_img_url, thumb_url=thumb_img_url,
                                    desc=item['desc'], source=cls.SOURCE)
                page_obj = model.Page(keyword=keyword, url=page_url, source=cls.SOURCE)
                img_dict_list.append(img_obj.to_dict())
                page_dict_list.append(page_obj.to_dict())

            # 上传页面到服务器
            res = cls.client.upload_page(page_dict_list)
            if res['status'] != 'success':
                cls.logger.warning(f'页面上传失败...')
            else:
                cls.logger.info(f'页面上传成功,上传了{len(page_dict_list)}个页面...')
            res = cls.client.upload_img(img_dict_list)
            if res['status'] != 'success':
                cls.logger.warning(f'图片上传失败...')
            else:
                cls.logger.info(f'图片上传成功,上传了{len(page_dict_list)}个图片...')

            # 6.结束 最后一页
            if done_func(data_list, per_page_count):
                end = time.time_ns()
                cls.logger.warning(
                    f'{spider_name}-api抓取结束,一共抓取了{len(origin_img_url_set)}原始图片链接,{len(thumb_img_url_set)}个缩略图片链接,{len(page_url_set)}个页面链接,耗时:{(end - start) / 1000000000}...')
                break

            tmp_end = time.time_ns()
            cls.logger.info(
                f'{spider_name}-api抓取,页码:{page_num},抓取了{len(tmp_origin_img_url_set)}个原始图片链接,{len(tmp_thumb_img_url_set)}个缩略图片链接,{len(tmp_page_url_set)}个页面链接,耗时:{(tmp_end - tmp_start) / 1000000000},api地址:{api_url}')

            page_num += len(data_list)  # 页数增加

            conf.api_crawled_set.add(api_url)  # 将此api添加到已爬取的集合中

    # 根据关键字获取图片所在页面的地址
    async def get_page_and_img_by_keyword(self):
        spider_name = self.__class__.__name__
        keyword = self.keyword
        page_num = 1
        per_page_count = 50
        API_url = self.API
        await self.common_spider(spider_name, keyword, page_num, per_page_count, API_url, self.extract, self.done)

    @classmethod
    async def do_upload_img(cls):
        cls.logger.warning(f'图片上传服务已启动...')
        now = time.time()
        while True:
            await asyncio.sleep(1)
            end = time.time()
            # 每10秒或者已爬取的图片集合数量大于50
            if (end - now) > 10 or len(conf.img_crawled_set) > 50:
                if len(conf.img_crawled_set) > 0:
                    img_dict_list = []
                    img_list = []
                    for img_obj in conf.img_crawled_set:
                        img_list.append(img_obj)
                        img_dict_list.append(img_obj.to_dict())
                    try:
                        res = conf.img_client.upload_img(img_dict_list)
                        if res.json()['status'] == 'success':
                            # 抛弃已经上传的
                            for img in img_list:
                                conf.img_crawled_set.discard(img)
                            cls.logger.info(
                                f'图片上传成功,上传了{len(img_dict_list)}张图片,len(img_crawled_set)={len(conf.img_crawled_set)}...')
                        else:
                            cls.logger.info(f'图片上传失败...')
                    except Exception as e:
                        cls.logger.info(f'图片上传失败...msg:{e}')

                    # 重置时间
                    now = time.time()

            # 结束
            for _ in range(20):
                await asyncio.sleep(1)
                if len(conf.img_crawled_set) > 0:
                    break
            else:
                cls.logger.warning('图片上传服务已退出...')
                break


# 定时工作
async def timed_task():
    await asyncio.gather(
        BaseSpider.do_upload_img()  # 定时上传图片
    )


# 启动定时任务
def run_timed_task():
    asyncio.run(timed_task())


if __name__ == '__main__':
    spider = BaseSpider('大海')
