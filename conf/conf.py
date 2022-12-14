# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 21:59  
import os
import sys

import requests
import selenium.webdriver.chrome.service as chrome_service
import selenium.webdriver as webdriver
import socket

sys.path.append('..' + os.sep)
import log.logger as log
import client.client as client

# 设置timeout时间为6秒
socket.setdefaulttimeout(6)

# workdir
workdir = os.path.abspath('.')  # 工作目录


# 日志器
img_spider_logger = log.MyLogger().get_logger()

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
}

# 关闭警告
requests.packages.urllib3.disable_warnings()

# 客户端
img_client = client.Client()

# selenium相关配置

# 指定driver的位置
CHROMEDRIVER_SERVICE = chrome_service.Service('./chromedriver')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('headless')
