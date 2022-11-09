# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 22:01  
import asyncio
import aiohttp
import aiofiles
import requests
import os
import sys

sys.path.append(f'..{os.sep}')
import conf.conf as conf
import conf.model as model


class BaseSpider:

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword

    def get(self, url, headers=conf.HEADERS):
        res = requests.get(url, headers=headers, verify=False)
        if res.status_code != 200:
            conf.img_spider_logger.warning(f'[{self.__class__.__name__}.get] 响应码不为200!...')

        return res

    async def download_img(self, img_obj: model.Img, save_path: str):
        async with aiohttp.ClientSession() as session:
            aiohttp.ClientTimeout(5)
            async with session.get(img_obj.url, headers=conf.HEADERS) as res:
                async with aiofiles.open(save_path, 'wb') as f:
                    content = await res.content.read()
                    await f.write(content)
                    print('下载完成...')


if __name__ == '__main__':
    spider = BaseSpider('http://edu.chachaba.com/Uploads/2020-03-20/5e74678a17ab4.jpg')
    asyncio.run(spider.download_img('1.jpg'))
