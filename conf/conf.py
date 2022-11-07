# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 21:59  
import queue

# page_ready_to_crawl_queue:待爬取的页面
# page_crawled_queue:已爬取的页面
page_ready_to_crawl_queue = queue.Queue()
page_crawled_queue = queue.Queue()

# img_ready_to_crawl_queue:待爬取的图片
# img_crawled_queue:已爬取的图片
img_ready_to_crawl_queue = queue.Queue()
img_crawled_queue = queue.Queue()


