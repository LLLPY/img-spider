# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/7 21:24

import sys
import os
import re
import lxml.etree as etree
from base_spider import BaseSpider

# 关闭警告
import requests
requests.packages.urllib3.disable_warnings()
sys.path.append(f'..{os.sep}')
import conf.conf as conf
import conf.model as model
import utils.utils as utils

API_BAIDU = 'https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&fp=result&word={}&cl=2&lm=-1&ie=utf-8&oe=utf-8&pn={}&rn={}'


# 关键字爬虫：根据关键字，爬取相关页面，产出imgurl
class BaiduSpider(BaseSpider):

    def __init__(self, keyword: str) -> None:
        super(BaiduSpider, self).__init__(keyword)

    # 根据关键字获取图片所在页面的地址

    @utils.clocked
    async def get_page_url_by_keyword(self):
        page_num = 0  # 页码
        per_page = 30  # 每页的数量
        page_set = set()
        while True:
            url = API_BAIDU.format(
                self.keyword, page_num, per_page)  # TODO:#判断该url是否已爬取
            res = requests.get(url, headers=conf.HEADERS, verify=False)
            if res.status_code != 200:
                return
            json_content = res.json()
            data_list = json_content['data']
            for item in data_list:
                page_url = None
                if 'replaceUrl' in item:
                    
                    items = item['replaceUrl']
                    for inner_item in items:
                        if 'FromUrl' in inner_item:
                            page_url = inner_item['FromUrl']
                            # TODO 判断该page_url是否已爬取，如果没有爬取就添加到消费队列
                            page_set.add(page_url)
                            page_obj = model.Page(self.keyword, page_url)
                            conf.page_ready_to_crawl_queue.put(page_obj)
                            conf.img_spider_logger.info(f'page_url:{page_url}')

                if 'objURL' in item:
                    # 图片的原始地址 TODO:判断该图片是否已爬取 如果没有爬取就添加到消费队列
                    img_url = self.parse_encrypt_url(item['objURL'])
                    img_obj = model.Img(self.keyword, page_url, img_url)
                    conf.img_ready_to_crawl_queue.put(img_obj)  # 添加到消费队列

            if len(data_list) < per_page or page_num>=60:  # 最后一页
                break

            page_num += per_page
        conf.img_spider_logger.info(
            f'func[get_page_url_by_keyword]->keyword:{self.keyword},crwaled {page_num} page(s),get {len(page_set)} page_url(s).')

    # 通过以图搜图的方式来获取相应的page链接

    @utils.clocked
    def get_page_url_by_img(self):
        pass

    # 根据获取一个page上的img链接
    async def get_img_url_on_page(self):
        
        conf.img_spider_logger.info('开始抓取page上的img链接...')
        while True:
            page_obj = conf.page_ready_to_crawl_queue.get()
            
            success,res = self.get(page_obj.url)
            if not success:
                continue
            html = res.text
            try:
                e = etree.HTML(html)
                img_list = e.xpath('//body//img/@src')
                for img in img_list:
                    img_obj = model.Img(self.keyword, page_obj.url, img)
                    conf.img_ready_to_crawl_queue.put(img_obj)
            except:
                print('页面解析出错...',page_obj.url)

    # 下载图片
    async def download_imgs(self):
        while True:
            img_obj = conf.img_ready_to_crawl_queue.get()            
            await super().download_img(img_obj)
            conf.img_spider_logger.info(f'下载完成img:{img_obj.url}')

            

    # 解析加密的url

    @staticmethod
    def parse_encrypt_url(encrypt_url: str = 'ippr_z2C$qAzdH3FAzdH3Fi7wkwg_z&e3Bv54AzdH3FrtgfAzdH3F8ddal9lcaAzdH3F') -> str:
        mapping = {
            'w': "a",
            'k': "b",
            'v': "c",
            '1': "d",
            'j': "e",
            'u': "f",
            '2': "g",
            'i': "h",
            't': "i",
            '3': "j",
            'h': "k",
            's': "l",
            '4': "m",
            'g': "n",
            '5': "o",
            'r': "p",
            'q': "q",
            '6': "r",
            'f': "s",
            'p': "t",
            '7': "u",
            'e': "v",
            'o': "w",
            '8': "1",
            'd': "2",
            'n': "3",
            '9': "4",
            'c': "5",
            'm': "6",
            '0': "7",
            'b': "8",
            'l': "9",
            'a': "0",
            '_z2C$q': ":",
            "_z&e3B": ".",
            'AzdH3F': "/"
        }  # 映射表
        encrypt_url = re.sub('AzdH3F', '/', encrypt_url)  # 替换
        encrypt_url = re.sub("_z&e3B", ".", encrypt_url)
        encrypt_url = re.sub('_z2C\$q', ":", encrypt_url)
        url_list = []
        for c in encrypt_url:
            if c in mapping:  # 替换掉加密的url中的一些字符
                c = mapping[c]
            url_list.append(c)
        return ''.join(url_list)


# 执行
async def run_baidu_spider(keyword: str = '美女'):
    baidu_spider = BaiduSpider(keyword)
    await baidu_spider.get_page_url_by_keyword()
    await baidu_spider.download_imgs()
    await baidu_spider.get_img_url_on_page()


if __name__ == '__main__':
    import asyncio
  
    asyncio.run(run_baidu_spider())
