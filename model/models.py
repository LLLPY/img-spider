# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/7 22:08
import hashlib
import uuid
import datetime
import os
from typing import Dict

from conf.conf import workdir


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

    def __init__(self, keyword: str, url: str, source: str, status: int = STATUS_UNCRAWL,
                 crawl_time=datetime.datetime.now(), desc: str = '', err_msg: str = '') -> None:
        self.keyword = keyword  # 关键词
        self.url = url  # 地址
        self.source = source  # 爬取源
        self.status = status  # 爬取状态
        self.crawl_time = crawl_time  # 爬取的时间
        self.desc = desc  # 简介
        self.err_msg = err_msg  # 错误信息
        self.uid = int(uuid.uuid3(uuid.NAMESPACE_URL, self.url).hex, 16)  # 唯一标识

    @classmethod
    def to_hash(cls, url: str) -> int:
        return int(uuid.uuid3(uuid.NAMESPACE_URL, url).hex, 16)

    def __hash__(self) -> int:
        return self.uid

    # 将一个对象转成一个字典
    def to_dict(self) -> Dict:
        dict_con = {
            'keyword': self.keyword,
            'url': self.url,
            'source': self.source,
            'status': self.status,
            'crawl_time': self.crawl_time.timestamp(),
            'desc': self.desc,
            'err_msg': self.err_msg,
            'uid': self.uid,

        }
        return dict_con

    # 创建文件保存的路径
    def create_save_path(self) -> str:
        date_now = datetime.datetime.now()
        return os.path.join(workdir, 'data', self.keyword, str(date_now.year), str(
            date_now.month), str(date_now.day), str(self.uid) + '.jpg')

    # 将一个字典转成对象
    @classmethod
    def to_obj(cls, obj_dict: dict):
        img_obj = cls(keyword='', url='', source='')
        img_obj.keyword = obj_dict.get('keyword')  # 所属分类，根据哪个关键字爬取的就是哪个分类
        img_obj.url = obj_dict.get('url')  # 原图
        img_obj.source = obj_dict.get('source')
        img_obj.status = obj_dict.get('status', cls.STATUS_UNCRAWL)  # 爬取状态(是否已用于图片爬取)
        img_obj.crawl_time = datetime.datetime.fromtimestamp(obj_dict.get('crawl_time'))
        img_obj.desc = obj_dict.get('desc')
        img_obj.err_msg = obj_dict.get('err_msg', '')
        img_obj.uid = obj_dict.get('uid', cls.to_hash(img_obj.url))
        return img_obj


# API
class API(Base):

    def __init__(self, keyword: str, url: str, source: str, status: int = Base.STATUS_UNCRAWL,
                 crawl_time=datetime.datetime.now(), desc: str = '', err_msg: str = '', md5: str = '') -> None:
        super().__init__(keyword, url, source, status, crawl_time, desc, err_msg)
        self.md5 = md5

    @classmethod
    def md5(cls, content: str) -> str:
        return hashlib.md5(content.encode('utf8')).hexdigest()

    def to_dict(self) -> Dict:
        dict_con = super(API, self).to_dict()
        dict_con['md5'] = self.md5
        return dict_con


# 页面
class Page(Base):
    def __init__(self, keyword: str, url: str, source: str, status: int = Base.STATUS_UNCRAWL,
                 crawl_time=datetime.datetime.now(), desc: str = '', err_msg: str = '', deep: int = 1, api: str = ''):
        self.deep = deep  # 爬取深度
        self.api = api
        super().__init__(keyword=keyword, url=url, source=source, status=status, crawl_time=crawl_time, desc=desc,
                         err_msg=err_msg)

    def to_dict(self) -> dict:
        dict_con = super(Page, self).to_dict()
        dict_con.update({
            'deep': self.deep,
            'api': self.api,
        })
        return dict_con

    @classmethod
    def to_obj(cls, obj_dict: dict):
        obj = super().to_obj(obj_dict)
        obj.deep = obj_dict.get('deep', 1)
        return obj


# 图片
class Img(Base):
    FILE_IMAGE = 0  # 图片
    FILE_VIDEO = 1  # 视频
    UNDOWNLOAD = 0  # 未下载
    DOWNLOADED = 1  # 已下载

    def __init__(self, keyword: str, url: str, source: str, thumb_url: str = '', page_url: str = '',
                 status: int = Base.STATUS_UNCRAWL, crawl_time=datetime.datetime.now(),
                 desc: str = '', err_msg: str = '', qualify: int = Base.UNQUALIFY, file_type: int = FILE_IMAGE,
                 api: str = '', download=UNDOWNLOAD):
        self.thumb_url = thumb_url  # 缩略图
        self.page_url = page_url  # 图片所在的页面
        self.qualify = qualify  # 是否合格,默认不合格
        self.file_type = file_type  # 文件类型
        self.api = api  # api
        self.download = download  # 是否已下载
        super().__init__(keyword=keyword, url=url, source=source, status=status, crawl_time=crawl_time, desc=desc,
                         err_msg=err_msg)
        self.save_path = self.create_save_path()  # 保存的地址

    def to_dict(self):
        dict_con = super(Img, self).to_dict()
        dict_con.update({
            'thumb_url': self.thumb_url,
            'page_url': self.page_url,
            'qualify': self.qualify,
            'file_type': self.file_type,
            'api': self.api,
            'download': self.download

        })
        return dict_con

    # 将一个字典转成对象
    @classmethod
    def to_obj(cls, obj_dict: dict):
        obj = super().to_obj(obj_dict)
        obj.thumb_url = obj_dict.get('thumb_url')  # 缩略图
        obj.page_url = obj_dict.get('page_url')  # 图片所在的页面
        obj.qualify = obj_dict.get('qualify', cls.UNQUALIFY)  # 是否合格,默认不合格
        obj.save_path = obj.create_save_path()
        return obj


if __name__ == '__main__':
    img = Img('a', 'b', 'c')
    b = img.to_dict()
    a = Img.to_obj(b)
    print(a.crawl_time)
