# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/17 22:40  

import re
import asyncio
from .base_spider import BaseSpider
import conf.conf as conf
import json
import conf.model as model

API_360='https://image.so.com/j?callback=jQuery1830230393401408725_1668736904746&q={}&qtag=&pd=1&pn=60&adstar=0&tab=all&sid=15d39fba0b6f9e26589eed4f9434a0c5&ras=6&cn=0&gn=0&kn=11&crn=0&bxn=20&cuben=0&pornn=0&manun=4&sn={}&ps={}&pc={}'


# 关键字爬虫：根据关键字，爬取相关页面，产出imgurl
class _360Spider(BaseSpider):
    headers = {
        'cookie': '__guid=16527278.4082153822803365400.1646141706668.241; __huid=11Hvv3UD9R1dvCxvfpzmOac7pj%2BUE2vX1yEBTJb4qyB%2FQ%3D; QiHooGUID=D6991E17ACF01EAEA1F34D30D6B63266.1646280271067; so_huid=11Hvv3UD9R1dvCxvfpzmOac7pj%2BUE2vX1yEBTJb4qyB%2FQ%3D; biz_huid=11Hvv3UD9R1dvCxvfpzmOac7pj%2BUE2vX1yEBTJb4qyB%2FQ%3D; opqopq=19dad04ff4e51811cf8d73967410ac30.1668695144; gtHuid=1; test_cookie_enable=null; tracker=tab_www|1668695215912; erules=p1-10%7Cp4-15%7Ckd-1',
        'referer': 'https://image.so.com/i?q=%E5%A4%A7%E6%B5%B7&src=tab_www',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
        'Connection': 'keep-alive',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }

    def __init__(self, keyword: str) -> None:
        super(_360Spider, self).__init__(keyword)

    # 根据关键字获取图片所在页面的地址
    async def get_page_url_by_keyword(self):
        page_set = set()
        sn=0 #起始页
        ps=0 #起始页
        pc=50 #每页的数量
        while True:
            await asyncio.sleep(0)
            url=API_360.format(self.keyword,sn,ps,pc)
            if url in conf.api_crawled_set:
                continue  # 如果是已经爬取的url，就不用再爬取了
            success, res = self.get(url, headers=self.headers)
            if not success:
                conf.api_crawled_set.add(url)  # 将失败的url添加到api_crawled_set集合中
                continue
            
            # 数据抽取
            json_content = res.text
            json_content = re.sub('jQuery\d+_\d+\(', '', json_content).strip(');')
            json_content = json.loads(json_content)
            data_list = json_content['list']

            for item in data_list:
                img_url = item['thumb']
                page_url=item['link'] #图片所在的页面
                if img_url not in conf.img_crawled_set:
                    img_obj = model.Img(self.keyword, page_url, img_url)
                    conf.img_ready_to_crawl_queue.put(img_obj)  # 添加到消费队列
                    
            conf.api_crawled_set.add(url)  # 该url已爬取
            sn+=len(data_list)
            ps+=len(data_list)
            if len(data_list)==0:
                break
            conf.img_spider_logger.info(
                f'keyword:{self.keyword},get {len(page_set)} img_url(s) from page:{url}.')

    
            # task.add_done_callback()
            # conf.img_crawled_set.add(img_obj.url)  # 添加到已爬取的集合中


async def _360_spider(keyword: str):
    _360_spider = _360Spider(keyword)
    await asyncio.gather(
        _360_spider.get_page_url_by_keyword(),
        # _360_spider.get_img_url_on_page(),
        _360_spider.download_imgs()
    )  # 并发运行


# 执行
def run_360_spider(keyword: str):
    asyncio.run(_360_spider(keyword))


if __name__ == '__main__':
    run_360_spider('大海')
