# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/27 11:38  
import conf.conf as conf
import os
from queue import Queue
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor


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

    # 初始化时只需要知道keyword即可
    def __init__(self, keyword):
        self.keyword = keyword
        self.chrome = Chrome(service=conf.CHROMEDRIVER_SERVICE, options=conf.chrome_options)

    def __del__(self):
        try:
            self.chrome.close()
        except Exception as e:
            conf.img_spider_logger.error(f'浏览器窗口关闭失败...错误原因:{e}')
