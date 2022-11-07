# -*- coding: UTF-8 -*-                            
# @Author  ：LLL                         
# @Date    ：2022/11/7 22:08  
import pickle
import os

#页面
class Page:

    def __int__(self, url, keyword, uid, crawl_time, status):
        self.url = url
        self.keyword = keyword  # 所属分类，根据哪个关键字爬取的就是哪个分类
        self.uid = uid  # 唯一标识
        self.status = status  # 爬取状态

#图片
class Img:
    def __int__(self, url, keyword, uid, crawl_time, status,page_url):
        self.url = url
        self.keyword = keyword  # 所属分类，根据哪个关键字爬取的就是哪个分类
        self.uid = uid  # 唯一标识
        self.status = status  # 爬取状态
        self.page_url=page_url #图片所在的页面


class MyPickle:

    def __int__(self,file_path):
        self.file_path=file_path
        if not os.path.isfile(self.file_path):
            return

    def load(self):

        with open(self.file_path,'rb') as f:
            pickle.load(f)


    def dump(self,obj):
        pickle.dump(obj,self.file_path)
