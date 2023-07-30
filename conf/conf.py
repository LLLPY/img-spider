# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 21:59  
import os
import sys
import json
import requests
import selenium.webdriver.chrome.service as chrome_service
import selenium.webdriver as webdriver
import socket
import pprint

sys.path.append('..' + os.sep)
import log.logger as log
import client.client as client

# 配置文件
try:
    config_data = json.load(open('config.json', 'r', encoding='utf8'))
    print('*' * 48 + '配置文件' + '*' * 48)
    for k in config_data:
        print(k, ':', end=' ')
        pprint.pprint(config_data[k])
    print('*' * 48 + '配置文件' + '*' * 48)

except Exception as e:
    print(f'配置文件加载异常,程序退出!{e}')
    exit(0)

# 设置timeout时间为默认为6秒
socket.setdefaulttimeout(config_data.get('timeout'))

# workdir
workdir = os.path.abspath('.')  # 工作目录

# 日志器
img_spider_logger = log.MyLogger(log_to_file=config_data.get('log_to_file')).get_logger()

# 请求头
headers = config_data.get('headers')

# 关闭警告
requests.packages.urllib3.disable_warnings()

# 客户端
host = config_data.get('host', '127.0.0.1')
port = config_data.get('port', '8000')
img_client = client.Client(host, port, headers)

# selenium相关配置

# 指定driver的位置
CHROMEDRIVER_SERVICE = chrome_service.Service('./chromedriver')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
headless = config_data.get('img_spider').get('headless')
if headless: chrome_options.add_argument('headless')

prefs = {
    'profile.default_content_setting_values': {
        'images': 2,  # 不加载图片
        'videos': 2,  # 不加载图片
        # 'javascript': 2,  # 不加载JS

    }
}
chrome_options.add_experimental_option('prefs', prefs)
