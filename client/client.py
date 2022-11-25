import requests
import json


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
        json_content = self.post(url, data=data)

        return json_content

    # 上传page
    def upload_page(self, page_list):
        pass


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
