# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/6 22:05  

from keyword_spider import baidu_spider as keyword_baidu_spider
from keyword_spider import _360_spider  as keyword_360_spider
from keyword_spider import bing_spider as keyword_bing_spider
from keyword_spider import sougou_spider as keyword_sougou_spider
from keyword_spider import chinaso_spider as keyword_chinaso_spider
from img_spider import baidu_spider as img_baidu_spider
from concurrent.futures import ThreadPoolExecutor


# 程序启动接口
def main():
    # print(f'=============================')
    # print(f'#  🕸️        🕷️             #')
    # print(f'#    🕸️Img Spider🕷️         #')
    # print(f'#           🕸️2022-11-06🕸️  #')
    # print(f'#      powered by python🕷️  #')
    # print(f'=============================')
    # keyword = input('请输入关键字：')

    keyword = '航拍沙滩'
    th_pool = ThreadPoolExecutor(10)
    # 关键字爬虫
    th_pool.submit(keyword_baidu_spider.BaiduSpider.run, keyword)  # 百度爬虫
    th_pool.submit(keyword_360_spider._360Spider.run, keyword)  # 360爬虫
    th_pool.submit(keyword_bing_spider.BingSpider.run, keyword)  # bing爬虫
    th_pool.submit(keyword_sougou_spider.SouGouSpider.run, keyword)  # 搜狗爬虫
    th_pool.submit(keyword_chinaso_spider.ChinaSoSpider.run, keyword)  # 中国搜索爬虫

    # 图片爬虫
    th_pool.submit(img_baidu_spider.BaiduSpider.run, keyword)

    th_pool.shutdown()


if __name__ == '__main__':
    # main()
    baidu_spider = img_baidu_spider.BaiduSpider.run('美女')
