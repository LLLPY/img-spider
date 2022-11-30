# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/6 22:05  

from keyword_spider import baidu_spider as keyword_baidu_spider
from keyword_spider import _360_spider  as keyword_360_spider
from keyword_spider import bing_spider as keyword_bing_spider
from keyword_spider import sougou_spider as keyword_sougou_spider
from keyword_spider import chinaso_spider as keyword_chinaso_spider
from keyword_spider import base_spider as keyword_base_spider
from concurrent.futures import ThreadPoolExecutor
from img_spider import baidu_spider as img_baidu_spider


# 程序启动接口
def main():
    print(f'=============================')
    print(f'#  🕸️        🕷️             #')
    print(f'#    🕸️Img Spider🕷️         #')
    print(f'#           🕸️2022-11-06🕸️  #')
    print(f'#      powered by python🕷️  #')
    print(f'=============================')
    keyword = input('请输入关键字：')

    # keyword = '雪山'
    th_pool = ThreadPoolExecutor(10)
    # 每类爬虫单独启一个线程
    # th_pool.submit(keyword_baidu_spider.run_baidu_spider, keyword)  # 百度爬虫
    # th_pool.submit(keyword_360_spider.run_360_spider, keyword)  # 360爬虫
    # th_pool.submit(keyword_bing_spider.run_bing_spider, keyword)  # bing爬虫
    # th_pool.submit(keyword_sougou_spider.run_sougou_spider, keyword)  # 搜狗爬虫
    th_pool.submit(keyword_chinaso_spider.run_chinaso_spider, keyword)  # 中国搜索爬虫
    # th_pool.submit(keyword_base_spider.run_timed_task)  # 定时定量上传图片到服务器
    th_pool.shutdown()


if __name__ == '__main__':
    main()
    # baidu_spider = baidu_spider.BaiduSpider('美女')
    # baidu_spider.get_img_link_by_img()
