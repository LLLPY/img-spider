# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/6 22:05  

from spider import baidu_spider, _360_spider, bing_spider, sougou_spider, chinaso_spider
from concurrent.futures import ThreadPoolExecutor


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
    th_pool.submit(baidu_spider.run_baidu_spider,keyword)  # 百度爬虫
    th_pool.submit(_360_spider.run_360_spider,keyword)  # 360爬虫
    th_pool.submit(bing_spider.run_bing_spider,keyword)  # bing爬虫
    th_pool.submit(sougou_spider.run_sougou_spider,keyword)  # 搜狗爬虫
    th_pool.submit(chinaso_spider.run_chinaso_spider,keyword)  # 中国搜索爬虫
    th_pool.shutdown()


if __name__ == '__main__':
    main()
