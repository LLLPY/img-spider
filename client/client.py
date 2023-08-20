import json
import aiohttp
import asyncio
from typing import *


class Client:
    img_server_prefix = 'img-spider-server/img_server'
    page_server_prefix = 'img-spider-server/page_server'
    keyword_server_prefix = 'img-spider-server/keyword_server'
    api_server_prefix = 'img-spider-server/api_server'

    def __init__(self, host, port, headers):
        self.HOST = 'http://' + host
        self.PORT = port
        self.HEADERS = headers

    async def async_get(self, url: str) -> Dict:
        timeout = aiohttp.ClientTimeout(total=10)  # 10秒过期
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=self.HEADERS) as response:
                json_content = await response.json(content_type='application/json', encoding='utf-8')
                return json_content

    async def async_post(self, url: str, data: Dict) -> Dict:
        timeout = aiohttp.ClientTimeout(total=10)  # 10秒过期
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=self.HEADERS, data=data) as response:
                json_content = await response.json(content_type='application/json', encoding='utf-8')
                return json_content

    # 获取关键字列表
    async def get_keyword_list(self) -> List[str]:
        url = f'{self.HOST}:{self.PORT}/{self.keyword_server_prefix}'
        json_content = await self.async_get(url)
        keyword_list = json_content['data']
        return keyword_list

    # 上传img
    async def upload_img(self, img_list: List[Dict]):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/upload_img'
        data = {
            'img_list': json.dumps(img_list),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 上传page
    async def upload_page(self, page_list: List[Dict]):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}'
        data = {
            'page_list': json.dumps(page_list),
        }

        json_content = await self.async_post(url, data=data)
        return json_content

    # 检测重复的uid
    async def check_dup_uid(self, uid_list: List[str]) -> object:
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/check_dup_uid'
        data = {
            'uid_list': json.dumps(uid_list),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 获取待爬取的page
    async def get_ready_page(self, keyword: str = None):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/get_ready_page'
        data = {
            'keyword': keyword,
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 获取待下载的图片
    async def get_undownload_img_list(self, keyword: str = None):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/get_undownload_img_list'
        data = {
            'keyword': keyword,
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 更新page的状态
    async def update_page(self, page_dict: Dict):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/update_page'
        data = {
            'page': json.dumps(page_dict),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 更新img的状态
    async def update_img(self, img_dict_list: List[Dict]):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/update_img'
        data = {
            'img_list': json.dumps(img_dict_list),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 用于图片识别
    async def get_uncrawl_img(self, keyword: str, source: str):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/get_uncrawl_img'
        data = {
            'keyword': keyword,
            'source': source
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 上传api
    async def upload_api(self, api_dict):
        url = f'{self.HOST}:{self.PORT}/{self.api_server_prefix}/upload_api'
        json_content = await self.async_post(url, data=api_dict)
        return json_content

    # 检查api是否已被爬取
    async def is_crawled_api(self, api_md5):
        url = f'{self.HOST}:{self.PORT}/{self.api_server_prefix}/status'
        data = {
            'md5': api_md5,
        }
        json_content = await self.async_post(url, data=data)
        return json_content


if __name__ == '__main__':
    host = '127.0.0.1'
    host = '192.168.137.1'
    port = 8000
    headers = {}
    client = Client(host, port, headers)
    img_dict = {
        'keyword': '老虎',
        'url': 'http://mms0.baidu.com/it/u=757334435,1194450662&fm=253&app=138&f=JPEG&fmt=auto&q=75?w=333&h=500',
        'source': '百度', 'status': 0, 'update_time': 1671115915.828697, 'desc': '1', 'err_msg': '2',
        'uid': 80107739018836482980858344225516516387,
        'thumb_url': 'http://mms0.baidu.com/it/u=757334435,1194450662&fm=253&app=138&f=JPEG&fmt=auto&q=75?w=333&h=500',
        'page_uid': 'https://graph.baidu.com/s?sign=1261eb90419a6975c06d901671115921&f=all&tn=pc&tn=pc&idctag=gz&idctag=gz&sids=10007_10521_10968_10974_11032_17851_17070_18101_17200_17202_18314_19192_19162_19215_19268_19280_19670_19807_20005_20013_20063_20072_20081_20091_20130_20140_20163_20172_20180_20193_20234_20243_20250_20271_20282_20292_20305_20310_1059049_1060576&sids=10007_10521_10968_10974_11032_17851_17070_18101_17200_17202_18314_19192_19162_19215_19268_19280_19670_19807_20005_20013_20063_20072_20081_20091_20130_20140_20163_20172_20180_20193_20234_20243_20250_20271_20282_20292_20305_20310_1059049_1060576&logid=2185248120&logid=2185248120&pageFrom=graph_upload_bdbox&pageFrom=graph_upload_pcshitu&srcp=&gsid=&extUiData%5BisLogoShow%5D=1&tpl_from=pc&entrance=general',
        'qualify': 1,
        'file_type': 0,
        'api_uid': '1',
        'download': 0,
        'status_config': {}
    }
    # res = asyncio.run(client.upload_img([img_dict]))
    # res = asyncio.run(client.get_keyword_list())
    # res = asyncio.run(client.check_dup_uid(['1121232323']))
    # res = asyncio.run(client.get_ready_page('苹果'))
    # res = asyncio.run(client.get_undownload_img_list('苹果'))
    # res = asyncio.run(client.update_page({}))
    # res = asyncio.run(client.update_img([]))
    # res = asyncio.run(client.get_uncrawl_img('苹果', '百度'))
    # res = asyncio.run(client.upload_api({}))
    res = asyncio.run(client.is_crawled_api('awefawefwaefa'))
    print(res)
