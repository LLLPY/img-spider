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

sys.path.append(f'..{os.sep}')
import conf.conf as conf
import conf.model as model


class BaseSpider:

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword

    def get(self, url, headers=conf.HEADERS):
        success=True
        try:
            res = requests.get(url, headers=headers, verify=False,timeout=5)
            
        except Exception as e:
            print(url,e)
            res=None
            success=False
        return success,res


    #下载图片
    async def download_img(self, img_obj: model.Img):  
        dirs=img_obj.save_path.rsplit(os.sep,1)[0]
        if not os.path.isdir(dirs):
            os.makedirs(dirs)
        urlretrieve(img_obj.url,img_obj.save_path)         
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
    img_obj=model.Img(spider.keyword,'','http://edu.chachaba.com/Uploads/2020-03-20/5e74678a17ab4.jpg')
    asyncio.run(spider.download_img(img_obj))
