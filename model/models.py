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

    fields = []

    # @get_fields
    def __init__(self, keyword: str = None, url: str = None, source: str = None, status: int = None,
                 desc: str = None, err_msg: str = None, *args, **kwargs) -> None:
        self.keyword = keyword or ''  # 关键词
        self.url = url or ''  # 地址
        self.source = source  # 爬取源
        self.status = status or self.STATUS_UNCRAWL  # 爬取状态
        self.desc = desc or ''  # 简介
        self.err_msg = err_msg or ''  # 错误信息
        self.uid = self.to_hash(self.url)  # 唯一标识

        self.__class__.fields = ['keyword', 'url', 'source', 'status', 'desc', 'err_msg', 'uid']
        self.__class__.fields.extend(args)
        self.__class__.fields.extend(kwargs.keys())

    @classmethod
    def to_hash(cls, url: str) -> int:
        return int(uuid.uuid3(uuid.NAMESPACE_URL, url).hex, 16)

    @classmethod
    def md5(cls, content: str) -> str:
        return hashlib.md5(content.encode('utf8')).hexdigest()

    def __hash__(self) -> int:
        return self.uid

    # 将一个对象转成一个字典
    def to_dict(self) -> Dict:
        con = {}
        for field in self.fields:
            con.setdefault(field, getattr(self, field))
        return con

    # 将一个字典转成对象
    @classmethod
    def to_obj(cls, obj_dict: dict):
        _self = cls()
        for attr in cls.fields:
            setattr(_self, attr, obj_dict.get(attr))
        return _self


# API
class API(Base):

    def __init__(self, keyword: str = None, url: str = None, source: str = None, status: int = None,
                 desc: str = None, err_msg: str = None, md5: str = None, *args, **kwargs) -> None:
        super(API, self).__init__(keyword=keyword, url=url, source=source, status=status, desc=desc, err_msg=err_msg,
                                  *args, **kwargs)
        self.md5 = md5
        self.__class__.fields.extend(['md5'])


# 页面
class Page(Base):
    def __init__(self, keyword: str = None, url: str = None, source: str = None, status: int = None,
                 desc: str = None, err_msg: str = None, md5: str = None, deep: int = None, api_url: str = None, *args,
                 **kwargs):
        super(Page, self).__init__(keyword=keyword, url=url, source=source, status=status, desc=desc, err_msg=err_msg,
                                   *args, **kwargs)
        self.md5 = md5
        self.deep = deep or 1  # 爬取深度
        self.api_url = api_url or ''
        self.api_uid = self.to_hash(self.api_url)

        self.__class__.fields.extend(['md5', 'deep', 'api_url', 'api_uid'])



# 图片
class Img(Base):
    FILE_IMAGE = 0  # 图片
    FILE_VIDEO = 1  # 视频
    UNDOWNLOAD = 0  # 未下载
    DOWNLOADED = 1  # 已下载
    DOWNLOADIMG = 2  # 下载中
    DOWNLOADERROR = 3  # 下载失败

    # 合格的图片
    QUALIFY = 0
    # 不合格的图片
    UNQUALIFY = 1

    def __init__(self, keyword: str = None, url: str = None, source: str = None, thumb_url: str = None,
                 page_url: str = None, status_config: dict = None, desc: str = None, err_msg: str = None,
                 is_qualify: int = None, file_type: int = None, api_url: str = None, is_download: int = None, *args,
                 **kwargs):
        super(Img, self).__init__(keyword=keyword, url=url, source=source, desc=desc, err_msg=err_msg, *args, **kwargs)

        self.thumb_url = thumb_url or ''  # 缩略图
        self.page_url = page_url or ''  # 图片所在的页面
        self.page_uid = self.to_hash(self.page_url)
        self.is_qualify = is_qualify or self.UNQUALIFY  # 是否合格,默认不合格
        self.file_type = file_type or self.FILE_IMAGE  # 文件类型
        self.api_url = api_url or ''  # api
        self.api_uid = self.to_hash(self.api_url)
        self.is_download = is_download or self.UNDOWNLOAD  # 是否已下载
        self.status_config = status_config or {}  #
        self.__save_path = os.path.join(self.save_dir, self.name)
        self.__class__.fields.extend(
            ['thumb_url', 'page_url', 'page_uid', 'is_qualify', 'file_type', 'api_url', 'api_uid', 'is_download',
             'status_config','save_path'])

    @property
    def save_dir(self):
        date_now = datetime.datetime.now()
        return os.path.join(workdir, 'data', self.keyword, str(date_now.year), str(date_now.month), str(date_now.day))
        # 创建文件保存的路径

    @property
    def name(self) -> str:
        suffix = '.jpg' if self.file_type == self.FILE_IMAGE else '.mp4'
        return str(self.uid) + suffix

    @property
    def save_path(self):
        return self.__save_path

    @save_path.setter
    def save_path(self, val):
        self.__save_path = val


if __name__ == '__main__':
    img = Img(source='百度')
    # b = img.to_dict()
    # c = Img.to_obj(b)
    # print(b)
