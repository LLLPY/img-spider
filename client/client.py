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
                # json_content = await response.json(content_type='application/json', encoding='utf-8')
                print(await response.text())
                json_content = json.loads(await response.text())
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
        print(66666)
        json_content = await self.async_post(url, data=data)
        print(json_content)
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
    page_dict_list=[{'keyword': '大象', 'url': 'https://graph.baidu.com/pcpage/similar?originSign=12634610933816428704201671007772&srcp=crs_pc_similar&tn=pc&idctag=gz&sids=10007_10521_10968_10974_11031_17850_17070_18101_17200_17202_18311_19195_19162_19215_19268_19280_19670_19807_20001_20013_20046_20060_20073_20081_20090_20133_20140_20162_20172_20181_20193_20220_20230_20243_20250_20271_20282_20292_20304_20310_1059043_1065801_20260&gsid=&logid=2290516633&entrance=general&tpl_from=pc&pageFrom=graph_upload_pcshitu&inspire=general&image=http%3A%2F%2Fmms1.baidu.com%2Fit%2Fu%3D338370534%2C1727923326%26fm%3D253%26app%3D138%26f%3DJPEG%3Fw%3D750%26h%3D500&carousel=503&index=28&page=40&shituToken=e75c70', 'source': '百度', 'status': 0, 'crawl_time': 1671007753.088035, 'desc': '', 'err_msg': '', 'uid': 166694579410544107287144189241767364810, 'deep': 1, 'api': ''}, {'keyword': '大象', 'url': 'https://graph.baidu.com/pcpage/similar?originSign=12634610933816428704201671007772&srcp=crs_pc_similar&tn=pc&idctag=gz&sids=10007_10521_10968_10974_11031_17850_17070_18101_17200_17202_18311_19195_19162_19215_19268_19280_19670_19807_20001_20013_20046_20060_20073_20081_20090_20133_20140_20162_20172_20181_20193_20220_20230_20243_20250_20271_20282_20292_20304_20310_1059043_1065801_20260&gsid=&logid=2290516633&entrance=general&tpl_from=pc&pageFrom=graph_upload_pcshitu&inspire=general&image=http%3A%2F%2Fmms0.baidu.com%2Fit%2Fu%3D2288434759%2C3546229732%26fm%3D253%26app%3D120%26f%3DJPEG%3Fw%3D500%26h%3D375&carousel=503&index=1&page=6&shituToken=4dff73', 'source': '百度', 'status': 0, 'crawl_time': 1671007753.088035, 'desc': '', 'err_msg': '', 'uid': 24294272369977674752564750235943157450, 'deep': 1, 'api': ''}, {'keyword': '大象', 'url': 'https://graph.baidu.com/pcpage/similar?originSign=12634610933816428704201671007772&srcp=crs_pc_similar&tn=pc&idctag=gz&sids=10007_10521_10968_10974_11031_17850_17070_18101_17200_17202_18311_19195_19162_19215_19268_19280_19670_19807_20001_20013_20046_20060_20073_20081_20090_20133_20140_20162_20172_20181_20193_20220_20230_20243_20250_20271_20282_20292_20304_20310_1059043_1065801_20260&gsid=&logid=2290516633&entrance=general&tpl_from=pc&pageFrom=graph_upload_pcshitu&inspire=general&image=http%3A%2F%2Fmms2.baidu.com%2Fit%2Fu%3D3396983850%2C1758481809%26fm%3D253%26app%3D138%26f%3DJPEG%3Fw%3D738%26h%3D500&carousel=503&index=25&page=20&shituToken=2d8f75', 'source': '百度', 'status': 0, 'crawl_time': 1671007753.088035, 'desc': '', 'err_msg': '', 'uid': 253920554605044482224791717059732226655, 'deep': 1, 'api': ''}, {'keyword': '大象', 'url': 'https://graph.baidu.com/pcpage/similar?originSign=12634610933816428704201671007772&srcp=crs_pc_similar&tn=pc&idctag=gz&sids=10007_10521_10968_10974_11031_17850_17070_18101_17200_17202_18311_19195_19162_19215_19268_19280_19670_19807_20001_20013_20046_20060_20073_20081_20090_20133_20140_20162_20172_20181_20193_20220_20230_20243_20250_20271_20282_20292_20304_20310_1059043_1065801_20260&gsid=&logid=2290516633&entrance=general&tpl_from=pc&pageFrom=graph_upload_pcshitu&inspire=general&image=http%3A%2F%2Fmms2.baidu.com%2Fit%2Fu%3D2825719914%2C3342725340%26fm%3D253%26app%3D138%26f%3DJPEG%3Fw%3D450%26h%3D320&carousel=503&index=29&page=35&shituToken=bef22d', 'source': '百度', 'status': 0, 'crawl_time': 1671007753.088035, 'desc': '', 'err_msg': '', 'uid': 114990179503012202466866694316095180323, 'deep': 1, 'api': ''}, {'keyword': '大象', 'url': 'https://graph.baidu.com/pcpage/similar?originSign=12634610933816428704201671007772&srcp=crs_pc_similar&tn=pc&idctag=gz&sids=10007_10521_10968_10974_11031_17850_17070_18101_17200_17202_18311_19195_19162_19215_19268_19280_19670_19807_20001_20013_20046_20060_20073_20081_20090_20133_20140_20162_20172_20181_20193_20220_20230_20243_20250_20271_20282_20292_20304_20310_1059043_1065801_20260&gsid=&logid=2290516633&entrance=general&tpl_from=pc&pageFrom=graph_upload_pcshitu&inspire=general&image=http%3A%2F%2Fmms0.baidu.com%2Fit%2Fu%3D3845637146%2C2650320396%26fm%3D253%26app%3D138%26f%3DJPEG%3Fw%3D333%26h%3D500&carousel=503&index=11&page=47&shituToken=a05d20', 'source': '百度', 'status': 0, 'crawl_time': 1671007753.088035, 'desc': '', 'err_msg': '', 'uid': 270772898336467908701664701353370484793, 'deep': 1, 'api': ''}, {'keyword': '大象', 'url': 'https://graph.baidu.com/pcpage/similar?originSign=12634610933816428704201671007772&srcp=crs_pc_similar&tn=pc&idctag=gz&sids=10007_10521_10968_10974_11031_17850_17070_18101_17200_17202_18311_19195_19162_19215_19268_19280_19670_19807_20001_20013_20046_20060_20073_20081_20090_20133_20140_20162_20172_20181_20193_20220_20230_20243_20250_20271_20282_20292_20304_20310_1059043_1065801_20260&gsid=&logid=2290516633&entrance=general&tpl_from=pc&pageFrom=graph_upload_pcshitu&inspire=general&image=http%3A%2F%2Fmms2.baidu.com%2Fit%2Fu%3D373255366%2C1648488206%26fm%3D253%26app%3D138%26f%3DJPEG%3Fw%3D752%26h%3D500&carousel=503&index=26&page=5&shituToken=39d6c2', 'source': '百度', 'status': 0, 'crawl_time': 1671007753.088035, 'desc': '', 'err_msg': '', 'uid': 194743338727000706754834856954645053486, 'deep': 1, 'api': ''}]
    # res = asyncio.run(client.upload_page(page_dict_list))
    res = asyncio.run(client.get_keyword_list())
    print(res)
