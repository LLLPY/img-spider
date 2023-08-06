# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/6 22:05
from img_spider.download_spider import DownloadSpider
from keyword_spider import baidu_spider as keyword_baidu_spider
from keyword_spider import _360_spider  as keyword_360_spider
from keyword_spider import bing_spider as keyword_bing_spider
from keyword_spider import sougou_spider as keyword_sougou_spider
from keyword_spider import chinaso_spider as keyword_chinaso_spider

from img_spider import baidu_spider as img_baidu_spider
from img_spider import _360_spider as img_360_spider
from img_spider import sougou_spider as img_sougou_spider
from img_spider import yandex_spider as img_yandex_spider
from img_spider import google_spider as img_google_spider

from concurrent.futures import ThreadPoolExecutor


# 程序启动接口
def main():
    print(f'=============================')
    print(f'#  🕸️        🕷️             #')
    print(f'#    🕸️Img Spider🕷️         #')
    print(f'#           🕸️2022-11-06🕸️  #')
    print(f'#      powered by python🕷️  #')
    print(f'=============================')
    # keyword = input('请输入关键字：')

    keyword = 'pizza'
    th_pool = ThreadPoolExecutor(10)
    # 关键字爬虫
    th_pool.submit(keyword_baidu_spider.KeywordBaiduSpider.run, keyword)  # 百度爬虫
    # th_pool.submit(keyword_360_spider.Keyword360Spider.run, keyword)  # 360爬虫
    # th_pool.submit(keyword_bing_spider.KeywordBingSpider.run, keyword)  # bing爬虫
    # th_pool.submit(keyword_sougou_spider.KeywordSouGouSpider.run, keyword)  # 搜狗爬虫
    # th_pool.submit(keyword_chinaso_spider.KeywordChinaSoSpider.run, keyword)  # 中国搜索爬虫

    # 图片爬虫
    # th_pool.submit(img_baidu_spider.ImgBaiduSpider.run, keyword)
    # th_pool.submit(img_360_spider.Img360Spider.run, keyword)
    # th_pool.submit(img_sougou_spider.ImgSougouSpider.run, keyword)
    # th_pool.submit(img_yandex_spider.ImgYandexSpider.run, keyword)
    # th_pool.submit(img_google_spider.ImgGoogleSpider.run, keyword)
    # th_pool.submit(DownloadSpider.run,keyword)
    th_pool.shutdown()


if __name__ == '__main__':
    main()
