import requests
import json
import conf.conf as conf
import time
import asyncio


class Client:
    HOST = 'http://127.0.0.1'
    PORT = '8000'
    img_server_prefix = 'img_server'
    page_server_prefix = 'page_server'
    salt = ''

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
    }

    @classmethod
    def get(cls, url):
        return requests.get(url, headers=cls.HEADERS, verify=False, timeout=(5, 10))

    @classmethod
    def post(cls, url, data):
        return requests.post(url, headers=cls.HEADERS, data=data, verify=False, timeout=(5, 10))

    # 获取关键字列表
    def get_keyword_list(self):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/keyword_list'
        json_content = self.get(url).json()
        keyword_list = json_content['keyword_list']
        return keyword_list

    # 检测img是否已被爬取
    def is_img_crawled(self, img):
        pass

    # 检测page是否被爬取
    def is_page_crawled(self, page):
        pass

    # 上传img
    def upload_img(self, img_list):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/upload_img/'
        data = {
            'img_list': json.dumps(img_list),
        }
        json_content = self.post(url, data=data).json()

        return json_content

    @classmethod
    async def do_upload_img(cls):
        conf.img_spider_logger.warning(f'图片上传服务已启动...')
        now = time.time()
        while True:
            await asyncio.sleep(1)
            end = time.time()
            # 每10秒或者已爬取的图片集合数量大于50
            if (end - now) > 10 or len(conf.img_crawled_set) > 50:
                if len(conf.img_crawled_set) > 0:
                    img_dict_list = []
                    img_list = []
                    for img_obj in conf.img_crawled_set:
                        img_list.append(img_obj)
                        img_dict_list.append(img_obj.to_dict())
                    try:
                        res = conf.img_client.upload_img(img_dict_list)
                        if res.json()['status'] == 'success':
                            # 抛弃已经上传的
                            for img in img_list:
                                conf.img_crawled_set.discard(img)
                            conf.img_spider_logger.info(
                                f'图片上传成功,上传了{len(img_dict_list)}张图片,len(img_crawled_set)={len(conf.img_crawled_set)}...')
                        else:
                            conf.img_spider_logger.info(f'图片上传失败...')
                    except Exception as e:
                        conf.img_spider_logger.info(f'图片上传失败...msg:{e}')

                    # 重置时间
                    now = time.time()

            # 结束
            for _ in range(20):
                await asyncio.sleep(1)
                if len(conf.img_crawled_set) > 0:
                    break
            else:
                conf.img_spider_logger.warning('图片上传服务已退出...')
                break

    # 上传page
    def upload_page(self, page_list):
        url = f'{self.HOST}:{self.PORT}/{self.page_server_prefix}/upload_page/'
        data = {
            'page_list': json.dumps(page_list),
        }
        json_content = self.post(url, data=data).json()
        return json_content

    # 检测重复的uid
    def check_dup_uid(self, uid_list):
        url = f'{self.HOST}:{self.PORT}/{self.img_server_prefix}/check_dup_uid/'
        data = {
            'uid_list': json.dumps(uid_list),
        }
        json_content = self.post(url, data=data).json()
        return json_content


if __name__ == '__main__':
    client = Client()
    keyword_list = client.get_keyword_list()
    img_list = [
        {
            'url': 'www.lll.plus',
            'thumb_url': 'www.lll.plus',
        },
        {
            'url': 'www.666.plus',
            'thumb_url': 'www.666.plus',
        },
    ]

    res = client.upload_img(img_list)
    print(res.json())
