# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/27 11:38
import queue
import time
import conf.conf as conf
import os
from selenium.webdriver import Chrome
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
        self.img_queue = queue.Queue()  # 图片消费队列
        self.img_crawled_queue = queue.Queue()  # 下载完成的图片队列

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
            page = model.Page(page_obj.keyword, page_url)
            thumb_url = page_thumb[1]
            thumb_url_set.add(thumb_url)
            img = model.Img(page_obj.keyword, page_url, thumb_url, thumb_url)

        # 匹配原图
        img_list = re.findall(r'<img.*src="(.*?)".*>', page_html)
        for img in img_list:
            if img not in thumb_url_set:
                img_obj = model.Img(page_obj.url, img, img)

    def download_img_callback(self, msg):
        result = msg.result()
        status = result['status']
        success = ['失败', '成功'][status]
        img_obj = result['img_obj']

        if success == '成功':
            img_obj.status = model.Img.STATUS_CRAWLED
        else:
            img_obj.status = model.Img.STATUS_ERROR
        msg = result['msg']
        self.logger.info(
            f'下载{success},msg:{msg},剩余{self.img_queue.qsize()}待爬取...img_url:{img_obj.url}')
        self.img_crawled_queue.put(img_obj)

    # 定时上传爬取完成的图片
    def timed_upload_img(self):
        self.logger.info(f'图片上传服务已启动...')
        start = time.time()
        while True:
            if self.img_crawled_queue.qsize() > 20 or time.time() - start > 10:
                img_dict_list = []
                while not self.img_crawled_queue.empty():
                    img_obj = self.img_crawled_queue.get()
                    img_dict_list.append(img_obj.to_dict())
                if img_dict_list:
                    res = self.client.update_img(img_dict_list)
                    if res['code'] == '200':
                        self.logger.info(f'图片上传成功,上传了{len(img_dict_list)}个图片...')
                    else:
                        msg = res['msg']
                        self.logger.warning(f'图片上传失败,msg:{msg}...')

                start = time.time()
            time.sleep(1)

    # 下载图片
    @classmethod
    def download_img(cls, img_obj: model.Img):
        # 创建下载目录
        dirs = img_obj.save_path.rsplit(os.sep, 1)[0]
        try:
            if not os.path.isdir(dirs):
                os.makedirs(dirs)
        except:
            pass
        success = True
        msg = ''
        try:
            urlretrieve(img_obj.url, img_obj.save_path)
        except Exception as e:
            msg = e
            success = False
        return {'status': success, 'msg': msg, 'img_obj': img_obj}

    def supply_img_queue(self):
        res = self.client.get_ready_img_list(self.keyword)
        if res['code'] == '200':
            img_dict_list = res['data']
            for img_dict in img_dict_list:
                img_obj = model.Img.to_obj(img_dict)
                self.img_queue.put(img_obj)
            self.logger.info(f'补充了张{len(img_dict_list)}图片到消费队列...')

    # 下载图片
    def download_imgs(self):
        self.logger.warning(f'{self.__class__.__name__}开始下载图片...')
        self.supply_img_queue()
        while True:
            th_pool = ThreadPoolExecutor(5)
            for _ in range(5):  # 每次启动5个任务去下载图片
                if not self.img_queue.empty():
                    img_obj = self.img_queue.get()
                    future = th_pool.submit(self.download_img, img_obj)
                    future.add_done_callback(self.download_img_callback)
            # 等待当前批次的下载任务完成之后再进行下一批次的任务进行
            th_pool.shutdown()

            # 结束下载
            if self.img_queue.empty():
                self.supply_img_queue()
                # 如果连续15秒内队列中都没有新的数据，就结束爬取
                for _ in range(15):
                    time.sleep(1)
                    if not self.img_queue.empty():
                        break
                else:
                    self.logger.warning(f'{self.__class__.__name__}图片下载结束...')
                    break

    def get_img_link_by_img(self):
        pass

    @classmethod
    def run(cls, keyword):
        spider = cls(keyword)
        th_pool = ThreadPoolExecutor(5)
        # th_pool.submit(spider.get_img_link_by_img)
        th_pool.submit(spider.download_imgs)
        th_pool.submit(spider.timed_upload_img)
        th_pool.shutdown()
