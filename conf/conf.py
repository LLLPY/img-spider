# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 21:59  
import queue
import os

import sys
sys.path.append('..'+os.sep)
import log.logger as log

# page_ready_to_crawl_queue:待爬取的页面
# page_crawled_queue:已爬取的页面
page_ready_to_crawl_queue = queue.Queue()
page_crawled_queue = queue.Queue()

# img_ready_to_crawl_queue:待爬取的图片
# img_crawled_queue:已爬取的图片
img_ready_to_crawl_queue = queue.Queue()
img_crawled_queue = queue.Queue()


#日志器
img_spider_logger=log.MyLogger().get_logger()


#请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
    'Connection': 'keep-alive',
    'Cookie': 'winWH=%5E6_1536x760; BDIMGISLOGIN=0; BDqhfp=%E5%A4%A7%E6%B5%B7%26%26NaN-1undefined%26%260%26%261; BIDUPSID=DAF9F732F5E7194E4C40073E6D597F5C; PSTM=1635870319; __yjs_duid=1_c9e50b0601fb34e9d5496d8d586043011635987389929; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BAIDUID=6C15C2AA607EF52C69767D84A939DFCD:FG=1; BAIDUID_BFESS=6C15C2AA607EF52C69767D84A939DFCD:FG=1; ZFY=hdyEzkktTSJSAz7iqn1l:BE:Bcm:Aex1ByfctpUfRs88jA:C; indexPageSugList=%5B%22%E8%80%81%E9%BC%A0%22%2C%22%E6%89%8B%E9%87%8C%E6%8B%BF%E7%9D%80%E7%83%9F%E7%9A%84%E5%9B%BE%E7%89%87%E7%9C%9F%E5%AE%9E%22%2C%22%E8%87%AA%E5%97%A8%22%2C%22%E8%87%AA%E6%8B%8D%22%2C%22%E6%AF%94%E5%BF%83%E6%89%8B%E5%8A%BF%22%2C%22%E9%A3%9F%E5%93%81%E5%B9%BF%E5%91%8A%22%2C%22%E8%A7%86%E5%B1%8F%E5%B9%BF%E5%91%8A%22%2C%22%E6%8A%A4%E8%82%A4%E5%93%81%E5%B9%BF%E5%91%8A%22%2C%22%E6%B4%97%E9%9D%A2%E5%A5%B6%E5%B9%BF%E5%91%8A%22%5D; __bid_n=1844d56671e59fb58f4207; H_PS_PSSID=36553_37691_36885_34812_37486_37726_37537_37497_37673_26350_37479; delPer=0; PSINO=1; BA_HECTOR=01ah0k2h2l8g01a10h242ec71hmi0cf1f; BDRCVFR[dG2JNJb_ajR]=mk3SLVN4HKm; userFrom=www.baidu.com; BDRCVFR[-pGxjrCMryR]=mk3SLVN4HKm; BDRCVFR[Txj84yDU4nc]=mk3SLVN4HKm; BDRCVFR[tox4WRQ4-Km]=mk3SLVN4HKm; ab_sr=1.0.1_YmQ2NDYyNzEyZmY1NDIyYTFjMjY1YjBhOTllOWI1MTdkMDk1YjIxNGUxZGNjYWRlZmNlNzlhMmUxNDM1Y2Y2MDE2Yzg3OGUzMzk5YjE3NjA4YzA1NjhmMTA0MDA0YjdkMDcxMTA5ZGViZDU2ZWUzYmNjMzUzMDIyNTQyZDIwZjNiY2U2MDBlYWJhZWZjMDI5MTA5ZjU1NmRlOGY2ZjNlZg==',
    'Host': 'image.baidu.com'
}