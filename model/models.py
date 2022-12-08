# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/7 22:08

import uuid
import datetime
import os
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

    def __init__(self,keyword:str,url:str,source:str,status:int=STATUS_UNCRAWL,crawl_time=datetime.datetime.now(),desc:str='',err_msg:str='') -> None:
        self.keyword=keyword #关键词
        self.url=url # 地址
        self.source=source #爬取源
        self.status = status  # 爬取状态
        self.crawl_time = crawl_time  # 爬取的时间
        self.desc=desc #简介
        self.err_msg=err_msg #错误信息
        self.uid = int(uuid.uuid3(uuid.NAMESPACE_URL, self.url).hex, 16)  # 唯一标识

    @classmethod
    def to_hash(cls, url):
        return int(uuid.uuid3(uuid.NAMESPACE_URL, url).hex, 16)

    
    def __hash__(self) -> int:
        return self.uid
    
    #将一个对象转成一个字典
    def to_dict(self):
        
        dict_con = {
            'keyword': self.keyword,
            'url': self.url,
            'source': self.source,
            'status': self.status,
            # 'crawl_time':self.crawl_time.timestamp(),
            'desc': self.desc,
            'err_msg':self.err_msg,
            'uid': self.uid,

        }
        return dict_con
    
    
    # 将一个字典转成对象
    @classmethod
    def to_obj(cls, obj_dict: dict):
        img_obj = cls(keyword='', url='',source='')
        img_obj.keyword = obj_dict.get('keyword')  # 所属分类，根据哪个关键字爬取的就是哪个分类
        img_obj.url = obj_dict.get('url')  # 原图
        img_obj.source = obj_dict.get('source')
        img_obj.status = obj_dict.get('status', cls.STATUS_UNCRAWL)  # 爬取状态(是否已用于图片爬取)
        # img_obj.crawl_time=obj_dict.get('crawl_time')
        img_obj.desc = obj_dict.get('desc')
        img_obj.err_msg=obj_dict.get('err_msg','')
        img_obj.uid = obj_dict.get('uid', cls.to_hash(img_obj.url))
        return img_obj
    
    @classmethod
    def str_to_datetime(cls, datetime_str):
        return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    
    
    
# 页面
class Page(Base):
    def __init__(self, keyword:str, url:str, source:str,status:int=Base.STATUS_UNCRAWL,crawl_time=datetime.datetime.now(), desc:str='',err_msg:str='',deep=1):
        self.deep = deep  # 爬取深度
        super().__init__(self,keyword=keyword,url=url,source=source,status=status,crawl_time=crawl_time,desc=desc,err_msg=err_msg)

    
    def to_dict(self):
        dict_con=super(Page,self).to_dict()
        dict_con.update( {
            'deep': self.deep
        })
        return dict_con

    @classmethod
    def to_obj(cls, obj_dict: dict):
        obj= super().to_obj(obj_dict)
        obj.deep=obj_dict.get('deep',1)
        return obj



# 图片
class Img(Base):
    def __init__(self, keyword:str, url:str, source:str,  thumb_url:str='',page_url:str='', status:int=Base.STATUS_UNCRAWL,crawl_time=datetime.datetime.now(),
                  desc:str='',err_msg:str='', qualify:int=Base.UNQUALIFY):
        self.thumb_url = thumb_url  # 缩略图
        self.page_url = page_url  # 图片所在的页面
        self.qualify = qualify  # 是否合格,默认不合格
        self.save_path = self.create_save_path()  # 保存的地址
        super().__init__(self,keyword=keyword,url=url,source=source,status=status,crawl_time=crawl_time,desc=desc,err_msg=err_msg)

    def to_dict(self):
        dict_con=super(Img,self).to_dict()
        dict_con.update({
            'thumb_url': self.thumb_url,
            'page_url': self.page_url,
            'qualify': self.qualify,

        })
        return dict_con

    #创建文件保存的路径
    def create_save_path(self):
        date_now = datetime.datetime.now()
        return os.path.join(workdir, 'data', self.keyword, str(date_now.year), str(
            date_now.month), str(date_now.day), str(self.uid) + '.jpg')
        
    

    # 将一个字典转成对象
    @classmethod
    def to_obj(cls, obj_dict: dict):
        obj= super().to_obj(obj_dict)
        obj.thumb_url = obj_dict.get('thumb_url')  # 缩略图
        obj.page_url = obj_dict.get('page_url')  # 图片所在的页面
        obj.qualify = obj_dict.get('qualify', cls.UNQUALIFY)  # 是否合格,默认不合格
        obj.save_path = obj.create_save_path()
        return obj


if __name__ == '__main__':
    print(datetime.datetime.now())
    uid = uuid.uuid3(uuid.NAMESPACE_URL, 'http://www.lll.plus')  # 唯一标识
    print(uid.hex)
    print(workdir)
