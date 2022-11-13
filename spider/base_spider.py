# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 22:01  
import asyncio
import aiohttp
import aiofiles
import requests
import os
import sys
from urllib.request import urlretrieve
from lxml import etree

sys.path.append(f'..{os.sep}')
import conf.conf as conf
import conf.model as model

requests.packages.urllib3.disable_warnings()  # 关闭警告


class BaseSpider:

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword

    # get请求
    def get(self, url, headers=conf.HEADERS):
        success = True
        try:
            res = requests.get(url, headers=headers, verify=False, timeout=5)
        except Exception as e:
            conf.img_spider_logger.error(f'get request failed,error info: {e}, url {url}')
            res = None
            success = False
        return success, res

    # 根据获取一个page上的img链接
    async def get_img_url_on_page(self):
        while True:
            await asyncio.sleep(0)  # 让出cpu
            page_obj = conf.page_ready_to_crawl_queue.get()
            success, res = self.get(page_obj.url)
            if not success:
                conf.page_crawled_set.add(page_obj.url)  # 不成功就添加到已爬取的集合中
                conf.img_spider_logger.warning(f'get img url failed from page:{page_obj.url}')
                continue
            html = res.text
            try:
                e = etree.HTML(html)
                img_list = e.xpath('//body//img/@src')
                crawled_n = 0
                for img in img_list:
                    img_obj = model.Img(self.keyword, page_obj.url, img)
                    if img not in conf.img_crawled_set:
                        conf.img_ready_to_crawl_queue.put(img_obj)
                    else:
                        crawled_n += 1
                conf.img_spider_logger.info(
                    f'keyword:{self.keyword},extract done，get {len(img_list)} img(s), {crawled_n} have been crawled.page url:{page_obj.url}')
            except Exception as e:
                conf.img_spider_logger.warning(
                    f'keyword:{self.keyword},page url:{page_obj.url},extract failed,error info:{e}')
            conf.page_crawled_set.add(page_obj.url)  # 不管数据有没有抽取成功，都添加到已爬取的集合中

    # 下载图片
    @classmethod
    async def download_img(cls, img_obj: model.Img):
        dirs = img_obj.save_path.rsplit(os.sep, 1)[0]
        if not os.path.isdir(dirs):
            os.makedirs(dirs)
        try:
            urlretrieve(img_obj.url, img_obj.save_path)
        except Exception as e:
            conf.img_spider_logger.warning(f'download img failed,error info {e},img url:{img_obj.url}')

        # async with aiohttp.ClientSession() as session:
        #     aiohttp.ClientTimeout(5) #最大等待时间为5秒
        #     async with session.get(img_obj.url, headers=conf.HEADERS) as res:
        #         dirs=img_obj.save_path.rsplit(os.sep,1)[0]
        #         if not os.path.isdir(dirs):
        #             os.makedirs(dirs)
        #         async with aiofiles.open(img_obj.save_path, 'wb') as f:
        #             content = await res.content.read()
        #             await f.write(content)
        #             print('下载完成...')


if __name__ == '__main__':
    spider = BaseSpider('大海')
    img_obj = model.Img(spider.keyword, '', 'http://edu.chachaba.com/Uploads/2020-03-20/5e74678a17ab4.jpg')
    asyncio.run(spider.download_img(img_obj))
