# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 21:59  
import queue
import os
import sys
import selenium.webdriver.chrome.service as chrome_service

sys.path.append('..' + os.sep)
import log.logger as log
import file_system.file_system as file_system
import client.client as client
# 指定driver的位置
CHROMEDRIVER_SERVICE = chrome_service.Service('chromedriver.exe')

# workdir
workdir = os.path.abspath('.')  # 工作目录

# page_ready_to_crawl_queue:待爬取的页面
# page_crawled_queue:已爬取的页面
page_ready_to_crawl_queue = queue.Queue()
page_crawled_queue = queue.Queue()

# img_ready_to_crawl_queue:待爬取的图片
# img_crawled_queue:已爬取的图片
img_ready_to_crawl_queue = queue.Queue()
img_crawled_queue = queue.Queue()

# page_url和img_url的集合
my_api_crawled_pickle = file_system.MyPickle(os.path.join(workdir, 'data', 'set', 'api_crawled_set'))
my_page_crawled_pickle = file_system.MyPickle(os.path.join(workdir, 'data', 'set', 'page_crawled_set'))
my_img_crawled_pickle = file_system.MyPickle(os.path.join(workdir, 'data', 'set', 'img_crawled_set'))
api_crawled_set = my_api_crawled_pickle.load()
page_crawled_set = my_page_crawled_pickle.load()
img_crawled_set = my_img_crawled_pickle.load()


my_api_ready_pickle = file_system.MyPickle(os.path.join(workdir, 'data', 'set', 'api_ready_set'))
my_page_ready_pickle = file_system.MyPickle(os.path.join(workdir, 'data', 'set', 'page_ready_set'))
my_img_ready_pickle = file_system.MyPickle(os.path.join(workdir, 'data', 'set', 'img_ready_set'))
api_ready_set = my_api_ready_pickle.load()
page_ready_set = my_page_ready_pickle.load()
img_ready_set = my_img_ready_pickle.load()



# 日志器
img_spider_logger = log.MyLogger().get_logger()

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
}

#客户端
img_client=client.Client()
