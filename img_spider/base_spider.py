# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/27 11:38
import time

import conf.conf as conf
import os
from queue import Queue
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
import re
import conf.model as model
from urllib.request import urlretrieve


# 工人
class ChromeWorker:
    STATUS_READY = 0
    STATUS_RUNNING = 1
    STATUS_DONE = 2

    def __init__(self):
        self.status = self.STATUS_READY  # 0:待启动 1:运行中 2:运行结束
        self.chrome = Chrome(service=conf.CHROMEDRIVER_SERVICE, options=conf.chrome_options)

    # 启动
    def start(self, img_obj):
        self.status = self.STATUS_RUNNING
        res = self.chrome.get(img_obj.url)
        time.sleep(1)
        self.status = self.STATUS_DONE
        return res, img_obj

    def is_ready(self):
        return self.status == self.STATUS_READY

    # callback
    def done(self, msg):
        res = msg.result()
        self.status = self.STATUS_READY

    def close(self):
        self.chrome.close()


# 监工
class ChromeWorkerManager:
    instance = None

    def __init__(self, workrom_size=5):
        self.workroom = [ChromeWorker() for _ in range(workrom_size)]

    # 分配任务
    def dispatch(self, url_list):
        th_pool = ThreadPoolExecutor(len(self.workroom))
        for i in range(len(self.workroom)):
            if self.workroom[i].is_ready() and url_list:
                future = th_pool.submit(self.workroom[i].start, url_list.pop())
                future.add_done_callback(self.workroom[i].done)
        th_pool.shutdown()

    # 关闭所有任务
    def done(self):
        for i in range(len(self.workroom)):
            self.workroom[i].close()


# 以图搜图
class BaseSpider:
    HEADERS = conf.HEADERS

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

    # 初始化时只需要知道keyword即可
    def __init__(self, keyword):
        self.keyword = keyword
        self.chrome = Chrome(service=conf.CHROMEDRIVER_SERVICE, options=conf.chrome_options)

    def __del__(self):
        try:
            self.chrome.close()
        except Exception as e:
            conf.img_spider_logger.error(f'浏览器窗口关闭失败...错误原因:{e}')

    # 抽取页面内容
    def extract_page(self, page_obj, page_html):
        pattern = r'<a.*href="(.*?)".*<img.*src="(.*?)".*</a>'
        host = page_obj.url.split('/', 1)[0]
        thumb_url_set = set()
        # 匹配缩略图和页面链接
        page_thumb_list = re.findall(pattern, page_html)
        for page_thumb in page_thumb_list:
            page_url = page_thumb[0].strip('/')
            page_url = f'{host}/{page_url}'
            page = model.Page(page_obj.keyword,page_url)
            thumb_url = page_thumb[1]
            thumb_url_set.add(thumb_url)
            img = model.Img(page_obj.keyword,page_url, thumb_url, thumb_url)

        # 匹配原图
        img_list = re.findall(r'<img.*src="(.*?)".*>', page_html)
        for img in img_list:
            if img not in thumb_url_set:
                img_obj = model.Img(page_obj.url, img, img)
    
    @staticmethod
    def download_img_callback(msg):
        result = msg.result()
        status = result['status']
        success = ['失败', '成功'][status]
        msg = result['msg']
        img_obj = result['img_obj'] #TODO
        BaseSpider.logger.info(
            f'下载{success},msg:{msg},剩余{conf.img_queue.qsize()}待爬取...img_url:{img_obj.url}')

     # 下载图片
    @classmethod
    def download_img(cls, img_obj: model.Img):
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


      # 下载图片
    def download_imgs(self):
        self.logger.warning(f'{self.__class__.__name__}开始下载图片...')
        th_pool=ThreadPoolExecutor(5)
        while True:
            for _ in range(5):  # 每次启动5个任务去下载图片
                if not conf.img_queue.empty():
                    img_obj = conf.img_queue.get()
                    th_pool.submit(self.do_upload_img,img_obj)

            # 等待当前批次的下载任务完成之后再进行下一批次的任务进行
            th_pool.shutdown()

            # 结束下载
            if conf.img_queue.empty():
                # 如果连续15秒内队列中都没有新的数据，就结束爬取
                for _ in range(15):
                    time.sleep(1)
                    if not conf.img_queue.empty():
                        break
                else:
                    self.logger.warning(f'{self.__class__.__name__}图片下载结束...')
                    break
            