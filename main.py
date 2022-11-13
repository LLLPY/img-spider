# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/6 22:05  

from spider import baidu_spider
from concurrent.futures import ThreadPoolExecutor


# 程序启动接口
def main():
    th_pool = ThreadPoolExecutor(10)
    # keyword=input('请输入关键字：')
    keyword = '美女'
    # 没类爬虫单独启一个线程
    th_pool.submit(baidu_spider.run_baidu_spider(keyword))  # 百度爬虫
    th_pool.shutdown()


if __name__ == '__main__':
    main()
