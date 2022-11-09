# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 22:01  
import asyncio
import aiohttp
import aiofiles
import os
import sys
sys.path.append(f'..{os.sep}')
import conf.conf as conf



class BaseSpider:

    def __init__(self,url):
        self.url=url
        
    
    async def download_img(self,save_path:str):
        async with aiohttp.ClientSession() as session:
            aiohttp.ClientTimeout(5)
            async with session.get(self.url,headers=conf.HEADERS) as res:   
                print(self.url) 
                async with aiofiles.open(save_path,'wb') as f:
                    content=await res.content.read()
                    await f.write(content)
                    print(content)
                    print('下载完成...')                
        



if __name__ == '__main__':
    spider=BaseSpider('http://edu.chachaba.com/Uploads/2020-03-20/5e74678a17ab4.jpg')
    asyncio.run(spider.download_img('1.html'))
