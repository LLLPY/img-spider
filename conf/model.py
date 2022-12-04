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
    # 爬取错误
    STATUS_ERROR = 3
    status_mapping = {
        STATUS_UNCRAWL: '待爬取',
        STATUS_CRAWLIMG: '爬取中',
        STATUS_CRAWLED: '已爬取',
        STATUS_ERROR: '爬取错误'
    }

    # 合格的图片
    QUALIFY = 0
    # 不合格的图片
    UNQUALIFY = 1

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
            'success': self.success,
            'deep': self.deep

        }
        return dict_con

    def str_to_datetime(self, datetime_str):
        return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')


# 图片
class Img(Base):
    def __init__(self, keyword, url, page_url=None, thumb_url=None, crawl_time=datetime.datetime.now(), status=0,
                 source='', desc='', qualify=1):
        self.keyword = keyword  # 所属分类，根据哪个关键字爬取的就是哪个分类
        self.url = url  # 原图
        self.thumb_url = thumb_url  # 缩略图
        self.page_url = page_url  # 图片所在的页面
        self.uid = int(uuid.uuid3(uuid.NAMESPACE_URL, self.url).hex, 16)  # 唯一标识
        self.status = status  # 爬取状态(是否已用于图片爬取)
        self.crawl_time = crawl_time  # 爬取的时间
        self.qualify = qualify  # 是否合格,默认不合格
        self.source = source
        self.desc = desc
        self.save_path = self.create_save_path()  # 保存的地址

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
            'qualify': self.qualify,
            'desc': self.desc

        }
        return dict_con

    def create_save_path(self):
        date_now = datetime.datetime.now()
        return os.path.join(workdir, 'data', self.keyword, str(date_now.year), str(
            date_now.month), str(date_now.day), str(self.uid) + '.jpg')
    @classmethod
    def str_to_datetime(cls, datetime_str):
        return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

    # 将一个字典转成对象
    @classmethod
    def to_obj(cls, obj_dict: dict):
        img_obj = cls(keyword='', url='')
        img_obj.url = obj_dict.get('url')  # 原图
        img_obj.thumb_url = obj_dict.get('thumb_url')  # 缩略图
        img_obj.keyword = obj_dict.get('keyword')  # 所属分类，根据哪个关键字爬取的就是哪个分类
        img_obj.status = obj_dict.get('status', cls.STATUS_UNCRAWL)  # 爬取状态(是否已用于图片爬取)
        img_obj.page_url = obj_dict.get('page_url')  # 图片所在的页面
        img_obj.qualify = obj_dict.get('qualify', cls.UNQUALIFY)  # 是否合格,默认不合格
        img_obj.source = obj_dict.get('source')
        img_obj.desc = obj_dict.get('source')
        img_obj.uid = obj_dict.get('uid', cls.to_hash(img_obj.url))
        img_obj.save_path = img_obj.create_save_path()
        return img_obj


if __name__ == '__main__':
    print(datetime.datetime.now())
    uid = uuid.uuid3(uuid.NAMESPACE_URL, 'http://www.lll.plus')  # 唯一标识
    print(uid.hex)
    print(workdir)
