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
    chrome_pool = ChromeWorkerManager(5)

    # 初始化时只需要知道keyword即可
    def __init__(self, keyword):
        self.keyword = keyword
        self.chrome = Chrome(service=conf.CHROMEDRIVER_SERVICE, options=conf.chrome_options)

    def __del__(self):
        try:
            self.chrome.close()
        except Exception as e:
            conf.img_spider_logger.error(f'浏览器窗口关闭失败...错误原因:{e}')
