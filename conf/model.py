# -*- coding: UTF-8 -*-
# @Author  ：LLL
# @Date    ：2022/11/7 22:08

import uuid
import datetime
import os
from .conf import workdir
# 页面


class Page:

    STATUS_READY = 1
    STATUS_CRAWLED = 2
    status_mapping = {
        STATUS_READY: '待爬取',
        STATUS_CRAWLED: '已爬取'
    }

    def __init__(self, keyword, url, crawl_time=datetime.datetime.now(), status=1):
        self.url = url
        self.keyword = keyword  # 所属分类，根据哪个关键字爬取的就是哪个分类
        self.uid = uuid.uuid3(uuid.NAMESPACE_URL, self.url)  # 唯一标识
        self.status = status  # 爬取状态
        self.crawl_time = crawl_time  # 爬取的时间

    def __hash__(self) -> str:
        return self.uid


# 图片
class Img:

    STATUS_READY = 1  # 待爬取
    STATUS_CRAWLED = 2  # 已爬取
    status_mapping = {
        STATUS_READY: '待爬取',
        STATUS_CRAWLED: '已爬取'
    }

    def __init__(self, keyword, page_url,  url=None,thumb_url=None ,crawl_time=datetime.datetime.now(), status=1):
        self.url = url #原图
        self.thumb_url=thumb_url #缩略图
        self.keyword = keyword  # 所属分类，根据哪个关键字爬取的就是哪个分类
        self.uid = uuid.uuid3(uuid.NAMESPACE_URL, self.url).hex   # 唯一标识
        self.status = status  # 爬取状态
        self.page_url = page_url  # 图片所在的页面
        self.crawl_time = crawl_time  # 爬取的时间
        date_now = datetime.datetime.now()
        self.save_path = os.path.join(workdir, 'data', keyword, str(date_now.year), str(
            date_now.month), str(date_now.day), self.uid+'.jpg')  # 保存的地址

    def __hash__(self) -> str:
        return self.uid


if __name__ == '__main__':
    print(datetime.datetime.now())
    uid = uuid.uuid3(uuid.NAMESPACE_URL, 'http://www.lll.plus')   # 唯一标识
    print(uid.hex)
    print(workdir)
