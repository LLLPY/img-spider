# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/7 21:24

import re
import asyncio
from .base_spider import BaseSpider
import conf.conf as conf
import conf.model as model
import utils.utils as utils

API_BAIDU = 'https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&fp=result&word={}&cl=2&lm=-1&ie=utf-8&oe=utf-8&pn={}&rn={}'


# 关键字爬虫：根据关键字，爬取相关页面，产出imgurl
class BaiduSpider(BaseSpider):

    def __init__(self, keyword: str) -> None:
        super(BaiduSpider, self).__init__(keyword)

    # 根据关键字获取图片所在页面的地址
    async def get_page_url_by_keyword(self):
        page_num = 0  # 页码
        per_page = 30  # 每页的数量
        page_set = set()
        while True:
            await asyncio.sleep(0)
            url = API_BAIDU.format(
                self.keyword, page_num, per_page)  # done:#判断该url是否已爬取
            if url in conf.api_crawled_set:
                continue  # 如果是已经爬取的url，就不用再爬取了
            success, res = self.get(url, headers=conf.HEADERS)
            if not success:
                conf.api_crawled_set.add(url)  # 将失败的url添加到api_crawled_set集合中
                continue
            # 数据抽取
            json_content = res.json()
            data_list = json_content['data']
            conf.img_spider_logger.info(f'get {len(data_list)} items from {url}')
            for item in data_list:
                page_url = None
                if 'replaceUrl' in item:
                    items = item['replaceUrl']
                    for inner_item in items:
                        if 'FromUrl' in inner_item:
                            page_url = inner_item['FromUrl']
                            # done 判断该page_url是否已爬取，如果没有爬取就添加到消费队列
                            if page_url in conf.page_crawled_set:
                                continue
                            page_set.add(page_url)
                            page_obj = model.Page(self.keyword, page_url)
                            conf.page_ready_to_crawl_queue.put(page_obj)

                if 'objURL' in item:
                    # 图片的原始地址 done:判断该图片是否已爬取 如果没有爬取就添加到消费队列
                    img_url = self.parse_encrypt_url(item['objURL'])
                    if img_url not in conf.img_crawled_set:
                        img_obj = model.Img(self.keyword, page_url, img_url)
                        conf.img_ready_to_crawl_queue.put(img_obj)  # 添加到消费队列

            conf.api_crawled_set.add(url)  # 该url已爬取
            if len(data_list) < per_page:  # or page_num >= 60:  # 最后一页
                # conf.my_api_pickle.dump(conf.api_crawled_set)  # 写入文件
                conf.img_spider_logger.info(f'func get_page_url_by_keyword done,get {len(page_set)} url(s).')
                break

            page_num += per_page
        conf.img_spider_logger.info(
            f'keyword:{self.keyword},get {page_num} page(s),get {len(page_set)} page_url(s).')

    # 通过以图搜图的方式来获取相应的page链接
    @utils.clocked
    def get_page_url_by_img(self):
        pass


    # 下载图片
    async def download_imgs(self):
        while True:
            await asyncio.sleep(0)  # 让出cpu
            task_list = []
            while conf.img_ready_to_crawl_queue.qsize(): #只要有待消费的图片，就创建一个协程任务
                img_obj = conf.img_ready_to_crawl_queue.get()
                task = asyncio.create_task(self.download_img(img_obj))
                task_list.append(task)
            for task in task_list:
                await task
            # task.add_done_callback()
            # conf.img_crawled_set.add(img_obj.url)  # 添加到已爬取的集合中

    # 解析加密的url
    @staticmethod
    def parse_encrypt_url(
            encrypt_url: str = 'ippr_z2C$qAzdH3FAzdH3Fi7wkwg_z&e3Bv54AzdH3FrtgfAzdH3F8ddal9lcaAzdH3F') -> str:
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


async def baidu_spider(keyword: str):
    baidu_spider = BaiduSpider(keyword)
    await asyncio.gather(
        baidu_spider.get_page_url_by_keyword(),
        baidu_spider.get_img_url_on_page(),
        baidu_spider.download_imgs()
    )  # 并发运行


# 执行
def run_baidu_spider(keyword: str):
    asyncio.run(baidu_spider(keyword))


if __name__ == '__main__':
    run_baidu_spider('')
