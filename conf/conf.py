# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 21:59  
import queue
import os
import sys
import selenium.webdriver.chrome.service as chrome_service
import selenium.webdriver as webdriver
import socket

sys.path.append('..' + os.sep)
import log.logger as log
import file_system.file_system as file_system
import client.client as client


# 设置timeout时间为6秒
socket.setdefaulttimeout(6)

# workdir
workdir = os.path.abspath('.')  # 工作目录

page_queue = queue.Queue()
img_queue = queue.Queue()

# page_url和img_url的集合
my_img_pickle = file_system.MyPickle(os.path.join(workdir, 'data', 'set', 'img_set'))
my_page_pickle = file_system.MyPickle(os.path.join(workdir, 'data', 'set', 'page_set'))

img_set = my_img_pickle.load()
page_set = my_page_pickle.load()

my_api_crawled_pickle = file_system.MyPickle(os.path.join(workdir, 'data', 'set', 'api_crawled_set'))
api_crawled_set = my_api_crawled_pickle.load()

# 日志器
img_spider_logger = log.MyLogger().get_logger()

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
}

# 客户端
img_client = client.Client()

# selenium相关配置

# 指定driver的位置
CHROMEDRIVER_SERVICE = chrome_service.Service('./chromedriver')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('headless')
