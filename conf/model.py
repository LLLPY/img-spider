# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/7 22:08

import uuid
import datetime
import os
from .conf import workdir


class Base:
    # 待爬取
    STATUS_UNCRAWL = 0
    # 爬取中
    STATUS_CRAWLIMG = 1
    # 已爬取
    STATUS_CRAWLED = 2
    status_mapping = {
        STATUS_UNCRAWL: '待爬取',
        STATUS_CRAWLIMG: '爬取中',
        STATUS_CRAWLED: '已爬取'
    }

    @classmethod
    def to_hash(cls, url):
        return int(uuid.uuid3(uuid.NAMESPACE_URL, url).hex, 16)


# 页面
class Page(Base):
    def __init__(self, keyword, url, crawl_time=datetime.datetime.now(), success=False, status=0, source='', deep=1,
                 img_count=0):
        self.url = url
        self.keyword = keyword  # 所属分类，根据哪个关键字爬取的就是哪个分类
        self.uid = int(uuid.uuid3(uuid.NAMESPACE_URL, self.url).hex, 16)  # 唯一标识
        self.status = status  # 爬取状态
        self.img_count = img_count  # 抽取到的图片数量
        self.crawl_time = crawl_time  # 爬取的时间
        self.deep = deep  # 爬取深度
        self.success = success  # 是否爬取成功

        self.source = source

    def __hash__(self) -> int:
        return self.uid

    def to_dict(self):
        dict_con = {
            'url': self.url,
            'keyword': self.keyword,
            'uid': self.uid,
            'status': self.status,
            'source': self.source,
            'img_count': self.img_count,
            'crawl_time': self.crawl_time.strftime('%Y-%m-%d %H:%M:%S'),
            'success': self.success,
            'deep': self.deep

        }
        return dict_con

    def str_to_datetime(self, datetime_str):
        return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')


# 图片
class Img(Base):
    def __init__(self, keyword, page_url, url=None, thumb_url=None, crawl_time=datetime.datetime.now(), success=False,
                 status=0, source='', desc='', qualify=1):
        self.url = url  # 原图
        self.thumb_url = thumb_url  # 缩略图
        self.keyword = keyword  # 所属分类，根据哪个关键字爬取的就是哪个分类
        self.uid = int(uuid.uuid3(uuid.NAMESPACE_URL, self.url).hex, 16)  # 唯一标识
        self.status = status  # 爬取状态(是否已用于图片爬取)
        self.page_url = page_url  # 图片所在的页面
        self.crawl_time = crawl_time  # 爬取的时间
        self.success = success  # 是否爬取成功
        self.qualify = qualify  # 是否合格,默认不合格
        date_now = datetime.datetime.now()
        self.source = source
        self.desc = desc
        self.save_path = os.path.join(workdir, 'data', keyword, str(date_now.year), str(
            date_now.month), str(date_now.day), str(self.uid) + '.jpg')  # 保存的地址

    def __hash__(self) -> int:
        return self.uid

    def to_dict(self):
        dict_con = {
            'url': self.url,
            'thumb_url': self.thumb_url,
            'keyword': self.keyword,
            'uid': self.uid,
            'status': self.status,
            'page_url': self.page_url,
            'source': self.source,
            'crawl_time': self.crawl_time.strftime('%Y-%m-%d %H:%M:%S'),
            'success': self.success,
            'qualify': self.qualify,
            'desc': self.desc

        }
        return dict_con


if __name__ == '__main__':
    print(datetime.datetime.now())
    uid = uuid.uuid3(uuid.NAMESPACE_URL, 'http://www.lll.plus')  # 唯一标识
    print(uid.hex)
    print(workdir)
