# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 22:01  
import asyncio
import hashlib

import aiohttp
import aiofiles
import requests
import os
import sys
from urllib.request import urlretrieve
from lxml import etree
import selenium
import re
import time
from selenium import webdriver
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
    
    
    #urlretrieve
    @staticmethod
    def urlretrieve_get(url,save_path,is_delete=False):
    
        urlretrieve(url,save_path)
        #如果仅仅是临时文件，就将其删除

        with open(save_path,'r',encoding='utf8') as f:
            content=f.read()

        if is_delete:
            os.remove(save_path)
        return save_path,content


        
    #chrome get
    @staticmethod
    def chrome_get(url):        
        chrome_options=webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_driver=webdriver.Chrome(chrome_options=chrome_options,service=conf.CHROMEDRIVER_SERVICE)
        chrome_driver.get(url)
        time.sleep(1)
        page=chrome_driver.page_source
        chrome_driver.close()
        return page
   

    # 根据获取一个page上的img链接
    async def get_img_url_on_page(self):
        while True:
            await asyncio.sleep(0)  # 让出cpu

            page_obj = conf.page_ready_to_crawl_queue.get()
            success, res = self.get(page_obj.url)
            # if not success:
            #     conf.page_crawled_set.add(page_obj.url)  # 不成功就添加到已爬取的集合中
            #     conf.img_spider_logger.warning(f'get img url failed from page:{page_obj.url}')
            #     continue
            # html = res.text
            # html=self.chrome_get(page_obj.url)
            _,html=self.urlretrieve_get(page_obj.url,hashlib.sha1(str(page_obj.url).encode('utf8')).hexdigest()+'.html')
            relate_links=self.get_pre_and_next_links(html)
            conf.img_spider_logger.info(f'page:{page_obj.url}\n,relate_links:{relate_links}')

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


    #获取某个页面中上一页和下一页的链接
    @staticmethod
    def get_pre_and_next_links(html):
        pattern=r'<a.*href="(.*?)".*>.*{}.*</a>'
        tag_list=['上一页','pre','下一页','next','page']
        res=[]
        for tag in tag_list:
            tmp_res=re.findall(pattern.format(tag),html,re.IGNORECASE)
            res.extend(tmp_res)
        return list(set(res))



if __name__ == '__main__':
    spider = BaseSpider('大海')
    img_obj = model.Img(spider.keyword, '', 'http://edu.chachaba.com/Uploads/2020-03-20/5e74678a17ab4.jpg')
    asyncio.run(spider.download_img(img_obj))
