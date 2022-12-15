import json
import aiohttp
import asyncio
from typing import *


class Client:
    HOST = 'http://127.0.0.1'
    # HOST = 'http://www.lll.plus'
    PORT = '80'
    img_server_prefix = 'img-spider-server/img_server'
    page_server_prefix = 'img-spider-server/page_server'
    salt = ''
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
    }

    @classmethod
    async def async_get(cls, url: str) -> Dict:
        timeout = aiohttp.ClientTimeout(total=10)  # 10秒过期
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=cls.HEADERS) as response:
                json_content = await response.json(content_type='application/json', encoding='utf-8')
                return json_content

    @classmethod
    async def async_post(cls, url: str, data: Dict) -> Dict:
        timeout = aiohttp.ClientTimeout(total=10)  # 10秒过期
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=cls.HEADERS, data=data) as response:
                json_content = await response.json(content_type='application/json', encoding='utf-8')
                # print(await response.text())
                # json_content = json.loads(await response.text())
                return json_content

    # 获取关键字列表
    async def get_keyword_list(self) -> List[str]:
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/keyword_list'
        json_content = await self.async_get(url)
        keyword_list = json_content['keyword_list']
        return keyword_list

    # 上传img
    async def upload_img(self, img_list: List[Dict]):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/upload_img/'
        data = {
            'img_list': json.dumps(img_list),
        }
        json_content = await self.async_post(url, data=data)

        return json_content

    # 上传page
    async def upload_page(self, page_list: List[Dict]):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/upload_page/'
        data = {
            'page_list': json.dumps(page_list),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 检测重复的uid
    async def check_dup_uid(self, uid_list: List[str]):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/check_dup_uid/'
        data = {
            'uid_list': json.dumps(uid_list),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 获取待爬取的page
    async def get_ready_page(self, keyword: str = None):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/get_ready_page/'
        data = {
            'keyword': keyword,
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 获取待爬取的图片
    async def get_ready_img_list(self, keyword: str = None):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/get_ready_img_list/'
        data = {
            'keyword': keyword,
        }
        json_content = self.async_post(url, data=data)
        return json_content

    # 更新page的状态
    async def update_page(self, page_dict: Dict):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/update_page/'
        data = {
            'page': json.dumps(page_dict),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 更新img的状态
    async def update_img(self, img_dict_list: List[Dict]):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/update_img/'
        data = {
            'img_list': json.dumps(img_dict_list),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 用于图片识别
    async def get_uncrawl_img_by_keyword(self, keyword: str):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/get_uncrawl_img_by_keyword/'
        data = {
            'keyword': keyword,
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 上传api
    async def upload_api(self, api_dict):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/upload_api/'
        data = {
            'api_dict': json.dumps(api_dict),
        }
        json_content = await self.async_post(url, data=data)
        return json_content

    # 检查api是否已被爬取
    async def is_crawled_api(self, api_md5):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/is_crawled_api/'
        data = {
            'api_md5': api_md5,
        }
        json_content = await self.async_post(url, data=data)
        return json_content


if __name__ == '__main__':
    client = Client()
    img_dict = {'keyword': '老虎', 'url': 'http://mms0.baidu.com/it/u=757334435,1194450662&fm=253&app=138&f=JPEG&fmt=auto&q=75?w=333&h=500', 'source': '百度', 'status': 0, 'crawl_time': 1671115915.828697, 'desc': '', 'err_msg': '', 'uid': 80107739018836482980858344225516516387, 'thumb_url': 'http://mms0.baidu.com/it/u=757334435,1194450662&fm=253&app=138&f=JPEG&fmt=auto&q=75?w=333&h=500', 'page_url': 'https://graph.baidu.com/s?sign=1261eb90419a6975c06d901671115921&f=all&tn=pc&tn=pc&idctag=gz&idctag=gz&sids=10007_10521_10968_10974_11032_17851_17070_18101_17200_17202_18314_19192_19162_19215_19268_19280_19670_19807_20005_20013_20063_20072_20081_20091_20130_20140_20163_20172_20180_20193_20234_20243_20250_20271_20282_20292_20305_20310_1059049_1060576&sids=10007_10521_10968_10974_11032_17851_17070_18101_17200_17202_18314_19192_19162_19215_19268_19280_19670_19807_20005_20013_20063_20072_20081_20091_20130_20140_20163_20172_20180_20193_20234_20243_20250_20271_20282_20292_20305_20310_1059049_1060576&logid=2185248120&logid=2185248120&pageFrom=graph_upload_bdbox&pageFrom=graph_upload_pcshitu&srcp=&gsid=&extUiData%5BisLogoShow%5D=1&tpl_from=pc&entrance=general', 'qualify': 1, 'file_type': 0, 'api': '', 'download': 0}

    res = asyncio.run(client.upload_img([img_dict]))
    print(res)
