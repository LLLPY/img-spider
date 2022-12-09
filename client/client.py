import json
import aiohttp
import asyncio
from typing import *
class Client:
    HOST = 'http://127.0.0.1'
    HOST = 'http://www.lll.plus'
    PORT = '80'
    img_server_prefix = 'img-spider-server/img_server'
    page_server_prefix = 'img-spider-server/page_server'
    salt = ''
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
    }

    @classmethod
    async def async_get(cls, url: str) ->dict:
        timeout = aiohttp.ClientTimeout(total=10)  # 10秒过期
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=cls.HEADERS) as response:
                json_content = await response.json(content_type='application/json', encoding='utf-8')
                return json_content

    @classmethod
    async def async_post(cls, url: str, data: dict)->dict:
        timeout = aiohttp.ClientTimeout(total=10)  # 10秒过期
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=cls.HEADERS, data=data) as response:
                json_content = await response.json(content_type='application/json', encoding='utf-8')
                return json_content

    # 获取关键字列表
    async def get_keyword_list(self)->List[str]:
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/keyword_list'
        json_content = await self.async_get(url)
        keyword_list = json_content['keyword_list']
        return keyword_list

    # 上传img
    async def upload_img(self, img_list:List[dict]):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/upload_img/'
        data = {
            'img_list': json.dumps(img_list),
        }
        json_content = await self.async_post(url, data=data)

        return json_content

    # 上传page
    async def upload_page(self, page_list:List[dict]):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/upload_page/'
        data = {
            'page_list': json.dumps(page_list),
        }

        json_content = await self.async_post(url, data=data)
        return json_content

    # 检测重复的uid
    async def check_dup_uid(self, uid_list:List[str]):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/check_dup_uid/'
        data = {
            'uid_list': json.dumps(uid_list),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 获取待爬取的page
    async def get_ready_page(self, keyword:str=None):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/get_ready_page/'
        data = {
            'keyword': keyword,
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 获取待爬取的图片
    async def get_ready_img_list(self, keyword:str=None):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/get_ready_img_list/'
        data = {
            'keyword': keyword,
        }
        json_content = self.async_post(url, data=data)
        return json_content

    # 更新page的状态
    async def update_page(self, page_dict:dict):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/update_page/'
        data = {
            'page': json.dumps(page_dict),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 更新img的状态
    async def update_img(self, img_dict_list:List[dict]):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/update_img/'
        data = {
            'img_list': json.dumps(img_dict_list),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 用于图片识别
    async def get_uncrawl_img_by_keyword(self, keyword:str):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/get_uncrawl_img_by_keyword/'
        data = {
            'keyword': keyword,
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    #上传api
    async def upload_api(self,api_dict):
        pass

    #检查api是否已被爬取
    async def is_crawled_api(self,api_uid):
        pass
    
    


if __name__ == '__main__':
    client = Client()
    res=asyncio.run(client.get_ready_page())
    print(res)